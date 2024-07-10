import streamlit as st
import pandas as pd
import pyperclip
from datetime import datetime
from database import init_db, get_user, add_login_record, get_login_history, get_attendance_report, get_countries, update_nickname_copied, update_phrase_written, update_zoom_link_clicked

# Initialize database
init_db()

ZOOM_LINK = "https://zoom.us/j/example"
ZOOM_PASSWORD = "123456"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'show_zoom_info' not in st.session_state:
    st.session_state.show_zoom_info = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def reset_session():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state.page = 'login'
    st.experimental_rerun()

def set_page(page_name):
    st.session_state.page = page_name

# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Sidebar for navigation
def sidebar():
    with st.sidebar:
        st.title("Navigation")
        if st.session_state.get('logged_in', False):
            if st.session_state.get('is_admin', False):
                st.button("Admin Page", on_click=set_page, args=('admin',))
            else:
                st.button("Zoom Access", on_click=set_page, args=('zoom',))
            if st.button("Logout"):
                reset_session()
        elif st.session_state.page != 'login':
            set_page('login')
# Main layout
def main_layout():
    sidebar()
    
    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'admin':
        admin_page()
    elif st.session_state.page == 'zoom':
        zoom_access()

def login_page():
    with st.container():
        st.title("Login")
        countries = get_countries()
        country = st.selectbox("Country", options=countries).lower()
        name = st.text_input("Name").lower()
        if st.button("Login"):
            if country == "korea" and name == "dnmd":
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                set_page('admin')
                st.success("Logged in as admin!")
            else:
                user = get_user(country, name)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_data = {'id': user[0], 'country': user[1], 'name': user[2]}
                    set_page('zoom')
                    st.success("Logged in successfully!")
                else:
                    st.error("Invalid country or name")

def admin_page():
    with st.container():
        st.title("Admin Page")
        if st.button("Show Attendance Report"):
            report = get_attendance_report()
            
            total_users = len(report)
            attended_users = sum(1 for r in report if r[2] is not None)
            attendance_percentage = (attended_users / total_users) * 100 if total_users > 0 else 0
            
            st.write(f"Total users: {total_users}")
            st.write(f"Users who attended: {attended_users}")
            st.write(f"Attendance percentage: {attendance_percentage:.2f}%")
            
            st.write("Detailed Attendance List:")
            
            # 데이터프레임 생성
            df = pd.DataFrame(report, columns=['Country', 'Name', 'Login Time', 'Nickname Copied', 'Phrase Written', 'Zoom Link Clicked'])
            
            # 'Login Time'이 None인 행을 맨 위로 정렬
            df = df.sort_values('Login Time', ascending=True, na_position='first')
            
            # 스타일 적용
            def highlight_no_login(row):
                if pd.isnull(row['Login Time']):
                    return ['background-color: yellow'] * len(row)
                return [''] * len(row)
            
            styled_df = df.style.apply(highlight_no_login, axis=1)
            
            st.dataframe(styled_df)

def zoom_access():
    if not st.session_state.logged_in or st.session_state.user_data is None:
        st.error("Please log in first.")
        set_page('login')
        return

    with st.container():
        st.title("Zoom Link Access")
        user_data = st.session_state.user_data
        nickname = f"{user_data['country']} / {user_data['name']}"
        st.write(f"Your Zoom nickname: {nickname}")

        if st.button("Copy Nickname"):
            pyperclip.copy(nickname)
            st.success("Nickname copied to clipboard!")
            update_nickname_copied(user_data['id'])

        st.markdown("Type the following phrase to confirm:")
        st.markdown("**I will use my nickname to join Zoom**")
        
        confirmation = st.text_input("Confirmation:")
        if confirmation.lower() == "i will use my nickname to join zoom":
            st.session_state.show_zoom_info = True
            update_phrase_written(user_data['id'])
            
            # Record login at this point
            login_time = add_login_record(user_data['id'])

        if st.session_state.show_zoom_info:
            st.success("Authorized! Here is your Zoom information:")
            if st.button("Click to show Zoom Link"):
                st.write(f"Zoom Link: {ZOOM_LINK}")
                st.write(f"Zoom Password: {ZOOM_PASSWORD}")
                update_zoom_link_clicked(user_data['id'])

            login_history = get_login_history(user_data['id'])
            
            if login_history:
                first_login = login_history[0][0]
                last_login = login_history[-1][0]
                st.write(f"First login: {first_login}")
                st.write(f"Most recent login: {last_login}")
                st.write(f"Total logins: {len(login_history)}")
            else:
                st.write("This is your first login.")

def main():
    main_layout()

if __name__ == "__main__":
    main()