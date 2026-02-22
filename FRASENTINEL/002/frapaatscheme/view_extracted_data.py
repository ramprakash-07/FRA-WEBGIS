#!/usr/bin/env python3
"""
Script to view extracted Patta data in a readable format
"""

import json
import os
from pathlib import Path

def view_patta_data(json_file_path):
    """Display extracted Patta data in a formatted way"""
    
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        return
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("📋 EXTRACTED PATTA DATA")
        print("=" * 60)
        
        # Display each field with proper formatting
        field_names = {
            "district": "🏛️  District (மாவட்டம்)",
            "taluk": "🏘️  Taluk/Circle (வட்டம்)", 
            "village": "🏡 Village (வருவாய் கிராமம்)",
            "patta_number": "📄 Patta Number (பட்டா எண்)",
            "owner_name": "👤 Owner Name (உரிமையாளர் பெயர்)",
            "relationship": "👥 Relationship",
            "survey_number": "📊 Survey Number (புல எண்)",
            "sub_division": "🔢 Sub-division (உட்பிரிவு)",
            "dry_land_area": "🌾 Dry Land Area (புன்செய் பரப்பு)",
            "tax_amount": "💰 Tax Amount (தீர்வை)",
            "signed_by": "✍️  Signed By",
            "signed_on": "📅 Signed On",
            "reference_number": "🔗 Reference Number",
            "verification_url": "🌐 Verification URL"
        }
        
        for key, display_name in field_names.items():
            if key in data and data[key]:
                print(f"{display_name}: {data[key]}")
        
        print("\n" + "=" * 60)
        print("📁 File Information:")
        print(f"   Source JSON: {json_file_path}")
        print(f"   Data Fields: {len([k for k, v in data.items() if v])}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def list_all_extracted_files():
    """List all extracted Patta data files"""
    
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("❌ Uploads directory not found")
        return []
    
    json_files = list(uploads_dir.glob("patta_data_*.json"))
    
    if not json_files:
        print("📁 No extracted data files found")
        print("   Upload a Patta document first at: http://127.0.0.1:8000/docs")
        return []
    
    print("📁 Available Extracted Data Files:")
    print("=" * 50)
    
    for i, json_file in enumerate(json_files, 1):
        print(f"{i}. {json_file.name}")
        
        # Show file size and modification time
        stat = json_file.stat()
        size_kb = stat.st_size / 1024
        print(f"   Size: {size_kb:.1f} KB")
        print(f"   Modified: {stat.st_mtime}")
        print()
    
    return json_files

def main():
    """Main function to view extracted data"""
    
    print("🔍 PATTA DATA VIEWER")
    print("=" * 60)
    
    # List available files
    json_files = list_all_extracted_files()
    
    if not json_files:
        return
    
    # If only one file, show it directly
    if len(json_files) == 1:
        print("📊 Displaying data from the only available file:")
        view_patta_data(json_files[0])
    else:
        # Let user choose which file to view
        try:
            choice = input(f"\nEnter file number (1-{len(json_files)}) or 'all' to view all: ").strip()
            
            if choice.lower() == 'all':
                for json_file in json_files:
                    print(f"\n📊 Data from {json_file.name}:")
                    view_patta_data(json_file)
                    print("\n" + "-" * 60)
            else:
                file_index = int(choice) - 1
                if 0 <= file_index < len(json_files):
                    view_patta_data(json_files[file_index])
                else:
                    print("❌ Invalid file number")
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()

