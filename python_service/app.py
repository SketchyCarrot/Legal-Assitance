from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "legal-saathi-python-service"})

@app.route('/form-fill', methods=['POST'])
def form_fill():
    try:
        data = request.json
        # TODO: Implement form filling logic
        return jsonify({"status": "success", "message": "Form filled successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 