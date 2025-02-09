import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(__file__), 'favicon_c2.db')

def init_db():
    """Initialize the SQLite database and create necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table for implants
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS implants (
        implant_id TEXT PRIMARY KEY,
        last_checkin TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table for commands
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        implant_id TEXT,
        command TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (implant_id) REFERENCES implants(implant_id)
    )
    ''')

    # Table for results
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        implant_id TEXT,
        command TEXT,
        output TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def get_pending_command(implant_id):
    """Return the next pending command for this implant."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, command
        FROM commands
        WHERE implant_id = ? AND status = 'pending'
        ORDER BY created_at ASC
        LIMIT 1
    ''', (implant_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None, None

def mark_command_executed(cmd_id):
    """Mark a command as executed after the implant retrieves it."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE commands
        SET status = 'executed'
        WHERE id = ?
    ''', (cmd_id,))
    conn.commit()
    conn.close()

def add_implant(implant_id):
    """Add a new implant to the database if it doesn't exist already."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO implants (implant_id) VALUES (?)
    ''', (implant_id,))
    conn.commit()
    conn.close()

def update_checkin(implant_id):
    """Update the last check-in time for an implant."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE implants
        SET last_checkin = CURRENT_TIMESTAMP
        WHERE implant_id = ?
    ''', (implant_id,))
    conn.commit()
    conn.close()

def queue_command(implant_id, command_str):
    """Queue a command for a specific implant."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO commands (implant_id, command)
        VALUES (?, ?)
    ''', (implant_id, command_str))
    conn.commit()
    conn.close()

def store_result(implant_id, command, output):
    """Store the results of an executed command from the implant."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO results (implant_id, command, output)
        VALUES (?, ?, ?)
    ''', (implant_id, command, output))
    conn.commit()
    conn.close()

def get_all_results():
    """Retrieve all stored results for viewing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT implant_id, command, output, created_at FROM results')
    rows = cursor.fetchall()
    conn.close()
    return rows
