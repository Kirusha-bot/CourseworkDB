import streamlit as st

USERS = {
    "admin":  {"password": "admin123", "role": "Администратор"},
    "person": {"password": "person123", "role": "Персонал"},
}

def check_auth():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None

    if not st.session_state.logged_in:
        st.title("Вход в систему")
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.role = USERS[username]["role"]
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Неверный логин или пароль")
        st.stop()