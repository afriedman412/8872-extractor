import io
import logging
import os

import pdfplumber
from flask import (Flask, Response, jsonify, render_template, request,
                   send_file, session)

from .helpers import compress_files, establish_files, extract_one_file

app = Flask(__name__)
app.secret_key = "xxxxxx"

logger = logging.getLogger(__name__)
log_level = os.getenv('LOG_LEVEL', 'INFO')
logger.setLevel(log_level)


@app.route('/')
def home() -> str:
    return render_template('index.html', content_page="drop.html")


@app.route('/upload', methods=['POST'])
def upload_pdf() -> Response:
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    elif isinstance(file.filename, str):
        file_name = file.filename.replace(".pdf", "")
    session['file_name'] = file_name
    establish_files()

    with io.BytesIO(file.read()) as pdf_data:
        print("**** loading pdf data ...")
        with pdfplumber.open(pdf_data) as p:
            print("**** extracting pdf ...")
            extract_one_file(p)
            print("**** creating files ...")
            compress_files()

    return jsonify({'message': 'File uploaded successfully'})


@app.route('/download')
def download() -> Response:
    print(session.get('archive'))
    archive_file = session.get('archive', "NO_FILE_NAME.zip")
    return send_file(archive_file, as_attachment=True)
