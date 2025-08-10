from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)

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
            'year': int(self.year_edit.text()),
            'rating': float(self.rating_edit.text())
        }