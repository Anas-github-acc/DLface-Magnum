from flask import Flask, request, render_template
from face_detection import Training, Detection
from socket import gethostname, gethostbyname
import os
import cv2

app = Flask(__name__)

@app.route('/')
def upload_form():
    return render_template('upload.html', root_path = app.root_path)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    
    if file.filename == '':
        return '<div style="color:red;">choose a file</div>'

    if file:
        file.save(os.path.join(app.root_path, 'uploads', file.filename))
        match = Detection()
        if match[file.filename]:
            return match[file.filename][0]
        else:
            return 'no face found'

if __name__ == '__main__':
    app.run(host=gethostbyname(gethostname()), debug=True, port = 5000)