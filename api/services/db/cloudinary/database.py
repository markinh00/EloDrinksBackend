import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from starlette import status
from starlette.exceptions import HTTPException
from api.helpers.get_img_id import get_img_id_by_public_url

load_dotenv()

class Cloudinary:
    def __init__(self):
        self.client = cloudinary
        self.client.config(
            cloud_name=os.getenv("CLOUDINARY_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True,
        )

    async def upload_image(self, image_file: UploadFile) -> str | None:
        try:
            result = self.client.uploader.upload(await image_file.read(), folder=os.getenv("CLOUDINARY_FOLDER"))

            if not result["secure_url"]:
                HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="error while uploading the image!"
                )

            return result["secure_url"]
        except Exception as e:
            print("Error while uploading image:", e)
            return None

    def delete_image(self, image_url: str) -> bool:
        try:
            public_id = get_img_id_by_public_url(image_url)

            result = self.client.uploader.destroy(f"{os.getenv('CLOUDINARY_FOLDER')}/{public_id}")
            if result['result'] != "ok":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not delete image from server"
                )

            return True
        except Exception as e:
            print("Error while deleting image: ", e)
            return False
