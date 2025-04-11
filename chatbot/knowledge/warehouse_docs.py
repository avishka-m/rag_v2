import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
# from langchain_chroma import Chroma
from config import CHROMA_PERSIST_DIRECTORY, OPENAI_API_KEY

class WarehouseKnowledgeBase:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        self.docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "docs")
        
        # Create vector store if it doesn't exist
        if not os.path.exists(CHROMA_PERSIST_DIRECTORY):
            self._create_vector_store()
        
        # Load the existing vector store
        self.db = Chroma(
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=self.embeddings
        )
    
    def _create_vector_store(self):
        """Create the vector store from warehouse documentation files"""
        # Make sure the docs directory exists
        if not os.path.exists(self.docs_path):
            os.makedirs(self.docs_path)
            # Create a sample document if none exist
            with open(os.path.join(self.docs_path, "sample_procedures.txt"), "w") as f:
                f.write("Warehouse procedures include: receiving, picking, packing, and shipping.")
        
        # Load documents
        loader = DirectoryLoader(self.docs_path, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        splits = text_splitter.split_documents(documents)
        
        # Create and persist the vector store
        Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIRECTORY
        )
        
    def query_knowledge_base(self, query, n_results=3):
        """Query the knowledge base for relevant information"""
        results = self.db.similarity_search(query, k=n_results)
        return results
    
    def add_document(self, file_path):
        """Add a new document to the knowledge base"""
        loader = TextLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # Add documents to existing vector store
        self.db.add_documents(splits)
        self.db.persist()
        
        return f"Added {len(splits)} chunks from {file_path} to the knowledge base"