import sqlite3
import bcrypt

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create user table with username and password
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
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

# Save new user with hashed password
def save_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()

# Authenticate user by checking username and password
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()

    if result:
        stored_password = result[0]  # This is already a bytes object
        # Since stored_password is bytes, do not call .encode() on it
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)
    return False


# Get user data (without password)
def get_user(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    user = c.fetchone()
    conn.close()
    return user

# Update user details (same as your current update_user function)
def update_user(username, age=None, location=None, medical_details=None, eating_habits=None, lifestyle_details=None, preferences=None, last_query=None, classification=None):
    user = get_user(username)
    if user:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        # Update fields if provided, otherwise use existing values
        c.execute('''UPDATE users 
                     SET age=?, location=?, medical_details=?, eating_habits=?, lifestyle_details=?, preferences=?, last_query=?, classification=? 
                     WHERE username=?''', 
                  (age if age else user[2], 
                   location if location else user[3], 
                   medical_details if medical_details else user[4], 
                   eating_habits if eating_habits else user[5], 
                   lifestyle_details if lifestyle_details else user[6], 
                   preferences if preferences else user[7], 
                   last_query if last_query else user[8], 
                   classification if classification else user[9], 
                   username))
        conn.commit()
        conn.close()
