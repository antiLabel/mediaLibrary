import json
from models.media_model import MediaItem

class JSONRepository:
    def __init__(self, path: str = ''):
        self._path = path

    def save(self, items: list[MediaItem], path: str = None):
        file_path = path or self._path
        if not file_path:
            raise ValueError("No path specified for saving library.")
        data = [item.to_dict() for item in items]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: str = None) -> list[MediaItem]:
        file_path = path or self._path
        if not file_path:
            raise ValueError("No path specified for loading library.")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [MediaItem.from_dict(d) for d in data]