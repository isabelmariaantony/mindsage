import sqlite3

# Initialize SQLite database and add necessary fields
def init_db():
    conn = sqlite3.connect('dementia_tips.db')
    cursor = conn.cursor()

    # Create a table to store user information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        age INTEGER,
        location TEXT,
        medical_details TEXT,
        eating_habits TEXT,
        lifestyle_details TEXT,
        preferences TEXT,
        last_query TEXT,
        classification TEXT
    )''')

    conn.commit()
    conn.close()

# Function to update or insert user information in the database
def update_user(username, age=None, location=None, medical_details=None, eating_habits=None,
                lifestyle_details=None, preferences=None, last_query=None, classification=None):
    conn = sqlite3.connect('dementia_tips.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    if user:
        cursor.execute('''
            UPDATE users SET age = ?, location = ?, medical_details = ?, eating_habits = ?, 
            lifestyle_details = ?, preferences = ?, last_query = ?, classification = ? 
            WHERE username = ?
        ''', (age, location, medical_details, eating_habits, lifestyle_details, preferences, last_query, classification, username))
    else:
        cursor.execute('''
            INSERT INTO users (username, age, location, medical_details, eating_habits, lifestyle_details, preferences, last_query, classification)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, age, location, medical_details, eating_habits, lifestyle_details, preferences, last_query, classification))

    conn.commit()
    conn.close()

# Function to retrieve user information
def get_user(username):
    conn = sqlite3.connect('dementia_tips.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    conn.close()
    return user
