import numpy as np
import pandas as pd
import time
import openai
import os
import faiss
from typing import List
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.document_loaders import OnlinePDFLoader, PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings

MAX_TEXT_LENGTH = 512
NUMBER_PRODUCTS = 1000
PDF_DIR = "data/pdfs/"
DEPARTMENT_OF_EDUCATION_DATA = "data/DOE/edubasealldata20240108.csv"

class DataOperator:

    def __init__(self):
        self.doe_data = self.create_doe_vector_store()
        self.pdf_data = None #self.create_pdf_vector_store()

    def auto_truncate(self, val):
        return val[:MAX_TEXT_LENGTH]

    def create_pdf_vector_store(self):
        all_documents = []
        loaders = [PyPDFLoader(os.path.join(pdf_folder_path, fn)) for fn in os.listdir(pdf_folder_path)]
        for loader in loaders:
            pdf_doc = loader.load()
            # Split by separator and merge by character count
            # Create a CharacterTextSplitter object
            text_splitter = CharacterTextSplitter(
                separator="\n\n",
                chunk_size=800,
                chunk_overlap=100,
                length_function=len,
            )
            documents = text_splitter.split_documents(pdf_doc)
            all_documents.extend(documents)

        hf_embeddings = self.create_hf_embeddings()

        # Create vectors
        try:
            faiss_db = FAISS.load_local('faiss_pdf_index_constitution', hf_embeddings)
        except:
            faiss_db = FAISS.from_documents(all_documents, hf_embeddings)
            # Persist the vectors locally on disk
            faiss_db.save_local("faiss_pdf_index_constitution")

        return faiss_db

    def create_extra_description(self, row):
        """Creates a new description of the school
        returns str
        """

        # EstablishmentName
        # TypeOfEstablishment(name)
        # PhaseOfEducation(name)
        # StatutoryLowAge
        # StatutoryHighAge
        # Gender(name)
        # ReligiousEthos(name)
        # RSCRegion(name)
        # OfstedRating(name)

        description = f"The name of this school is {row['EstablishmentName']} and it's located in {row['AdministrativeWard (name)']} in {row['RSCRegion(name)']}. It is a {row['TypeOfEstablishment(name)']} {row['PhaseOfEducation(name)']} school for {row['Gender(name)']} genders." \
                      f", The religous ethos is {row['ReligiousEthos(name)']} \
        The ofsted rating for this establishment is {row['OfstedRating(name)']}."
        return description


    def preprocess_data(self, df):
        # london_regions = ['', '', '']
        df['extra_description'] = [create_extra_description(row) for id, row in df.iterrows()]

        return df

    def create_hf_embeddings(self):
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        hf_embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs
        )
        return hf_embeddings


    def create_doe_vector_store(self):
        df = pd.read_csv(DEPARTMENT_OF_EDUCATION_DATA, header=0)
        hf_embeddings = self.create_hf_embeddings()

        #create langchain documents from dataset
        documents = [Document(page_content=row['extra_description'], metadata=row) for id, row in df.iterrows()]
        print(documents)
        text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)

        # Create vectors
        try:
            vectorstore = FAISS.load_local('faiss_doe_index_constitution', hf_embeddings)
        except:
            vectorstore = FAISS.from_documents(texts, hf_embeddings)
            # Persist the vectors locally on disk
            vectorstore.save_local("faiss_doe_index_constitution")

        return vectorstore

    def vector_search_ofsted_reports(self, query):
        return self.vector_search(query, self.pdf_data)

    def vector_search_doe_table(self, query):
        return self.vector_search(query, self.doe_data)

    def vector_search(self, query, faiss_vector_store, top_k=4):
        is_relevant = False
        relevant_docs = faiss_vector_store.similarity_search(query, k=4)[:top_k]
        is_relevant = are_docs_relevant_to_query(query, relevant_docs)
        return {"docs":relevant_docs, "are_relevant":is_relevant}