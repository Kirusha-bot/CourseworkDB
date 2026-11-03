import streamlit as st
from db import run_query, run_execute, init_history_table, log_action
from auth import check_auth
from ui.queries import render_all_queries
from ui.admin import render_admin, render_history

# Инициализация
init_history_table()

# Авторизация
check_auth()

# Заголовок
st.set_page_config(page_title="Военный округ", layout="wide")
st.title("Информационная система военного округа")
st.caption(f"Роль: {st.session_state.role} | Пользователь: {st.session_state.get('username', '')}")

# Боковая панель
if st.sidebar.button("Выйти"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()
if st.sidebar.button("Обновить"):
    st.cache_data.clear()
    st.rerun()

# Вкладки запросов
st.markdown("---")
st.subheader("Информационные запросы")
render_all_queries()

# Вкладки управления/истории
st.markdown("---")
if st.session_state.role == "Администратор":
    st.subheader("Управление")
    tabs_admin = st.tabs(["Управление", "История"])
    with tabs_admin[0]:
        render_admin()
    with tabs_admin[1]:
        render_history()

st.markdown("---")
st.caption("Информационная система военного округа")
