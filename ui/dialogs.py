from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QAction
from iconmanager.icon_manager import IconManager
from datetime import date

class AddEditDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle('编辑媒体' if item else '添加媒体')
        self._create_ui(item)

    def _create_ui(self, item):
        layout = QFormLayout(self)
        self.title_edit = QLineEdit(item.title if item else '')
        self.creator_edit = QLineEdit(item.creator if item else '')
        self.year_edit = QLineEdit(str(item.year) if item else '')
        self.rating_edit = QLineEdit(str(item.rating) if item else '')
        layout.addRow('标题：', self.title_edit)
        layout.addRow('导演/作者：', self.creator_edit)
        layout.addRow('年份：', self.year_edit)
        layout.addRow('评分：', self.rating_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self) -> dict:
        return {
            'title': self.title_edit.text(),
            'creator': self.creator_edit.text(),
            'year': int(self.year_edit.text() or date.today().year),
            'rating': float(self.rating_edit.text() or 0.0)
        }
    


class AddWarningDialog(QDialog):
    def __init__(self, message, warning_icon, parent=None):
        super().__init__(parent)
        self.setWindowTitle('警告')

        layout = QHBoxLayout(self)

        self.message_icon_button = QPushButton(self)
        self.message_icon_button.setIcon(warning_icon)
        self.message_icon_button.setIconSize(QSize(32, 32))
        self.message_icon_button.setFlat(True)
        self.message_icon_button.setFixedSize(32, 32)
        self.message_icon_button.setDisabled(True)
        self.message_icon_button.setStyleSheet("background: transparent;")

        layout.addWidget(self.message_icon_button)
        self.message_label = QLabel(message, self)
        layout.addWidget(self.message_label)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok, parent=self)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)