import streamlit as st
from PIL import Image
from openai import OpenAI
import io
import base64

api_key = ''
client = OpenAI(api_key=api_key)


def classify_labels_with_gpt4(description, fileBase64):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
                "content": "You are an assistant that classifies image labels."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Classify the following description into number of customers, promotion girls, and type of place: {description}"
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
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Determine weather in my location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state e.g. San Francisco, CA"
                            },
                            "unit": {
                                "type": "string",
                                "enum": [
                                    "c",
                                    "f"
                                ]
                            }
                        },
                        "required": [
                            "location"
                        ]
                    }
                }
            }
        ]
    )

    return response.choices[0].message.content


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
        st.image(image, caption='Uploaded Image', use_column_width=True)
        st.write("")

        description = st.text_area("Describe the image")

        if st.button("Analyze"):
            # resized_img = image.resize((150, 100))
            # st.write("Description:", compress_image(image, new_height=150))
            st.write("Analyzing...")
            classification = classify_labels_with_gpt4(
                description, compress_image(image, new_height=150))
            st.write("Classified Labels:", classification)
