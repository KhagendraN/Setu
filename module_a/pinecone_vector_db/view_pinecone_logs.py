"""
Script to view Pinecone logs from the log file
Shows recent Pinecone activity and operations
"""

import sys
from pathlib import Path
from datetime import datetime

from module_a.config import LOG_FILE


def view_logs(lines: int = 50, filter_pinecone: bool = True):
    """
    View recent log entries, optionally filtered for Pinecone operations
    
    Args:
        lines: Number of lines to show (from end of file)
        filter_pinecone: If True, only show Pinecone-related logs
    """
    if not LOG_FILE.exists():
        print(f"❌ Log file not found: {LOG_FILE}")
        print("\nThe log file will be created when you run the application.")
        print("Start your application and then run this script again.")
        return
    
    print("=" * 80)
    print("Pinecone Activity Log Viewer")
    print("=" * 80)
    print(f"\nLog file: {LOG_FILE}")
    print(f"File size: {LOG_FILE.stat().st_size / 1024:.2f} KB")
    print(f"Last modified: {datetime.fromtimestamp(LOG_FILE.stat().st_mtime)}")
    print()
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # Get last N lines
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        if filter_pinecone:
            # Filter for Pinecone-related logs
            pinecone_keywords = [
                'pinecone', 'Pinecone', 'PINECONE',
                'vector_db', 'Vector DB', 'vector database',
                'index', 'Index', 'query', 'Query',
                'upsert', 'Upsert', 'retrieve', 'Retrieve'
            ]
            
            filtered_lines = []
            for line in recent_lines:
                if any(keyword in line for keyword in pinecone_keywords):
                    filtered_lines.append(line)
            
            if filtered_lines:
                print(f"Showing {len(filtered_lines)} Pinecone-related log entries:\n")
                print("-" * 80)
                for line in filtered_lines:
                    print(line.rstrip())
            else:
                print("No Pinecone-related log entries found in recent logs.")
                print("\nShowing all recent logs instead:\n")
                print("-" * 80)
                for line in recent_lines[-20:]:  # Show last 20 if no matches
                    print(line.rstrip())
        else:
            print(f"Showing last {len(recent_lines)} log entries:\n")
            print("-" * 80)
            for line in recent_lines:
                print(line.rstrip())
        
        print()
        print("=" * 80)
        print("Log View Complete")
        print("=" * 80)
        print(f"\n💡 Tip: To see all logs, check: {LOG_FILE}")
        print(f"💡 Tip: To see real-time logs, use: tail -f {LOG_FILE}")
        
    except Exception as e:
        print(f"❌ Error reading log file: {e}")


def show_pinecone_status():
    """Show summary of Pinecone activity from logs"""
    if not LOG_FILE.exists():
        print("❌ Log file not found. Start your application first.")
        return
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Count Pinecone operations
        init_count = sum(1 for line in lines if 'Initializing Pinecone' in line or 'Using Pinecone' in line)
        query_count = sum(1 for line in lines if 'Querying Pinecone' in line or 'Retrieved' in line)
        error_count = sum(1 for line in lines if 'ERROR' in line and 'pinecone' in line.lower())
        
        print("=" * 80)
        print("Pinecone Activity Summary")
        print("=" * 80)
        print(f"\nInitializations: {init_count}")
        print(f"Queries: {query_count}")
        print(f"Errors: {error_count}")
        
        # Show last few Pinecone operations
        print("\nRecent Pinecone Operations:")
        print("-" * 80)
        pinecone_lines = [line for line in lines if any(kw in line.lower() for kw in ['pinecone', 'vector_db', 'index'])]
        for line in pinecone_lines[-10:]:
            print(line.rstrip())
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='View Pinecone logs')
    parser.add_argument('--lines', type=int, default=50, help='Number of lines to show')
    parser.add_argument('--all', action='store_true', help='Show all logs, not just Pinecone')
    parser.add_argument('--status', action='store_true', help='Show summary status')
    
    args = parser.parse_args()
    
    if args.status:
        show_pinecone_status()
    else:
        view_logs(lines=args.lines, filter_pinecone=not args.all)


if __name__ == "__main__":
    main()
