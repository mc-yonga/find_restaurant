import json
import streamlit as st

if "admin_district" not in st.session_state.keys():
    with open('admin_district.json', 'r', encoding='utf-8') as file:
        st.session_state["admin_district"] = json.load(file)
        st.session_state["main_state"] = list(st.session_state["admin_district"].keys())


main_state_select = st.selectbox('주요 행정구역을 선택하세요', st.session_state.main_state)

if main_state_select:
    sub_state = st.session_state.admin_district[main_state_select]
    main_state_select = st.multiselect('자치구, 행정시, 부/군 등을 선택하세요', sub_state)

search_btn = st.button(':stuffed_flatbread:Search:stuffed_flatbread:')







