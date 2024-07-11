import streamlit as st
from streamlit_card import card
import streamlit_authenticator as stauth
import pandas as pd
import pyperclip
from datetime import datetime
from database import init_db, get_user, add_login_record, get_login_history, get_attendance_report, get_countries, update_nickname_copied, update_phrase_written, update_zoom_link_clicked, get_country_code, get_user_full_name
import streamlit.components.v1 as components

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

# Initialize admin credentials
admin_country = "korea"
admin_name = "dnmd"

# Check if admin credentials are set


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
    st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">Welcome to Zoom Access Portal</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        card(
            title="Login",
            text="Please enter your credentials",
            image="https://static.streamlit.io/examples/dice.jpg",
            styles={
                "card": {
                    "width": "100%",
                    "height": "300px",
                    "border-radius": "10px",
                    "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                }
            }
        )

        countries = get_countries()
        country = st.selectbox("Country", options=countries, format_func=lambda x: x.capitalize())
        
        # 이메일 입력
        email = st.text_input("E-mail")

        # 로그인 버튼
        if st.button("Login", key="login_button"):
            do_login(country, email)

def do_login(country, email):
    user = get_user(country, email)
    if user:
        st.session_state.logged_in = True
        st.session_state.user_data = {
            'id': user[0], 
            'email': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'country': user[4],
            'country_codes': user[5],
            'user_type': user[6]
        }
        set_page('zoom')
        st.success("Logged in successfully!")
    else:
        st.error("Invalid country or email")

def admin_page():
    with st.container():
        st.title("Admin Page")
        if st.button("Show Attendance Report"):
            report = get_attendance_report()
            
            total_users = len(report)
            attended_users = sum(1 for r in report if r[3] is not None)
            attendance_percentage = (attended_users / total_users) * 100 if total_users > 0 else 0
            
            st.write(f"Total users: {total_users}")
            st.write(f"Users who attended: {attended_users}")
            st.write(f"Attendance percentage: {attendance_percentage:.2f}%")
            
            st.write("Detailed Attendance List:")
            
            # 데이터프레임 생성
            df = pd.DataFrame(report, columns=['Country', 'Name', 'User Type', 'First Login', 'Last Login', 'Login Count'])
            
            # 'First Login'이 None인 행을 맨 위로 정렬
            df = df.sort_values('First Login', ascending=True, na_position='first')
            
            # 스타일 적용
            def highlight_no_login(row):
                if pd.isnull(row['First Login']):
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

        # 사용자 데이터를 보기 좋게 표시
        st.subheader("Your Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Name:**", f"{user_data['first_name']} {user_data['last_name']}")
            st.write("**Email:**", user_data['email'])
        with col2:
            st.write("**Country:**", user_data['country'])
            st.write("**User Type:**", user_data['user_type'].capitalize())

        st.write("---")

        country_code = user_data['country_codes']
        full_name = f"{user_data['first_name']} {user_data['last_name']}"
        
        nickname = f"{country_code} / {full_name}"
        
        st.write("Your Zoom nickname:")
        st.code(nickname, language="")
        st.info("Please copy your nickname above and use it when joining the Zoom meeting.")

        st.markdown("Type the following phrase to confirm:")
        st.markdown("**I will use my nickname to join Zoom**")
        
        confirmation = st.text_input("Confirmation:")
        if confirmation.lower() == "i will use my nickname to join zoom":
            st.session_state.show_zoom_info = True
            update_phrase_written(user_data['id'])
            update_nickname_copied(nickname)
            
            # Record login at this point
            login_time = add_login_record(nickname)

        if st.session_state.show_zoom_info:
            st.success("Authorized! Here is your Zoom information:")
            if st.button("Click to show Zoom Link"):
                st.markdown(f"""
                <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
                    <h3 style="color: #007bff;">Zoom Link:</h3>
                    <p><a href="{ZOOM_LINK}" target="_blank">{ZOOM_LINK}</a></p>
                    <h3 style="color: #007bff;">Zoom Password:</h3>
                    <p><strong>{ZOOM_PASSWORD}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                update_zoom_link_clicked(nickname)

            login_history = get_login_history(nickname)
            
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