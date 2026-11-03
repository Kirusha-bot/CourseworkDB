import streamlit as st
import pandas as pd
from db import run_query, run_execute, log_action

def render_admin():
    st.subheader("Управление военнослужащими")
    action = st.radio("Действие:", ["Добавить", "Редактировать", "Удалить"], horizontal=True, key="admin_action")

    if action == "Добавить":
        render_add()
    elif action == "Редактировать":
        render_edit()
    else:
        render_delete()

def render_add():
    st.markdown("### Добавить военнослужащего")
    c1, c2, c3 = st.columns(3)
    with c1:
        surname = st.text_input("Фамилия")
        first_name = st.text_input("Имя")
        patronymic = st.text_input("Отчество")
    with c2:
        birth_date = st.date_input("Дата рождения")
        ranks_df = run_query("SELECT id_rank, name FROM `Rank` ORDER BY id_rank")
        rank_id = st.selectbox("Звание", ranks_df['name'].tolist(), key="add_rank")
        rank_id = ranks_df[ranks_df['name'] == rank_id]['id_rank'].values[0]
    with c3:
        subunits_df = run_query("SELECT id_subunit, name FROM Subunit_Hierarchy ORDER BY name")
        subunit_id = st.selectbox("Подразделение", subunits_df['name'].tolist(), key="add_subunit")
        subunit_id = subunits_df[subunits_df['name'] == subunit_id]['id_subunit'].values[0]

    specialties_df = run_query("SELECT id_specialty, name FROM Specialty ORDER BY name")
    selected_specs = st.multiselect("Специальности", specialties_df['name'].tolist(), key="add_specs")

    if st.button("Добавить", key="add_btn"):
        # Проверка: фамилия и имя обязательны
        if not surname.strip():
            st.error("Поле 'Фамилия' обязательно для заполнения")
        elif not first_name.strip():
            st.error("Поле 'Имя' обязательно для заполнения")
        # Проверка: минимум одна специальность
        elif len(selected_specs) == 0:
            st.error("Необходимо выбрать хотя бы одну специальность")
        else:
            run_execute(f"""
                INSERT INTO Serviceman (id_subunit, id_rank, surname, first_name, patronymic, birth_date)
                VALUES ({subunit_id}, {rank_id}, '{surname}', '{first_name}', '{patronymic}', '{birth_date}')
            """)
            new_id = int(run_query("SELECT MAX(id_serviceman) AS id FROM Serviceman").iloc[0]['id'])

            for spec_name in selected_specs:
                spec_id = specialties_df[specialties_df['name'] == spec_name]['id_specialty'].values[0]
                run_execute(f"""
                    INSERT INTO Specialty_Assignment (id_serviceman, id_specialty, date_received)
                    VALUES ({new_id}, {spec_id}, CURDATE())
                """)

            details = (f"Добавлен: {surname} {first_name}, звание: {rank_id}, подразделение: {subunit_id}"
                       f", специальности: {selected_specs}")
            undo = f"DELETE FROM Serviceman WHERE id_serviceman = {new_id}"
            log_action("INSERT", "Serviceman", new_id, details, undo)
            st.cache_data.clear()
            st.success(f"Военнослужащий {surname} {first_name} добавлен (ID: {new_id})")
            st.rerun()

