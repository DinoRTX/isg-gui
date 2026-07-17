import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLabel, QProgressBar, QMessageBox,
    QLineEdit, QFormLayout, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon

from theme import THEME, get_style_sheet
from worker import ConvertWorker, RecoverWorker

CONFIG_FILE = "config.json"

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

class ThemeCustomDialog(QDialog):
    def __init__(self, current_theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Colors")
        self.setMinimumWidth(460)
        self.current_theme = current_theme.copy()
        
        layout = QFormLayout()
        self.fields = {}
        self.color_previews = {}

        keys = ["background", "accent", "text", "button_bg", "drop_background", "drop_border"]
        
        for key in keys:
            hbox = QHBoxLayout()
            
            preview = QLabel()
            preview.setFixedSize(24, 24)
            preview.setStyleSheet(f"background-color: {self.current_theme.get(key, '#000000')}; border: 1px solid #666;")
            self.color_previews[key] = preview
            
            edit = QLineEdit(self.current_theme.get(key, "#000000"))
            edit.textChanged.connect(lambda text, k=key: self.update_preview(k, text))
            self.fields[key] = edit
            
            hbox.addWidget(preview)
            hbox.addWidget(edit)
            layout.addRow(f"{key}:", hbox)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def update_preview(self, key, hex_color):
        if key in self.color_previews:
            color = hex_color if hex_color.startswith('#') else f"#{hex_color}"
            self.color_previews[key].setStyleSheet(f"background-color: {color}; border: 1px solid #666;")

    def get_colors(self):
        return {k: v.text().strip() for k, v in self.fields.items()}


class ISGWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setWindowTitle("Infinite Storage Glitch (ISG)")
        self.setMinimumSize(490, 520)
        self.setAcceptDrops(True)

        self.file_path = None
        self.output_dir = os.getcwd()
        self.current_theme = self.load_config()
        self.worker = None

        self.drop_label = QLabel("Drag & Drop a file here")
        self.drop_label.setObjectName("dropLabel")
        self.drop_label.setMinimumHeight(150)
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)

        self.status_label = QLabel(f"Output folder: {os.path.basename(self.output_dir)}")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.convert_btn = QPushButton("Convert to Video")
        self.recover_btn = QPushButton("Recover File")

        self.custom_btn = QPushButton("Customize Colors (HEX)")
        self.output_btn = QPushButton("Choose Output Folder")

        self.custom_btn.clicked.connect(self.show_custom_dialog)
        self.output_btn.clicked.connect(self.choose_output_dir)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        layout.addWidget(self.custom_btn)
        layout.addWidget(self.output_btn)
        layout.addWidget(self.drop_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addWidget(self.convert_btn)
        btn_layout.addWidget(self.recover_btn)
        layout.addLayout(btn_layout)

        self.convert_btn.clicked.connect(self.start_convert)
        self.recover_btn.clicked.connect(self.start_recover)

        self.apply_theme()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    custom = data.get("custom_theme", {})
                    base = THEME.copy()
                    base.update(custom)
                    return base
            except:
                pass
        return THEME.copy()

    def save_config(self):
        config = {"custom_theme": {k: v for k, v in self.current_theme.items()}}
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass

    def apply_theme(self):
        self.setStyleSheet(get_style_sheet(self.current_theme))
        self.update_drop_style(normal=True)

    def update_drop_style(self, normal=True):
        if normal:
            border_color = self.current_theme.get("drop_border", "#666666")
            bg_color = self.current_theme.get("drop_background", "#2b2b2b")
            self.drop_label.setStyleSheet(f"""
                border: 2px dashed {border_color};
                border-radius: 12px;
                background-color: {bg_color};
                padding: 20px;
            """)
        else:
            accent = self.current_theme.get("accent", "#00aaff")
            self.drop_label.setStyleSheet(f"""
                border: 2px dashed {accent};
                border-radius: 12px;
                background-color: {self.current_theme.get("drop_background", "#2b2b2b")};
                padding: 20px;
            """)

    def show_custom_dialog(self):
        dialog = ThemeCustomDialog(self.current_theme, self)
        if dialog.exec() == QDialog.Accepted:
            new_colors = dialog.get_colors()
            self.current_theme.update(new_colors)
            self.apply_theme()
            self.save_config()
            QMessageBox.information(self, "Success", "Custom colors saved!")

    def choose_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Choose Output Folder", self.output_dir)
        if dir_path:
            self.output_dir = dir_path
            self.status_label.setText(f"Output folder: {os.path.basename(self.output_dir)}")
            return True
        return False

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.update_drop_style(normal=False)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.update_drop_style(normal=True)

    def dropEvent(self, event: QDropEvent):
        self.update_drop_style(normal=True)
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            self.file_path = path
            self.status_label.setText(f"Selected: {os.path.basename(path)}")

    def start_convert(self):
        if not self.file_path:
            QMessageBox.warning(self, "Error", "Please drag a file first!")
            return
        self.run_worker(ConvertWorker, "Converting to video...")

    def start_recover(self):
        if not self.file_path:
            QMessageBox.warning(self, "Error", "Please drag a video first!")
            return
        self.run_worker(RecoverWorker, "Recovering file...")

    def run_worker(self, worker_class, initial_message):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(initial_message)

        self.worker = worker_class(self.file_path, self.output_dir)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self, output):
        self.progress_bar.setValue(100)
        self.status_label.setText(f"✅ Done: {os.path.basename(output)}")
        QMessageBox.information(self, "Success", f"File saved to:\n{output}")
        self.progress_bar.setVisible(False)

    def on_error(self, error):
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Error")
        QMessageBox.critical(self, "Error", str(error))

    def closeEvent(self, event):
        self.save_config()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("icon.ico")))

    window = ISGWindow()
    window.show()

    sys.exit(app.exec())