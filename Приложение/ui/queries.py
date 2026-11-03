import streamlit as st
import pandas as pd
from db import run_query


def render_all_queries():
    """Отрисовка всех вкладок с запросами"""
    tabs = st.tabs([
        "Части", "Офицеры", "Рядовые", "Подчинённость",
        "Дислокация", "Техника", "Сооружения", "Техника >N",
        "Вооружение", "Специальности", "Специалисты",
        "Вооружение >N", "Статистика", "Все"
    ])

    with tabs[0]:
        query1_parts()
    with tabs[1]:
        query2_officers()
    with tabs[2]:
        query3_enlisted()
    with tabs[3]:
        query4_chain()
    with tabs[4]:
        query5_locations()
    with tabs[5]:
        query6_equipment()
    with tabs[6]:
        query7_facilities()
    with tabs[7]:
        query8_equipment_filter()
    with tabs[8]:
        query9_armament()
    with tabs[9]:
        query10_specialties()
    with tabs[10]:
        query11_specialists()
    with tabs[11]:
        query12_armament_filter()
    with tabs[12]:
        query13_stats()
    with tabs[13]:
        query14_all_servicemen()



# 1. ЧАСТИ С КОМАНДИРАМИ
def query1_parts():
    st.subheader("Перечень частей с командирами")
    sub = st.radio(
        "Фильтр:",
        ["Все части", "По армии", "По дивизии", "По корпусу"],
        horizontal=True,
        key="r1"
    )

    if sub == "Все части":
        df = run_query("""
            SELECT DISTINCT
                sh.id_military_unit AS `ID`,
                mu.name             AS `Часть`,
                sh.name             AS `Подразделение`,
                sh.commander_name   AS `Командир`
            FROM Subunit_Hierarchy sh
            JOIN Military_Unit mu
                ON sh.id_military_unit = mu.id_military_unit
            WHERE sh.unit_type = 'Часть'
              AND sh.commander_name != ''
        """)

    elif sub == "По армии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Армия'
        """)
        sel = st.selectbox("Армия", items['name'].tolist(), key="s1a")
        df = run_query(f"""
            SELECT DISTINCT
                sh.id_military_unit AS `ID`,
                mu.name             AS `Часть`,
                sh.name             AS `Подразделение`,
                sh.commander_name   AS `Командир`
            FROM Subunit_Hierarchy sh
            JOIN Military_Unit mu
                ON sh.id_military_unit = mu.id_military_unit
            WHERE sh.unit_type = 'Часть'
              AND sh.path LIKE '{sel}%'
              AND sh.id_military_unit IS NOT NULL
        """)

    elif sub == "По дивизии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Дивизия'
        """)
        sel = st.selectbox("Дивизия", items['name'].tolist(), key="s1d")
        df = run_query(f"""
            SELECT DISTINCT
                sh.id_military_unit AS `ID`,
                mu.name             AS `Часть`,
                sh.name             AS `Подразделение`,
                sh.commander_name   AS `Командир`
            FROM Subunit_Hierarchy sh
            JOIN Military_Unit mu
                ON sh.id_military_unit = mu.id_military_unit
            WHERE sh.unit_type = 'Часть'
              AND sh.path LIKE '%{sel}%'
              AND sh.id_military_unit IS NOT NULL
        """)

    else:
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Корпус'
        """)
        sel = st.selectbox("Корпус", items['name'].tolist(), key="s1c")
        df = run_query(f"""
            SELECT DISTINCT
                sh.id_military_unit AS `ID`,
                mu.name             AS `Часть`,
                sh.name             AS `Подразделение`,
                sh.commander_name   AS `Командир`
            FROM Subunit_Hierarchy sh
            JOIN Military_Unit mu
                ON sh.id_military_unit = mu.id_military_unit
            WHERE sh.unit_type = 'Часть'
              AND sh.path LIKE '%{sel}%'
              AND sh.id_military_unit IS NOT NULL
        """)

    st.dataframe(df, use_container_width=True)



# 2. ОФИЦЕРСКИЙ СОСТАВ
def query2_officers():
    st.subheader("Офицерский состав")

    c1, c2 = st.columns(2)
    with c1:
        rank = st.selectbox(
            "Звание",
            [
                "Все", "Генерал", "Генерал-полковник", "Генерал-лейтенант",
                "Генерал-майор", "Полковник", "Подполковник", "Майор",
                "Капитан", "Лейтенант"
            ],
            key="s2r"
        )
    with c2:
        scope = st.selectbox(
            "В составе",
            ["Всего округа", "Армии", "Дивизии", "Корпуса", "Военной части"],
            key="s2s"
        )

    cond = "rank_category = 'Офицерский состав'"
    if rank != "Все":
        cond += f" AND `rank` = '{rank}'"

    if scope == "Всего округа":
        df = run_query(f"""
            SELECT
                id_serviceman  AS `ID`,
                full_name      AS `ФИО`,
                birth_date     AS `Дата рождения`,
                `rank`         AS `Звание`,
                subunit        AS `Подразделение`,
                military_unit  AS `Часть`
            FROM Serviceman_Full_Info
            WHERE {cond}
            ORDER BY full_name
        """)

    elif scope == "Армии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Армия'
        """)
        sel = st.selectbox("Армия", items['name'].tolist(), key="s2a")
        df = run_query(f"""
            SELECT
                sfi.id_serviceman  AS `ID`,
                sfi.full_name      AS `ФИО`,
                sfi.birth_date     AS `Дата рождения`,
                sfi.`rank`         AS `Звание`,
                sfi.subunit        AS `Подразделение`,
                sfi.military_unit  AS `Часть`
            FROM Serviceman_Full_Info sfi
            JOIN Subunit_Hierarchy sh
                ON sfi.id_subunit = sh.id_subunit
            WHERE sh.path LIKE '{sel}%'
              AND {cond}
            ORDER BY sfi.full_name
        """)

    elif scope == "Дивизии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Дивизия'
        """)
        sel = st.selectbox("Дивизия", items['name'].tolist(), key="s2d")
        df = run_query(f"""
            SELECT
                sfi.id_serviceman  AS `ID`,
                sfi.full_name      AS `ФИО`,
                sfi.birth_date     AS `Дата рождения`,
                sfi.`rank`         AS `Звание`,
                sfi.subunit        AS `Подразделение`,
                sfi.military_unit  AS `Часть`
            FROM Serviceman_Full_Info sfi
            JOIN Subunit_Hierarchy sh
                ON sfi.id_subunit = sh.id_subunit
            WHERE sh.path LIKE '%{sel}%'
              AND {cond}
            ORDER BY sfi.full_name
        """)

    elif scope == "Корпуса":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Корпус'
        """)
        sel = st.selectbox("Корпус", items['name'].tolist(), key="s2c")
        df = run_query(f"""
            SELECT
                sfi.id_serviceman  AS `ID`,
                sfi.full_name      AS `ФИО`,
                sfi.birth_date     AS `Дата рождения`,
                sfi.`rank`         AS `Звание`,
                sfi.subunit        AS `Подразделение`,
                sfi.military_unit  AS `Часть`
            FROM Serviceman_Full_Info sfi
            JOIN Subunit_Hierarchy sh
                ON sfi.id_subunit = sh.id_subunit
            WHERE sh.path LIKE '%{sel}%'
              AND {cond}
            ORDER BY sfi.full_name
        """)

    else:
        items = run_query("""
            SELECT id_military_unit, military_unit
            FROM Serviceman_Full_Info
            WHERE military_unit IS NOT NULL
            GROUP BY id_military_unit, military_unit
        """)
        sel = st.selectbox("Часть", items['military_unit'].tolist(), key="s2u")
        uid = items[items['military_unit'] == sel]['id_military_unit'].values[0]
        df = run_query(f"""
            SELECT
                id_serviceman  AS `ID`,
                full_name      AS `ФИО`,
                birth_date     AS `Дата рождения`,
                `rank`         AS `Звание`,
                subunit        AS `Подразделение`
            FROM Serviceman_Full_Info
            WHERE id_military_unit = {uid}
              AND {cond}
            ORDER BY full_name
        """)

    st.dataframe(df, use_container_width=True)



