import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QWidget, QTextEdit,QLabel,QHBoxLayout,QDesktopWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl,Qt
from PyQt5.QtGui import QPixmap

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


        # Add logo
        self.logo_label = QLabel()
        pixmap = QPixmap("download.png")  # Adjust the path to your logo image
        self.logo_label.setPixmap(pixmap)
        self.layout.addWidget(self.logo_label)

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
# class DocumentProcessorApp(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         # Initialize class variables to store data
#         self.provided_text = ""
#         self.ranked_documents = []
#         self.current_document_index = 0

#         self.setWindowTitle("RSC systems pvt ltd")

#         # Set your desired window size
#         window_width = 800
#         window_height = 600

#         # Calculate the center point of the screen
#         screen_geometry = QDesktopWidget().screenGeometry()
#         screen_center_x = (screen_geometry.width() - window_width) / 2
#         screen_center_y = (screen_geometry.height() - window_height) / 2

#         # Set window geometry to be centered
#         self.setGeometry(screen_center_x, screen_center_y, window_width, window_height)

#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#         self.layout = QVBoxLayout()

#         # Create a horizontal layout for logo and center it
#         logo_layout = QHBoxLayout()
#         logo_layout.setAlignment(Qt.AlignCenter)

#         # Add logo to the center-aligned layout
#         self.logo_label = QLabel()
#         pixmap = QPixmap("download.png")  # Adjust the path to your logo image
#         self.logo_label.setPixmap(pixmap)
#         logo_layout.addWidget(self.logo_label)

#         # Add the logo layout to the main layout
#         self.layout.addLayout(logo_layout)

#         # Create a style for the buttons
#         button_style = """
#             QPushButton {
#                 background-color: green;
#                 color: white;
#                 border: none;
#                 padding: 8px 16px;
#                 border-radius: 4px;
#             }
#             QPushButton:hover {
#                 background-color: #3d8d3d; /* slightly darker green */
#             }
#         """

#         self.upload_button = QPushButton("Upload Documents", self)
#         self.upload_button.setStyleSheet(button_style)  # Apply the style
#         self.upload_button.clicked.connect(self.upload_documents)
#         self.layout.addWidget(self.upload_button)

#         self.retrieve_button = QPushButton("Retrieve Data", self)
#         self.retrieve_button.setStyleSheet(button_style)  # Apply the style
#         self.retrieve_button.clicked.connect(self.retrieve_data)
#         self.layout.addWidget(self.retrieve_button)

#         self.central_widget.setLayout(self.layout)

#         self.web_view = QWebEngineView()
#         self.layout.addWidget(self.web_view)

#         self.text_display = QTextEdit()  # Create a QTextEdit widget
#         self.layout.addWidget(self.text_display)  # Add the QTextEdit widget to your layout


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


        # Clear any previous content in the web view
        self.web_view.setHtml('')

        # Display the highest ranked PDF
        self.display_current_document()

            

    def display_current_document(self):
        if self.current_document_index < len(self.ranked_documents):
            current_document = self.ranked_documents[self.current_document_index]
            pdf_url = QUrl.fromLocalFile(current_document[0])
            print(pdf_url)
            self.web_view.setUrl(pdf_url)
            print("url")

    def next_document(self):
        self.current_document_index += 1
        if self.current_document_index >= len(self.ranked_documents):
            self.current_document_index = 0  # Loop back to the beginning if reached the end
        self.display_current_document()            

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
