import sqlite3
from datetime import datetime
import csv

def get_db_connection():
    return sqlite3.connect('login.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  email TEXT NOT NULL,
                  first_name TEXT NOT NULL,
                  last_name TEXT NOT NULL,
                  country TEXT NOT NULL,
                  country_codes TEXT NOT NULL,
                  user_type TEXT NOT NULL CHECK(user_type IN ('participant', 'staff')))''')
    
    # Create login_records table (combining login_history and login_records)
    c.execute('''CREATE TABLE IF NOT EXISTS login_records
                 (id INTEGER PRIMARY KEY,
                  nickname TEXT NOT NULL,
                  login_time TEXT NOT NULL,
                  nickname_copied TEXT,
                  phrase_written TEXT,
                  zoom_link_clicked TEXT)''')
    
    # Drop country_db table
    c.execute('DROP TABLE IF EXISTS country_db')
    
    conn.commit()
    conn.close()

def get_user(country, email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE LOWER(country)=LOWER(?) AND LOWER(email)=LOWER(?)", (country, email))
    user = c.fetchone()
    conn.close()
    return user

def get_country_code(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT country_codes FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        print(f"Country code not found for email: {email}")  # 디버깅을 위한 출력
        return None

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
               COUNT(login_records.id) as login_count
        FROM users
        LEFT JOIN login_records ON login_records.nickname = (
            users.country_codes || ' / ' || 
            users.first_name || ' ' || users.last_name
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
    c.execute("SELECT DISTINCT country FROM users ORDER BY country")
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

def import_csv_to_db(csv_file_path):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 기존 users 테이블의 모든 데이터 삭제
    cursor.execute("DELETE FROM users")

    # CSV 파일 읽기 및 데이터 삽입
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            cursor.execute("""
                INSERT INTO users (email, first_name, last_name, country, country_codes, user_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                row['email'],
                row['first_name'],
                row['last_name'],
                row['country'],
                row['country_codes'],
                row['user_type']
            ))

    conn.commit()
    conn.close()
    print("CSV 데이터가 성공적으로 데이터베이스에 삽입되었습니다.")

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")

from database import import_csv_to_db

import_csv_to_db('2024 게이트웨이 DB_0711_수정.csv')