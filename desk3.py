import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QMessageBox, QLineEdit, QVBoxLayout, QWidget,QTextEdit
from PyPDF2 import PdfReader
import sqlite3

# Placeholder function for processing uploaded documents


  # Connect to SQLite database
conn = sqlite3.connect('document_database.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS uploaded_documents
             (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, text_content TEXT)''')
conn.commit()

# Close the connection when the application exits
def close_connection():
    conn.close()


def process_documents(filename ):
    print(filename,"file process documents")
    text = ""
    # for file in filenames:
    pdf_reader = PdfReader(filename )
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
        # print(text)
    return text


# Placeholder function for processing user-entered text
def process_user_text(text):
    # Placeholder implementation
    print("Processing user-entered text:", text)
    return "Processed result"

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

        self.text_entry = QLineEdit()
        self.layout.addWidget(self.text_entry)

        self.central_widget.setLayout(self.layout)

        

        # self.text_display = QTextEdit()  # Create a QTextEdit widget
        # self.layout.addWidget(self.text_display)  # Add the QTextEdit widget to your layout
        
              
        

    def upload_documents(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Documents to Upload", "", "PDF files (*.pdf);;Word files (*.docx)")
        if filenames:
            num_documents = len(filenames)
            QMessageBox.information(self, "Upload Successful", f"{num_documents} documents uploaded.")
            for filename  in filenames:
                print(filename)
                text_content = process_documents(filename )
                print(text_content,"1")
                # Save uploaded document and extracted text to database
                c.execute("INSERT INTO uploaded_documents (filename, text_content) VALUES (?, ?)", (filename, text_content))
                conn.commit()
                print("stored----------------------")
            # print(process_documents(filenames))

    # def retrieve_data(self):
    #     # user_text = self.text_entry.text()
    #     # if user_text:
    #     #     results = process_user_text(user_text)
    #     #     QMessageBox.information(self, "Data Retrieved", f"Results: {results}")
        
    #     self.c.execute("SELECT * FROM uploaded_documents")
    #     results = self.c.fetchall()

    #     all_data = ""
    #     for result in results:
    #         all_data += f"ID: {result[0]}, Filename: {result[1]}, Text Content: {result[2]}\n"

    #     self.text_display.setPlainText(all_data)  # Set the plain text content of the QTextEdit widget 
    # def retrieve_data(self):
    #     c.execute("SELECT * FROM uploaded_documents")
    #     results = c.fetchall()

    #     all_data = ""
    #     for result in results:
    #         all_data += f"ID: {result[0]}, Filename: {result[1]}, Text Content: {result[2]}\n"

    #     self.text_display.setPlainText(all_data)
    def retrieve_data(self):
        c.execute("SELECT id FROM uploaded_documents")
        results = c.fetchall()

        if results:
            document_ids = [result[0] for result in results]
            print("Document IDs:", document_ids)
        else:
            print("No documents found in the database.")

            
            

def main():
    app = QApplication(sys.argv)
    window = DocumentProcessorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
