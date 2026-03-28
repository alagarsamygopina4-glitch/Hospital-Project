import urllib.request
import urllib.parse
import re
import json

try:
    url = 'http://127.0.0.1:8000/appointments/'
    
    # 1. GET request
    req1 = urllib.request.Request(url)
    resp1 = urllib.request.urlopen(req1)
    text1 = resp1.read().decode('utf-8')
    cookie_header = resp1.getheader('Set-Cookie')
    
    csrf_token = ''
    if cookie_header:
        match = re.search(r'csrftoken=([^;]+)', cookie_header)
        if match:
            csrf_token = match.group(1)
            
    if not csrf_token:
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', text1)
        if match:
             csrf_token = match.group(1)
             
    # 2. POST request
    data = {
        'csrfmiddlewaretoken': csrf_token,
        'patient_name': 'Test User',
        'patient_email': 'test@example.com',
        'patient_phone': '1234567890',
        'appointment_date': '2026-03-29',
        'appointment_time': '10:00',
        'reason': 'Checkup',
        'doctor': ''
    }
    
    data_encoded = urllib.parse.urlencode(data).encode('utf-8')
    req2 = urllib.request.Request(url, data=data_encoded, method='POST')
    req2.add_header('Referer', url)
    if csrf_token:
        req2.add_header('Cookie', f'csrftoken={csrf_token}')
        
    try:
        resp2 = urllib.request.urlopen(req2)
        print('POST Status:', resp2.status)
        text2 = resp2.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print('POST Failed Status:', e.code)
        text2 = e.read().decode('utf-8')
        
    with open('error_log.html', 'w', encoding='utf-8') as f:
        f.write(text2)
        
except Exception as e:
    print('Error:', e)
