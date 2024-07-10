import streamlit as st
import pyperclip
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

# Load user database
USER_DB = pd.read_csv('user_database.csv')

ZOOM_LINK = "https://zoom.us/j/example"
ZOOM_PASSWORD = "123456"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

def login():
    st.title("Login")
    country = st.text_input("Country")
    name = st.text_input("Name")
    if st.button("Login"):
        user = USER_DB[(USER_DB['country'] == country) & (USER_DB['name'] == name)]
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.user_data = user.iloc[0]
            st.success("Logged in successfully!")
            
            # Record login time
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            login_record = pd.DataFrame({'country': [country], 'name': [name], 'login_time': [login_time]})
            login_record.to_csv('login_history.csv', mode='a', header=False, index=False)
        else:
            st.error("Invalid country or name")

def zoom_access():
    st.title("Zoom Link Access")
    user_data = st.session_state.user_data
    nickname = f"{user_data['country']} / {user_data['name']}"
    st.write(f"Your Zoom nickname will be: {nickname}")
    
    if st.button("Copy Nickname"):
        pyperclip.copy(nickname)
        st.success("Nickname copied to clipboard!")

    st.success("Authorized! Here is your Zoom information:")
    st.write(f"Zoom Link: {ZOOM_LINK}")
    st.write(f"Zoom Password: {ZOOM_PASSWORD}")

def main():
    if not st.session_state.logged_in:
        login()
    else:
        zoom_access()

if __name__ == "__main__":
    main()