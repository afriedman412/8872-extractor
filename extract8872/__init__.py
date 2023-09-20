from flask import Flask, request, render_template, jsonify, session, send_file
from .helpers import extract_one_file, create_files
import io
import pdfplumber
import glob
import os


app = Flask(__name__)
app.secret_key = "xxxxxx"

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

    pdf_data = io.BytesIO(file.read())
    p = pdfplumber.open(pdf_data)
    extracted_data = extract_one_file(p)
    file_name = file.filename.replace(".pdf", "")
    session['arc_path'] = create_files(extracted_data, file_name)
    
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/download')
def download():
    dir_path = os.path.dirname(session['arc_path'])
    csvcsv = glob.glob(os.path.join(dir_path, "/*.csv"))
    return send_file(csvcsv[0])