import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QLabel, QWidget, QTextEdit, QMessageBox
from PyQt5.QtCore import Qt
from docx import Document
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Upload and Text Extraction")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.upload_btn = QPushButton("Upload Files", self)
        self.upload_btn.clicked.connect(self.upload_files)
        self.layout.addWidget(self.upload_btn)

        self.info_label = QLabel("No files uploaded yet.", self)
        self.layout.addWidget(self.info_label)

        self.text_edit = QTextEdit(self)
        self.layout.addWidget(self.text_edit)

        self.extract_btn = QPushButton("Extract and Store Text", self)
        self.extract_btn.clicked.connect(self.extract_and_store)
        self.layout.addWidget(self.extract_btn)

        self.central_widget.setLayout(self.layout)

        self.db_connection = sqlite3.connect("files.db")
        self.cursor = self.db_connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS files (
                                    id INTEGER PRIMARY KEY,
                                    filename TEXT,
                                    text TEXT
                                )''')
        self.db_connection.commit()

    def upload_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "PDF Files (*.pdf);;Word Files (*.docx)")
        if files:
            self.files = files
            self.info_label.setText(f"{len(files)} files uploaded.")

    def extract_and_store(self):
        if hasattr(self, 'files'):
            for file in self.files:
                filename = os.path.basename(file)
                text = self.extract_text(file)
                self.store_text(filename, text)
            QMessageBox.information(self, "Extraction Complete", "Text extraction and storage complete.")
            self.text_edit.clear()
        else:
            QMessageBox.warning(self, "No Files", "Please upload files first.")

    def extract_text(self, file_path):
        if file_path.endswith('.pdf'):
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfFileReader(file)
                    text = ''
                    for page_num in range(reader.numPages):
                        page = reader.getPage(page_num)
                        text += page.extractText()
                    return text
            except Exception as e:
                print(e)
                return ""
        elif file_path.endswith('.docx'):
            try:
                doc = Document(file_path)
                text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                return text
            except Exception as e:
                print(e)
                return ""
        else:
            return ""

    def store_text(self, filename, text):
        self.cursor.execute("INSERT INTO files (filename, text) VALUES (?, ?)", (filename, text))
        self.db_connection.commit()

    def closeEvent(self, event):
        self.db_connection.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
