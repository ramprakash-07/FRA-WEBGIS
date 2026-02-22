# Quick test to see what the upload endpoint returns
import requests

# Create a simple test file
with open('test.txt', 'w') as f:
    f.write('test content')

# Test upload
files = {'file': open('test.txt', 'rb')}
response = requests.post('http://127.0.0.1:5000/api/upload', files=files)

print("Status:", response.status_code)
print("Response:", response.text)
print("JSON:", response.json())

# Clean up
import os
os.remove('test.txt')






