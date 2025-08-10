import json
from repository.json_repository import JSONRepository
from models.media_model import MediaItem

def test_json_repository(tmp_path):
    file = tmp_path / "repo.json"
    items = [MediaItem('X','A',1999,5.5), MediaItem('Y','B',2001,8.0)]
    repo = JSONRepository()
    repo.save(items, str(file))
    loaded = repo.load(str(file))
    assert len(loaded) == 2
    assert loaded[0].title == 'X'
