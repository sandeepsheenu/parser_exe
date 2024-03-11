import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog,QMessageBox
import sqlite3
import PyPDF2
from docx import Document

class ResumeParserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resume Parser")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Text display area
        self.text_display = QTextEdit()
        layout.addWidget(self.text_display)
        
        # Upload button
        upload_button = QPushButton("Upload Resume")
        upload_button.clicked.connect(self.upload_resume)
        upload_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        layout.addWidget(upload_button)
        
        # Extract button
        extract_button = QPushButton("upload")
        extract_button.clicked.connect(self.extract_text)
        layout.addWidget(extract_button)

         # Retrieve button
        retrieve_button = QPushButton("Retrieve All Text")
        retrieve_button.clicked.connect(self.retrieve_all_text)
        layout.addWidget(retrieve_button)
        
        # Database connection
        self.conn = sqlite3.connect('resumes.db')
        self.cur = self.conn.cursor()
        self.create_table()
        
    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS Resumes (
                            id INTEGER PRIMARY KEY,
                            text TEXT
                            )''')
        self.conn.commit()
        
    def upload_resume(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Resume", "", "PDF Files (*.pdf);;Word Files (*.docx)")
        if file_path:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                resume_text = file.read()
            self.text_display.setText(resume_text)
        else:
            QMessageBox.warning(self, "Error", "Please select a document.")
    def extract_text(self):
        resume_text = self.text_display.toPlainText()
        # Insert extracted text into the database
        self.cur.execute('''INSERT INTO Resumes (text) VALUES (?)''', (resume_text,))
        self.conn.commit()
        self.text_display.clear()
        self.text_display.append("Text extracted and stored in the database.")

    # def retrieve_all_text(self):
    #     # Retrieve all text from the database
    #     self.cur.execute("SELECT text FROM Resumes")
    #     results = self.cur.fetchall()
        
    #     all_text = ""
    #     for result in results:
    #         all_text += result[0] + "\n"
        
    #     self.text_display.setText(all_text)  
        
    def retrieve_all_text(self):
        # Retrieve only the primary keys from the database
        self.cur.execute("SELECT * FROM Resumes")
        results = self.cur.fetchall()
        
        all_ids = ""
        for result in results:
            all_ids += str(result[0]) + "\n"
        
        self.text_display.setText(all_ids)    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResumeParserApp()
    window.show()
    sys.exit(app.exec_())
