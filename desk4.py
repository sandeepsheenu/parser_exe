import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QWidget,QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

from PyPDF2 import PdfReader
import sqlite3
import tempfile
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Connect to the SQLite database
conn = sqlite3.connect('my_documents.db')
c = conn.cursor()

def preprocess_text(text):
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.lower() not in stop_words]
    return ' '.join(tokens)

def compare_texts(text1, text2):
    vectorizer = TfidfVectorizer()
    vector1 = vectorizer.fit_transform([text1])
    vector2 = vectorizer.transform([text2])
    similarity = cosine_similarity(vector1, vector2)
    return similarity[0][0]

def compare_text_with_jd(provided_text, jd_texts):
    #print(jd_texts)
    provided_text = preprocess_text(provided_text)

    similarities = []

    for key, jd_text in jd_texts.items():
        jd_text = preprocess_text(jd_text)
        similarity = compare_texts(jd_text, provided_text)
        similarities.append((key, similarity))

    # Sort the similarities in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities

conn = sqlite3.connect('my_documents.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS documents
             (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, file_content BLOB, text_content TEXT)''')
conn.commit()

def close_connection():
    conn.close()

def process_documents(filename):
    text = ""
    with open(filename, 'rb') as file:
        file_content = file.read()  # Read the file content as binary data
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return file_content, text

class DocumentProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RSC systems pvt ltd")
        self.setGeometry(0, 0, 2000, 1000)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        self.upload_button = QPushButton("Upload Documents", self)
        self.upload_button.clicked.connect(self.upload_documents)
        self.layout.addWidget(self.upload_button)

        self.retrieve_button = QPushButton("Retrieve Data", self)
        self.retrieve_button.clicked.connect(self.retrieve_data)
        self.layout.addWidget(self.retrieve_button)

        self.central_widget.setLayout(self.layout)


        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)


    
        self.text_display = QTextEdit()  # Create a QTextEdit widget
        self.layout.addWidget(self.text_display)  # Add the QTextEdit widget to your layout
        

    def upload_documents(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Documents to Upload", "", "PDF files (*.pdf);;Word files (*.docx)")
        if filenames:
            num_documents = len(filenames)
            QMessageBox.information(self, "Upload Successful", f"{num_documents} documents uploaded.")
            for filename in filenames:
                file_content, text_content = process_documents(filename)

                print(text_content)
                c.execute("INSERT INTO documents (filename, file_content, text_content) VALUES (?, ?, ?)", (filename, file_content, text_content))
                conn.commit()
    

    def retrieve_data(self):
        provided_text = self.text_display.toPlainText()
        #print(provided_text,"provided text")
        if not provided_text:
            QMessageBox.information(self, "Error", "Please provide text content to retrieve similar documents.")
            return

        c.execute("SELECT id, text_content FROM documents")
        all_texts = dict(c.fetchall())
        #print(all_texts,"tet content are coming")

        similarities = compare_text_with_jd(provided_text, all_texts)
 
        # Placeholder for further processing/display of similar documents and similarities
        for pk, similarity_score in similarities:
            print("Document ID:", pk, "Similarity Score:", similarity_score)
   
    # def retrieve_data(self):
    # # Get the text content entered by the user
    #     text_content = self.text_display.toPlainText()
    #     print(text_content,"text")

    #     if text_content:
    #         # If text content is available, retrieve data
    #         c.execute("SELECT * FROM documents")
    #         results = c.fetchall()

    #         if results:
    #             for result in results:
    #                 print("ID:", result[0])
    #                 print("Filename:", result[1])
    #                 print("Text Content:", result[3])

    #                 # If file content is stored as BLOB, you may print its length or decode it if it's a text file
    #                 #print("File Content Length:", len(result[2]))
    #                 # file_content_bytes = bytes(result[2])
    #                 # print("File Content (Hex):", file_content_bytes.hex())
    #                 # print("File Content:", result[2].decode('utf-8'))
    #                 print("\n")
    #         else:
    #             print("No documents found in the database.")
    #     else:
    #         # If no text content is entered, display a message
    #         QMessageBox.information(self, "Warning", "Need text content to retrieve data.")
   
    # def retrieve_data(self):
    #     c.execute("SELECT * FROM documents")
    #     results = c.fetchall()

    #     if results:
    #         for result in results:
    #             print("ID:", result[0])
    #             print("Filename:", result[1])
    #             print("Text Content:", result[3])
    #             #If file content is stored as BLOB, you may print its length or decode it if it's a text file
    #             print("File Content Length:", len(result[2]))
    #             #file_content_bytes = bytes(result[2])
    #             #print("File Content (Hex):", file_content_bytes.hex())
    #             # print("File Content:", result[2].decode('utf-8'))
    #             print("\n")            

def main():
    app = QApplication(sys.argv)
    window = DocumentProcessorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
