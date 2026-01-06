"""
Diagnostic script to help troubleshoot Pinecone API key issues
This will show you exactly what's happening with your environment variables
"""

import os
import sys
from pathlib import Path

print("=" * 80)
print("Pinecone API Key Diagnostic Tool")
print("=" * 80)
print()

# Check 1: Direct environment variable
print("1. Checking environment variable directly:")
print("-" * 80)
env_value = os.getenv("PINECONE_API_KEY")
if env_value:
    masked = env_value[:8] + "..." + env_value[-4:] if len(env_value) > 12 else "***"
    print(f"   ✓ Found: {masked}")
    print(f"   Length: {len(env_value)} characters")
else:
    print("   ✗ NOT FOUND in environment")
print()

# Check 2: .env file
print("2. Checking for .env file:")
print("-" * 80)
base_dir = Path(__file__).parent.parent
env_file = base_dir / ".env"
if env_file.exists():
    print(f"   ✓ Found .env file at: {env_file}")
    # Try to read it
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            if "PINECONE_API_KEY" in content:
                print("   ✓ PINECONE_API_KEY found in .env file")
                # Extract the value (simple parsing)
                for line in content.split('\n'):
                    if line.strip().startswith("PINECONE_API_KEY"):
                        key_part = line.split('=', 1)[1].strip().strip('"').strip("'")
                        if key_part:
                            masked = key_part[:8] + "..." + key_part[-4:] if len(key_part) > 12 else "***"
                            print(f"   Value (masked): {masked}")
            else:
                print("   ✗ PINECONE_API_KEY NOT found in .env file")
    except Exception as e:
        print(f"   ⚠ Could not read .env file: {e}")
else:
    print(f"   ✗ .env file NOT found at: {env_file}")
    print(f"   Expected location: {env_file}")
print()

# Check 3: Try loading with dotenv
print("3. Testing dotenv loading:")
print("-" * 80)
try:
    from dotenv import load_dotenv
    print("   ✓ python-dotenv is installed")
    
    # Clear the variable first
    if "PINECONE_API_KEY" in os.environ:
        del os.environ["PINECONE_API_KEY"]
    
    # Try loading
    if env_file.exists():
        load_dotenv(env_file, override=True)
        after_load = os.getenv("PINECONE_API_KEY")
        if after_load:
            masked = after_load[:8] + "..." + after_load[-4:] if len(after_load) > 12 else "***"
            print(f"   ✓ After loading .env: {masked}")
        else:
            print("   ✗ Still not found after loading .env")
    else:
        print("   ⚠ No .env file to load")
except ImportError:
    print("   ✗ python-dotenv is NOT installed")
    print("   Install with: pip install python-dotenv")
print()

# Check 4: What config.py sees
print("4. What config.py sees:")
print("-" * 80)
try:
    # Import after potential dotenv load
    from module_a.config import PINECONE_API_KEY
    if PINECONE_API_KEY:
        masked = PINECONE_API_KEY[:8] + "..." + PINECONE_API_KEY[-4:] if len(PINECONE_API_KEY) > 12 else "***"
        print(f"   ✓ config.PINECONE_API_KEY: {masked}")
    else:
        print("   ✗ config.PINECONE_API_KEY is empty/not set")
except Exception as e:
    print(f"   ⚠ Error importing config: {e}")
print()

# Check 5: Recommendations
print("5. Recommendations:")
print("-" * 80)
if not env_value and not env_file.exists():
    print("   → Set the environment variable in your current terminal:")
    print("     PowerShell: $env:PINECONE_API_KEY='your-key'")
    print("     CMD:        set PINECONE_API_KEY=your-key")
    print()
    print("   → OR create a .env file in project root with:")
    print("     PINECONE_API_KEY=your-key")
elif env_file.exists() and "PINECONE_API_KEY" not in open(env_file).read():
    print("   → Add PINECONE_API_KEY to your .env file:")
    print("     PINECONE_API_KEY=your-key")
elif env_value:
    print("   → Environment variable is set!")
    print("   → Make sure you restart your application after setting it")
    print("   → Run: python -m module_a.check_vector_db")
else:
    print("   → Check that the API key value is not empty")
    print("   → Make sure there are no extra spaces or quotes")

print()
print("=" * 80)
print("Diagnostic Complete")
print("=" * 80)
