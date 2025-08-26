#!/usr/bin/env python3
"""
Test script to verify PDF processing pipeline for KFH Real Estate Report.
Run this script to test the complete pipeline from PDF to database.
"""

import os
import sys
from pathlib import Path

def test_pdf_exists():
    """Test if the PDF file exists."""
    pdf_path = Path("KFH_Real_Estate_Report_2025_Q1.pdf")
    if pdf_path.exists():
        print(f"✅ PDF file found: {pdf_path}")
        print(f"   Size: {pdf_path.stat().st_size / (1024*1024):.1f} MB")
        return True
    else:
        print(f"❌ PDF file not found: {pdf_path}")
        print("   Please ensure KFH_Real_Estate_Report_2025_Q1.pdf is in the current directory")
        return False

def test_dependencies():
    """Test if required dependencies are available."""
    try:
        import docling
        print("✅ Docling imported successfully")
    except ImportError as e:
        print(f"❌ Docling import failed: {e}")
        return False
    
    try:
        import lancedb
        print("✅ LanceDB imported successfully")
    except ImportError as e:
        print(f"❌ LanceDB import failed: {e}")
        return False
    
    try:
        from openai import AzureOpenAI
        print("✅ Azure OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ Azure OpenAI import failed: {e}")
        return False
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    return True

def test_environment_variables():
    """Test if required environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_pdf_extraction():
    """Test basic PDF extraction."""
    try:
        from docling.document_converter import DocumentConverter
        
        converter = DocumentConverter()
        result = converter.convert("KFH_Real_Estate_Report_2025_Q1.pdf")
        
        if result.document:
            print("✅ PDF extraction successful")
            
            # Check different possible attributes for content
            if hasattr(result.document, 'pages'):
                print(f"   Document has pages: {len(result.document.pages)}")
            else:
                print("   Document structure:", dir(result.document))
            
            # Try to export to see what's available
            try:
                markdown_content = result.document.export_to_markdown()
                print(f"   Document exported to markdown: {len(markdown_content)} characters")
                print(f"   Preview: {markdown_content[:200]}...")
            except Exception as export_error:
                print(f"   Export error: {export_error}")
                print(f"   Available methods: {[m for m in dir(result.document) if not m.startswith('_')]}")
            
            return True
        else:
            print("❌ PDF extraction failed - no document returned")
            return False
            
    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        return False

def test_database_creation():
    """Test if database directory can be created."""
    try:
        db_dir = Path("data/lancedb")
        db_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Database directory created/verified")
        return True
    except Exception as e:
        print(f"❌ Database directory creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing KFH Real Estate Report PDF Processing Pipeline")
    print("=" * 60)
    
    tests = [
        ("PDF File Exists", test_pdf_exists),
        ("Dependencies Available", test_dependencies),
        ("Environment Variables", test_environment_variables),
        ("PDF Extraction", test_pdf_extraction),
        ("Database Setup", test_database_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python 1-extraction.py")
        print("2. Run: python 2-chunking.py")
        print("3. Run: python 3-embedding.py")
        print("4. Run: python 4-search.py")
        print("5. Run: streamlit run 5-chat.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
