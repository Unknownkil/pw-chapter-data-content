from flask import Flask, request, render_template, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # सुरक्षा के लिए एक मजबूत सीक्रेट की सेट करें

# JWT टोकन को स्टोर करने के लिए सत्र का उपयोग
def get_jwt_token():
    return session.get('jwt_token')

def set_jwt_token(token):
    session['jwt_token'] = token

# उपयोगकर्ता लॉगिन पेज
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_no = request.form['phone_no']
        # OTP प्राप्त करना
        otp_response = get_otp(phone_no)
        if otp_response:
            return redirect(url_for('verify_otp', phone_no=phone_no))
        else:
            return "OTP जनरेट करने में विफल", 400
    return render_template('login.html')

# OTP सत्यापन पेज
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    phone_no = request.args.get('phone_no')
    if request.method == 'POST':
        otp = request.form['otp']
        token = get_token(phone_no, otp)
        if token:
            set_jwt_token(token)
            return redirect(url_for('dashboard'))
        else:
            return "टोकन जनरेट करने में विफल", 400
    return render_template('verify_otp.html', phone_no=phone_no)

# डैशबोर्ड जहाँ उपयोगकर्ता चैप्टर URL डाल सकते हैं
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not get_jwt_token():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        chapter_url = request.form['chapter_url']
        data = fetch_chapter_data(chapter_url)
        return render_template('dashboard.html', data=data)
    
    return render_template('dashboard.html', data=None)

# OTP प्राप्त करने का फ़ंक्शन
def get_otp(phone_no):
    url = "https://api.penpencil.co/v1/users/get-otp"
    query_params = {"smsType": "0"}
    headers = {
        "Content-Type": "application/json",
        "Client-Id": "5eb393ee95fab7468a79d189",
        "Client-Type": "WEB",
        "Client-Version": "2.6.12",
        "Integration-With": "Origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    }
    payload = {
        "username": phone_no,
        "countryCode": "+91",
        "organizationId": "5eb393ee95fab7468a79d189",
    }
    try:
        response = requests.post(url, params=query_params, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error during OTP request: {e}")
        return False

# टोकन प्राप्त करने का फ़ंक्शन
def get_token(phone_no, otp):
    url = "https://api.penpencil.co/v3/oauth/token"
    payload = {
        "username": phone_no,
        "otp": otp,
        "client_id": "system-admin",
        "client_secret": "KjPXuAVfC5xbmgreETNMaL7z",
        "grant_type": "password",
        "organizationId": "5eb393ee95fab7468a79d189",
        "latitude": 0,
        "longitude": 0
    }
    headers = {
        "Content-Type": "application/json",
        "Client-Id": "5eb393ee95fab7468a79d189",
        "Client-Type": "WEB",
        "Client-Version": "2.6.12",
        "Integration-With": "",
        "Randomid": "990963b2-aa95-4eba-9d64-56bb55fca9a9",
        "Referer": "https://www.pw.live/",
        "Sec-Ch-Ua": "\"Not A(Brand\";v=\"99\", \"Microsoft Edge\";v=\"121\", \"Chromium\";v=\"121\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
    }
    try:
        r = requests.post(url, json=payload, headers=headers)
        r.raise_for_status()
        resp = r.json()
        token = resp['data']['access_token']
        return token
    except requests.exceptions.RequestException as e:
        print(f"Error during token request: {e}")
        return None

# चैप्टर डेटा प्राप्त करने का फ़ंक्शन
def fetch_chapter_data(chapter_url):
    try:
        # उदाहरण URL: https://www.pw.live/study/batches/yakeen-neet-2-0-2025-801657/subjects/physics-legend-885582/subject-topics/topics/ch-01---basic-maths-and-calculus-246028/contents
        parts = chapter_url.split('/')
        batch_id = parts[5]
        subject_id = parts[7]
        chapter_id = parts[11].split('/')[0]
        
        token = get_jwt_token()
        headers = {
            'Host': 'api.penpencil.co',
            'authorization': f"Bearer {token}",
            'client-id': '5eb393ee95fab7468a79d189',
            'client-version': '12.84',
            'user-agent': 'Android',
            'randomid': 'e4307177362e86f1',
            'client-type': 'MOBILE',
            'device-meta': '{APP_VERSION:12.84,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.physicswalb}',
            'content-type': 'application/json; charset=UTF-8',
        }
        params = {
           'mode': '1',
           'filter': 'false',
           'exam': '',
           'amount': '',
           'organisationId': '5eb393ee95fab7468a79d189',
           'classes': '',
           'limit': '20',
           'page': '1',
           'programId': '',
           'ut': '1652675230446', 
        }
        # API कॉल
        response = requests.get(f'https://api.penpencil.co/v3/batches/{batch_id}/subject/{subject_id}/contents', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()["data"]
        return data
    except Exception as e:
        print(f"Error fetching chapter data: {e}")
        return None

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render par PORT environment variable se read hoga
    app.run(host='0.0.0.0', port=port, debug=False)  # Debug ko production ke liye off karein
