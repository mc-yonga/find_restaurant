from crawler import *

if "admin_district" not in st.session_state.keys():
    with open('admin_district.json', 'r', encoding='utf-8') as file:
        st.session_state["admin_district"] = json.load(file)
        st.session_state["main_state"] = list(st.session_state["admin_district"].keys())

if "main_state_select" not in st.session_state.keys():
    st.session_state["main_state_select"] = None
if "sub_state_select" not in st.session_state.keys():
    st.session_state["sub_state_select"] = None
if "total_restaurant_df" not in st.session_state.keys():
    st.session_state["total_restaurant_df"] = None


if __name__ == '__main__':

    st.set_page_config(layout = "wide")

    main_state_select = st.selectbox('주요 행정구역을 선택하세요', st.session_state.main_state)
    sub_state = st.session_state.admin_district[main_state_select]
    sub_state_select = st.selectbox('자치구, 행정시, 부/군 등을 선택하세요', sub_state)
    search_btn = st.button(':stuffed_flatbread:Search:stuffed_flatbread:')

    if search_btn:
        with st.spinner('구글 데이터를 기반으로 맛집 탐색을 시작합니다.'):
            if main_state_select and sub_state_select:
                st.session_state["main_state_select"] = main_state_select
                st.session_state["sub_state_select"] = sub_state_select
                execute()
            else:
                st.error('지역을 선택하세요')

    if st.session_state["total_restaurant_df"] is not None:
        st.dataframe(st.session_state["total_restaurant_df"])


        type_of_food = st.session_state["total_restaurant_df"]['종류'].unique().tolist()

        st.markdown('---')

        col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
        with col1:
            type_of_food_select = st.multiselect("음식종류를 선택하세요", tuple(type_of_food))

        with col2:
            rating = st.number_input('평점을 입력하세요', value = 4.0)

        with col3:
            review_amount = st.number_input('리뷰수를 입력하세요', value = 1000)

        with col4:
            run_btn = st.button('필터링')

        if run_btn:
            df = st.session_state["total_restaurant_df"]
            df["평점"] = df["평점"].apply(lambda x : float(x))
            df["리뷰수"] = df["리뷰수"].apply(lambda x : float(x))
            cond = (df["종류"].isin(type_of_food_select)) & (df["평점"] >= rating) & (df["리뷰수"] >= review_amount)
            st.dataframe(df[cond])