# 3. РЯДОВОЙ И СЕРЖАНТСКИЙ СОСТАВ
def query3_enlisted():
    st.subheader("Рядовой и сержантский состав")

    c1, c2 = st.columns(2)
    with c1:
        rank = st.selectbox(
            "Звание",
            ["Все", "Старшина", "Сержант", "Прапорщик", "Ефрейтор", "Рядовой"],
            key="s3r"
        )
    with c2:
        scope = st.selectbox(
            "В составе",
            ["Всего округа", "Армии", "Дивизии", "Корпуса", "Военной части"],
            key="s3s"
        )

    cond = "rank_category = 'Рядовой и сержантский состав'"
    if rank != "Все":
        cond += f" AND `rank` = '{rank}'"

    if scope == "Всего округа":
        df = run_query(f"""
            SELECT
                id_serviceman  AS `ID`,
                full_name      AS `ФИО`,
                birth_date     AS `Дата рождения`,
                `rank`         AS `Звание`,
                subunit        AS `Подразделение`,
                military_unit  AS `Часть`
            FROM Serviceman_Full_Info
            WHERE {cond}
            ORDER BY full_name
        """)

    elif scope == "Армии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Армия'
        """)
        sel = st.selectbox("Армия", items['name'].tolist(), key="s3a")
        df = run_query(f"""
            SELECT
                sfi.id_serviceman  AS `ID`,
                sfi.full_name      AS `ФИО`,
                sfi.birth_date     AS `Дата рождения`,
                sfi.`rank`         AS `Звание`,
                sfi.subunit        AS `Подразделение`,
                sfi.military_unit  AS `Часть`
            FROM Serviceman_Full_Info sfi
            JOIN Subunit_Hierarchy sh
                ON sfi.id_subunit = sh.id_subunit
            WHERE sh.path LIKE '{sel}%'
              AND {cond}
            ORDER BY sfi.full_name
        """)

    elif scope == "Дивизии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Дивизия'
        """)
        sel = st.selectbox("Дивизия", items['name'].tolist(), key="s3d")
        df = run_query(f"""
            SELECT
                sfi.id_serviceman  AS `ID`,
                sfi.full_name      AS `ФИО`,
                sfi.birth_date     AS `Дата рождения`,
                sfi.`rank`         AS `Звание`,
                sfi.subunit        AS `Подразделение`,
                sfi.military_unit  AS `Часть`
            FROM Serviceman_Full_Info sfi
            JOIN Subunit_Hierarchy sh
                ON sfi.id_subunit = sh.id_subunit
            WHERE sh.path LIKE '%{sel}%'
              AND {cond}
            ORDER BY sfi.full_name
        """)

    elif scope == "Корпуса":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Корпус'
        """)
        sel = st.selectbox("Корпус", items['name'].tolist(), key="s3c")
        df = run_query(f"""
            SELECT
                sfi.id_serviceman  AS `ID`,
                sfi.full_name      AS `ФИО`,
                sfi.birth_date     AS `Дата рождения`,
                sfi.`rank`         AS `Звание`,
                sfi.subunit        AS `Подразделение`,
                sfi.military_unit  AS `Часть`
            FROM Serviceman_Full_Info sfi
            JOIN Subunit_Hierarchy sh
                ON sfi.id_subunit = sh.id_subunit
            WHERE sh.path LIKE '%{sel}%'
              AND {cond}
            ORDER BY sfi.full_name
        """)

    else:
        items = run_query("""
            SELECT id_military_unit, military_unit
            FROM Serviceman_Full_Info
            WHERE military_unit IS NOT NULL
            GROUP BY id_military_unit, military_unit
        """)
        sel = st.selectbox("Часть", items['military_unit'].tolist(), key="s3u")
        uid = items[items['military_unit'] == sel]['id_military_unit'].values[0]
        df = run_query(f"""
            SELECT
                id_serviceman  AS `ID`,
                full_name      AS `ФИО`,
                birth_date     AS `Дата рождения`,
                `rank`         AS `Звание`,
                subunit        AS `Подразделение`
            FROM Serviceman_Full_Info
            WHERE id_military_unit = {uid}
              AND {cond}
            ORDER BY full_name
        """)

    st.dataframe(df, use_container_width=True)



# 4. ЦЕПОЧКА ПОДЧИНЁННОСТИ
def query4_chain():
    st.subheader("Цепочка подчинённости снизу доверху")

    items = run_query("""
        SELECT id_serviceman, full_name
        FROM Serviceman_Full_Info
        ORDER BY full_name
    """)
    sel = st.selectbox("Военнослужащий", items['full_name'].tolist(), key="s4")
    sid = items[items['full_name'] == sel]['id_serviceman'].values[0]

    info = run_query(f"""
        SELECT
            full_name      AS `ФИО`,
            `rank`         AS `Звание`,
            subunit        AS `Подразделение`,
            military_unit  AS `Часть`
        FROM Serviceman_Full_Info
        WHERE id_serviceman = {sid}
    """)
    st.table(info)

    st.caption("Цепочка подчинённости:")
    df = run_query(f"""
        WITH RECURSIVE chain AS (
            SELECT *
            FROM Subunit_Hierarchy
            WHERE id_subunit = (
                SELECT id_subunit
                FROM Serviceman
                WHERE id_serviceman = {sid}
            )

            UNION ALL

            SELECT sh.*
            FROM Subunit_Hierarchy sh
            JOIN chain c
                ON sh.id_subunit = c.id_parent
        )
        SELECT
            depth_level    AS `Уровень`,
            unit_type      AS `Тип подразделения`,
            name           AS `Название`,
            commander_name AS `Командир`
        FROM chain
        ORDER BY depth_level
    """)
    st.dataframe(df, use_container_width=True)



# 5. МЕСТА ДИСЛОКАЦИИ
def query5_locations():
    st.subheader("Места дислокации")

    scope = st.selectbox(
        "В составе",
        ["Всего округа", "Армии", "Дивизии", "Корпуса", "Военной части"],
        key="s5"
    )

    if scope == "Всего округа":
        df = run_query("""
            SELECT DISTINCT
                l.name        AS `Место дислокации`,
                l.coordinates AS `Координаты`,
                mu.name       AS `Воинская часть`
            FROM Location l
            JOIN Military_Unit mu
                ON l.id_location = mu.id_location
            ORDER BY l.name, mu.name
        """)

    elif scope == "Армии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Армия'
        """)
        sel = st.selectbox("Армия", items['name'].tolist(), key="s5a")
        df = run_query(f"""
            SELECT DISTINCT
                l.name        AS `Место дислокации`,
                l.coordinates AS `Координаты`,
                mu.name       AS `Воинская часть`
            FROM Subunit_Hierarchy sh
            JOIN Military_Unit mu
                ON sh.id_military_unit = mu.id_military_unit
            JOIN Location l
                ON mu.id_location = l.id_location
            WHERE sh.path LIKE '{sel}%'
              AND sh.id_military_unit IS NOT NULL
            ORDER BY l.name, mu.name
        """)

    elif scope == "Дивизии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Дивизия'
        """)
        sel = st.selectbox("Дивизия", items['name'].tolist(), key="s5d")
        df = run_query(f"""
            SELECT DISTINCT
                l.name        AS `Место дислокации`,
                l.coordinates AS `Координаты`,
                mu.name       AS `Воинская часть`
            FROM Subunit_Hierarchy sh
            JOIN Military_Unit mu
                ON sh.id_military_unit = mu.id_military_unit
            JOIN Location l
                ON mu.id_location = l.id_location
            WHERE sh.path LIKE '%{sel}%'
              AND sh.id_military_unit IS NOT NULL
            ORDER BY l.name, mu.name
        """)

    elif scope == "Корпуса":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Корпус'
        """)
        sel = st.selectbox("Корпус", items['name'].tolist(), key="s5c")
        df = run_query(f"""
            SELECT DISTINCT
                l.name        AS `Место дислокации`,
                l.coordinates AS `Координаты`,
                mu.name       AS `Воинская часть`
            FROM Subunit_Hierarchy sh
            JOIN Military_Unit mu
                ON sh.id_military_unit = mu.id_military_unit
            JOIN Location l
                ON mu.id_location = l.id_location
            WHERE sh.path LIKE '%{sel}%'
              AND sh.id_military_unit IS NOT NULL
            ORDER BY l.name, mu.name
        """)

    else:
        items = run_query("""
            SELECT id_military_unit, name
            FROM Military_Unit
            ORDER BY name
        """)
        sel = st.selectbox("Часть", items['name'].tolist(), key="s5u")
        uid = items[items['name'] == sel]['id_military_unit'].values[0]
        df = run_query(f"""
            SELECT
                l.name        AS `Место дислокации`,
                l.coordinates AS `Координаты`,
                mu.name       AS `Воинская часть`
            FROM Location l
            JOIN Military_Unit mu
                ON l.id_location = mu.id_location
            WHERE mu.id_military_unit = {uid}
        """)

    st.dataframe(df, use_container_width=True)



