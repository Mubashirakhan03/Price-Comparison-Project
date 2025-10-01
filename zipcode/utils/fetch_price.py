import requests
from bs4 import BeautifulSoup
import json
import asyncio
import re

def fetch_homeshopping_data(product_url):
    """Fetch product data from a Homeshopping product page."""
    try:
        response = requests.get(product_url, timeout=10)  # Set timeout to 10 seconds
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize variables
        img_src = None
        title = None
        price = None
        
        # Find all <script> tags containing JSON-LD data
        script_tags = soup.find_all('script', type='application/ld+json')
        
        for script in script_tags:
            try:
                # Parse the JSON-LD data
                json_data = json.loads(script.string)
                
                # Check if the JSON-LD data is of type "Product"
                if json_data.get("@type") == "Product":
                    # Extract the necessary fields
                    img_src = json_data.get('image', None)
                    title = json_data.get('name', 'Title not available')
                    product_url = json_data.get('offers', {}).get('url', product_url)
                    price = json_data['offers'].get('price', 'Price not available')
                    website = 'homeshopping'
                    
                    # Break out of the loop if we found valid data
                    break
            except json.JSONDecodeError:
                # Skip any scripts that don't contain valid JSON
                continue
        
        # If img_src is empty, fetch it from the first <li> in the #glasscase <ul>
        if not img_src:
            glasscase = soup.find('ul', id='glasscase')
            if glasscase:
                first_li = glasscase.find('li')
                if first_li and first_li.find('img'):
                    img_src = first_li.find('img')['src']
                else:
                    img_src = 'Image not available'
            else:
                img_src = 'Image not available'
        
        if not title:
            title = 'Title not available'

        # Return the data in the requested format
        return {
            'img_src': img_src,
            'title': title,
            'product_url': product_url,
            'site': website,
            'price': f'PKR {price}' if price else 'Price not available'
        }

    except requests.exceptions.Timeout:
        print(f"Request timed out for {product_url} on Homeshopping.")
    except requests.RequestException as e:
        print(f"Request error for {product_url} on Homeshopping: {e}")
    except Exception as e:
        print(f"Error processing data for {product_url} on Homeshopping: {e}")
    return None

def fetch_telemart_data(product_url):
    """Fetch product data from a Telemart product page."""
    try:
        response = requests.get(product_url, timeout=10)  # Set timeout to 10 seconds
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the <script> tag containing the JSON-LD data
        script_tag = soup.find('script', type='application/ld+json')
        
        if not script_tag:
            print("Could not find the JSON-LD data on the page.")
            return None
        
        # Parse the JSON-LD data
        json_data = json.loads(script_tag.string)
        
        # Extract the necessary fields
        img_src = json_data.get('image', 'Image not available')
        title = json_data.get('name', 'Title not available')
        product_url = json_data.get('url', product_url)
        price = json_data['offers'].get('price', 'Price not available')
        website = 'telemart'

        # Return the data in the requested format
        return {
            'img_src': img_src,
            'title': title,
            'product_url': product_url,
            'site': website,
            'price': f'PKR {price}' if price else 'Price not available'
        }

    except requests.exceptions.Timeout:
        print(f"Request timed out for {product_url} on Telemart.")
    except requests.RequestException as e:
        print(f"Request error for {product_url} on Telemart: {e}")
    except Exception as e:
        print(f"Error processing data for {product_url} on Telemart: {e}")
    return None

# # Example usage
# product_url = "https://homeshopping.pk/products/WestPoint-Induction-Cooker-WF142-Price-In-Pakistan-.html"
# product_data = fetch_homeshopping_data(product_url)
# print(product_data)



# # Example usage
# product_url = "https://homeshopping.pk/products/Apple-AirPod-Pro-with-Wireless-Charging-Case-%28-Replica%29.html"
# product_data = fetch_homeshopping_data(product_url)
# print(product_data)


