import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status

async def cloudinary_upload(avatar_image: UploadFile) -> dict:
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if avatar_image.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported file type")
    
    max_size = 2 * 1024 * 1024

    content = await avatar_image.read()

    if len(content) > max_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Max size of file should be 2MB only")
    
    try:
        result = cloudinary.uploader.upload(
            content,
            folder="blog_profile_picture",
            transformation=[
                {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
                {"quality": "auto"},      # auto compress
                {"fetch_format": "auto"}  # serve webp to browsers that support it
            ]
        )


        return {
            "avatar_url": result["secure_url"],
            "avatar_public_id": result["public_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Image Upload Failed: {str(e)}")
    

async def cloudinary_delete(avatar_public_id: str):
    try:
        cloudinary.uploader.destroy(public_id=avatar_public_id)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to delete old avatar")