def render_edit():
    st.markdown("### Редактировать военнослужащего")
    serv_df = run_query("SELECT id_serviceman, full_name "
                        "FROM Serviceman_Full_Info "
                        "ORDER BY full_name")
    sel = st.selectbox("Выберите", serv_df['full_name'].tolist(), key="edit_sel")
    sid = serv_df[serv_df['full_name'] == sel]['id_serviceman'].values[0]
    info = run_query(f"SELECT * FROM Serviceman WHERE id_serviceman = {sid}").iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        ns = st.text_input("Фамилия", value=info['surname'])
        nf = st.text_input("Имя", value=info['first_name'])
        np = st.text_input("Отчество", value=info['patronymic'] or "")
    with c2:
        nb = st.date_input("Дата рождения", value=info['birth_date'])
        ranks_df = run_query("SELECT id_rank, name "
                             "FROM `Rank` "
                             "ORDER BY id_rank")
        cr = ranks_df[ranks_df['id_rank'] == info['id_rank']]['name'].values[0]
        nr = st.selectbox("Звание", ranks_df['name'].tolist(),
                          index=ranks_df['name'].tolist().index(cr), key="edit_rank")
        nri = ranks_df[ranks_df['name'] == nr]['id_rank'].values[0]
    with c3:
        subunits_df = run_query("SELECT id_subunit, name "
                                "FROM Subunit_Hierarchy "
                                "ORDER BY name")
        cs = subunits_df[subunits_df['id_subunit'] == info['id_subunit']]['name'].values[0]
        nsb = st.selectbox("Подразделение", subunits_df['name'].tolist(),
                           index=subunits_df['name'].tolist().index(cs), key="edit_sub")
        nsi = subunits_df[subunits_df['name'] == nsb]['id_subunit'].values[0]

    st.markdown("#### Специальности")
    specialties_df = run_query("SELECT id_specialty, name "
                               "FROM Specialty "
                               "ORDER BY name")
    current_specs_df = run_query(f"SELECT id_specialty "
                                 f"FROM Specialty_Assignment "
                                 f"WHERE id_serviceman = {sid}")
    current_spec_ids = current_specs_df['id_specialty'].tolist()
    current_spec_names = specialties_df[specialties_df['id_specialty'].isin(current_spec_ids)]['name'].tolist()
    selected_specs = st.multiselect(
        "Выберите специальности",
        specialties_df['name'].tolist(),
        default=current_spec_names,
        key="edit_specs"
    )

    if st.button("Сохранить", key="save_btn"):
        if not ns.strip():
            st.error("Поле 'Фамилия' обязательно для заполнения")
        elif not nf.strip():
            st.error("Поле 'Имя' обязательно для заполнения")
        elif len(selected_specs) == 0:
            st.error("Необходимо выбрать хотя бы одну специальность")
        else:
            old = (f"{info['surname']} {info['first_name']}, звание: {info['id_rank']}, "
                   f"подразделение: {info['id_subunit']}, специальности: {current_spec_names}")
            undo = (f"UPDATE Serviceman SET surname = '{info['surname']}', first_name = '{info['first_name']}', "
                    f"patronymic = '{info['patronymic']}', birth_date = '{info['birth_date']}'"
                    f", id_rank = {info['id_rank']}, id_subunit = {info['id_subunit']} "
                    f"WHERE id_serviceman = {sid}")

            run_execute(f"""
                UPDATE Serviceman SET surname = '{ns}', first_name = '{nf}', patronymic = '{np}',
                    birth_date = '{nb}', id_rank = {nri}, id_subunit = {nsi}
                WHERE id_serviceman = {sid}
            """)

            run_execute(f"DELETE FROM Specialty_Assignment WHERE id_serviceman = {sid}")
            new_spec_names = []
            for spec_name in selected_specs:
                spec_id = specialties_df[specialties_df['name'] == spec_name]['id_specialty'].values[0]
                run_execute(f"""
                    INSERT INTO Specialty_Assignment (id_serviceman, id_specialty, date_received)
                    VALUES ({sid}, {spec_id}, CURDATE())
                """)
                new_spec_names.append(spec_name)

            details = (f"Изменён id={sid}. Было: {old} | Стало: {ns} {nf}, звание: {nri}, подразделение: {nsi},"
                       f" специальности: {new_spec_names}")
            log_action("UPDATE", "Serviceman", int(sid), details, undo)
            st.cache_data.clear()
            st.success("Изменения сохранены")
            st.rerun()

def render_delete():
    st.markdown("### Удалить")
    serv_df = run_query("SELECT id_serviceman, full_name FROM Serviceman_Full_Info ORDER BY full_name")
    sel = st.selectbox("Выберите", serv_df['full_name'].tolist(), key="del_sel")
    sid = serv_df[serv_df['full_name'] == sel]['id_serviceman'].values[0]
    info = run_query(f"SELECT * FROM Serviceman WHERE id_serviceman = {sid}").iloc[0]
    st.warning(f"Будет удалён: {info['surname']} {info['first_name']}")
    if st.button("Удалить", key="del_btn"):
        undo = (f"INSERT INTO Serviceman (id_serviceman, id_subunit, id_rank, surname, "
                f"first_name, patronymic, birth_date)"
                f"VALUES ({sid}, {info['id_subunit']}, {info['id_rank']}, '{info['surname']}', '{info['first_name']}', "
                f"'{info['patronymic']}', '{info['birth_date']}')")
        run_execute(f"DELETE FROM Serviceman WHERE id_serviceman = {sid}")
        log_action("DELETE", "Serviceman", int(sid),
                   f"Удалён: {info['surname']} {info['first_name']}", undo)
        st.cache_data.clear()
        st.success("Удалён")
        st.rerun()

def render_history():
    st.subheader("История действий")
    df = run_query("""
        SELECT id AS `ID`, action_time AS `Время`, action_type AS `Действие`,
               table_name AS `Таблица`, record_id AS `ID записи`,
               details AS `Описание`, performed_by AS `Пользователь`
        FROM Action_History ORDER BY action_time DESC LIMIT 100
    """)
    st.dataframe(df, use_container_width=True)
    st.markdown("---")
    st.subheader("Отменить последнее действие")
    last = run_query("SELECT * FROM Action_History ORDER BY action_time DESC LIMIT 1")
    if len(last) > 0:
        last = last.iloc[0]
        if st.button("Отменить", key="undo_btn"):
            if last['undo_query']:
                run_execute(last['undo_query'])
                run_execute(f"DELETE FROM Action_History WHERE id = {last['id']}")
                st.cache_data.clear()
                st.success("Отменено")
                st.rerun()
