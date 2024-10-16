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

def update_user(username, age=None, location=None, medical_details=None, eating_habits=None, lifestyle_details=None, preferences=None, last_query=None, classification=None):
    # Fetch current user details from the database
    user = get_user(username)
    
    if user:
        # Preserve old values if new values are not provided (None)
        age = age if age is not None else user[2]
        location = location if location else user[3]
        medical_details = medical_details if medical_details else user[4]
        eating_habits = eating_habits if eating_habits else user[5]
        lifestyle_details = lifestyle_details if lifestyle_details else user[6]
        preferences = preferences if preferences else user[7]
        last_query = last_query if last_query else user[8]
        classification = classification if classification else user[9]

        # Update the user information in the database with new values or preserve old ones
        conn = sqlite3.connect('dementia_tips.db')
        c = conn.cursor()
        c.execute('''UPDATE users SET age=?, location=?, medical_details=?, eating_habits=?, lifestyle_details=?, preferences=?, last_query=?, classification=? WHERE username=?''',
                  (age, location, medical_details, eating_habits, lifestyle_details, preferences, last_query, classification, username))
        conn.commit()
        conn.close()
    else:
        # Insert new user if they don't exist
        conn = sqlite3.connect('dementia_tips.db')
        c = conn.cursor()
        c.execute('''INSERT INTO users (username, age, location, medical_details, eating_habits, lifestyle_details, preferences, last_query, classification) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (username, age, location, medical_details, eating_habits, lifestyle_details, preferences, last_query, classification))
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
