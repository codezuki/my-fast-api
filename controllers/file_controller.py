from fastapi import APIRouter, UploadFile, File, Depends

from services.file_service import FileService
from utils.auth import get_current_user


router = APIRouter(
    prefix="/api/files",
    tags=["File Processing"]
)

file_service = FileService()


@router.post("/extract")
async def extract_file(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):

    return await file_service.extract_data(file)
