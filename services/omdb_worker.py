import os
import requests
from PySide6.QtCore import QThread, Signal
from dotenv import load_dotenv

load_dotenv()
class OMDbWorker(QThread):
    fetched = Signal(dict)

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.title = title
        self.api_key = os.getenv('OMDB_API_KEY', '')
        print("OMDb API Key:", self.api_key)

    def run(self):
        if not self.api_key:
            return
        url = 'http://www.omdbapi.com/'
        params = {'t': self.title, 'apikey': self.api_key, 'plot': 'short'}
        try:
            response = requests.get(url, params=params, timeout=10)
            print(response)
            if response.status_code == 200:
                data = response.json()
                info = {
                    'poster_url': data.get('Poster', ''),
                    'plot': data.get('Plot', '')
                }
                self.fetched.emit(info)
        except Exception:
            pass