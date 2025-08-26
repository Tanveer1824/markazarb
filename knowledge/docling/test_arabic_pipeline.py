#!/usr/bin/env python3
"""
Comprehensive Arabic PDF Processing Pipeline Test
Tests the complete pipeline from extraction to chat interface
"""

import os
import sys
import time
from pathlib import Path

def run_pipeline_step(step_name, script_path, description):
    """Run a pipeline step and report results"""
    
    print(f"\n{'='*60}")
    print(f"🚀 STEP: {step_name}")
    print(f"📝 {description}")
    print(f"🔧 Script: {script_path}")
    print(f"{'='*60}")
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        print(f"⏳ Running {script_path}...")
        start_time = time.time()
        
        # Run the script
        result = os.system(f"python {script_path}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result == 0:
            print(f"✅ {step_name} completed successfully in {duration:.2f} seconds")
            return True
        else:
            print(f"❌ {step_name} failed with exit code {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {step_name}: {e}")
        return False

def check_requirements():
    """Check if all required dependencies are available"""
    
    print("🔍 Checking requirements...")
    print("=" * 40)
    
    required_packages = [
        "docling",
        "lancedb", 
        "openai",
        "streamlit",
        "dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages available")
    return True

def check_environment():
    """Check if environment variables are set"""
    
    print("\n🔍 Checking environment variables...")
    print("=" * 40)
    
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
    ]
    
    optional_vars = [
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            print(f"❌ {var}")
            missing_required.append(var)
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            print(f"⚠️  {var} (optional)")
            missing_optional.append(var)
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please set these in your .env file")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_files():
    """Check if required files exist"""
    
    print("\n🔍 Checking required files...")
    print("=" * 40)
    
    required_files = [
        "KFH_Real_Estate_Report_2025_Q1_arb.pdf"
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            size_mb = os.path.getsize(file) / (1024*1024)
            print(f"✅ {file} ({size_mb:.2f} MB)")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files available")
    return True

def run_complete_pipeline():
    """Run the complete Arabic PDF processing pipeline"""
    
    print("🧪 COMPREHENSIVE ARABIC PDF PROCESSING PIPELINE TEST")
    print("=" * 80)
    
    # Step 1: Check requirements
    if not check_requirements():
        print("❌ Requirements check failed. Please install missing packages.")
        return False
    
    # Step 2: Check environment
    if not check_environment():
        print("❌ Environment check failed. Please configure environment variables.")
        return False
    
    # Step 3: Check files
    if not check_files():
        print("❌ File check failed. Please ensure required files are present.")
        return False
    
    print("\n🎯 All checks passed! Starting pipeline...")
    
    # Step 4: Extract Arabic PDF
    step1_success = run_pipeline_step(
        "PDF Extraction",
        "1-extraction-arabic.py",
        "Extract and clean Arabic text from PDF"
    )
    
    if not step1_success:
        print("❌ Pipeline failed at extraction step")
        return False
    
    # Step 5: Create optimized chunks
    step2_success = run_pipeline_step(
        "Text Chunking", 
        "2-chunking-arabic.py",
        "Create Arabic-optimized text chunks"
    )
    
    if not step2_success:
        print("❌ Pipeline failed at chunking step")
        return False
    
    # Step 6: Generate embeddings and store in database
    step3_success = run_pipeline_step(
        "Embedding & Storage",
        "3-embedding-arabic.py", 
        "Generate embeddings and store in LanceDB"
    )
    
    if not step3_success:
        print("❌ Pipeline failed at embedding step")
        return False
    
    # Step 7: Test the system
    print(f"\n{'='*60}")
    print("🧪 TESTING THE SYSTEM")
    print(f"{'='*60}")
    
    # Check if database was created
    db_path = "data/arabic_lancedb"
    if os.path.exists(db_path):
        print(f"✅ Database created: {db_path}")
        
        # Check table
        try:
            import lancedb
            db = lancedb.connect(db_path)
            table = db.open_table("arabic_chunks")
            count = len(table.to_pandas())
            print(f"✅ Table 'arabic_chunks' created with {count} chunks")
        except Exception as e:
            print(f"❌ Failed to access table: {e}")
    else:
        print(f"❌ Database not found: {db_path}")
    
    print(f"\n{'='*80}")
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"{'='*80}")
    print("✅ Arabic PDF processed and stored in vector database")
    print("✅ Ready for chat interface")
    print("\n🚀 Next steps:")
    print("   1. Launch chat interface: streamlit run 5-chat-arabic.py")
    print("   2. Ask questions in Arabic or English")
    print("   3. Explore the real estate report content")
    print(f"\n📁 Output files:")
    print(f"   - Cleaned content: arabic_content_cleaned.md")
    print(f"   - Chunks: arabic_chunks.txt") 
    print(f"   - Database: {db_path}")
    print(f"{'='*80}")
    
    return True

def main():
    """Main function"""
    
    # Check if we're in the right directory
    if not os.path.exists("KFH_Real_Estate_Report_2025_Q1_arb.pdf"):
        print("❌ Please run this script from the knowledge/docling directory")
        print("   cd knowledge/docling")
        print("   python test_arabic_pipeline.py")
        return
    
    # Run the complete pipeline
    success = run_complete_pipeline()
    
    if success:
        print("\n🎯 Ready to test the chat interface!")
        print("Run: streamlit run 5-chat-arabic.py")
    else:
        print("\n❌ Pipeline failed. Please check the errors above.")

if __name__ == "__main__":
    main()
