# Simple test using only built-in Python libraries
import urllib.request
import urllib.parse
import json

# Create a test file
with open('test.txt', 'w') as f:
    f.write('test content')

# Test upload using urllib
with open('test.txt', 'rb') as f:
    data = f.read()

# Create multipart form data manually
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = f'--{boundary}\r\n'
body += 'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n'
body += 'Content-Type: text/plain\r\n\r\n'
body += data.decode('utf-8')
body += f'\r\n--{boundary}--\r\n'

req = urllib.request.Request('http://127.0.0.1:5000/api/upload', 
                           data=body.encode('utf-8'),
                           headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})

try:
    response = urllib.request.urlopen(req)
    result = response.read().decode('utf-8')
    print("Upload Response:")
    print(result)
    
    # Try to parse JSON
    try:
        json_result = json.loads(result)
        print("\nParsed JSON:")
        print(json_result)
        print(f"File ID: {json_result.get('file_id')}")
    except:
        print("Could not parse as JSON")
        
except Exception as e:
    print(f"Error: {e}")

# Clean up
import os
os.remove('test.txt')