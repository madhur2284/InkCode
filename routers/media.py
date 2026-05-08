from fastapi import APIRouter, status, UploadFile, File, HTTPException
from services.cloudinary import cloudinary_upload

router = APIRouter(
    prefix="/media",
    tags=["media"]
)


@router.post(path='/upload', status_code=status.HTTP_200_OK)
async def upload_image(image: UploadFile = File()) -> str:
    image_url = await cloudinary_upload(image)
    if not image_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Image not uploaded sucessfully")
    return image_url