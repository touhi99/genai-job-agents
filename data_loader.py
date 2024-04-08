from langchain_community.document_loaders import PyPDFLoader

def load_cv(file):
    loader = PyPDFLoader(file)
    pages = loader.load()
    page_content = ''
    for i in range(len(pages)):
        page_content += pages[i].page_content
    return page_content