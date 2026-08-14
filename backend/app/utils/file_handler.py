import os
import uuid

from flask import current_app

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB, matches Config.MAX_CONTENT_LENGTH


class FileValidationError(Exception):
    pass


def _get_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext.lower()


def validate_script_file(file_storage) -> str:
    """
    Validate an uploaded file. Returns the lowercase extension if valid,
    otherwise raises FileValidationError with a user-facing message.
    """
    if not file_storage or not file_storage.filename:
        raise FileValidationError("No file was uploaded.")

    ext = _get_extension(file_storage.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file type '{ext}'. Accepted formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )

    # Determine size without loading the whole file into memory
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)

    if size == 0:
        raise FileValidationError("The uploaded file is empty.")
    if size > MAX_FILE_SIZE_BYTES:
        raise FileValidationError("File is too large. Maximum size is 20 MB.")

    return ext


def save_uploaded_file(file_storage, project_id: str) -> dict:
    """
    Persist an uploaded script file to storage.

    Currently implemented as local disk storage under UPLOAD_FOLDER. Swap this
    function's body for an S3/Supabase upload later — callers only depend on
    the returned dict shape, not on where the bytes actually live.

    Returns: {"file_url": str, "original_filename": str, "stored_path": str}
    """
    ext = validate_script_file(file_storage)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    project_folder = os.path.join(upload_folder, project_id)
    os.makedirs(project_folder, exist_ok=True)

    stored_filename = f"{uuid.uuid4()}{ext}"
    stored_path = os.path.join(project_folder, stored_filename)

    file_storage.save(stored_path)

    return {
        # In local mode this is a filesystem path; once storage moves to
        # S3/Supabase this becomes the public/object URL instead.
        "file_url": stored_path,
        "original_filename": file_storage.filename,
        "stored_path": stored_path,
    }


def delete_stored_file(stored_path: str) -> None:
    """Remove a previously stored file, if it exists. Swap for S3 delete later."""
    if stored_path and os.path.exists(stored_path):
        os.remove(stored_path)