import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_priceoye_data(product_url):
    """Fetch product data from a PriceOye product page."""
    try:
        response = requests.get(product_url, timeout=10)  # Set timeout to 10 seconds
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the <script> tag containing the product data
        script_tag = None
        for script in soup.find_all('script'):
            if script.string and "window.product_data" in script.string:
                script_tag = script
                print("found the script tag")
                break
        
        if not script_tag:
            print("Could not find the product data script on the page.")
            return None
        
        # Extract the JSON data from the script
        script_content = script_tag.string
        # print(script_content,"script_content")
        json_data_match = re.search(r'window\.product_data\s*=\s*(\{.*\})', script_content, re.DOTALL)
        if not json_data_match:
            print("Could not extract JSON data from the script.")
            return None
        
        json_data = json.loads(json_data_match.group(1))
        
        # Extract the necessary fields from the JSON data
        product_config = json_data.get("product_config", {})
        dataSet = json_data.get("dataSet", {})
        # Assuming we are looking for the first available price option
        img_src, title, price, rating, product_url = None, None, None, None, product_url
        price = product_config.get('selectedStorePrice', 'Price not available')
        title = dataSet.get('title', 'Title not available')
        rating = dataSet.get('rating_stars', 0)
        images = dataSet.get('api_image', [])
        img_src = images[0]

        if not img_src or not title or not price or not rating:
            print("No valid price information found.")
            return None

        website = 'priceoye'

        # Return the data in the requested format
        return {
            'img_src': img_src,
            'title': title,
            'product_url': product_url,
            'site': website,
            'rating':rating,
            'price': f'PKR {price}' if price else 'Price not available'
        }

    except requests.exceptions.Timeout:
        print(f"Request timed out for {product_url} on PriceOye.")
    except requests.RequestException as e:
        print(f"Request error for {product_url} on PriceOye: {e}")
    except Exception as e:
        print(f"Error processing data for {product_url} on PriceOye: {e}")
    return None


# # Example usage
# product_url = "https://priceoye.pk/wireless-earbuds/assorted/m10-tws-wireless-bluetooth-earbuds"
# product_data = fetch_priceoye_data(product_url)
# print(product_data)


import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_bonanzasatrangi_data(product_url):
    """Fetch product data from a Bonanza Satrangi product page."""
    try:
        response = requests.get(product_url, timeout=10)  # Set timeout to 10 seconds
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the <script> tag with id="web-pixels-manager-setup"
        script_tag = soup.find('script', id='web-pixels-manager-setup')
        
        if not script_tag:
            print("Could not find the web pixels manager script on the page.")
            return None
        
        script_content = script_tag.string
        
        # Save the script content to a file for inspection
        with open('bonanzasatrangi_script_content.txt', 'w', encoding='utf-8') as file:
            file.write(script_content)

        # Adjust regex to capture JSON object, accounting for nested braces
        json_data_match = re.search(r'initData:\s*(\{(?:[^{}]*|\{(?:[^{}]*|\{[^{}]*\})*\})*\})\s*,', script_content, re.DOTALL)
        
        if not json_data_match:
            print("Could not extract JSON data from the script.")
            return None
        
        json_data_str = json_data_match.group(1)
        
        # Attempt to parse the JSON data
        try:
            json_data = json.loads(json_data_str)
            print("JSON Data Successfully Parsed")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw JSON content: {json_data_str[:500]}")  # Print the first 500 characters for debugging
            return None
        
        # Extract the necessary fields from the JSON data
        shop_data = json_data.get("shop", {})
        product_variants = json_data.get("productVariants", [])
        
        if not product_variants:
            print("No product variants found.")
            return None

        # Assuming we are looking for the first product variant
        product_variant = product_variants[0]
        title = product_variant.get("product", {}).get("title", "Title not available")
        price = product_variant.get("price", {}).get("amount", "Price not available")
        img_src = product_variant.get("image", {}).get("src", "Image not available")
        product_url = product_variant.get("product", {}).get("url", product_url)

        website = shop_data.get("name", "Bonanza Satrangi")
        data = {
            'img_src': img_src,
            'title': title,
            'product_url': f'https://bonanzasatrangi.com{product_url}',
            'site': website,
            'price': f'PKR {price}' if price else 'Price not available'
        }
        # print(data,"data")
        # Return the data in the requested format
        return data

    except requests.exceptions.Timeout:
        print(f"Request timed out for {product_url} on Bonanza Satrangi.")
    except requests.RequestException as e:
        print(f"Request error for {product_url} on Bonanza Satrangi: {e}")
    except Exception as e:
        print(f"Error processing data for {product_url} on Bonanza Satrangi: {e}")
    return None

