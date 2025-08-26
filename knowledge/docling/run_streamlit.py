#!/usr/bin/env python3
"""
Helper script to run Streamlit with the correct working directory and environment
"""

import os
import subprocess
import sys

def main():
    """Run Streamlit from the correct directory"""
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    print(f"Changed working directory to: {os.getcwd()}")
    print(f"Database path: {os.path.join(script_dir, 'data', 'lancedb')}")
    
    # Check if database exists
    db_path = os.path.join(script_dir, "data", "lancedb")
    if not os.path.exists(db_path):
        print(f"❌ Database path not found: {db_path}")
        return 1
    
    # Check if the docling table exists
    try:
        import lancedb
        db = lancedb.connect(db_path)
        tables = db.table_names()
        if "docling" not in tables:
            print(f"❌ Table 'docling' not found. Available tables: {tables}")
            return 1
        print(f"✅ Database connection successful. Found table: {tables}")
    except ImportError:
        print("❌ LanceDB not installed. Please install it first:")
        print("   pip install lancedb")
        return 1
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return 1
    
    # Set environment variable for the database path
    env = os.environ.copy()
    env["DB_PATH"] = db_path
    env["DEBUG"] = "true"  # Enable debug output
    
    print("\n🚀 Starting Streamlit...")
    print("   Press Ctrl+C to stop")
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "5-chat.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], env=env, check=True)
    except KeyboardInterrupt:
        print("\n👋 Streamlit stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
