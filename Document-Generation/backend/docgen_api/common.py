from enum import Enum
class FolderFileType(Enum):
    TEMPLATES = "templates"
    REQUESTS = "requests"


class ContentType(Enum):
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    PDF = "application/pdf"
    JSON = "application/json"
    IMG = "image/png"


class FileExtension(Enum):
    PDF = [".pdf"]
    XLSX = [".xlsx"]
    DOCX = [".docx"]
    IMG = [".jpg", ".jpeg", ".png"]

class FileCategory(Enum):
    CROP = "Crop"
    Origin = "Origin"
    BREAK = "Break"
    EXCEL = "Excel"