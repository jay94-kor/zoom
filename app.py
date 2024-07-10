import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Check if user_database.csv exists, if not create it
if not os.path.exists('user_database.csv'):
    initial_data = pd.DataFrame({
        'country': ['Korea', 'USA', 'Japan', 'China'],
        'name': ['Dongjae', 'John', 'Yuki', 'Li Wei']
    })
    initial_data.to_csv('user_database.csv', index=False)

# Check if login_history.csv exists, if not create it
if not os.path.exists('login_history.csv'):
    pd.DataFrame(columns=['country', 'name', 'login_time']).to_csv('login_history.csv', index=False)

# Load user database
USER_DB = pd.read_csv('user_database.csv')
USER_DB['country'] = USER_DB['country'].str.lower()
USER_DB['name'] = USER_DB['name'].str.lower()

ZOOM_LINK = "https://zoom.us/j/example"
ZOOM_PASSWORD = "123456"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'show_zoom_info' not in st.session_state:
    st.session_state.show_zoom_info = False

def login():
    st.title("Login")
    country = st.text_input("Country").lower()
    name = st.text_input("Name").lower()
    if st.button("Login"):
        user = USER_DB[(USER_DB['country'] == country) & (USER_DB['name'] == name)]
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.user_data = user.iloc[0]
            st.success("Logged in successfully!")
            
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            login_record = pd.DataFrame({'country': [user.iloc[0]['country']], 'name': [user.iloc[0]['name']], 'login_time': [login_time]})
            login_record.to_csv('login_history.csv', mode='a', header=False, index=False)
        else:
            st.error("Invalid country or name")

def zoom_access():
    st.title("Zoom Link Access")
    user_data = st.session_state.user_data
    nickname = f"{user_data['country']} / {user_data['name']}"
    st.write(f"Your Zoom nickname: {nickname}")

    # Add a button to copy the nickname
    st.markdown(f"""
    <button onclick="navigator.clipboard.writeText('{nickname}')">
        Copy Nickname
    </button>
    """, unsafe_allow_html=True)

    confirmation = st.text_input("Type 'I will use my nickname to join Zoom' to confirm:")
    if confirmation.lower() == "i will use my nickname to join zoom":
        st.session_state.show_zoom_info = True

    if st.session_state.show_zoom_info:
        st.success("Authorized! Here is your Zoom information:")
        st.write(f"Zoom Link: {ZOOM_LINK}")
        st.write(f"Zoom Password: {ZOOM_PASSWORD}")

        # Display login history
        login_history = pd.read_csv('login_history.csv')
        user_history = login_history[(login_history['country'] == user_data['country']) & (login_history['name'] == user_data['name'])]
        
        if not user_history.empty:
            first_login = user_history['login_time'].min()
            last_login = user_history['login_time'].max()
            st.write(f"First login: {first_login}")
            st.write(f"Most recent login: {last_login}")
        else:
            st.write("This is your first login.")

def main():
    if not st.session_state.logged_in:
        login()
    else:
        zoom_access()

if __name__ == "__main__":
    main()