# # Example usage
# if __name__ == "__main__":
#     url = "https://bonanzasatrangi.com/products/asr233p17-blue"
#     data = fetch_bonanzasatrangi_data(url)
#     print(data)



# import requests
# from bs4 import BeautifulSoup
# import json
# import re

# def fetch_gulahmed_data(product_url):
#     """Fetch product data from a GulAhmed product page."""
#     try:
#         response = requests.get(product_url, timeout=10)  # Set timeout to 10 seconds
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Initialize variables
#         img_srcs = []
#         title = None
#         price = None
#         website = 'gulahmedshop'

#         # Find all <script> tags of type text/x-magento-init
#         script_tags = soup.find_all('script', type='text/x-magento-init')

#         for script in script_tags:
#             try:
#                 # Parse the JSON data within the script tag
#                 json_data = json.loads(script.string)

#                 if json_data and "[data-role=swatch-options]" in json_data:
#                     product_data = json_data["[data-role=swatch-options]"]["Magento_Swatches/js/swatch-renderer"]["jsonConfig"]
                    
#                     # Extract the image URLs from the galleryData
#                     if "magictoolbox" in product_data:
#                         if "galleryData" in product_data["magictoolbox"]:
#                             gallery_data = product_data["magictoolbox"]["galleryData"]
#                             for key, html in gallery_data.items():
#                                 if html:
#                                     # Create a new BeautifulSoup object for each HTML string
#                                     img_soup = BeautifulSoup(html, 'html.parser')
#                                     img_tag = img_soup.find('img')
#                                     if img_tag and img_tag['src']:
#                                         img_srcs.append(img_tag['src'])

#                     prices = product_data.get("prices", {})
#                     final_price_data = prices.get("finalPrice", {})
#                     price = final_price_data.get("amount", 'Price not available')

#                     title = soup.find("h1", class_="page-title").get_text(strip=True)  # Assuming the title is in an h1 tag with class "page-title"
                    
#                     break  # Break out of the loop after finding the relevant data
#             except (json.JSONDecodeError, KeyError) as e:
#                 # Skip any scripts that don't contain valid JSON or don't have the expected structure
#                 continue
        
#         if not img_srcs:
#             img_srcs = ['Image not available']
        
#         if not title:
#             title = 'Title not available'

#         # Return the data in the requested format
#         return {
#             'img_srcs': img_srcs,
#             'title': title,
#             'product_url': product_url,
#             'site': website,
#             'price': f'PKR {price}' if price else 'Price not available'
#         }

#     except requests.exceptions.Timeout:
#         print(f"Request timed out for {product_url} on GulAhmed.")
#     except requests.RequestException as e:
#         print(f"Request error for {product_url} on GulAhmed: {e}")
#     except Exception as e:
#         print(f"Error processing data for {product_url} on GulAhmed: {e}")
#     return None



# using [data-role=swatch-options]
# import requests
# from bs4 import BeautifulSoup
# import json
# import re

# def fetch_gulahmed_data(product_url):
#     """Fetch product data from a GulAhmed product page."""
#     try:
#         response = requests.get(product_url, timeout=10)  # Set timeout to 10 seconds
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Initialize variables
#         img_src = None
#         title = None
#         price = None
#         website = 'gulahmedshop'

#         # Find all <script> tags of type text/x-magento-init
#         script_tags = soup.find_all('script', type='text/x-magento-init')

#         for script in script_tags:
#             try:
#                 # Parse the JSON data within the script tag
#                 json_data = json.loads(script.string)

#                 # Example: We're interested in the part of the JSON that has "jsonConfig" as a key
#                 if json_data and "[data-role=swatch-options]" in json_data:
#                     product_data = json_data["[data-role=swatch-options]"]["Magento_Swatches/js/swatch-renderer"]["jsonConfig"]
                    
#                     # Extract the image URLs from the galleryData
#                     if "magictoolbox" in product_data:
#                         if "galleryData" in product_data["magictoolbox"]:
#                             gallery_data = product_data["magictoolbox"]["galleryData"]
#                             for key, html in gallery_data.items():
#                                 if html:
#                                     # Extract image src using regex
#                                     img_matches = re.findall(r'<img.*?src="(.*?)"', html)
#                                     img_src=img_matches[0]
#                                     break

