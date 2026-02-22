# Test script to check if the patta digitization system is working
import requests
import json
import os

def test_patta_system():
    print("🧪 Testing FRA Patta Digitization System...")
    
    # Create a test file
    test_content = """
    PATTA DOCUMENT
    
    Claimant Name: John Doe
    Father/Spouse: Robert Doe
    Village: Sample Village
    District: Sample District
    Survey Number: 123
    Area: 2.5 hectares
    """
    
    with open('test_patta.txt', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Test 1: Upload file
        print("\n📤 Step 1: Testing file upload...")
        with open('test_patta.txt', 'rb') as f:
            files = {'file': f}
            response = requests.post('http://127.0.0.1:5000/api/upload', files=files)
        
        print(f"Upload Status: {response.status_code}")
        print(f"Upload Response: {response.text}")
        
        if response.status_code == 200:
            upload_data = response.json()
            file_id = upload_data.get('file_id')
            print(f"✅ Upload successful! File ID: {file_id}")
            
            # Test 2: Extract data
            print("\n🔍 Step 2: Testing data extraction...")
            extract_data = {
                'file_id': file_id,
                'extract_ocr': True,
                'extract_ner': True,
                'languages': ['eng', 'hin', 'tam', 'tel']
            }
            
            response = requests.post('http://127.0.0.1:5000/api/extract', 
                                   json=extract_data,
                                   headers={'Content-Type': 'application/json'})
            
            print(f"Extract Status: {response.status_code}")
            print(f"Extract Response: {response.text}")
            
            if response.status_code == 200:
                extract_result = response.json()
                print("✅ Extraction successful!")
                print(f"OCR Text: {extract_result.get('ocr_result', {}).get('text', 'N/A')[:100]}...")
                print(f"Patta Data: {extract_result.get('patta_data', {})}")
                
                # Test 3: Save patta
                print("\n💾 Step 3: Testing patta save...")
                patta_data = extract_result.get('patta_data', {})
                save_data = {
                    'patta_data': patta_data,
                    'source': 'test_extraction',
                    'timestamp': '2025-09-28T12:00:00Z'
                }
                
                response = requests.post('http://127.0.0.1:5000/api/patta',
                                       json=save_data,
                                       headers={'Content-Type': 'application/json'})
                
                print(f"Save Status: {response.status_code}")
                print(f"Save Response: {response.text}")
                
                if response.status_code == 200:
                    print("✅ Save successful!")
                    print("🎉 All tests passed! The system is working correctly.")
                else:
                    print("❌ Save failed")
            else:
                print("❌ Extraction failed")
        else:
            print("❌ Upload failed")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists('test_patta.txt'):
            os.remove('test_patta.txt')
        print("\n🧹 Test file cleaned up")

if __name__ == "__main__":
    test_patta_system()






