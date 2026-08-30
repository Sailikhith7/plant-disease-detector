import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

# Cloudinary automatically configures via the CLOUDINARY_URL env variable
cloudinary.config()

def upload_image_to_cloud(file_bytes, folder="pikrakshak_cases"):
    """
    Uploads raw image bytes directly to Cloudinary and returns a public HTTPS URL.
    Returns None if upload fails or CLOUDINARY_URL is missing.
    """
    cloudinary_url = os.getenv("CLOUDINARY_URL")
    if not cloudinary_url:
        print("[Cloudinary Warning]: CLOUDINARY_URL not found in .env")
        return None

    try:
        response = cloudinary.uploader.upload(
            file_bytes,
            folder=folder,
            resource_type="image"
        )
        return response.get("secure_url")
    except Exception as e:
        print(f"[Cloudinary Upload Error]: {e}")
        return None