# 6. БОЕВАЯ ТЕХНИКА
def query6_equipment():
    st.subheader("Боевая техника")

    c1, c2 = st.columns(2)
    with c1:
        cat = st.selectbox(
            "Категория",
            [
                "Все", "Гусеничная", "Колёсная", "Автомобильная",
                "Самолёт", "Вертолёт", "ЗРК", "БПЛА"
            ],
            key="s6c"
        )
    with c2:
        scope = st.selectbox(
            "В составе",
            ["Всего округа", "Армии", "Дивизии", "Корпуса", "Военной части"],
            key="s6s"
        )

    cond = "" if cat == "Все" else f"AND ues.equipment_category = '{cat}'"

    if scope == "Всего округа":
        df = run_query(f"""
            SELECT
                ues.id_military_unit   AS `ID части`,
                ues.unit_name          AS `Воинская часть`,
                ues.equipment_category AS `Категория`,
                ues.model              AS `Модель`,
                ues.quantity           AS `Количество`
            FROM Unit_Equipment_Summary ues
            WHERE 1 = 1 {cond}
            ORDER BY ues.unit_name
        """)

    elif scope in ("Армии", "Дивизии", "Корпуса"):
        type_map = {
            "Армии": "Армия",
            "Дивизии": "Дивизия",
            "Корпуса": "Корпус"
        }
        items = run_query(f"""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = '{type_map[scope]}'
        """)
        sel = st.selectbox(type_map[scope], items['name'].tolist(), key=f"s6{scope[0]}")
        like = f"{sel}%" if scope == "Армии" else f"%{sel}%"
        df = run_query(f"""
            SELECT
                ues.id_military_unit   AS `ID части`,
                ues.unit_name          AS `Воинская часть`,
                ues.equipment_category AS `Категория`,
                ues.model              AS `Модель`,
                ues.quantity           AS `Количество`
            FROM Unit_Equipment_Summary ues
            JOIN Subunit_Hierarchy sh
                ON ues.id_military_unit = sh.id_military_unit
            WHERE sh.path LIKE '{like}'
              AND sh.unit_type = 'Часть'
              {cond}
            ORDER BY ues.unit_name
        """)

    else:
        items = run_query("""
            SELECT id_military_unit, military_unit
            FROM Serviceman_Full_Info
            WHERE military_unit IS NOT NULL
            GROUP BY id_military_unit, military_unit
        """)
        sel = st.selectbox("Часть", items['military_unit'].tolist(), key="s6u")
        uid = items[items['military_unit'] == sel]['id_military_unit'].values[0]
        df = run_query(f"""
            SELECT
                ues.equipment_category AS `Категория`,
                ues.model              AS `Модель`,
                ues.quantity           AS `Количество`
            FROM Unit_Equipment_Summary ues
            WHERE ues.id_military_unit = {uid}
              {cond}
            ORDER BY ues.equipment_category
        """)

    st.dataframe(df, use_container_width=True)



