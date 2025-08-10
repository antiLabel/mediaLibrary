from PySide6.QtGui import QStandardItem
from models.media_model import MediaItem

class LibraryController:
    def __init__(self, model, repository):
        self._model = model
        self._repo = repository
        self._items: list[MediaItem] = []

    def add_item(self, data: dict) -> MediaItem:
        item = MediaItem.from_dict(data)
        self._items.append(item)
        self._add_to_model(item)
        return item

    def _add_to_model(self, item: MediaItem):
        row = [
            QStandardItem(item.title),
            QStandardItem(item.creator),
            QStandardItem(str(item.year)),
            QStandardItem(str(item.rating))
        ]
        self._model.appendRow(row)

    def delete_item(self, row: int):
        if 0 <= row < len(self._items):
            del self._items[row]
            self._model.removeRow(row)

    def edit_item(self, row: int, data: dict):
        if 0 <= row < len(self._items):
            item = self._items[row]
            item.title = data.get('title', item.title)
            item.creator = data.get('creator', item.creator)
            item.year = int(data.get('year', item.year))
            item.rating = float(data.get('rating', item.rating))
            self._update_model_row(row, item)

    def _update_model_row(self, row: int, item: MediaItem):
        self._model.setItem(row, 0, QStandardItem(item.title))
        self._model.setItem(row, 1, QStandardItem(item.creator))
        self._model.setItem(row, 2, QStandardItem(str(item.year)))
        self._model.setItem(row, 3, QStandardItem(str(item.rating)))

    def get_item(self, row: int) -> MediaItem:
        return self._items[row]

    def update_item(self, item: MediaItem, info: dict):
        item.poster_url = info.get('poster_url', item.poster_url)
        item.plot = info.get('plot', item.plot)
        # 这里可以根据需要更新 UI