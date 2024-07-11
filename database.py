import sqlite3
from datetime import datetime

def get_db_connection():
    return sqlite3.connect('login.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  country TEXT NOT NULL,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL)''')
    
    # Create login_history table
    c.execute('''CREATE TABLE IF NOT EXISTS login_history
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER NOT NULL,
                  login_time TEXT NOT NULL,
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
    
    # Create country_db table
    c.execute('''CREATE TABLE IF NOT EXISTS country_db
                 (id INTEGER PRIMARY KEY,
                  nationality TEXT NOT NULL,
                  country_codes TEXT NOT NULL)''')
    
    conn.commit()
    conn.close()

def get_user(country, email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE LOWER(country)=LOWER(?) AND LOWER(email)=LOWER(?)", (country, email))
    user = c.fetchone()
    conn.close()
    return user

def get_country_code(nationality):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT country_codes FROM country_db WHERE LOWER(nationality) = LOWER(?)", (nationality,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_full_name(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def add_login_record(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    current_time = datetime.now()

    # 기존 로그인 기록 확인
    cursor.execute("SELECT login_time FROM login_history WHERE user_id = ? ORDER BY login_time ASC", (user_id,))
    existing_records = cursor.fetchall()

    if not existing_records:
        # 첫 로그인인 경우
        cursor.execute("INSERT INTO login_history (user_id, login_time) VALUES (?, ?)", (user_id, current_time))
    else:
        # 이미 로그인 기록이 있는 경우
        first_login = existing_records[0][0]
        cursor.execute("DELETE FROM login_history WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO login_history (user_id, login_time) VALUES (?, ?), (?, ?)",
                       (user_id, first_login, user_id, current_time))

    conn.commit()
    conn.close()
    return current_time

def get_login_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT login_time FROM login_history WHERE user_id = ? ORDER BY login_time ASC", (user_id,))
    login_history = cursor.fetchall()
    conn.close()
    return login_history

def get_attendance_report():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.country, users.name, 
               MIN(login_history.login_time) as first_login,
               MAX(login_history.login_time) as last_login
        FROM users
        LEFT JOIN login_history ON users.id = login_history.user_id
        GROUP BY users.id
        ORDER BY users.country, users.name
    """)
    report = cursor.fetchall()
    conn.close()
    return report

def get_countries():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT nationality FROM country_db ORDER BY nationality")
    countries = [row[0] for row in c.fetchall()]
    conn.close()
    return countries

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")