# 7. СООРУЖЕНИЯ
def query7_facilities():
    st.subheader("Сооружения")

    sub = st.radio(
        "Вариант:",
        ["Указанной части", "Более 1 подразделения", "Без подразделений"],
        horizontal=True,
        key="r7"
    )

    if sub == "Указанной части":
        items = run_query("""
            SELECT id_military_unit, name
            FROM Military_Unit
            ORDER BY name
        """)
        sel = st.selectbox("Часть", items['name'].tolist(), key="s7u")
        uid = items[items['name'] == sel]['id_military_unit'].values[0]
        df = run_query(f"""
            SELECT
                facility_name AS `Сооружение`,
                facility_type AS `Тип`,
                start_date    AS `Начало`,
                end_date      AS `Конец`
            FROM Unit_Facilities
            WHERE id_military_unit = {uid}
        """)

    elif sub == "Более 1 подразделения":
        df = run_query("""
            SELECT
                f.name                AS `Сооружение`,
                ft.name               AS `Тип`,
                COUNT(su.id_subunit)  AS `Подразделений`
            FROM Facility f
            JOIN Facility_Type ft
                ON f.id_facility_type = ft.id_facility_type
            JOIN Military_Subunit su
                ON f.id_facility = su.id_facility
            GROUP BY f.id_facility, f.name, ft.name
            HAVING COUNT(su.id_subunit) > 1
        """)

    else:
        df = run_query("""
            SELECT
                f.name  AS `Сооружение`,
                ft.name AS `Тип`
            FROM Facility f
            JOIN Facility_Type ft
                ON f.id_facility_type = ft.id_facility_type
            LEFT JOIN Military_Subunit su
                ON f.id_facility = su.id_facility
            WHERE su.id_subunit IS NULL
        """)

    st.dataframe(df, use_container_width=True)



