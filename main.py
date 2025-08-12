import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QDialog, QMessageBox, QFileDialog
)
from PySide6.QtGui import (
    QAction, QIcon, QStandardItemModel, QStandardItem, QPalette, QPainter, QColor, QPixmap
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QSettings, Slot, QTimer
)

from PySide6.QtSvg import QSvgRenderer

from qt_material import apply_stylesheet

from models.media_model import MediaItem
from controllers.library_controller import LibraryController
from services.omdb_worker import OMDbWorker
from repository.json_repository import JSONRepository
from settings.settings_manager import SettingsManager
from ui.dialogs import AddEditDialog
from iconmanager.icon_manager import IconManager
from ui.dialogs import AddWarningDialog
from services.application_manager import ApplicationManager





class MainWindow(QMainWindow):
    worker_created = Signal(QThread)

    """主窗口: UI层"""
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.setWindowTitle("Media Library Manager")
        self.theme = 'dark_teal.xml'

        apply_stylesheet(
            QApplication.instance(), theme=self.theme, 
            invert_secondary=('light' in self.theme))

        icon_path_root = os.path.join(self.base_dir, 'icons')
        self.icon_manager = IconManager(self.theme, base_path=icon_path_root)

        self.setWindowIcon(self.icon_manager.get_app_icon())

        self._init_settings()
        self._init_ui()
        self._init_controller()


    def _init_settings(self):
        """加载并应用用户设置"""
        self.settings = SettingsManager()
        geometry = self.settings.value('window/geometry')
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.setGeometry(100, 100, 800, 600)
        self.last_path = self.settings.get_last_path()

    def closeEvent(self, event):
        self.settings.set_last_path(self.last_path)
        self.settings.set_value('window/geometry', self.saveGeometry())
        super().closeEvent(event)

    def _init_ui(self):
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_status_bar()
        self._create_table_view()

    def _create_actions(self):
        """创建并配置动作"""
        icon_path = lambda name: os.path.join(self.base_dir, 'icons', name)
        icon = self.icon_manager.get_add_icon()
        self.add_action = QAction(icon, '添加', self)
        self.add_action.setStatusTip('添加新媒体项')
        self.add_action.triggered.connect(self.on_add)

        icon = self.icon_manager.get_delete_icon()
        self.delete_action = QAction(icon, '删除', self)
        self.delete_action.setStatusTip('删除选中的媒体项')
        self.delete_action.triggered.connect(self.on_delete)

        icon = self.icon_manager.get_edit_icon()
        self.edit_action = QAction(icon, '编辑', self)
        self.edit_action.setStatusTip('编辑选中的媒体项')
        self.edit_action.triggered.connect(self.on_edit)

        icon = self.icon_manager.get_save_icon()
        self.save_action = QAction(icon, '保存', self)
        self.save_action.setStatusTip('保存媒体库到文件')
        self.save_action.triggered.connect(self.on_save)

        icon = self.icon_manager.get_file_open_icon()
        self.load_action = QAction(icon, '加载', self)
        self.load_action.setStatusTip('从文件加载媒体库')
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
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

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
            worker = OMDbWorker(item.title, self)
            worker.fetched.connect(lambda info: self.controller.update_item(item, info))
            self.worker_created.emit(worker)
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
            warning_icon = self.icon_manager.get_warning_icon()
            message_box = AddWarningDialog('请选择要编辑的媒体项', warning_icon,self)
            message_box.setWindowModality(Qt.NonModal)
            message_box.show()
            QTimer.singleShot(3000, message_box.accept)
            return
        row = selected.row()
        item = self.controller.get_item(row)
        dialog = AddEditDialog(self, item)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.controller.edit_item(row, data)

    @Slot()
    def on_save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, '保存媒体库', (self.last_path if self.last_path else ''), 
            'JSON Files (*.json)'
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

    def closeEvent(self, event):
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app_manager = ApplicationManager(app)
    window = MainWindow()
    window.worker_created.connect(app_manager.add_worker)
    window.show()
    app.lastWindowClosed.connect(app_manager.check_quit)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
