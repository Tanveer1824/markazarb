#!/usr/bin/env python3
"""
Test script to verify Streamlit app deployment readiness
"""

import os
import sys
import subprocess

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
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
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    return True

def test_environment_variables():
    """Test environment variable configuration"""
    print("\n🔍 Testing environment variables...")
    
    # Load .env file if it exists
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file found and loaded")
    else:
        print("⚠️  .env file not found (this is normal for cloud deployment)")
    
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("   These need to be set in Streamlit Cloud secrets")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_database_paths():
    """Test database path accessibility"""
    print("\n🔍 Testing database paths...")
    
    possible_paths = [
        "data/lancedb",
        "knowledge/docling/data/lancedb",
        "/mount/src/markazarb/knowledge/docling/data/lancedb"
    ]
    
    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            found_paths.append(path)
            print(f"✅ Database path found: {path}")
        else:
            print(f"⚠️  Database path not found: {path}")
    
    if found_paths:
        print(f"✅ Found {len(found_paths)} database path(s)")
        return True
    else:
        print("❌ No database paths found")
        print("   This is normal for cloud deployment without database files")
        return False

def test_streamlit_config():
    """Test Streamlit configuration"""
    print("\n🔍 Testing Streamlit configuration...")
    
    config_path = ".streamlit/config.toml"
    if os.path.exists(config_path):
        print(f"✅ Streamlit config found: {config_path}")
        return True
    else:
        print(f"⚠️  Streamlit config not found: {config_path}")
        return False

def main():
    """Run all tests"""
    print("🚀 Streamlit Deployment Readiness Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Variables", test_environment_variables),
        ("Database Paths", test_database_paths),
        ("Streamlit Config", test_streamlit_config)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your app is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please address the issues before deployment.")
        
        if not any(name == "Environment Variables" and result for name, result in results):
            print("\n💡 For Streamlit Cloud deployment:")
            print("   1. Set environment variables in Streamlit Cloud secrets")
            print("   2. Ensure your main file path is: knowledge/docling/5-chat.py")
            print("   3. Include requirements.txt in your repository")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