# 8. ЧАСТИ С ТЕХНИКОЙ (фильтр по количеству)
def query8_equipment_filter():
    st.subheader("Части с техникой")

    items = run_query("""
        SELECT
            MIN(e.id_equipment) AS id,
            CONCAT(ec.name, ' — ', e.model) AS name
        FROM Equipment e
        JOIN Equipment_Category ec
            ON e.id_equipment_category = ec.id_equipment_category
        GROUP BY ec.name, e.model
        ORDER BY name
    """)
    sel = st.selectbox("Техника", items['name'].tolist(), key="s8")
    eid = items[items['name'] == sel]['id'].values[0]
    n = st.number_input(
        "Минимальное количество",
        min_value=0,
        value=5,
        step=1,
        key="n8"
    )

    if n == 0:
        df = run_query(f"""
            SELECT
                id_military_unit AS `ID`,
                name             AS `Часть`
            FROM Military_Unit
            WHERE id_military_unit NOT IN (
                SELECT DISTINCT id_military_unit
                FROM Unit_Equipment_Summary
                WHERE id_equipment = {eid}
            )
        """)
        st.caption(f"Части, где отсутствует: {sel}")
    else:
        df = run_query(f"""
            SELECT
                mu.name               AS `Часть`,
                ues.equipment_category AS `Категория`,
                ues.model              AS `Модель`,
                ues.quantity           AS `Количество`
            FROM Unit_Equipment_Summary ues
            JOIN Military_Unit mu
                ON ues.id_military_unit = mu.id_military_unit
            WHERE ues.id_equipment = {eid}
              AND ues.quantity >= {n}
        """)
        st.caption(f"Части, где {sel} >= {n}")

    st.dataframe(df, use_container_width=True)



# 9. ВООРУЖЕНИЕ
def query9_armament():
    st.subheader("Вооружение")

    c1, c2 = st.columns(2)
    with c1:
        cat = st.selectbox(
            "Категория",
            [
                "Все", "Стрелковое", "Ручные гранатомёты",
                "Автоматические гранатомёты", "Артиллерия", "Зенитные ракеты"
            ],
            key="s9c"
        )
    with c2:
        scope = st.selectbox(
            "В составе",
            ["Всего округа", "Армии", "Дивизии", "Корпуса", "Военной части"],
            key="s9s"
        )

    cond = "" if cat == "Все" else f"AND uas.armament_category = '{cat}'"

    if scope == "Всего округа":
        df = run_query(f"""
            SELECT
                uas.id_military_unit   AS `ID части`,
                uas.unit_name          AS `Воинская часть`,
                uas.armament_category  AS `Категория`,
                uas.armament_name      AS `Наименование`,
                uas.quantity           AS `Количество`
            FROM Unit_Armament_Summary uas
            WHERE 1 = 1 {cond}
            ORDER BY uas.unit_name
        """)

    elif scope in ("Армии", "Дивизии", "Корпуса"):
        type_map = {
            "Армии": "Армия",
            "Дивизии": "Дивизия",
            "Корпуса": "Корпус"
        }
        items = run_query(f"""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = '{type_map[scope]}'
        """)
        sel = st.selectbox(type_map[scope], items['name'].tolist(), key=f"s9{scope[0]}")
        like = f"{sel}%" if scope == "Армии" else f"%{sel}%"
        df = run_query(f"""
            SELECT
                uas.id_military_unit   AS `ID части`,
                uas.unit_name          AS `Воинская часть`,
                uas.armament_category  AS `Категория`,
                uas.armament_name      AS `Наименование`,
                uas.quantity           AS `Количество`
            FROM Unit_Armament_Summary uas
            JOIN Subunit_Hierarchy sh
                ON uas.id_military_unit = sh.id_military_unit
            WHERE sh.path LIKE '{like}'
              AND sh.unit_type = 'Часть'
              {cond}
            ORDER BY uas.unit_name
        """)

    else:
        items = run_query("""
            SELECT id_military_unit, military_unit
            FROM Serviceman_Full_Info
            WHERE military_unit IS NOT NULL
            GROUP BY id_military_unit, military_unit
        """)
        sel = st.selectbox("Часть", items['military_unit'].tolist(), key="s9u")
        uid = items[items['military_unit'] == sel]['id_military_unit'].values[0]
        df = run_query(f"""
            SELECT
                uas.armament_category AS `Категория`,
                uas.armament_name     AS `Наименование`,
                uas.quantity          AS `Количество`
            FROM Unit_Armament_Summary uas
            WHERE uas.id_military_unit = {uid}
              {cond}
            ORDER BY uas.armament_category
        """)

    st.dataframe(df, use_container_width=True)



