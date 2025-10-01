import os
import google.generativeai as genai
import json
import re
from .config import HIISTORY,API_KEY


def get_search_intent(products_list, image_path=None):
    print(products_list, "products_list")
    # Configure the API key
    genai.configure(api_key=API_KEY)

    # Create the model with specified configuration
    generation_config = {
        "temperature": 1.2,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        tools='code_execution',
    )
    # Start a chat session with the model using the loaded history
    chat_session = model.start_chat(
        history=HIISTORY
    )
    # Upload images if provided
    if image_path:
        
        import PIL.Image

        sample_file = PIL.Image.open(image_path)
        # Prompt the model with text and the previously uploaded image.
        # response = model.generate_content([sample_file, "Describe how this product might be manufactured."])
        response = chat_session.send_message([products_list,sample_file])
    else:
         # Send the message to the model
        response = chat_session.send_message(products_list)

    # Clean the response to extract the valid JSON
    cleaned_response = re.search(r'{\s*"search_intent":\s*"[^"]*"\s*}', response.text)
    
    if cleaned_response:
        return json.loads(cleaned_response.group(0))
    else:
        return json.dumps({"error": "Invalid response format"}, indent=2)

# x=get_search_intent("[{'img_src': 'https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRh9Z3Bhdln0OWy6CDrsoFybbcczKooZSddNmwaJLMn7L06GONu', 'title': '3PC Unstitched Gold and Lacquer Printed Lawn Suit with Gold and Lacquer Dupatta CL-42278', 'product_url': 'https://www.gulahmedshop.com/3pc-unstitched-gold-and-lacquer-printed-lawn-suit-with-gold-and-lacquer-dupatta-cl-42278'}, {'img_src': 'https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcS_KOWwFK3wkTjIhTelNDt1hoe1FS_Vz_roZG-Qh58Lclova3kl', 'title': '3-Piece Unstitched Florence Collection By Gul Ahmed Printed Lawn Suits CL-22232 B', 'product_url': 'https://askanigroup.com/product/3-piece-unstitched-florence-collection-by-gul-ahmed-printed-lawn-suits-cl-22232-b/'}, {'img_src': 'https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcRXdAiHgYzDYCkiip0WfspSSNvrv43c8FDd-g9Jc7Bh4bLVGiTq', 'title': '3PC Unstitched Embroidered – Diners Pakistan', 'product_url': 'https://diners.com.pk/products/unstitched-3-pieces-emb-jacquard-shirt-digital-printed-zari-dupatta-dyed-cotton-trouser'}, {'img_src': 'https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcQunjOh7a3k223sIq-GIDDSyK0f8SPG-Y9kSMm0gMszQC8EjN6j', 'title': '3 Piece - Embroidered Cotton Suit - S', 'product_url': 'https://sapphiree.shop/products/pee-dy23v1-1-1'}, {'img_src': 'https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQeqRycmae2dL1Mzev97Yaf7DVR6-ntgm63la8-sQZXMBJGOzE5', 'title': 'Zellbury Sale 2024 Upto 50% Off Clearance With Price', 'product_url': 'https://www.stylostreet.com/zellbury-khaddar-sale-for-women/'}]", image_path="images/ideas1.jpg")
# print(x)
