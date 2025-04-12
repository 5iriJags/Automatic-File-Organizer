import os
from pathlib import Path

FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"],
    "Documents": [".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".csv"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".tar", ".7z"],
    "Executables": [".exe", ".dmg", ".apk"],
    "Others": []
}

def categorize_file(file_name):
    file_extension = Path(file_name).suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension in extensions:
            return category
    return "Others"