#                     prices = product_data.get("prices", {})
#                     final_price_data = prices.get("finalPrice", {})
#                     price = final_price_data.get("amount", 'Price not available')

#                     title = soup.find("h1", class_="page-title").get_text(strip=True)  # Assuming the title is in an h1 tag with class "page-title"
                    
#                     break  # Break out of the loop after finding the relevant data
#             except (json.JSONDecodeError, KeyError) as e:
#                 # Skip any scripts that don't contain valid JSON or don't have the expected structure
#                 continue
        
#         if not img_src:
#             img_src = 'Image not available'
        
#         if not title:
#             title = 'Title not available'
#         data={
#             'img_src': img_src,
#             'title': title,
#             'product_url': product_url,
#             'site': website,
#             'price': f'PKR {price}' if price else 'Price not available'
#         }
#         print(data,"data")
#         # Return the data in the requested format
#         return data

#     except requests.exceptions.Timeout:
#         print(f"Request timed out for {product_url} on GulAhmed.")
#     except requests.RequestException as e:
#         print(f"Request error for {product_url} on GulAhmed: {e}")
#     except Exception as e:
#         print(f"Error processing data for {product_url} on GulAhmed: {e}")
#     return None




def fetch_gulahmed_data(product_url):
    """Fetch product data from a GulAhmed product page."""
    try:
        response = requests.get(product_url, timeout=10)  # Set timeout to 10 seconds
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # Initialize variables
        price = None
        img_src = None
        title = None

        # Step 1: Extract Price and Img_src from the Magento Init Script
        magento_scripts = soup.find_all('script', type='text/x-magento-init')
        for magento_script in magento_scripts:
            if magento_script:
                try:
                    json_data = json.loads(magento_script.string)
                    # Navigate through the JSON structure carefully
                    provider_data = json_data.get("*", {}).get("Magento_Catalog/js/product/view/provider", {}).get("data", {}).get("items", {})
                    
                    if provider_data:  # If we found relevant data, break out of the loop
                        for key in provider_data:
                            item = provider_data[key]
                            price_info = item.get("price_info", {})
                            price = price_info.get("final_price", None)
                            break  # Only need the first product's details

                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"Error parsing Magento init script: {e}")

                if price:  # Stop if we've found the necessary data
                    break

        # Step 2: Extract Image Src and Title from the Data Layer Script
        script_tags = soup.find_all('script', type="text/javascript")
        for script in script_tags:
            if script.string and "window.dataLayer.push" in script.string:
                try:
                    data_layer_matches = re.findall(r'window.dataLayer\.push\((\{.*?\})\);', script.string, re.DOTALL)
                    for match in data_layer_matches:
                        data_layer_json = json.loads(match)
                        if data_layer_json.get("event") == "productPage":
                            product = data_layer_json.get("product", {})
                            title = product.get("name")
                            image_url = product.get("image_url")
                            if image_url:
                                img_src = image_url
                            break  # Exit after finding the relevant push
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"Error parsing data layer script: {e}")
                break  # Stop searching after the relevant script is found

        # Fallback if no title was found
        if not title:
            title_tag = soup.find('h1')
            if title_tag:
                title = title_tag.get_text(strip=True)

        if not img_src and (not price or price == "Price not available"):
            return None
        # Return the collected data
        return {
            'title': title,
            'site':"Gul Ahmed",
            'price': f'PKR {price}' if price else 'Price not available',
            'img_src': img_src,
            'product_url': product_url,
        }

    except requests.exceptions.Timeout:
        print(f"Request timed out for {product_url} on GulAhmed.")
    except requests.RequestException as e:
        print(f"Request error for {product_url} on GulAhmed: {e}")
    except Exception as e:
        print(f"Error processing data for {product_url} on GulAhmed: {e}")
    return None

# # Example usage
# product_url = "https://www.gulahmedshop.com/3pc-unstitched-zari-lawn-suit-with-cotton-net-dupatta-fs-50"
# product_data = fetch_gulahmed_data(product_url)
# print(product_data)


# # Example usage
# # product_url = "https://www.gulahmedshop.com/lurex-jacquard-shirt-and-trouser-kst-43031"
# product_url = "https://www.gulahmedshop.com/3-pc-unstitched-embroidered-lawn-suit-with-cotton-net-dupatta-fe-12014"

