import streamlit as st
from streamlit_card import card
import streamlit_authenticator as stauth
import pandas as pd
import pyperclip
from datetime import datetime
from database import init_db, get_user, get_countries
import streamlit.components.v1 as components

# Initialize database
init_db()

ZOOM_LINK = "https://us06web.zoom.us/j/85216023826?pwd=NtS5OUXcMAI9ZJbacJee18xYx90eaW.1"
ZOOM_PASSWORD = "254368"

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
admin_country = "republic of korea"
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
                if st.button("Admin Page"):
                    set_page('admin')
            else:
                if st.button("Zoom Access"):
                    set_page('zoom')
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
            title="DNMD",
            text="DNMD / ZOOM Link Solution",
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
    print(f"Debug - do_login: country={country}, email={email}")  # 디버그 출력 추가
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
        
        # 어드민 계정 확인
        if user[4].lower() == "republic of korea" and user[1].lower() == "dnmd":
            st.session_state.is_admin = True
            set_page('admin')
        else:
            st.session_state.is_admin = False
            set_page('zoom')
        
        st.success("Logged in successfully!")
    else:
        st.error(f"Invalid country or email: {country}, {email}")  # 에러 메시지에 입력값 추가
    
    print(f"Debug - do_login result: logged_in={st.session_state.get('logged_in')}, is_admin={st.session_state.get('is_admin')}")  # 디버그 출력 추가

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
            df = pd.DataFrame(report, columns=['Country', 'First Name', 'Last Name', 'User Type', 'First Login', 'Last Login', 'Login Count'])
            
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
        st.error("먼저 로그인해 주세요.")
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

        st.success("여기 Zoom 정보가 있습니다:")
        st.markdown(f"""
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
            <h3 style="color: #007bff;">Zoom Link:</h3>
            <p><a href="{ZOOM_LINK}" target="_blank">{ZOOM_LINK}</a></p>
            <h3 style="color: #007bff;">Zoom Password:</h3>
            <p><strong>{ZOOM_PASSWORD}</strong></p>
        </div>
        """, unsafe_allow_html=True)

def main():
    main_layout()

if __name__ == "__main__":
    main()