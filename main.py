import json
import logging
import os

import openai
import webuiapi
from dotenv import load_dotenv
from PIL import Image
import time
from uuid import uuid4

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
from appwrite.id import ID



SYSTEM_MESSAGE = """
Your are an assistant that generates prompts for stable diffusion, you would generate a json with two keys, "positive" and "negative", these will be the promprts provided for stable diffusion to generate an image, the positive prompt will be the thing that would be in the image and the negative the thing that wont apper on it,your job is to give descriptions of male game characters they should be humanoid. You will always generate this images using a white background and dont ask for weapons, tools or anithyng held by hands. Here are some example outputs:

Example 1:
{
"positive": "(white background) a man , blond short hair, red shirt, jeans",
"negative": "closed eyes, shadows"
}
Example 2:
{
"positive": "(white background) a nordic male warrior , white short hair, lethear armor",
"negative": "weapons, shields, shadows"
}
"""
POSES_IMAGE_PATH = "poses.png"

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize Appwrite Client
appwrite_client = Client()
appwrite_client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
appwrite_client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
appwrite_client.set_key(os.getenv("APPWRITE_API_KEY"))
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
api = webuiapi.WebUIApi()
api.util_set_model(name="pixel")
api.util_wait_for_ready()
poses_image = Image.open(POSES_IMAGE_PATH)

def start_generator():
    database = Databases(appwrite_client)
    storage = Storage(appwrite_client)
    images_collection_id = '65c6c71559e7e9f70463'
    while True:
        try:
            client = openai.Client()
            logging.info("Starting prompt generator")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[{"role": "system", "content": SYSTEM_MESSAGE}],
                response_format={"type": "json_object"},
            )
            logging.info("Generator finished")
            prompts = response.choices[0].message.content
            json_prompts = json.loads(prompts)
            logging.info(f"Prompts generated: {prompts}")
            logging.info("Loading controlnet")
            controlnet_unit= webuiapi.ControlNetUnit(input_image=poses_image, model="control_v11p_sd15_openpose", pixel_perfect=True)
            logging.info("Controlnet loaded")
            logging.info("Generating images")
            result = api.txt2img(prompt=json_prompts["positive"], negative_prompt=json_prompts["negative"],steps=32 ,width=1600, height=900, batch_size=4,controlnet_units=[controlnet_unit], cfg_scale=12)
            logging.info("Images generated")
            for i, image in enumerate(result.images):
                #Dont save the last image
                if i == 3:
                    break
                image_path = f"outputs/output_{uuid4()}.png"  # Ensure unique filename
                image.save(image_path)
                logging.info(f"Image saved locally: {image_path}")
                
                # Upload the image to Appwrite Storage
                upload_result = storage.create_file(bucket_id="65c6cb1181c9f5df4548",file_id=ID.unique(),
                                                          file=InputFile.from_path(image_path))
                logging.info(f"Image uploaded to Appwrite: {upload_result['$id']}")
                
                # Create a document in the database with the image ID and prompts
                document_data = {
                    'file_id': upload_result['$id'],
                    'positive_prompt': json_prompts["positive"],
                    'negative_prompt': json_prompts["negative"],
                    'rating': 'unrated'  # Default rating, can be updated later
                }
                database.create_document(
                    database_id="65c6c70f6bb8c40d181d",
                    document_id=ID.unique(),
                    collection_id=images_collection_id, data=document_data)
                logging.info("Document created in database with prompts and image ID.")
            logging.info("Waiting for 10 seconds")
            time.sleep(60)
            logging.info("Done waiting, starting again...")
            
        except Exception as e:
            logging.error(f"Error in generator: {e}")
            continue

start_generator()