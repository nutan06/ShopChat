import os
import sys
from dotenv import load_dotenv
from src.exception import CustomException
from src.logger import logging
from dataclasses import dataclass
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS

@dataclass
class DataEmbeddingConfig:
    json_file_path: str = os.path.join('artifacts', 'dataset.json')
    vector_db_path: str = os.path.join('artifacts', 'FAISS_DB')

    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    embeddings     = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")

class DataEmbedding:
    def __init__(self):
        self.ingestion_config=DataEmbeddingConfig()
    
    def initiate_data_embedding(self):
        logging.info("Data Embedding - started")
        try:
            loader = JSONLoader(file_path=DataEmbeddingConfig.json_file_path, jq_schema=".[]", text_content=False)
            documents = loader.load()
            vectors_db = FAISS.from_documents(documents, DataEmbeddingConfig.embeddings)
            vectors_db.save_local(DataEmbeddingConfig.vector_db_path)
            logging.info("Data Embedding - completed")
            return vectors_db
        
        except Exception as e:
            raise CustomException(e, sys)

if __name__=="__main__":
    obj=DataEmbedding()
    FAISS_db = obj.initiate_data_embedding()
