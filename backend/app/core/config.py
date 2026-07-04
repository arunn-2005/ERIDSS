from pathlib import Path

# Backend Root Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Upload Folder
UPLOAD_DIR = BASE_DIR / "uploads" / "documents"

# Create folder automatically if it doesn't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}

# Maximum file size (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024