# from flask import Flask, render_template, request, redirect, url_for
from utils.scrapper import image_search, text_search
import asyncio
import os
import threading
# app = Flask(__name__)
from quart import Quart, request, render_template, redirect, url_for
app = Quart(__name__)
# Define a temporary upload folder
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Provided product list
products = [
    {'img_src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxTObOPAmuCMNSVKMiMYe0IkPer6DCSpotz0W_ZIfIjCTXXwDK', 'title': 'OLIVE LINEN WAISTCOAT | CCVC-39344-A5', 'product_url': 'https://www.junaidjamshed.com/olive-linen-waistcoat-ccvc-39344-a5.html'}, {'img_src': 'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcT5h5i_3yXE_fsYQa5wxJP2YwAsGb9gI4383c9vTzQy7CAkHhWs', 'title': 'Kapok Khaki Stitched Waistcoat Suit for Men', 'product_url': 'https://www.daraz.pk/products/kapok-khaki-stitched-waistcoat-suit-for-men-i354240981.html'}, {'img_src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbmFUxUKJOmbH__Izcc5BWUCKj00OBRPXls1tDAtd8qTiRVdcg', 'title': 'WAISTCOAT-PARAMOUNT SAND IST-152 - SAND / S / Wash & Wear', 'product_url': 'https://istor.pk/products/ist-152-sand'}, {'img_src': 'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSjHKCzea_t8q_X-dzg2IimcR1Kz9bZyHNcHIa6U4NRoJbcH0l-', 'title': 'Cotton Waistcoat', 'product_url': 'https://www.limelight.pk/products/p6392wc-brn'}, {'img_src': 'https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcTJOtF8imSMzxqbe2ReZhisCnzGtjgWIiABO8a272UXd-O_4_tp', 'title': 'Firewood (3 Piece) Medium', 'product_url': 'https://tgmstore.pk/products/firewood-3-piece'}, {'img_src': 'https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRqyR2uq7uIaWNSIju5M4PzwEOwt_BmpxC2QKzxvxXpPRBBVZj0', 'title': 'Dyed Blended Waistcoat – Alkaram Studio', 'product_url': 'https://www.alkaramstudio.com/products/dyed-jacquard-waistcoat-gmwc120-grey'},
    {
        "img_src": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxTObOPAmuCMNSVKMiMYe0IkPer6DCSpotz0W_ZIfIjCTXXwDK",
        "title": "OLIVE LINEN WAISTCOAT | CCVC-39344-A5",
        "product_url": "https://www.junaidjamshed.com/olive-linen-waistcoat-ccvc-39344-a5.html",
        "site": "J.",
        "price": "PKR 16,990.00"
    },
    {
        "img_src": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcT5h5i_3yXE_fsYQa5wxJP2YwAsGb9gI4383c9vTzQy7CAkHhWs",
        "title": "Kapok Khaki Stitched Waistcoat Suit for Men",
        "product_url": "https://www.daraz.pk/products/kapok-khaki-stitched-waistcoat-suit-for-men-i354240981.html",
        "site": "daraz",
        "price": "Rs. 17,990"
    },
    {
        "img_src": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcRxyG-9f5h34Fair8Q7mzzuO-yW9XnxzDy-8_0aWqZBqW5X_Fru",
        "title": "Brown Gul 900 Gorgia PKW Unstitched Fabric",
        "product_url": "https://www.gulahmedshop.com/brown-gul-900-gorgia-pkw-unstitched-fabric",
        "site": "Gul Ahmad",
        "price": "PKR 2,633"
    },
    {
        "img_src": "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcQDPHmFvt55AS6XnSc0qdHBgas2_xbNMFel-Vr2jvz1RNNpHmgE",
        "title": "Stone Opus Paradise GSW | GulAhmed",
        "product_url": "https://www.gulahmedshop.com/stone-opus-paradise-gsw-unstitched-fabric",
        "site": "Gul Ahmad",
        "price": "PKR 2,525"
    }
]

@app.route('/', methods=['GET'])
async def index():
    query = request.args.get('s', '')
    filtered_products = [product for product in products if query.lower() in product['title'].lower()]
    return await render_template('index.html', products=filtered_products)



products2 = [
    {
        "img_src": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxTObOPAmuCMNSVKMiMYe0IkPer6DCSpotz0W_ZIfIjCTXXwDK",
        "title": "OLIVE LINEN WAISTCOAT | CCVC-39344-A5",
        "product_url": "https://www.junaidjamshed.com/olive-linen-waistcoat-ccvc-39344-a5.html",
        "site": "J.",
        "price": "PKR 16,990.00"
    },
    {
        "img_src": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcT5h5i_3yXE_fsYQa5wxJP2YwAsGb9gI4383c9vTzQy7CAkHhWs",
        "title": "Kapok Khaki Stitched Waistcoat Suit for Men",
        "product_url": "https://www.daraz.pk/products/kapok-khaki-stitched-waistcoat-suit-for-men-i354240981.html",
        "site": "daraz",
        "price": "Rs. 17,990"
    },
    {
        "img_src": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcRxyG-9f5h34Fair8Q7mzzuO-yW9XnxzDy-8_0aWqZBqW5X_Fru",
        "title": "Brown Gul 900 Gorgia PKW Unstitched Fabric",
        "product_url": "https://www.gulahmedshop.com/brown-gul-900-gorgia-pkw-unstitched-fabric",
        "site": "Gul Ahmad",
        "price": "PKR 2,633"
    },
    {
        "img_src": "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcQDPHmFvt55AS6XnSc0qdHBgas2_xbNMFel-Vr2jvz1RNNpHmgE",
        "title": "Stone Opus Paradise GSW | GulAhmed",
        "product_url": "https://www.gulahmedshop.com/stone-opus-paradise-gsw-unstitched-fabric",
        "site": "Gul Ahmad",
        "price": "PKR 2,525"
    }
]


# def run_in_thread(file_path):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     return loop.run_until_complete(image_search(file_path=file_path))

@app.route('/upload', methods=['POST'])
async def upload_image():
    # Await the request.files since it's a coroutine
    files = await request.files
    if 'image' not in files:
        return redirect(url_for('index'))

    image = files['image']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    await image.save(file_path)

    results = await image_search(file_path=file_path)
    # print(results,"from flask")
    os.remove(file_path)

    return await render_template('index.html', products=results)


# @app.route('/text-search', methods=['POST'])
# async def text_search():
#     # Await the request.files since it's a coroutine
#     print(request)
#     files = await request.files
#     if 'image' not in files:
#         return redirect(url_for('index'))

#     image = files['image']
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
#     await image.save(file_path)

#     results = await text_search(search_text=search_text)
#     # print(results,"from flask")
#     os.remove(file_path)

#     return await render_template('index.html')


@app.route('/search', methods=['POST'])
async def search():
    # Retrieve the search query from the POST request
    form = await request.form
    query = form.get('s', '').strip().lower()
    print(query,"query")
    # Filter products based on the search query
    # filtered_products = [product for product in products if query in product['title'].lower()]
    results = await text_search(search_text=query)
    # Render the template with the filtered products
    return await render_template('index.html', products=results)

if __name__ == "__main__":
    app.run(debug=True)


# ngrok http 5000