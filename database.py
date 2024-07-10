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
                  nickname_copied INTEGER DEFAULT 0,
                  phrase_written INTEGER DEFAULT 0,
                  zoom_link_clicked INTEGER DEFAULT 0,
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
    
    # 디버그 코드 추가
    print(f"Login record added for user_id: {user_id} at {login_time}")
    
    c.execute("SELECT * FROM login_records WHERE user_id=?", (user_id,))
    print(f"Login records for user_id {user_id}: {c.fetchall()}")
    
    conn.close()

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
                 CASE WHEN lr.user_id IS NOT NULL THEN 'Yes' ELSE 'No' END as logged_in,
                 CASE WHEN lr.nickname_copied = 1 THEN 'Yes' ELSE 'No' END as nickname_copied,
                 CASE WHEN lr.phrase_written = 1 THEN 'Yes' ELSE 'No' END as phrase_written,
                 CASE WHEN lr.zoom_link_clicked = 1 THEN 'Yes' ELSE 'No' END as zoom_link_clicked
                 FROM users u
                 LEFT JOIN login_records lr ON u.id = lr.user_id''')
    report = c.fetchall()
    conn.close()
    return report

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")