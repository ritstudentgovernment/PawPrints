from fastapi import APIRouter, Depends, File, UploadFile

from pawprints.api.service.image_service import ImageServiceDep
from pawprints.auth.permission import current_auth_user
from pawprints.models.schema import ReturnImageURI, Success

router = APIRouter(tags=["Images"])


@router.post("/upload", response_model=ReturnImageURI, dependencies=[Depends(current_auth_user)])
async def upload(im: ImageServiceDep, file: UploadFile = File(...)) -> ReturnImageURI:
    return await im.upload_petition_image(file=file)


@router.delete("/{filename}", response_model=Success, dependencies=[Depends(current_auth_user)])
async def delete(im: ImageServiceDep, filename: str) -> Success:
    return await im.delete_petition_image(filename=filename)