# 10. СПЕЦИАЛЬНОСТИ (фильтр по количеству)
def query10_specialties():
    st.subheader("Специальности")

    c1, c2 = st.columns(2)
    with c1:
        n = st.number_input(
            "Минимальное количество специалистов",
            min_value=0,
            value=5,
            step=1,
            key="n10"
        )
    with c2:
        scope = st.selectbox(
            "В составе",
            ["Всего округа", "Армии", "Дивизии", "Корпуса", "Военной части"],
            key="s10"
        )

    if scope == "Всего округа":
        if n == 0:
            df = run_query("""
                SELECT sp.name AS `Специальность`
                FROM Specialty sp
                LEFT JOIN Specialty_Assignment sa
                    ON sp.id_specialty = sa.id_specialty
                WHERE sa.id_serviceman IS NULL
            """)
            st.caption("Специальности без специалистов")
        else:
            df = run_query(f"""
                SELECT
                    sp.name                 AS `Специальность`,
                    COUNT(sa.id_serviceman) AS `Количество`
                FROM Specialty sp
                JOIN Specialty_Assignment sa
                    ON sp.id_specialty = sa.id_specialty
                GROUP BY sp.id_specialty, sp.name
                HAVING COUNT(sa.id_serviceman) >= {n}
                ORDER BY `Количество` DESC
            """)
            st.caption(f"Специальности с количеством специалистов >= {n}")

    elif scope in ("Армии", "Дивизии", "Корпуса"):
        type_map = {
            "Армии": "Армия",
            "Дивизии": "Дивизия",
            "Корпуса": "Корпус"
        }
        items = run_query(f"""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = '{type_map[scope]}'
        """)
        sel = st.selectbox(type_map[scope], items['name'].tolist(), key=f"s10{scope[0]}")
        like = f"{sel}%" if scope == "Армии" else f"%{sel}%"

        if n == 0:
            df = run_query(f"""
                SELECT sp.name AS `Специальность`
                FROM Specialty sp
                WHERE sp.id_specialty NOT IN (
                    SELECT DISTINCT sa.id_specialty
                    FROM Specialty_Assignment sa
                    JOIN Serviceman_Full_Info sfi
                        ON sa.id_serviceman = sfi.id_serviceman
                    JOIN Subunit_Hierarchy sh
                        ON sfi.id_subunit = sh.id_subunit
                    WHERE sh.path LIKE '{like}'
                )
            """)
        else:
            df = run_query(f"""
                SELECT
                    sp.name                 AS `Специальность`,
                    COUNT(sa.id_serviceman) AS `Количество`
                FROM Specialty sp
                JOIN Specialty_Assignment sa
                    ON sp.id_specialty = sa.id_specialty
                JOIN Serviceman_Full_Info sfi
                    ON sa.id_serviceman = sfi.id_serviceman
                JOIN Subunit_Hierarchy sh
                    ON sfi.id_subunit = sh.id_subunit
                WHERE sh.path LIKE '{like}'
                GROUP BY sp.id_specialty, sp.name
                HAVING COUNT(sa.id_serviceman) >= {n}
                ORDER BY `Количество` DESC
            """)

    else:
        items = run_query("""
            SELECT id_military_unit, military_unit
            FROM Serviceman_Full_Info
            WHERE military_unit IS NOT NULL
            GROUP BY id_military_unit, military_unit
        """)
        sel = st.selectbox("Часть", items['military_unit'].tolist(), key="s10u")
        uid = items[items['military_unit'] == sel]['id_military_unit'].values[0]

        if n == 0:
            df = run_query(f"""
                SELECT sp.name AS `Специальность`
                FROM Specialty sp
                WHERE sp.id_specialty NOT IN (
                    SELECT DISTINCT sa.id_specialty
                    FROM Specialty_Assignment sa
                    JOIN Serviceman_Full_Info sfi
                        ON sa.id_serviceman = sfi.id_serviceman
                    WHERE sfi.id_military_unit = {uid}
                )
            """)
        else:
            df = run_query(f"""
                SELECT
                    sp.name                 AS `Специальность`,
                    COUNT(sa.id_serviceman) AS `Количество`
                FROM Specialty sp
                JOIN Specialty_Assignment sa
                    ON sp.id_specialty = sa.id_specialty
                JOIN Serviceman_Full_Info sfi
                    ON sa.id_serviceman = sfi.id_serviceman
                WHERE sfi.id_military_unit = {uid}
                GROUP BY sp.id_specialty, sp.name
                HAVING COUNT(sa.id_serviceman) >= {n}
                ORDER BY `Количество` DESC
            """)

    st.dataframe(df, use_container_width=True)



