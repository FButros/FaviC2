# FaviC2 - A Favicon Command & Control (C2) Proof of Concept

**FaviC2** is a proof-of-concept Command & Control framework that embeds commands in a website’s `favicon.ico` file. It demonstrates how attackers or authorized red teams might leverage seemingly benign icon requests to stealthily send commands to a compromised host and receive execution results. **Use this only in authorized security tests or lab environments.**

---

## Table of Contents

- [Features](#features)  
- [How It Works](#how-it-works)  
- [Project Structure](#project-structure)  
- [Installation and Setup](#installation-and-setup)  
- [Usage](#usage)  
  - [Starting the C2 Server](#starting-the-c2-server)  
  - [Running the Implant](#running-the-implant)  
  - [Queueing Commands](#queueing-commands)  
  - [Viewing Results](#viewing-results)  
- [Demonstration Flow](#demonstration-flow)  
- [Disclaimer](#disclaimer)  
- [License](#license)  

---

## Features

1. **Covert Channel via Favicon**  
   - Commands are hidden in the server’s response to `/favicon.ico`, either appended to the icon file or embedded in a custom header.

2. **SQLite Database Storage**  
   - Simple, lightweight database for tracking implants, queued commands, and execution results.

3. **Lightweight Implant (Agent)**  
   - Polls the server at configurable intervals, executes received commands, and reports back.

4. **Minimal Dependencies**  
   - Server side uses [Flask](https://flask.palletsprojects.com/).  
   - Implant side uses [requests](https://pypi.org/project/requests/).

---

## How It Works

1. **Implant Registration**  
   - The implant calls `/favicon.ico?i=<implant_id>` to register/update itself in the database.

2. **Command Injection**  
   - If a command is queued for that implant, the server base64-encodes it and inserts it into the `.ico` response or an HTTP header.

3. **Command Execution**  
   - The implant decodes the command and executes it locally (e.g., via `subprocess` in Python).

4. **Result Reporting**  
   - The implant sends command output back to `/report`, and the server stores it in the SQLite database.

5. **Operator Inspection**  
   - The operator (red team) can review saved results by hitting `/results` or by building a custom interface.

---

## Project Structure

```bash
FaviC2/
├── c2_server/
│   ├── db.py             # SQLite DB creation and query logic
│   ├── server.py         # Flask server handling C2 logic
│   └── static/
│       └── base_favicon.ico  # Base icon file to be served/modified
└── implant/
    └── implant.py        # The implant script that polls for commands and reports results
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<YourUsername>/FaviC2.git
cd FaviC2
```

### 2. Server Environment Setup

```bash
cd c2_server
python3 -m venv venv
source venv/bin/activate       # On Linux/Mac
# On Windows: venv\Scripts\activate

pip install flask
```

### 3. Implant Environment Setup

```bash
cd ../implant
python3 -m venv venv
source venv/bin/activate
pip install requests
```

### 4. Base Favicon

In `c2_server/static/`, ensure you have a valid `base_favicon.ico`. You can download or create one using any icon generator.

---

## Usage

### Starting the C2 Server

From `c2_server`, run:

```bash
cd c2_server
source venv/bin/activate  # Activate your virtual environment if not already
python server.py
```

By default, this starts the Flask server on `http://127.0.0.1:5000`. You can change ports and settings in `server.py`.

### Running the Implant

In another terminal, navigate to `implant`:

```bash
cd implant
source venv/bin/activate
python implant.py
```

The implant will poll `http://localhost:5000/favicon.ico?i=test_implant` every 10 seconds (configurable in `implant.py`).

### Queueing Commands

Use `curl`, Postman, or similar to queue a command:

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"implant_id":"test_implant","command":"whoami"}' \
     http://127.0.0.1:5000/queue_command
```

When the implant polls again, it will receive and execute `whoami`, then send the results back.

### Viewing Results

Retrieve stored results with:

```bash
curl http://127.0.0.1:5000/results
```

You’ll see a JSON response containing implant IDs, commands, outputs, and timestamps.

---

## Demonstration Flow

1. **Start the C2 Server**

    ```bash
    python server.py
    ```

2. **Run the Implant**

    ```bash
    python implant.py
    ```

3. **Queue a Command**

    ```bash
    curl -X POST -H "Content-Type: application/json" \
         -d '{"implant_id":"test_implant","command":"whoami"}' \
         http://127.0.0.1:5000/queue_command
    ```

4. **Check Implant**

    - The implant logs the fetched command and executes it.
    - Output is sent back to the server.

5. **View Results**

    - Access `http://127.0.0.1:5000/results` to confirm the command’s output.

---

## Disclaimer

This tool is intended for authorized security testing and educational research purposes only. You are solely responsible for complying with all relevant laws. Do not use this software in unauthorized ways. The author(s) assume no liability for any misuse or damage.

---

## License

**MIT License**

Feel free to adapt or enhance the code for your use cases within the bounds of the license.
