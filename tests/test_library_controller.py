import os
import json
import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QStandardItemModel
from controllers.library_controller import LibraryController
from repository.json_repository import JSONRepository

@pytest.fixture(scope="module", autouse=True)
def app():
    return QCoreApplication([])

def test_add_edit_delete(tmp_path):
    repo = JSONRepository()
    model = QStandardItemModel()
    controller = LibraryController(model, repo)

    data = {'title':'Test','creator':'John','year':2021,'rating':8.5}
    item = controller.add_item(data)
    assert model.rowCount() == 1
    assert item.title == 'Test'

    new_data = {'title':'Test2','creator':'Jane','year':2022,'rating':9.0}
    controller.edit_item(0, new_data)
    assert controller.get_item(0).title == 'Test2'
    assert model.item(0,0).text() == 'Test2'

    controller.delete_item(0)
    assert model.rowCount() == 0


def test_save_load(tmp_path):
    file = tmp_path / "library.json"
    repo = JSONRepository()
    model = QStandardItemModel()
    controller = LibraryController(model, repo)

    controller.add_item({'title':'A','creator':'X','year':2000,'rating':7})
    controller.add_item({'title':'B','creator':'Y','year':2001,'rating':8})

    controller.save_library(str(file))
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert len(data) == 2

    model2 = QStandardItemModel()
    controller2 = LibraryController(model2, repo)
    controller2.load_library(str(file))
    assert model2.rowCount() == 2
    assert controller2.get_item(1).title == 'B'