# 11. ВОЕННОСЛУЖАЩИЕ ПО СПЕЦИАЛЬНОСТИ
def query11_specialists():
    st.subheader("Военнослужащие указанной специальности")

    c1, c2 = st.columns(2)
    with c1:
        items = run_query("""
            SELECT id_specialty, name
            FROM Specialty
            ORDER BY name
        """)
        spec = st.selectbox("Специальность", items['name'].tolist(), key="s11sp")
        sid = items[items['name'] == spec]['id_specialty'].values[0]
    with c2:
        scope = st.selectbox(
            "В составе",
            [
                "Всего округа", "Армии", "Дивизии", "Корпуса",
                "Военной части", "Подразделения"
            ],
            key="s11s"
        )

    base = f"""
        SELECT
            sfi.full_name     AS `ФИО`,
            sfi.`rank`        AS `Звание`,
            sfi.subunit       AS `Подразделение`,
            sfi.military_unit AS `Часть`
        FROM Serviceman_Full_Info sfi
        JOIN Specialty_Assignment sa
            ON sfi.id_serviceman = sa.id_serviceman
        WHERE sa.id_specialty = {sid}
    """

    if scope == "Всего округа":
        df = run_query(f"{base} ORDER BY sfi.full_name")

    elif scope == "Армии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Армия'
        """)
        sel = st.selectbox("Армия", items['name'].tolist(), key="s11a")
        df = run_query(f"""
            {base}
              AND sfi.id_subunit IN (
                  SELECT sh.id_subunit
                  FROM Subunit_Hierarchy sh
                  WHERE sh.path LIKE '{sel}%'
              )
            ORDER BY sfi.full_name
        """)

    elif scope == "Дивизии":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Дивизия'
        """)
        sel = st.selectbox("Дивизия", items['name'].tolist(), key="s11d")
        df = run_query(f"""
            {base}
              AND sfi.id_subunit IN (
                  SELECT sh.id_subunit
                  FROM Subunit_Hierarchy sh
                  WHERE sh.path LIKE '%{sel}%'
              )
            ORDER BY sfi.full_name
        """)

    elif scope == "Корпуса":
        items = run_query("""
            SELECT name
            FROM Subunit_Hierarchy
            WHERE unit_type = 'Корпус'
        """)
        sel = st.selectbox("Корпус", items['name'].tolist(), key="s11c")
        df = run_query(f"""
            {base}
              AND sfi.id_subunit IN (
                  SELECT sh.id_subunit
                  FROM Subunit_Hierarchy sh
                  WHERE sh.path LIKE '%{sel}%'
              )
            ORDER BY sfi.full_name
        """)

    elif scope == "Военной части":
        items = run_query("""
            SELECT id_military_unit, military_unit
            FROM Serviceman_Full_Info
            WHERE military_unit IS NOT NULL
            GROUP BY id_military_unit, military_unit
        """)
        sel = st.selectbox("Часть", items['military_unit'].tolist(), key="s11u")
        uid = items[items['military_unit'] == sel]['id_military_unit'].values[0]
        df = run_query(f"""
            SELECT
                sfi.full_name AS `ФИО`,
                sfi.`rank`    AS `Звание`,
                sfi.subunit   AS `Подразделение`
            FROM Serviceman_Full_Info sfi
            JOIN Specialty_Assignment sa
                ON sfi.id_serviceman = sa.id_serviceman
            WHERE sa.id_specialty = {sid}
              AND sfi.id_military_unit = {uid}
            ORDER BY sfi.full_name
        """)

    else:
        units = run_query("""
            SELECT id_military_unit, military_unit
            FROM Serviceman_Full_Info
            WHERE military_unit IS NOT NULL
            GROUP BY id_military_unit, military_unit
        """)
        sel_u = st.selectbox("Часть", units['military_unit'].tolist(), key="s11uu")
        uid = units[units['military_unit'] == sel_u]['id_military_unit'].values[0]

        subs = run_query(f"""
            SELECT id_subunit, name
            FROM Subunit_Hierarchy
            WHERE id_military_unit = {uid}
            ORDER BY name
        """)
        if len(subs) > 0:
            sel_s = st.selectbox("Подразделение", subs['name'].tolist(), key="s11sub")
            sub_id = subs[subs['name'] == sel_s]['id_subunit'].values[0]
            df = run_query(f"""
                SELECT
                    sfi.full_name AS `ФИО`,
                    sfi.`rank`    AS `Звание`,
                    sfi.subunit   AS `Подразделение`
                FROM Serviceman_Full_Info sfi
                JOIN Specialty_Assignment sa
                    ON sfi.id_serviceman = sa.id_serviceman
                WHERE sa.id_specialty = {sid}
                  AND sfi.id_subunit = {sub_id}
                ORDER BY sfi.full_name
            """)
        else:
            st.warning("У этой части нет подразделений")
            df = pd.DataFrame()

    st.dataframe(df, use_container_width=True)



