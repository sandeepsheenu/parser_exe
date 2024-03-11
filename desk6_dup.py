import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

from PyPDF2 import PdfReader
import sqlite3
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
    provided_text = preprocess_text(provided_text)
    if not provided_text:
        return []

    similarities = []
    provided_text = preprocess_text(provided_text)

    for key, jd_text in jd_texts.items():
        jd_text = preprocess_text(jd_text)
        if not jd_text:
            continue  # Skip if the preprocessed JD text is empty
        similarity = compare_texts(jd_text, provided_text)
        file_path = jd_texts[key]  # Fetch file path from the dictionary
        similarities.append((key, similarity, file_path))

    # Sort the similarities in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities

c.execute('''CREATE TABLE IF NOT EXISTS documents
             (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, file_content BLOB, text_content TEXT)''')
conn.commit()

UPLOADS_FOLDER = 'uploads'  # Folder to store uploaded files

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

        # Initialize class variables to store data
        self.provided_text = ""
        self.ranked_documents = []
        self.current_document_index = 0

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
                original_name = os.path.basename(filename)
                destination = os.path.join(UPLOADS_FOLDER, original_name)
                counter = 1
                # Check if the file with the original name exists in the folder
                while os.path.exists(destination):
                    # Append a counter to the filename until a unique filename is found
                    base_name, ext = os.path.splitext(original_name)
                    duplicate_name = f"{base_name}_duplicate_{counter}{ext}"
                    destination = os.path.join(UPLOADS_FOLDER, duplicate_name)
                    counter += 1
                # Copy the uploaded file to the destination folder
                shutil.copyfile(filename, destination)
                
                # Save the absolute path of the copied file in the database
                absolute_path = os.path.abspath(destination)

                # Save the new destination path in the database instead of the original filename
                c.execute("INSERT INTO documents (filename, file_content, text_content) VALUES (?, ?, ?)", (absolute_path, file_content, text_content))
                conn.commit()


    def retrieve_data(self):
        self.provided_text = self.text_display.toPlainText()
        if not self.provided_text:
            QMessageBox.information(self, "Error", "Please provide text content to retrieve similar documents.")
            return

        c.execute("SELECT id, filename, text_content FROM documents")  # Fetch filename along with id and text_content
        all_documents = c.fetchall()

        similarities = compare_text_with_jd(self.provided_text, {doc[0]: doc[1] for doc in all_documents})
        print(similarities)

        self.ranked_documents = [(file_path, similarity) for doc_id, similarity, file_path in similarities]

        # Display the highest ranked PDF
        self.display_current_document()
        

    def display_current_document(self):
        if self.current_document_index < len(self.ranked_documents):
            current_document = self.ranked_documents[self.current_document_index]
            pdf_url = QUrl.fromLocalFile(current_document[0])
            self.web_view.setUrl(pdf_url)
            self.current_document_index += 1  # Move to the next document for the next display


def main():
    # Create the uploads folder if it doesn't exist
    if not os.path.exists(UPLOADS_FOLDER):
        os.makedirs(UPLOADS_FOLDER)

    app = QApplication(sys.argv)
    window = DocumentProcessorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
