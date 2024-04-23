import os
import re
import tempfile
import openai
import requests
import io
import base64
from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import faiss
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import openai as lc_openai
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define global variable to store the knowledge base
knowledgebase = None

def process_pdf(pdf_url):
    response = requests.get(pdf_url, stream=True)
    if response.status_code != 200:
        print(f"Failed to download PDF: {response.status_code}")
        return None  # Handle error appropriately

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                tmp_file.write(chunk)

    pdf_reader = PdfReader(tmp_file.name)
    text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    embeddings = OpenAIEmbeddings()
    return faiss.FAISS.from_texts(chunks, embeddings)

def fetch_image_from_drive(file_name):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'pdf-python-420718-4a9ce0b58697.json'
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    
    results = service.files().list(q=f"name contains '{file_name}' and mimeType='image/jpeg'").execute()
    items = results.get('files', [])
    if not items:
        print(f"No images found for {file_name}")
        return None

    file_id = items[0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    base64_image = base64.b64encode(fh.getvalue()).decode('utf-8')
    print(f"Fetched and encoded image: {file_name}")
    return base64_image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask_pdf', methods=['POST'])
def ask_pdf():
    global knowledgebase
    if not knowledgebase:
        pre_uploaded_pdf_url = "https://drive.google.com/uc?id=1c5HjfBvqCxsmUS5ortY9gY1XgtT1YcWg"
        print("Processing PDF...")
        knowledgebase = process_pdf(pre_uploaded_pdf_url)

    user_question = request.json.get('user_question')
    print(f"Received question: {user_question}")
    docs = knowledgebase.similarity_search(user_question)
    llm = lc_openai.OpenAI()
    chain = load_qa_chain(llm, chain_type="stuff")
    response = chain.run(input_documents=docs, question=user_question)
    print(f"Generated response: {response}")

    figure_refs = re.findall(r"figur\s(\d+)", response, re.IGNORECASE)
    images = [fetch_image_from_drive(f"figur_{ref}.jpg") for ref in figure_refs]
    print(f"Images fetched: {len(images)} images found")
    return jsonify({'answer': response, 'images': images})

if __name__ == '__main__':
    app.run(debug=True)
