from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile

from app.layers.file_ingestion.file_parser import FileParser
from app.layers.file_ingestion.file_registry import file_registry

UPLOAD_DIR = Path("./data/upload")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class UploadService:
    def __init__(self):
        self.file_parser = FileParser()

    async def save_and_register_file(
        self,
        file: UploadFile,
        session_id: str | None,
        user_id: str | None = None,
    ) -> dict:
        if not session_id:
            session_id = "default-session"

        file_id = str(uuid4())
        ext = Path(file.filename).suffix.lower()
        safe_name = f"{file_id}{ext}"
        save_path = UPLOAD_DIR / safe_name

        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        parsed_file = self.file_parser.parse(str(save_path), file_id=file_id)

        # 保留原始文件名，便于前端显示
        parsed_file.file_name = file.filename

        file_registry.add_file(session_id=session_id, parsed_file=parsed_file)

        return {
            "file_id": file_id,
            "file_name": file.filename,
            "message": f"文件 {file.filename} 上传成功，后端现在可以让 LLM 读取它。",
            "num_chunks": len(parsed_file.chunks),
        }


upload_service = UploadService()