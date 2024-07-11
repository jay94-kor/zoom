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
                  first_name TEXT NOT NULL,
                  last_name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  user_type TEXT NOT NULL CHECK(user_type IN ('staff', 'participant')))''')
    
    # Create login_records table (combining login_history and login_records)
    c.execute('''CREATE TABLE IF NOT EXISTS login_records
                 (id INTEGER PRIMARY KEY,
                  nickname TEXT NOT NULL,
                  login_time TEXT NOT NULL,
                  nickname_copied TEXT,
                  phrase_written TEXT,
                  zoom_link_clicked TEXT)''')
    
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
    c.execute("SELECT first_name, last_name FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    result = c.fetchone()
    conn.close()
    return f"{result[0]} {result[1]}" if result else None

def add_login_record(nickname):
    conn = get_db_connection()
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO login_records (nickname, login_time) VALUES (?, ?)", (nickname, current_time))
    conn.commit()
    conn.close()
    return current_time

def get_login_history(nickname):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT login_time FROM login_records WHERE nickname = ? ORDER BY login_time ASC", (nickname,))
    login_history = cursor.fetchall()
    conn.close()
    return login_history

def get_attendance_report():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.country, users.first_name, users.last_name, users.user_type,
               MIN(login_records.login_time) as first_login,
               MAX(login_records.login_time) as last_login,
               COUNT(login_records.id) as login_count,
               login_records.nickname
        FROM users
        LEFT JOIN login_records ON login_records.nickname = (
            SELECT country_codes || ' / ' || 
            CASE 
                WHEN instr(users.first_name, ' ') > 0 
                THEN substr(users.first_name, 1, instr(users.first_name, ' ')-1) || ' ' || 
                     substr(users.first_name, instr(users.first_name, ' ', -1)+1)
                ELSE users.first_name
            END || ' ' || users.last_name
            FROM country_db 
            WHERE LOWER(country_db.nationality) = LOWER(users.country)
        )
        GROUP BY users.id
        ORDER BY users.country, users.first_name, users.last_name
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

def update_login_record(nickname, field):
    conn = get_db_connection()
    c = conn.cursor()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(f"UPDATE login_records SET {field} = ? WHERE nickname = ? AND {field} IS NULL", (time, nickname))
    conn.commit()
    conn.close()
    return time

def update_nickname_copied(nickname):
    return update_login_record(nickname, 'nickname_copied')

def update_phrase_written(nickname):
    return update_login_record(nickname, 'phrase_written')

def update_zoom_link_clicked(nickname):
    return update_login_record(nickname, 'zoom_link_clicked')

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")