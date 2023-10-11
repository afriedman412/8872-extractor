from flask import Flask, request, render_template, jsonify, session, send_file
from .helpers import extract_one_file, create_files
import io
import pdfplumber
import logging
import os

app = Flask(__name__)
app.secret_key = "xxxxxx"

logger = logging.getLogger(__name__)
log_level = os.getenv('LOG_LEVEL', 'INFO')
logger.setLevel(log_level)


@app.route('/')
def home():
    return render_template('index.html', content_page="drop.html")

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    with io.BytesIO(file.read()) as pdf_data:
        logger.info("loading pdf data ...")
        with pdfplumber.open(pdf_data) as p:
            logger.info("extracting pdf ...")
            extracted_data = extract_one_file(p)
            file_name = file.filename.replace(".pdf", "")
            logger.info("creating files ...")
            session['arc_path'] = create_files(extracted_data, file_name)
    
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/download')
def download():
    print(session.get('arc_path'))
    return send_file(session.get('arc_path'), as_attachment=True)