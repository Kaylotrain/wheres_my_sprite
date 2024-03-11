from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.services.storage import Storage
from dotenv import load_dotenv
import os
from joblib import Parallel, delayed

FOLDER_PATH = 'good_images/'

def download_image(image_id, bucket_id, storage, save_path):
    # Check if image already exists
    if not os.path.exists(f'{save_path}/{image_id}.png'):
        # Get the image file content
        image_file_response = storage.get_file_download(
            bucket_id=bucket_id,
            file_id=image_id)

        # Saving the file
        with open(f'{save_path}/{image_id}.png', 'wb') as f:
            f.write(image_file_response)
        print(f"Downloaded {image_id}.png")
    else:
        print(f"{image_id}.png already exists.")

def download_good_images():
    load_dotenv()
    appwrite_client = Client()
    appwrite_client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
    appwrite_client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
    appwrite_client.set_key(os.getenv("APPWRITE_API_KEY"))
    database = Databases(appwrite_client)
    storage = Storage(appwrite_client)
    images_collection_id = '65c6c71559e7e9f70463'
    images = database.list_documents(
        database_id="65c6c70f6bb8c40d181d",
        collection_id=images_collection_id,
        queries= [
            Query.equal('rating', ['good']),
            Query.limit(64)  # Limit to 100 images
        ]
    )

    # Ensure the directory for good images exists
    os.makedirs(FOLDER_PATH, exist_ok=True)

    # Download images in parallel
    Parallel(n_jobs=-1)(delayed(download_image)(
        image['file_id'], '65c6cb1181c9f5df4548', storage, FOLDER_PATH.replace('/', '')
    ) for image in images['documents'])

if __name__ == "__main__":
    download_good_images()
