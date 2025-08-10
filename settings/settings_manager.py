import os
from PySide6.QtCore import QSettings

class SettingsManager:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._file = os.path.join(base_dir, 'config.ini')
        self._settings = QSettings(self._file, QSettings.IniFormat)

    def value(self, key: str, default=None):
        return self._settings.value(key, default)

    def setValue(self, key: str, value):
        self._settings.setValue(key, value)

    def get_last_path(self) -> str:
        return self.value('file/last_path', '')

    def set_last_path(self, path: str):
        self.setValue('file/last_path', path)
