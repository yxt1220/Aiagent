from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.upload_service import upload_service

router = APIRouter()


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str | None = Form(None),
    user_id: str | None = Form(None),
):
    try:
        result = await upload_service.save_and_register_file(
            file=file,
            session_id=session_id,
            user_id=user_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))