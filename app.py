from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes or specify origins as needed

@app.route('/api', methods=['GET'])
def api_handler():
    token = request.args.get('token')  # Get token from user
    user_url = request.args.get('url')  # Get full API URL from user
    
    if not token or not user_url:
        return jsonify({"error": "Token and URL are required"}), 400

    # Log the received parameters
    print(f"Received Token: {token}")
    print(f"Received URL: {user_url}")

    # Set headers with the token
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Encoding": "gzip"
    }

    # Log headers
    print(f"Headers: {headers}")

    # Initialize a session with retries
    session = requests.Session()
    retries = requests.adapters.Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504]
    )
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))

    try:
        # Make the request to the PenPencil API
        response = session.get(user_url, headers=headers, timeout=30)
        print(f"API Response Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return jsonify({"error": "Failed to connect to the PenPencil API"}), 503

    # Check for a successful response
    if response.status_code == 200:
        try:
            data = response.json()
            return jsonify(data)
        except json.JSONDecodeError:
            print("JSON Decode Error")
            return jsonify({"error": "Failed to decode JSON from API response"}), 500
    else:
        print(f"API Error Response: {response.status_code} - {response.text}")
        return jsonify({"error": f"Request failed with status: {response.status_code}"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
