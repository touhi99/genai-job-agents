from langchain_community.document_loaders import PyPDFLoader
from docx import Document

def load_cv(file):
    loader = PyPDFLoader(file)
    pages = loader.load()
    page_content = ''
    for i in range(len(pages)):
        page_content += pages[i].page_content
    return page_content

def write_to_docx(text):
    print("Inside write to doc")
    print(text)
    doc = Document()
    paragraphs = text.split('\n')
    # Add each paragraph to the document
    for para in paragraphs:
        doc.add_paragraph(para)
    # Save the document to the specified file
    filename = 'tmp/cover_letter.docx'
    doc.save(filename)
    print(f"Document saved as {filename}")
    return filename