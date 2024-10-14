import sqlite3

# Initialize SQLite database and add a classification field
def init_db():
    conn = sqlite3.connect('dementia_tips.db')
    cursor = conn.cursor()

    # Create a table to store user preferences, last query, and dementia classification
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        preferences TEXT,
        last_query TEXT,
        classification TEXT
    )''')

    conn.commit()
    conn.close()

# Store or update user preferences, query, and classification
def update_user(username, preferences=None, last_query=None, classification=None):
    conn = sqlite3.connect('dementia_tips.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    if user:
        if preferences:
            cursor.execute('UPDATE users SET preferences = ? WHERE username = ?', (preferences, username))
        if last_query:
            cursor.execute('UPDATE users SET last_query = ? WHERE username = ?', (last_query, username))
        if classification:
            cursor.execute('UPDATE users SET classification = ? WHERE username = ?', (classification, username))
    else:
        cursor.execute('INSERT INTO users (username, preferences, last_query, classification) VALUES (?, ?, ?, ?)', (username, preferences, last_query, classification))

    conn.commit()
    conn.close()

# Retrieve user information, including classification
def get_user(username):
    conn = sqlite3.connect('dementia_tips.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    conn.close()
    return user
