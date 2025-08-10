import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QDialog, QMessageBox, QFileDialog
)
from PySide6.QtGui import (
    QAction, QIcon, QStandardItemModel, QStandardItem
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QSettings, Slot
)
import qt_material

from models.media_model import MediaItem
from controllers.library_controller import LibraryController
from services.omdb_worker import OMDbWorker
from repository.json_repository import JSONRepository
from settings.settings_manager import SettingsManager
from ui.dialogs import AddEditDialog


class MainWindow(QMainWindow):
    """主窗口: UI层"""
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.setWindowTitle("Media Library Manager")
        self._init_settings()
        self._init_ui()
        self._init_controller()

    def _init_settings(self):
        """加载并应用用户设置"""
        self.settings = SettingsManager()
        geometry = self.settings.value('window/geometry')
        if geometry:
            self.restoreGeometry(geometry)
        self.last_path = self.settings.get_last_path()

    def _init_ui(self):
        """创建界面元素: 菜单、工具栏、状态栏、主视图"""
        qt_material.apply_stylesheet(
            QApplication.instance(), theme='dark_teal.xml'
        )
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_status_bar()
        self._create_table_view()

    def _create_actions(self):
        """创建并配置动作"""
        icon_path = lambda name: os.path.join(self.base_dir, 'icons', name)
        self.add_action = QAction(QIcon(icon_path('add.png')), '添加', self)
        self.add_action.triggered.connect(self.on_add)
        self.delete_action = QAction(QIcon(icon_path('delete.png')), '删除', self)
        self.delete_action.triggered.connect(self.on_delete)
        self.edit_action = QAction(QIcon(icon_path('edit.png')), '编辑', self)
        self.edit_action.triggered.connect(self.on_edit)
        self.save_action = QAction(QIcon(icon_path('save.png')), '保存', self)
        self.save_action.triggered.connect(self.on_save)
        self.load_action = QAction(QIcon(icon_path('load.png')), '加载', self)
        self.load_action.triggered.connect(self.on_load)

    def _create_menus(self):
        """设置菜单栏"""
        file_menu = self.menuBar().addMenu('文件')
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.load_action)
        edit_menu = self.menuBar().addMenu('编辑')
        edit_menu.addAction(self.add_action)
        edit_menu.addAction(self.delete_action)
        edit_menu.addAction(self.edit_action)

    def _create_toolbar(self):
        """设置工具栏"""
        toolbar = self.addToolBar('工具')
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.delete_action)
        toolbar.addAction(self.edit_action)

    def _create_status_bar(self):
        """初始化状态栏"""
        self.statusBar().showMessage('就绪')

    def _create_table_view(self):
        """初始化QTableView和模型"""
        self.model = QStandardItemModel(0, 4, self)
        headers = ['标题', '导演/作者', '年份', '评分']
        self.model.setHorizontalHeaderLabels(headers)
        self.table_view = QTableView(self)
        self.table_view.setModel(self.model)
        self.setCentralWidget(self.table_view)

    def _init_controller(self):
        """初始化控制层: 管理数据操作"""
        repo = JSONRepository(self.last_path)
        self.controller = LibraryController(self.model, repo)

    @Slot()
    def on_add(self):
        dialog = AddEditDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            item = self.controller.add_item(data)
            worker = OMDbWorker(item.title)
            worker.fetched.connect(lambda info: self.controller.update_item(item, info))
            worker.start()

    @Slot()
    def on_delete(self):
        indexes = self.table_view.selectionModel().selectedRows()
        for index in sorted(indexes, reverse=True):
            self.controller.delete_item(index.row())

    @Slot()
    def on_edit(self):
        selected = self.table_view.currentIndex()
        if not selected.isValid():
            QMessageBox.warning(self, '提示', '请选择要编辑的条目')
            return
        row = selected.row()
        item = self.controller.get_item(row)
        dialog = AddEditDialog(self, item)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.controller.edit_item(row, data)

    @Slot()
    def on_save(self):
        path = self.settings.get_last_path()
        if not path:
            path, _ = QFileDialog.getSaveFileName(
                self, '保存媒体库', '', 'JSON Files (*.json)'
            )
        if path:
            self.controller.save_library(path)
            self.settings.set_last_path(path)

    @Slot()
    def on_load(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '加载媒体库', '', 'JSON Files (*.json)'
        )
        if path:
            self.controller.load_library(path)
            self.settings.set_last_path(path)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()