import os
import sys
from ImagePathIterator import ImagePathIterator

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPushButton, QVBoxLayout, QWidget, QScrollArea
)


class ImageViewer(QMainWindow):
    """Основное окно приложения для просмотра изображений."""

    def __init__(self) -> None:
        """Инициализирует окно просмотра изображений."""
        super().__init__()

        self.iterator: Optional[ImagePathIterator] = None
        self.pixmap: Optional[QPixmap] = None
        self.current_index: int = 0

        self.setWindowTitle("Просмотр изображений")
        self.setGeometry(100, 100, 800, 600)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Создает и настраивает элементы пользовательского интерфейса."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.image_label = QLabel("Выберите файл или папку")
        self.image_label.setAlignment(Qt.AlignCenter)
        scroll_area.setWidget(self.image_label)

        main_layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()

        csv_button = QPushButton("CSV файл")
        csv_button.clicked.connect(self.load_csv)
        button_layout.addWidget(csv_button)

        dir_button = QPushButton("Папка")
        dir_button.clicked.connect(self.load_dir)
        button_layout.addWidget(dir_button)

        self.prev_button = QPushButton("Назад")
        self.prev_button.clicked.connect(self.show_prev)
        self.prev_button.setEnabled(False)
        button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Вперед")
        self.next_button.clicked.connect(self.show_next)
        self.next_button.setEnabled(False)
        button_layout.addWidget(self.next_button)

        main_layout.addLayout(button_layout)

        self.status_bar = self.statusBar()

    def load_csv(self) -> None:
        """Загружает изображения из CSV файла с аннотациями."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите CSV", "", "CSV (*.csv)"
        )

        if file_path:
            try:
                self.iterator = ImagePathIterator(file_path)
                self._start_viewing()
            except Exception as e:
                error_message = f"Не удалось загрузить CSV\n{str(e)}"
                QMessageBox.critical(self, "Ошибка", error_message)

    def load_dir(self) -> None:
        """Загружает изображения из указанной директории."""
        dir_path = QFileDialog.getExistingDirectory(self, "Выберите папку")

        if dir_path:
            try:
                self.iterator = ImagePathIterator(dir_path)
                self._start_viewing()
            except Exception as e:
                error_message = f"Не удалось загрузить папку\n{str(e)}"
                QMessageBox.critical(self, "Ошибка", error_message)

    def _start_viewing(self) -> None:
        """Начинает просмотр загруженных изображений."""
        if self.iterator and len(self.iterator) > 0:
            self.current_index = 0
            self.next_button.setEnabled(True)
            self._show_current_image()
        else:
            self.image_label.setText("Нет изображений")

    def _show_current_image(self) -> None:
        """Отображает текущее изображение."""
        if not self.iterator:
            return

        try:
            self.iterator.current_index = self.current_index
            image_path = self.iterator.image_paths[self.current_index]

            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)

                if not pixmap.isNull():
                    self.pixmap = pixmap
                    self.image_label.setPixmap(pixmap)
                    self.image_label.adjustSize()

                    filename = os.path.basename(image_path)
                    total = len(self.iterator)
                    current = self.current_index + 1
                    self.status_bar.showMessage(f"{current}/{total}: {filename}")
                else:
                    self.image_label.setText("Ошибка загрузки изображения")
            else:
                self.image_label.setText("Файл не найден")

        except Exception as e:
            self.image_label.setText(f"Ошибка: {str(e)}")

    def show_next(self) -> None:
        """Переходит к следующему изображению."""
        if self.iterator and self.current_index < len(self.iterator) - 1:
            self.current_index += 1
            self.prev_button.setEnabled(True)
            self._show_current_image()

            if self.current_index == len(self.iterator) - 1:
                self.next_button.setEnabled(False)

    def show_prev(self) -> None:
        """Возвращается к предыдущему изображению."""
        if self.iterator and self.current_index > 0:
            self.current_index -= 1
            self.next_button.setEnabled(True)
            self._show_current_image()

            if self.current_index == 0:
                self.prev_button.setEnabled(False)


def main() -> None:
    """
    Точка входа в приложение.
    
    Создает и запускает главное окно просмотра изображений.
    """
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()