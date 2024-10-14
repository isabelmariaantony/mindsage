import sqlite3

def add_classification_column():
    conn = sqlite3.connect('dementia_tips.db')
    cursor = conn.cursor()

    # Add classification column if it doesn't already exist
    cursor.execute("ALTER TABLE users ADD COLUMN classification TEXT")
    
    conn.commit()
    conn.close()

add_classification_column()
