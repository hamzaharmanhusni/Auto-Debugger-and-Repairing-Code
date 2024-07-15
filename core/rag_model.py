from langchain_community.document_loaders import PythonLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.document_loaders.generic import GenericLoader
from langchain.text_splitter import Language
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter

#Chungking 
def chunk_file(path_file):
    # Create a loader object to load files from the filesystem
    loader = GenericLoader.from_filesystem(
        path=path_file,
        glob="**/*",
        suffixes=[".py"],
        parser=LanguageParser(language=Language.PYTHON, parser_threshold=500)
    )

    # Load documents using the loader
    docs = loader.load()

    # Create a text splitter to split documents into chunks
    documents_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=200,
        chunk_overlap=0
    )
    
    # Split the documents into chunks of text
    texts = documents_splitter.split_documents(docs)
    
    return texts

# Vector store

def vector_store(texts):
    vectorstore = Chroma.from_documents(
        documents=texts,
        collection_name="rag-chroma",
        embedding=OpenAIEmbeddings(),
    )
    
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k":5})
    
    return retriever

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

