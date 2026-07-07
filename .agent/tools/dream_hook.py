#!/usr/bin/env python3
import sys
import json
import subprocess
import os

def main():
    try:
        # PostInvocation hook or Stop hook
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dream_path = os.path.join(script_dir, "auto_dream.py")
        
        # Just run it
        subprocess.run([sys.executable, dream_path], capture_output=True)
        
        # Always return empty object for PostInvocation/Stop
        print(json.dumps({}))
    except Exception:
        print(json.dumps({}))

if __name__ == "__main__":
    main()