# 12. ЧАСТИ С ВООРУЖЕНИЕМ (фильтр по количеству)
def query12_armament_filter():
    st.subheader("Части с вооружением")

    items = run_query("""
        SELECT
            MIN(a.id_armament) AS id,
            CONCAT(ac.name, ' — ', a.name) AS name
        FROM Armament a
        JOIN Armament_Category ac
            ON a.id_armament_category = ac.id_armament_category
        GROUP BY ac.name, a.name
        ORDER BY name
    """)
    sel = st.selectbox("Вооружение", items['name'].tolist(), key="s12")
    aid = items[items['name'] == sel]['id'].values[0]
    n = st.number_input(
        "Минимальное количество",
        min_value=0,
        value=10,
        step=1,
        key="n12"
    )

    if n == 0:
        df = run_query(f"""
            SELECT
                id_military_unit AS `ID`,
                name             AS `Часть`
            FROM Military_Unit
            WHERE id_military_unit NOT IN (
                SELECT DISTINCT id_military_unit
                FROM Unit_Armament_Summary
                WHERE id_armament = {aid}
            )
        """)
        st.caption(f"Части, где отсутствует: {sel}")
    else:
        df = run_query(f"""
            SELECT
                mu.name              AS `Часть`,
                uas.armament_category AS `Категория`,
                uas.armament_name     AS `Наименование`,
                uas.quantity          AS `Количество`
            FROM Unit_Armament_Summary uas
            JOIN Military_Unit mu
                ON uas.id_military_unit = mu.id_military_unit
            WHERE uas.id_armament = {aid}
              AND uas.quantity >= {n}
        """)
        st.caption(f"Части, где {sel} >= {n}")

    st.dataframe(df, use_container_width=True)



# 13. СТАТИСТИКА ПО ЧАСТЯМ
def query13_stats():
    st.subheader("Количество воинских частей")

    c1, c2 = st.columns(2)
    with c1:
        utype = st.selectbox("Тип подразделения", ["Армия", "Дивизия", "Корпус"], key="s13t")
    with c2:
        sub = st.radio("Выбор:", ["Наибольшее", "Наименьшее"], horizontal=True, key="r13")

    order = "DESC" if sub == "Наибольшее" else "ASC"

    df = run_query(f"""
        SELECT
            parent.name         AS `Название`,
            parent.unit_type    AS `Тип`,
            COUNT(DISTINCT child.id_military_unit) AS `Количество частей`
        FROM Subunit_Hierarchy parent
        JOIN Subunit_Hierarchy child
            ON child.path LIKE CONCAT(parent.path, '%')
        WHERE parent.unit_type = '{utype}'
          AND child.id_military_unit IS NOT NULL
        GROUP BY parent.id_subunit, parent.name, parent.unit_type
        ORDER BY `Количество частей` {order}
        LIMIT 1
    """)

    if len(df) > 0:
        label = f"{utype} с {'наибольшим' if sub == 'Наибольшее' else 'наименьшим'} числом частей"
        st.metric(
            label=label,
            value=f"{df['Название'].values[0]} ({df['Количество частей'].values[0]} частей)"
        )

    st.caption("Все для сравнения:")
    all_df = run_query(f"""
        SELECT
            parent.name         AS `Название`,
            parent.unit_type    AS `Тип`,
            COUNT(DISTINCT child.id_military_unit) AS `Количество частей`
        FROM Subunit_Hierarchy parent
        JOIN Subunit_Hierarchy child
            ON child.path LIKE CONCAT(parent.path, '%')
        WHERE parent.unit_type = '{utype}'
          AND child.id_military_unit IS NOT NULL
        GROUP BY parent.id_subunit, parent.name, parent.unit_type
        ORDER BY `Количество частей` DESC
    """)
    st.dataframe(all_df, use_container_width=True)



# 14. ВСЕ ВОЕННОСЛУЖАЩИЕ С КОМАНДИРАМИ
def query14_all_servicemen():
    st.subheader("Все военнослужащие с прямыми командирами")

    df = run_query("""
        SELECT
            s.id_serviceman   AS `ID`,
            s.full_name       AS `Военнослужащий`,
            s.`rank`          AS `Звание`,
            s.subunit         AS `Подразделение`,
            sh.commander_name AS `Прямой командир`
        FROM Serviceman_Full_Info s
        JOIN Subunit_Hierarchy sh
            ON s.id_subunit = sh.id_subunit
        ORDER BY s.id_serviceman
    """)
    st.dataframe(df, use_container_width=True)
