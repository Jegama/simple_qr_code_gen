from flask import Flask, request, send_file, render_template, jsonify
import qrcode, os
from io import BytesIO

from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != app.config['SECRET_KEY']:
            return jsonify({'error': 'Invalid API key'}), 403
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)

# read key from environment variable
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
@require_api_key
def generate_qr():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return {'error': 'No text provided'}, 400

    img = qrcode.make(text)

    # Save the QR code to a BytesIO object to serve it as an image
    img_buffer = BytesIO()
    img.save(img_buffer, 'PNG')
    img_buffer.seek(0)

    return send_file(img_buffer, mimetype='image/png')

@app.route('/generate_qr_web', methods=['POST'])
def generate_qr_web():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True)