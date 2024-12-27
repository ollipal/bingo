from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from extract_bingo_data import extract_bingo_data
from generate_cards import generate_cards

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'xlsx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/generate-cards', methods=['POST'])
def generate_bingo_cards():
    # Check if a file was actually sent
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if the file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload an XLSX file'}), 400
    
    try:
        # Read file content
        file_content = file.read()
        
        # Extract data from Excel
        bingo_data, error = extract_bingo_data(file_content)
        
        if error:
            return jsonify({
                'error': error
            }), 400

        # Generate cards from the bingo data
        cards, error = generate_cards(bingo_data)
        
        if error:
            return jsonify({
                'error': error
            }), 400
            
        return jsonify({
            'cards': cards,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)