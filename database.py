import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('zoom_app.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  country TEXT NOT NULL,
                  name TEXT NOT NULL)''')
    
    # Create login_history table
    c.execute('''CREATE TABLE IF NOT EXISTS login_history
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER NOT NULL,
                  login_time TEXT NOT NULL,
                  login_type TEXT NOT NULL,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Create login_records table
    c.execute('''CREATE TABLE IF NOT EXISTS login_records
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER NOT NULL,
                  login_time TEXT NOT NULL,
                  nickname_copied TEXT,
                  phrase_written TEXT,
                  zoom_link_clicked TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Insert initial user data if the users table is empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        initial_users = [
            ('Korea', 'Dongjae'),
            ('USA', 'John'),
            ('Japan', 'Yuki'),
            ('China', 'Li Wei')
        ]
        c.executemany("INSERT INTO users (country, name) VALUES (?, ?)", initial_users)
    
    conn.commit()
    conn.close()

def get_user(country, name):
    conn = sqlite3.connect('zoom_app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE LOWER(country)=LOWER(?) AND LOWER(name)=LOWER(?)", (country, name))
    user = c.fetchone()
    conn.close()
    return user

def add_login_record(user_id):
    conn = sqlite3.connect('zoom_app.db')
    c = conn.cursor()
    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO login_records (user_id, login_time) VALUES (?, ?)",
              (user_id, login_time))
    conn.commit()
    conn.close()
    return login_time

def update_nickname_copied(user_id):
    conn = sqlite3.connect('zoom_app.db')
    c = conn.cursor()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE login_records SET nickname_copied = ? WHERE user_id = ? AND nickname_copied IS NULL",
              (time, user_id))
    conn.commit()
    conn.close()
    return time

def update_phrase_written(user_id):
    conn = sqlite3.connect('zoom_app.db')
    c = conn.cursor()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE login_records SET phrase_written = ? WHERE user_id = ? AND phrase_written IS NULL",
              (time, user_id))
    conn.commit()
    conn.close()
    return time

def update_zoom_link_clicked(user_id):
    conn = sqlite3.connect('zoom_app.db')
    c = conn.cursor()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE login_records SET zoom_link_clicked = ? WHERE user_id = ? AND zoom_link_clicked IS NULL",
              (time, user_id))
    conn.commit()
    conn.close()
    return time

def get_login_history(user_id):
    conn = sqlite3.connect('zoom_app.db')
    c = conn.cursor()
    c.execute("SELECT login_time FROM login_records WHERE user_id=? ORDER BY login_time", (user_id,))
    history = c.fetchall()
    conn.close()
    return history

def get_attendance_report():
    conn = sqlite3.connect('zoom_app.db')
    c = conn.cursor()
    c.execute('''SELECT u.country, u.name, 
                 lr.login_time,
                 lr.nickname_copied,
                 lr.phrase_written,
                 lr.zoom_link_clicked
                 FROM users u
                 LEFT JOIN login_records lr ON u.id = lr.user_id
                 ORDER BY lr.login_time DESC''')
    report = c.fetchall()
    conn.close()
    return report

def get_countries():
    conn = sqlite3.connect('zoom_app.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT country FROM users ORDER BY country")
    countries = [row[0] for row in c.fetchall()]
    conn.close()
    return countries

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")