# product_data = fetch_gulahmed_data(product_url)
# print(product_data)





import random
from pyppeteer import launch
from bs4 import BeautifulSoup
import re
import asyncio

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.18363 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    # Add more User-Agent strings here
]

# async def fetch_daraz_data(product_url):
#     """Fetch product data from a Daraz product page using Pyppeteer with random User-Agent."""
#     CHROME_PATH = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    
#     browser = await launch(headless=False, executablePath=CHROME_PATH)
#     page = await browser.newPage()
    
#     await page.setUserAgent(random.choice(USER_AGENTS))
    
#     try:
#         await page.goto(product_url, timeout=15000)  # Set timeout to 15 seconds
#     except asyncio.TimeoutError:
#         print(f"Navigation Timeout: {product_url} took too long to load.")
    
#     content = await page.content()
#     soup = BeautifulSoup(content, 'html.parser')
    
#     script_tags = soup.find_all('script')
#     print(f"Found {len(script_tags)} script tags.")

#     pdp_tracking_data = None

#     for script in script_tags:
#         script_content = script.string
#         if script_content and "var pdpTrackingData" in script_content:
#             print("Found the script containing pdpTrackingData")
            
#             # Print a snippet for debugging
#             print("Script content snippet:", script_content[:500])
            
#             # Refined regex to match the pdpTrackingData variable and its content
#             match = re.search(r'var pdpTrackingData\s*=\s*"({.*?})";', script_content, re.DOTALL)
#             if match:
#                 json_string = match.group(1)
#                 # Unescape the JSON string
#                 pdp_tracking_data = json.loads(json_string.encode('utf-8').decode('unicode_escape'))
#                 break

#     with open('scripts_output.txt', 'w', encoding='utf-8') as file:
#         for script in script_tags:
#             script_content = script.string
#             if script_content:
#                 file.write(script_content)
#                 file.write("\n\n")

#     print("Script contents saved to scripts_output.txt")
#     await browser.close()

#     if pdp_tracking_data:
#         print("Extracted pdpTrackingData:", pdp_tracking_data)
#     else:
#         print("pdpTrackingData not found.")
        
#     return pdp_tracking_data

import random
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import json
import re

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    # Add more User-Agent strings here if needed
]

async def fetch_daraz_data(product_url):
    """Fetch product data and rating from a Daraz product page using Pyppeteer with random User-Agent."""
    CHROME_PATH = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    
    browser = await launch(headless=False, executablePath=CHROME_PATH)
    page = await browser.newPage()
    
    await page.setUserAgent(random.choice(USER_AGENTS))
    
    pdp_tracking_data = None
    rating = None
    retries = 2

    try:
        # Attempt to load the page and fetch data
        try:
            await page.goto(product_url, waitUntil='networkidle2')
        except asyncio.TimeoutError:
            print(f"Navigation Timeout: {product_url} took too long to load.")
        
        # Finding data
        while True:
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            script_tags = soup.find_all('script')

            for script in script_tags:
                script_content = script.string
                if script_content and "var pdpTrackingData" in script_content:
                    match = re.search(r'var pdpTrackingData\s*=\s*"({.*?})";', script_content, re.DOTALL)
                    if match:
                        json_string = match.group(1)
                        pdp_tracking_data = json.loads(json_string.encode('utf-8').decode('unicode_escape'))
                        break

            if pdp_tracking_data:
                break  # Exit the loop if we found the data

            await asyncio.sleep(1)  # Short sleep before checking again

        title = pdp_tracking_data.get('pdt_name', 'Title not available')
        price = pdp_tracking_data.get('pdt_price', 'Price not available')
        img_src = pdp_tracking_data.get('pdt_photo', None)  # Set to None if not available
        print(img_src,"1st")
        # If img_src is None or empty, find it from the gallery-preview-panel__content
        if not img_src:
            img_element = soup.select_one('.gallery-preview-panel__content img')
            if img_element:
                img_src = img_element.get('src', 'Image not available')
        print(img_src,"2nd")

        # Finding reviews
        while retries > 0:
            print("retries =", retries)
            previous_height = await page.evaluate('document.body.scrollHeight')
            while True:
                await page.evaluate('window.scrollBy(0, window.innerHeight);')
                await asyncio.sleep(1)
                current_height = await page.evaluate('document.body.scrollHeight')
                if current_height == previous_height:
                    break
                previous_height = current_height

            try:
                await page.waitForSelector('span.score-average', visible=True, timeout=5000)
                rating_element = await page.querySelector('span.score-average')
                if rating_element:
                    rating = await page.evaluate('(element) => element.textContent', rating_element)
                    rating = rating.strip()
                    print(f"Found rating: {rating}")
                    if rating == '0':
                        retries -= 1
                        if retries > 0:
                            await page.reload(waitUntil='networkidle2')
                            continue
                        else:
                            print("Failed to find rating after multiple attempts.")
                            break
                else:
                    print("Rating not found. Reloading page...")
                    retries -= 1
                    if retries > 0:
                        await page.reload(waitUntil='networkidle2')
                        continue
                    else:
                        print("Failed to find rating after multiple attempts.")
                        break
            except Exception as e:
                print(f"Error finding rating: {e}")
                retries -= 1
                if retries > 0:
                    await page.reload(waitUntil='networkidle2')
                    continue
                else:
                    print("Failed to find rating after multiple attempts.")
                    break

            if pdp_tracking_data and rating:
                break

            await asyncio.sleep(1)

    except asyncio.TimeoutError:
        print(f"Navigation Timeout: {product_url} took too long to load.")
    
    await browser.close()

    data = {
        'title': title,
        'price': f'PKR {price}' if price else 'Price not available',
        'img_src': img_src,
        'product_url': product_url,
        'rating': rating,
        'site': 'daraz'
    }
    print(data, "data")
    return data

