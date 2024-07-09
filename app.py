import streamlit as st

# Sample user data
USER_DATA = {
    "username": "jangdongjae",
    "password": "1234"
}

ZOOM_LINK = "https://naver.com"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'authorized' not in st.session_state:
    st.session_state.authorized = False

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USER_DATA["username"] and password == USER_DATA["password"]:
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")

def zoom_access():
    st.title("Zoom Link Access")
    instruction = "I will change my nickname to Country / Name in Zoom."
    user_input = st.text_input("Enter the following to proceed: " + instruction)
    if user_input == instruction:
        st.session_state.authorized = True
        st.success("Authorized! Here is your Zoom link:")
        st.write(ZOOM_LINK)
    else:
        st.error("Incorrect input. Please enter the exact text.")

def main():
    if not st.session_state.logged_in:
        login()
    else:
        if not st.session_state.authorized:
            zoom_access()
        else:
            st.write("You are already authorized. Here is your Zoom link:")
            st.write(ZOOM_LINK)

if __name__ == "__main__":
    main()
