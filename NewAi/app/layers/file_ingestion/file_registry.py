from typing import Dict, List

from app.layers.file_ingestion.ingestion_schema import ParsedFile


class FileRegistry:
    def __init__(self):
        self._files_by_session: Dict[str, List[ParsedFile]] = {}

    def add_file(self, session_id: str, parsed_file: ParsedFile):
        if session_id not in self._files_by_session:
            self._files_by_session[session_id] = []
        self._files_by_session[session_id].append(parsed_file)

    def get_files(self, session_id: str) -> List[ParsedFile]:
        return self._files_by_session.get(session_id, [])

    def clear_files(self, session_id: str):
        if session_id in self._files_by_session:
            self._files_by_session.pop(session_id, None)

    def get_combined_context(
        self,
        session_id: str,
        max_chunks_per_file: int = 3
    ) -> str:
        files = self.get_files(session_id)
        if not files:
            return ""

        parts: List[str] = []

        # 倒序：最新上传的文件排最前面
        for idx, f in enumerate(reversed(files), start=1):
            parts.append(f"[Uploaded file #{idx} (most recent first): {f.file_name}]")

            if f.structured_summary:
                parts.append(str(f.structured_summary))
            else:
                for chunk in f.chunks[:max_chunks_per_file]:
                    parts.append(chunk.content)

        return "\n\n".join(parts)


file_registry = FileRegistry()