# Example usage
# product_url = "your_product_url_here"
# asyncio.run(fetch_daraz_data(product_url))


# if __name__ == "__main__":
#     # Example usage
#     # product_url = "https://www.daraz.pk/products/-i468826624-s2214264120.html?pvid=e3fdcafd-5f7a-4964-b919-167a01944253&search=jfy&scm=1007.28811.376629.0&priceCompare=skuId%3A2214264120%3Bsource%3Atpp-recommend-plugin-41701%3Bsn%3Ae3fdcafd-5f7a-4964-b919-167a01944253%3BunionTrace%3A21411ec417235770058424935e0b15%3BoriginPrice%3A14500%3BvoucherPrice%3A14500%3BdisplayPrice%3A14500%3BsourceTag%3A%23auto_collect%231%24auto_collect%24%3BsinglePromotionId%3A-1%3BsingleToolCode%3AmockedSalePrice%3BvoucherPricePlugin%3A1%3BbuyerId%3A0%3ButdId%3A-1%3Btimestamp%3A1723577005954&spm=a2a0e.tm80335159.just4u.d_468826624"
#     product_url="https://www.daraz.pk/products/airpods-pro-2nd-generation-anc-i432898320.html"
#     # product_url = "https://www.daraz.pk/products/yellow-color-airpods-pronew-i423205261.html"
#     asyncio.run(fetch_daraz_data(product_url))



# https://www.daraz.pk/products/yellow-color-airpods-pronew-i423205261.html
# # Example usage
# product_url = "https://www.daraz.pk/products/-i468826624-s2214264120.html?pvid=e3fdcafd-5f7a-4964-b919-167a01944253&search=jfy&scm=1007.28811.376629.0&priceCompare=skuId%3A2214264120%3Bsource%3Atpp-recommend-plugin-41701%3Bsn%3Ae3fdcafd-5f7a-4964-b919-167a01944253%3BunionTrace%3A21411ec417235770058424935e0b15%3BoriginPrice%3A14500%3BvoucherPrice%3A14500%3BdisplayPrice%3A14500%3BsourceTag%3A%23auto_collect%231%24auto_collect%24%3BsinglePromotionId%3A-1%3BsingleToolCode%3AmockedSalePrice%3BvoucherPricePlugin%3A1%3BbuyerId%3A0%3ButdId%3A-1%3Btimestamp%3A1723577005954&spm=a2a0e.tm80335159.just4u.d_468826624"
# product_data = fetch_daraz_data(product_url)
# print(product_data)

