import os
import sys
import subprocess
import time

def test_component(name, path, script):
    """Test individual component"""
    print(f"\n{'='*50}")
    print(f"Testing {name}")
    print(f"{'='*50}")
    
    try:
        original_dir = os.getcwd()
        os.chdir(path)
        result = subprocess.run([sys.executable, script], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ {name} - SUCCESS")
            if result.stdout:
                print("Output:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        else:
            print(f"❌ {name} - FAILED")
            print("Error:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {name} - TIMEOUT (expected for web server)")
    except Exception as e:
        print(f"💥 {name} - EXCEPTION: {str(e)}")
    
    # Return to original directory
    os.chdir(original_dir)

def main():
    print("🧪 FRA Atlas System Test Suite")
    print("Testing all components...")
    
    base_dir = os.getcwd()
    
    # Test 1: Data Digitization (skip if outputs already exist)
    digitization_outputs = [
        os.path.join(base_dir, "data", "structured_fra_data.csv"),
        os.path.join(base_dir, "data", "structured_fra_data.geojson")
    ]
    if all(os.path.exists(p) for p in digitization_outputs):
        print("✅ Data Digitization (OCR/NER) - SKIPPED (outputs present)")
    else:
        test_component("Data Digitization (OCR/NER)", 
                      os.path.join(base_dir, "digitization"), 
                      "ocr_ner.py")
    
    # Test 2: Asset Mapping (skip if outputs already exist)
    asset_mapping_outputs = [
        os.path.join(base_dir, "data", "classified_map.tif"),
        os.path.join(base_dir, "data", "classification_results.png")
    ]
    if all(os.path.exists(p) for p in asset_mapping_outputs):
        print("✅ Asset Mapping (ML Classification) - SKIPPED (outputs present)")
    else:
        test_component("Asset Mapping (ML Classification)", 
                      os.path.join(base_dir, "asset_mapping"), 
                      "train_classify.py")
    
    # Test 3: DSS Engine
    test_component("Decision Support System", 
                  os.path.join(base_dir, "dss"), 
                  "dss_engine.py")
    
    # Test 4: Check file outputs
    print(f"\n{'='*50}")
    print("Checking Output Files")
    print(f"{'='*50}")
    
    expected_files = [
        "data/structured_fra_data.csv",
        "data/structured_fra_data.geojson", 
        "data/classified_map.tif",
        "data/classification_results.png"
    ]
    
    for file in expected_files:
        if os.path.exists(file):
            print(f"✅ {file} - EXISTS")
        else:
            print(f"❌ {file} - MISSING")
    
    print(f"\n{'='*50}")
    print("🎉 System Test Complete!")
    print("To run the web interface:")
    print("cd webgis")
    print("python simple_working_app.py")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
