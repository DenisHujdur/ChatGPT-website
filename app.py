from flask import Flask, render_template, request, jsonify
import openai
import os
import requests
import tempfile
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import faiss
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import openai as lc_openai
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define global variable to store the knowledge base
knowledgebase = None

def process_pdf(pdf_url):
    response = requests.get(pdf_url, stream=True)
    if response.status_code != 200:
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask_pdf', methods=['POST'])
def ask_pdf():
    global knowledgebase
    if not knowledgebase:
        # Load and process PDF if not already loaded
        pre_uploaded_pdf_url = "https://drive.google.com/uc?id=1c5HjfBvqCxsmUS5ortY9gY1XgtT1YcWg"
        #https://drive.google.com/file/d/1c5HjfBvqCxsmUS5ortY9gY1XgtT1YcWg/view?usp=sharing
        knowledgebase = process_pdf(pre_uploaded_pdf_url)

    user_question = request.json.get('user_question')
    docs = knowledgebase.similarity_search(user_question)
    llm = lc_openai.OpenAI()
    chain = load_qa_chain(llm, chain_type="stuff")
    response = chain.run(input_documents=docs, question=user_question)
    return jsonify({'answer': response})

if __name__ == '__main__':
    app.run(debug=True)
