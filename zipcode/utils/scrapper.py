import nest_asyncio
import asyncio
import base64
from pyppeteer import launch
import json
from .gemini_intent import get_search_intent
from asyncio import Semaphore
from .fetch_price import fetch_telemart_data, fetch_homeshopping_data, fetch_gulahmed_data,\
                        fetch_daraz_data, fetch_priceoye_data, fetch_bonanzasatrangi_data

# Semaphore to limit the number of concurrent browsers to 4
semaphore = Semaphore(1)

nest_asyncio.apply()

# Website constants
HOMESHOPPING = "homeshopping"
TELEMART = "telemart"

DARAZ = "daraz"
GULAHMED = "gulahmed"
PRICEOYE= "priceoye"
BONANZASATRANGI="bonanza satrangi"

WEBSITES = {
    # DARAZ: "www.daraz.pk",
    # PRICEOYE: "priceoye.pk",
    GULAHMED: "gulahmedshop.com",
    BONANZASATRANGI:"bonanzasatrangi.com"

}

# Configurations
HEADLESS_MODE = False
CHROME_PATH = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
TIMEOUT = 60
RETRY_INTERVAL = 1

def image_to_base64(image_path):
    """Convert image to base64."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded_string}"

def check_website_in_url(url):
    """Identify the website based on the URL."""
    for key, site in WEBSITES.items():
        if site in url:
            return key
    return None

async def google_lens_search(file_path=None):
    """Perform Google Lens search and fetch product details."""
    async with semaphore:  # Semaphore to limit concurrent browsers
        browser = await launch(headless=HEADLESS_MODE, executablePath=CHROME_PATH)
        page = await browser.newPage()
        await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        print("Step 1: Browser launched and user agent set.")
        
        await page.goto("https://lens.google.com/")
        print("Step 2: Google Lens website loaded.")
        
        await page.waitForSelector('input[placeholder="Paste image link"]', visible=True)
        print("Step 3: Paste image link input found.")
        
        if file_path:
            base64_image = image_to_base64(file_path)
            await page.evaluate('''(base64_image) => {
                document.querySelector('input[placeholder="Paste image link"]').value = base64_image;
            }''', base64_image)
            print("Step 4: Base64 image data set in input field.")
            
            await page.waitForSelector('div[jsname="ZtOxCb"]', visible=True)
            await page.click('div[jsname="ZtOxCb"]')
            print("Step 5: Clicked on search button.")
        
        initial_url = page.url
        try:
            elapsed = 0
            while page.url == initial_url and elapsed < TIMEOUT:
                await asyncio.sleep(RETRY_INTERVAL)
                elapsed += RETRY_INTERVAL
                print("Waiting for the URL to change...")

            if page.url == initial_url:
                raise TimeoutError("Timeout: URL did not change.")
            print("Step 6: URL changed to:", page.url)
        except Exception as e:
            print(f"Error waiting for URL to change: {e}")
            await browser.close()
            return []

        await page.waitForSelector('div.G19kAf.ENn9pd', visible=True)
        elements = await page.querySelectorAll('div.G19kAf.ENn9pd')
        print(f"Found {len(elements)} elements with images and titles.")
        
        results = []
        filtered_results=[]
        for element in elements:
            try:
                img = await element.querySelector('div.Me0cf > img')
                title = await element.querySelector('div.UAiK1e')
                product_url = await element.querySelector('div.Vd9M6 > a')
                product_url = await page.evaluate('(product_url) => product_url.getAttribute("href")', product_url)
                
                img_src = await page.evaluate('(img) => img.getAttribute("src")', img)
                if str(img_src).startswith("data:image"):
                    img_src = await page.evaluate('(img) => img.getAttribute("data-src")', img)
                
                title_text = await page.evaluate('(title) => title.innerText', title)
                results.append({'img_src': img_src, 'title': title_text, "product_url": product_url})
                site_found=check_website_in_url(product_url)
                if site_found:
                    filtered_results.append({'img_src': img_src, 'title': title_text, "product_url": product_url,"site":site_found})
            except Exception as e:
                print(f"Error processing element: {e}")

        await page.screenshot({'path': 'google_lens_results_page.png'})
        print("Step 8: Screenshot taken of the results page.")
        
        await browser.close()
        return results[0:5],filtered_results

async def fetch_daraz_data_with_semaphore(product_url):
    async with semaphore:
        return await fetch_daraz_data(product_url)

async def google_images_search(intent, website):
    """Search the intent on Google Images and fetch product details."""
    browser = await launch(headless=HEADLESS_MODE, executablePath=CHROME_PATH)
    page = await browser.newPage()
    # intent=intent.replace(' ','+')
    # search_query = f"{intent}+{website.replace(' ','+')}"
    # google_page=f"https://www.google.com/search?q={search_query}&udm=2"
    search_query = f"{intent}+{website}"
    google_page=f"https://www.google.com/search?tbm=isch&q={search_query}"
    print(google_page,"google_page")
    await page.goto(google_page)
    print(f"Searching for {intent} on {website}...")

    retries = 2
    product_elements = []
    while retries > 0:
        try:
            await page.waitForSelector('div[jscontroller="XW992c"]', visible=True, timeout=5000)
            main_element = await page.querySelector('div[jscontroller="XW992c"]')
            product_elements = await main_element.querySelectorAll('div[jsname="dTDiAc"]')
            break
        except Exception:
            try:
                await page.waitForSelector('div[jscontroller="r5xl4"]', visible=True, timeout=5000)
                main_element = await page.querySelector('div[jscontroller="r5xl4"]')
                product_elements = await main_element.querySelectorAll('div[jsname="N9Xkfe"]')
                break
            except Exception as e:
                print(f"Attempt failed: {e}. Reloading page...")
                retries -= 1
                if retries > 0:
                    await page.reload(waitUntil='networkidle2')
                else:
                    print("Failed to find main container after multiple attempts.")
                    await browser.close()
                    return []

    print(f"Found {len(product_elements)} product elements.")

    # Collect all valid products, ensuring unique product URLs
    valid_products = {}
    results = []
    successful_count = 0

    for element in product_elements:
        if successful_count >= 8:
            break

        try:
            image_parent_div = await element.querySelector('div.H8Rx8c')
            img_element = await image_parent_div.querySelector('img:first-of-type')
            img_src = await page.evaluate('(img) => img.getAttribute("src")', img_element)

            if img_src.startswith("data:image/gif;base64,"):
                img_src = None

            title = await page.evaluate('(element) => element.querySelector("div.toI8Rb.OSrXXb").innerText', element)

            product_url = await page.evaluate('(element) => element.getAttribute("data-lpage")', element)
            if not product_url:
                product_url = await page.evaluate(
                    '(element) => element.querySelector("div.juwGPd a").getAttribute("href")', 
                    element
                )

            if WEBSITES[website] in product_url and product_url not in valid_products and "blog" not in product_url:
                valid_products[product_url] = {
                    'img_src': img_src,
                    'title': title,
                    'product_url': product_url,
                }

            successful_count += 1
        except Exception as e:
            print(f"Error processing product element: {e}")

    print(f"Found {len(valid_products)} valid products with URLs containing {WEBSITES[website]}.")

    await browser.close()

    # Run tasks for these valid products
    tasks = [
        fetch_price_and_store_result(
            product['img_src'], product['title'], product['product_url'], website, results
        )
        for product in valid_products.values()
    ]
    await asyncio.gather(*tasks)
    return results

async def fetch_price_and_store_result(img_src, title, product_url, website, image_results):
    """Fetch price and store the result, using the utils functions for homeshopping and telemart."""
    try:
        if website == HOMESHOPPING:
            product_data = fetch_homeshopping_data(product_url)
            if product_data:
                if product_data["img_src"] == '':
                    product_data["img_src"] = img_src
                image_results.append(product_data)
                return True  # Successful result
            else:
                print(f"Could not fetch data for {product_url} on Homeshopping.")
        
        elif website == TELEMART:
            product_data = fetch_telemart_data(product_url)
            if product_data:
                image_results.append(product_data)
                return True  # Successful result
            else:
                print(f"Could not fetch data for {product_url} on Telemart.")
        
        elif website == GULAHMED:
            product_data = fetch_gulahmed_data(product_url)
            # print(product_data,"here")
            if product_data:
                image_results.append(product_data)
                return True  # Successful result
            else:
                print(f"Could not fetch data for {product_url} on Gul Ahmed.")

        elif website == DARAZ:
            product_data = await fetch_daraz_data_with_semaphore(product_url)  # Use the semaphore-wrapped version
            if product_data:
                image_results.append(product_data)
                return True  # Successful result
            else:
                print(f"Could not fetch data for {product_url} on Daraz.")

        elif website == PRICEOYE:
            product_data = fetch_priceoye_data(product_url)  # Use the semaphore-wrapped version
            if product_data:
                image_results.append(product_data)
                return True  # Successful result
            else:
                print(f"Could not fetch data for {product_url} on Priceoye.")

        elif website == BONANZASATRANGI:
            product_data = fetch_bonanzasatrangi_data(product_url)  # Use the semaphore-wrapped version
            if product_data:
                image_results.append(product_data)
                return True  # Successful result
            else:
                print(f"Could not fetch data for {product_url} on Priceoye.")

        else:
            print(f"Website {website} is not supported.")
    
    except Exception as e:
        print(f"Error fetching data for {product_url} on {website}: {e}")

    return False  # If the function reaches here, it was not successful

async def image_search(file_path):
    results,filtered_results = await google_lens_search(file_path=file_path)
    print(results,"---results---")
    intent = get_search_intent(str(results),file_path)
    print("Search intent:", type(intent), intent)
    print(filtered_results,"filtered_results")
    fetch_filter_product=[]
    for product in filtered_results:
        await fetch_price_and_store_result(
                product['img_src'], product['title'], product['product_url'], product['site'], fetch_filter_product
            )
    collection = fetch_filter_product
    for website in WEBSITES:
        try:
            search_results = await google_images_search(intent["search_intent"], website)
            collection.extend(search_results)
        except Exception as e:
            print(f"Could not find this product for {website}: {e}")
    return collection


async def text_search(search_text):
    # results,filtered_results = await google_lens_search(file_path=file_path)
    # print(results,"---results---")
    # intent = get_search_intent(str(results),file_path)
    # print("Search intent:", type(intent), intent)
    # print(filtered_results,"filtered_results")
    # fetch_filter_product=[]
    # for product in filtered_results:
    #     await fetch_price_and_store_result(
    #             product['img_src'], product['title'], product['product_url'], product['site'], fetch_filter_product
    #         )
    collection = []
    for website in WEBSITES:
        try:
            search_results = await google_images_search(search_text, website)
            collection.extend(search_results)
        except Exception as e:
            print(f"Could not find this product for {website}: {e}")
    return collection

async def main():
    file_path = "./test_data/daraz/d1.jpg"  # Replace with your image path
    # file_path = "./test_data/ideas/ideas2.jpg"  # Replace with your image path

    results,filtered_results = await google_lens_search(file_path=file_path)
    intent = get_search_intent(str(results))
    print("Search intent:", type(intent), intent)
    print(filtered_results,"filtered_results")
    fetch_filter_product=[]
    for product in filtered_results:
        fetch_price_and_store_result(
                product['img_src'], product['title'], product['product_url'], website, fetch_filter_product
            )
        
    collection = fetch_filter_product
    for website in WEBSITES:
        print(website,"searching here")
        search_results = await google_images_search(intent["search_intent"], website)
        collection.extend(search_results)

if __name__ == "__main__":
    asyncio.run(main())
