#!/usr/bin/env python3
import sys
import json
import subprocess
import os

def main():
    try:
        input_data = json.load(sys.stdin)
        tool_call = input_data.get("toolCall", {})
        if tool_call.get("name") == "run_command":
            command = tool_call.get("args", {}).get("CommandLine", "")
            # Call gate.py
            script_dir = os.path.dirname(os.path.abspath(__file__))
            gate_path = os.path.join(script_dir, "gate.py")
            
            result = subprocess.run(
                [sys.executable, gate_path, "exec", command],
                capture_output=True,
                text=True
            )
            
            # gate.py outputs human readable + JSON
            # We need to extract the JSON part or parse the output
            lines = result.stdout.strip().split('\n')
            json_out = {}
            for line in reversed(lines):
                try:
                    json_out = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
            
            if json_out:
                decision = "allow" if json_out.get("allowed") else "deny"
                print(json.dumps({
                    "decision": decision,
                    "reason": json_out.get("message", "Gatekeeper check")
                }))
            else:
                print(json.dumps({"decision": "allow", "reason": "Gatekeeper failed to parse output"}))
        else:
            print(json.dumps({"decision": "allow"}))
    except Exception as e:
        print(json.dumps({"decision": "allow", "reason": f"Hook error: {str(e)}"}))

if __name__ == "__main__":
    main()
