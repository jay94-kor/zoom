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
    pd.DataFrame(columns=['country', 'name', 'login_time', 'login_type']).to_csv('login_history.csv', index=False)

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
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def login():
    st.title("Login")
    country = st.text_input("Country").lower()
    name = st.text_input("Name").lower()
    if st.button("Login"):
        if country == "korea" and name == "dnmd":
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.success("Logged in as admin!")
        else:
            user = USER_DB[(USER_DB['country'] == country) & (USER_DB['name'] == name)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_data = user.iloc[0]
                st.success("Logged in successfully!")
                
                login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                login_history = pd.read_csv('login_history.csv')
                user_history = login_history[(login_history['country'] == user.iloc[0]['country']) & (login_history['name'] == user.iloc[0]['name'])]
                login_type = "First login" if user_history.empty else "Subsequent login"
                login_record = pd.DataFrame({'country': [user.iloc[0]['country']], 'name': [user.iloc[0]['name']], 'login_time': [login_time], 'login_type': [login_type]})
                login_record.to_csv('login_history.csv', mode='a', header=False, index=False)
            else:
                st.error("Invalid country or name")

def admin_page():
    st.title("Admin Page")
    
    if st.button("Show Attendance Report"):
        user_db = pd.read_csv('user_database.csv')
        login_history = pd.read_csv('login_history.csv')
        
        # Get unique users who have logged in at least once
        attended_users = login_history[['country', 'name']].drop_duplicates()
        
        # Calculate attendance percentage
        total_users = len(user_db)
        attended_users_count = len(attended_users)
        attendance_percentage = (attended_users_count / total_users) * 100
        
        st.write(f"Total users: {total_users}")
        st.write(f"Users who attended: {attended_users_count}")
        st.write(f"Attendance percentage: {attendance_percentage:.2f}%")
        
        # Show detailed attendance list
        st.write("Detailed Attendance List:")
        attendance_list = user_db.merge(attended_users, on=['country', 'name'], how='left', indicator=True)
        attendance_list['Attended'] = attendance_list['_merge'].map({'both': 'Yes', 'left_only': 'No'})
        attendance_list = attendance_list.drop('_merge', axis=1)
        st.dataframe(attendance_list)

def zoom_access():
    st.title("Zoom Link Access")
    user_data = st.session_state.user_data
    nickname = f"{user_data['country']} / {user_data['name']}"
    st.write(f"Your Zoom nickname: {nickname}")

    # Add a text area with the nickname and a copy button
    st.text_area("Your Zoom nickname (click to copy)", nickname, height=50)
    st.info("Click the text area above to select the nickname, then use Ctrl+C (or Cmd+C on Mac) to copy.")

    st.markdown("Type the following phrase to confirm:")
    st.markdown("**I will use my nickname to join Zoom**")
    
    confirmation = st.text_input("Confirmation:")
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
            first_login = user_history[user_history['login_type'] == 'First login']['login_time'].iloc[0]
            last_login = user_history['login_time'].max()
            st.write(f"First login: {first_login}")
            st.write(f"Most recent login: {last_login}")
            st.write(f"Total logins: {len(user_history)}")
        else:
            st.write("This is your first login.")

def main():
    if not st.session_state.logged_in:
        login()
    elif st.session_state.is_admin:
    else:
        zoom_access()

if __name__ == "__main__":
    main()