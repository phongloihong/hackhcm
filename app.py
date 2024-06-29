import streamlit as st
from PIL import Image
from openai import OpenAI
import io
import base64
import json


api_key = ''
client = OpenAI(api_key=api_key)


def classify_labels_with_gpt4(fileBase64):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
                "content": """You are an specialist beer event assistant that classifies image labels about these brands with logo and product url:
                Heineken product: https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQU0hCIdc50nuj-Kj7-qD-EfHebm5NAzVCZoQ&s,
                learn carefully Promotion material images: https://drive.google.com/drive/folders/11WmGXKAtEVxDMfwpvdJ_NUlhPiqXB1yA and list all materials has Heineken logo in the image
                call save_analysis function to save the analysis every time  detect image.
                If don't have any heineken logo in the image, please return nothing.
                """},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Classify the following description into what brand ,number of customers, promotion girls, and type of place"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": fileBase64
                        }
                    }
                ]
            }
        ],
        max_tokens=150,
        temperature=0.1,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "save_analysis",
                    "description": "Save the analysis to a database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "decorator_items": {
                                "type": "string",
                                "description": "List of Heineken decoration items in the image (banner, standee, beer crate)"
                            },
                            "heineken_drinker": {
                                "type": "number",
                                "description": "number of Heineken beer drinker in the image"
                            },
                            "promotion_girl": {
                                "type": "number",
                                "description": "number of customer in the image exclude promotion girls"
                            },
                            "activities": {
                                "type": "string",
                                "description": "what activities are in the image: drinking, talking, playing game, Eating, Smiling, Shopping, etc."
                            },
                            "emotions": {
                                "type": "string",
                                "description": "what emotions are in the image: happy, sad, angry, enjoyable, neutral etc."
                            },
                            "heineken_products": {
                                "type": "string",
                                "description": "what products have heineken logo",
                            },
                            "promotion_materials": {
                                "type": "string",
                                "description": "what promotion materials are in the image: POSM, banner, poster, etc."
                            },
                            "brand_logos": {
                                "type": "string",
                                "description": "Is heineken logo in the image",
                                "enum": [
                                    "true",
                                    "false"
                                ]
                            },
                            "scenes": {
                                "type": "string",
                                "description": "what scenes are in the image: bar, pub, restaurant, etc."
                            },
                            "environments": {
                                "type": "string",
                                "description": "what environment are in the image: indoor, outdoor, etc."
                            }
                        },
                        "required": [
                            "decorator_items",
                            "heineken_drinker",
                            "promotion_girl",
                            "activities",
                            "emotions",
                            "heineken_products",
                            "promotion_materials",
                            "brand_logos",
                            "scenes",
                            "environments",
                        ]
                    }
                }
            }
        ]
    )

    tool_call = response.choices[0].message.tool_calls[0]
    if (tool_call.function.name == "save_analysis"):
        args_json = tool_call.function.arguments
        args = json.loads(args_json)
        save_analysis(
            args['decorator_items'],
            args['heineken_drinker'],
            args['promotion_girl'],
            args['activities'],
            args['emotions'],
            args['heineken_products'],
            args['promotion_materials'],
            args['brand_logos'],
            args['scenes'],
            args['environments'],
        )

    return response.choices[0].message.content


def save_analysis(decorator_items="", heineken_drinker=0, promotion_girl=0, activities="", emotions="", heineken_products="", promotion_materials="", brand_logos="", scenes="", environments=""):
    point = 0
    if (decorator_items != ""):
        st.write("decorator_items:", decorator_items)

    if (heineken_drinker != 0):
        point += 1
        st.write("heineken_drinker:", heineken_drinker)

    if (promotion_girl != 0):
        if (promotion_girl >= 2):
            point += 1

        st.write("promotion girl:", promotion_girl)

    if (activities != ""):
        st.write("activities:", activities)

    if (emotions != ""):
        st.write("emotions:", emotions)

    if (heineken_products != ""):
        st.write("heineken_products:", heineken_products)

    if (promotion_materials != ""):
        st.write("promotion_materials:", promotion_materials)

    if (brand_logos != ""):
        st.write("brand_logos:", brand_logos)

    if (scenes != ""):
        st.write("scenes:", scenes)

    if (environments != ""):
        st.write("environments:", environments)


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return "data:image/jpeg;base64,"+img_str


def compress_image(image, new_height=150, quality=50):
    width, height = image.size
    aspect_ratio = width / height
    new_width = int(new_height * aspect_ratio)
    resized_image = image.resize((new_width, new_height))

    buffer = io.BytesIO()
    resized_image.save(buffer, format="JPEG", quality=quality)
    image_data = buffer.getvalue()
    base64_encoded_image = base64.b64encode(image_data).decode('utf-8')
    return "data:image/jpeg;base64,"+base64_encoded_image


st.title('Image Analysis Application')
st.write('Upload an image and describe it to get labels such as the number of customers, promotion girls, and the type of place (bar, pub, restaurant, etc.)')

uploaded_files = st.file_uploader(
    "Choose images...", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image',
                 width=150, use_column_width=False)
        st.write("")

        if st.button("Analyze"):
            # resized_img = image.resize((150, 100))
            # st.write("Description:", compress_image(image, new_height=150))
            st.write("Analyzing...")
            classify_labels_with_gpt4(compress_image(image, new_height=150))
