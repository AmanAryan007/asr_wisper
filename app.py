import os
from bardapi import Bard
import streamlit as st
from langchain import PromptTemplate, HuggingFaceHub, LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
import nltk
import PyPDF2
import re
from nltk.tokenize import word_tokenize

os.environ["_BARD_API_KEY"] = "egj4echz57CPHGu2ZLDwrXITFaZ_UzNCBEN03pOIACrPU_dhu3TpCoIxuf-NtIJ0wFhnzw."
# Download NLTK data
nltk.download('punkt')

def extract_text_from_pdf(pdf_file):
    text = ""
    with open(pdf_file, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)

        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    return text

def clean_text(text):
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    tokens = word_tokenize(text)
    cleaned_tokens = [token for token in tokens if len(token) > 1 and not token.isdigit()]
    return " ".join(cleaned_tokens)

def limit_text(text, max_words):
    tokens = word_tokenize(text)
    num_words = len(tokens)

    if num_words <= max_words:
        return text

    limited_tokens = tokens[:max_words]
    limited_text = " ".join(limited_tokens)
    return limited_text

def process_pdf_folder(folder_path):
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    documents = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        pdf_text = extract_text_from_pdf(pdf_path)
        cleaned_text = clean_text(pdf_text)
        documents.append(cleaned_text)

    return documents

# Specify the folder path where the PDF files are located
pdf_folder_path = "/workspaces/asr_wisper/book"

# Process the PDF folder and get the extracted and cleaned text from each PDF
extracted_texts = process_pdf_folder(pdf_folder_path)

# Join the elements of the extracted_texts list with newline characters to create a single string
output_text = "\n".join(extracted_texts)

# Save the extracted, cleaned, and limited text into a text file
output_file = "documents.txt"
with open(output_file, "w", encoding="utf-8") as file:
    file.write(output_text)

# Load the documents
documents = TextLoader('documents.txt').load()

def split_docs(documents, chunk_size=400, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
    return docs

document_chunk = split_docs(documents)
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def main():
    st.title("PDF Text Extraction and Question Answering")

    # Sidebar
    pdf_folder_path = st.sidebar.text_input("Enter PDF Folder Path", "book")

    # File upload
    pdf_file = st.sidebar.file_uploader("Upload PDF File", type=["pdf"])

    if pdf_file:
        # Save the uploaded file to the specified folder
        upload_path = os.path.join(pdf_folder_path, pdf_file.name)
        with open(upload_path, "wb") as f:
            f.write(pdf_file.read())
        st.success(f"Uploaded file '{pdf_file.name}' saved to '{upload_path}'.")

    if st.sidebar.button("Process PDFs"):
        extracted_texts = process_pdf_folder(pdf_folder_path)
        output_text = "\n".join(extracted_texts)
        output_file = "documents.txt"
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(output_text)
        st.success(f"Extracted text from PDFs in the folder has been saved to '{output_file}'.")

    # Main content
    query = st.text_input("Enter your question:")
    change_language = st.checkbox("Change the language of the response?")

    if change_language:
        new_language = st.text_input("Enter the desired language:")

        if st.button("Get Answer"):
            # Here, you can replace the ChromaDB code with your desired logic for answering questions.
            # For simplicity, I'm using Bard API for answering questions.
            response = Bard().get_answer(query)['content']
            st.write("Response:", response)

            if change_language:
                trans_res = f"{response}\ntranslate into {new_language}".strip()
                translated_response = Bard().get_answer(str(trans_res))['content']
                st.write("Translated response:", translated_response)

if __name__ == "__main__":
    main()
