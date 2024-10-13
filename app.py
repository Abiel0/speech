import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gradio_client import Client
import shutil

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Get the directory of the current script (app.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def serve_html():
    return send_from_directory(current_dir, 'index.html')

@app.route('/translate', methods=['POST'])
def translate_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save the uploaded file temporarily
        temp_filepath = os.path.join(current_dir, 'temp_input.m4a')
        file.save(temp_filepath)
        
        # Create a Client instance
        client = Client("https://course-demos-speech-to-speech-translation.hf.space/")
        
        # Make the prediction
        result = client.predict(
            temp_filepath,
            api_name="/predict"
        )
        
        # Remove the temporary input file
        os.remove(temp_filepath)
        
        # The result should contain the path to the generated audio file
        if isinstance(result, str) and os.path.exists(result):
            # Generate a new filename (you can modify this as needed)
            new_filename = "generated_speech.wav"
            new_filepath = os.path.join(current_dir, new_filename)
            
            # Copy the file to the new location
            shutil.copy2(result, new_filepath)
            
            return jsonify({'success': True, 'filename': new_filename})
        else:
            return jsonify({'error': 'Unable to generate or find the translated speech file'}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(current_dir, filename)

if __name__ == '__main__':
    app.run(debug=True)