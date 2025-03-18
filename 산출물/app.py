import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from project1_map import get_shp, sido_map, sgg_map, before_map
import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px
# ---- 기본 설정 ----
st.set_page_config(page_title="등록 현황 대시보드", layout="wide")

@st.cache_data  # 데이터 캐싱
def get_data():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root1234',
        database='vehicle_db1',
        port=3306
    )
    query = "SELECT * FROM vehicle_db1.car_registration"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 초기 데이터 로드
df = get_data()

# ---- 세션 상태 초기화 ----
if "region" not in st.session_state:
    st.session_state["region"] = "-"
if "district" not in st.session_state:
    st.session_state["district"] = "-"
if "year" not in st.session_state:
    st.session_state["year"] = "-"
if "month" not in st.session_state:
    st.session_state["month"] = "-"
if "update" not in st.session_state:
    st.session_state["update"] = True  # 데이터 갱신 여부

# ---- 사이드바 ----
#st.sidebar.title("메뉴")
#menu = st.sidebar("이동할 페이지를 선택하세요", ["홈", "등록 현황 조회", "FAQ"])
if 'menu' not in st.session_state:
    st.session_state.menu = "홈"

st.sidebar.markdown("""
    <style>
    .sidebar-button {
        width: 200px;  /* 버튼 길이를 설정 */
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---- 사이드바 ----
if st.sidebar.button("🏠 홈", use_container_width=True):
    st.session_state.menu = "홈"
if st.sidebar.button("등록 현황 조회", use_container_width=True):
    st.session_state.menu = "등록 현황 조회"
if st.sidebar.button("❓FAQ", use_container_width=True):
    st.session_state.menu = "FAQ"

# ---- 홈 페이지 ----
if st.session_state.menu == "홈":
    # ✅ Streamlit의 기본 스타일 덮어쓰기 (크기 조정)
    st.markdown("""
        <style>
            h1 {
                text-align: center;
                font-size: 30px !important;  /* 타이틀 크기 조정 */
                font-weight: bold;
            }
            h2 {
                text-align: center;
                font-size: 20px !important;  /* 서브헤더 크기 조정 */
                font-weight: bold;
            }
            .source {
                text-align: right;
                font-size: 16px;
            }
        </style>
    """, unsafe_allow_html=True)

    # MySQL 연결 정보
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "root1234",
        "database": "vehicle_chart",
        "port": 3306
    }

    # ✅ 데이터베이스에서 데이터 가져오기
    def fetch_data():
        conn = pymysql.connect(**DB_CONFIG)
        query = """
            SELECT division, y_2015, y_2016, y_2017, y_2018, y_2019, 
                   y_2020, y_2021, y_2022, y_2023, y_2024 
            FROM car_registration_chart;
        """
        df = pd.read_sql(query, conn)
        conn.close()

        # 📌 컬럼명을 한글로 변경
        df.rename(columns={
            "division": "구분",
            "y_2015": "2015년", "y_2016": "2016년", "y_2017": "2017년", 
            "y_2018": "2018년", "y_2019": "2019년", "y_2020": "2020년", 
            "y_2021": "2021년", "y_2022": "2022년", "y_2023": "2023년", "y_2024": "2024년"
        }, inplace=True)

        return df

    # ✅ 타이틀 및 서브헤더 적용
    st.title("📊 차량 등록 현황 대시보드")
    st.subheader("MySQL 데이터를 기반으로 차량 등록 정보를 시각화합니다.")

    # ✅ 자료 출처 (우측 정렬 + 하이퍼링크 적용)
    st.markdown("""
        <p class="source">자료 출처 : 
        <a href="https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1257" target="_blank">
        e-나라지표</a></p>
    """, unsafe_allow_html=True)

    # ✅ 데이터 불러오기
    df = fetch_data()

    # ✅ 인덱스 제거 후 데이터 출력
    st.subheader("📋 차량 등록 현황 데이터")
    st.dataframe(df.set_index("구분"))  # ✅ 인덱스 제거하여 구분을 첫 번째 열로 설정

    # ✅ 구분선 추가
    st.markdown("---")

    # ✅ 데이터 변환 (연도별 데이터 피벗)
    df_melted = df.melt(id_vars=["구분"], var_name="연도", value_name="값")

    # 📌 연도별 차량 등록 현황 & 전년대비 증가대수 (Grouped Bar Chart)
    st.subheader("📊 연도별 차량 등록 현황 & 전년대비 증가대수")
    df_bar = df_melted[df_melted["구분"].isin(["등록대수(만대)", "전년대비 증가대수(천대)"])]
    fig_bar = px.bar(df_bar, x="연도", y="값", color="구분", 
                     title="📌 등록대수 & 전년대비 증가대수 변화",
                     barmode="group",  # ✅ 그룹형 바 차트 (겹쳐서 표시)
                     text_auto=True,  # ✅ 숫자 표시 추가
                     color_discrete_map={"등록대수(만대)": "#1f77b4", "전년대비 증가대수(천대)": "#FF69B4"})

    # ✅ 범례를 차트 아래로 이동
    fig_bar.update_layout(legend=dict(orientation="h", y=-0.2))

    st.plotly_chart(fig_bar)

    # ✅ 구분선 추가
    st.markdown("---")

    # 📌 전년대비 증감비(%) (꺾은선 그래프 + 수치 표시)
    st.subheader("📈 전년대비 증감비(%)")
    df_rate = df_melted[df_melted["구분"] == "전년대비 증감비(%)"]

    fig_line = px.line(df_rate, x="연도", y="값", markers=True, text=df_rate["값"],  
                       title="📌 전년대비 증감비 변화")

    # ✅ 숫자 표시 위치 조정
    fig_line.update_traces(textposition="top center")

    # ✅ 범례를 차트 아래로 이동
    fig_line.update_layout(legend=dict(orientation="h", y=-0.2))

    st.plotly_chart(fig_line)

    # ✅ 구분선 추가
    st.markdown("---")

# ---- 등록 현황 조회 ----
elif st.session_state.menu == "등록 현황 조회":
    st.title("등록 현황 조회")

    # 🔹 선택 상자 배치 + 조회 버튼 추가
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

    with col1:
        selected_region = st.selectbox("지역(시/도) 선택", ["-"] + list(df["region"].unique()), index=0)

    with col2:
        district_options = ["-"]
        if selected_region != "-":
            district_options += list(df[df["region"] == selected_region]["district"].unique())
        selected_district = st.selectbox("구/군 선택", district_options, index=0)

    with col3:
        selected_year = st.selectbox("연도 선택", ["-"] + sorted(df["record_month"].str[:4].unique()), index=0)

    with col4:
        month_options = ["-"] + sorted(df["record_month"].str[5:7].unique())
        selected_month = st.selectbox("월 선택", month_options, index=0)

    #############################################3
    with col5:
        type_options = ["전체", "승용차", "승합차", "화물차", "특수차"]
        selected_type = st.selectbox("차종 선택", type_options, index=0)
        dic = {
                '승용차' : 'passenger',
                '승합차' : 'van',
                '화물차' : 'truck',
                '특수차' : 'special',
                '전체' : 'all'}
        selected_type = dic[selected_type]
    #############################################33

    with col6:
        if st.button("조회"):  # 조회 버튼 클릭 시 세션 상태 업데이트
            st.session_state["region"] = selected_region
            st.session_state["district"] = selected_district
            st.session_state["year"] = selected_year
            st.session_state["month"] = selected_month
            st.session_state["update"] = True  # 데이터 갱신 여부 설정

    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;  /* 버튼을 화면 너비에 맞게 설정 */
        height: 3rem;  /* 버튼의 높이를 설정 */
        display: flex;
        align-items: center;  /* 버튼을 수직 가운데 정렬 */
        justify-content: center;  /* 버튼을 수평 가운데 정렬 */
    }

    .stSelectbox select {
        height: 3rem;  /* selectbox의 높이를 버튼과 맞춤 */
        padding: 0 10px;  /* selectbox의 패딩 설정 */
    }
    </style>
    """, unsafe_allow_html=True)

    # 🔹 조회 버튼을 누른 후 데이터 업데이트
    if st.session_state["update"]:
        region = st.session_state["region"]
        district = st.session_state["district"]
        year = st.session_state["year"]
        month = st.session_state["month"]

        # 🔹 필터링 적용 (표에 사용할 데이터)
        filtered_df = df.copy()
        if region != "-":
            filtered_df = filtered_df[filtered_df["region"] == region]
        if district != "-":
            filtered_df = filtered_df[filtered_df["district"] == district]
        if year != "-":
            filtered_df = filtered_df[filtered_df["record_month"].str.startswith(year)]
        if month != "-":
            filtered_df = filtered_df[filtered_df["record_month"] == f"{year}-{month}"]

        ################################################################################################
        # filtered_df = filtered_df.filter(like="selecte_type")
        ###########################################################################################

        # 🔹 필터링된 데이터 표시
        st.subheader("📋 필터링된 데이터")
        st.dataframe(
            filtered_df.loc[:, filtered_df.columns != "id"],  # id 컬럼 숨기기
            hide_index=True
        )

        # 🔹 차트용 데이터 (요약 데이터)
        summary_df = filtered_df.copy()

        group_by_col = "region"
        if region != "-":
            group_by_col = "district"
        if district != "-":
            group_by_col = None

        if group_by_col:
            summary_df = summary_df.groupby(group_by_col).sum()

        # 🔹 차량별 비율(%) 계산
        summary_df["승용차(K)"] = summary_df["passenger_total"] / 1000
        summary_df["승합차(K)"] = summary_df["van_total"] / 1000
        summary_df["화물차(K)"] = summary_df["truck_total"] / 1000
        summary_df["특수차(K)"] = summary_df["special_total"] / 1000

        # 🔹 차트 또는 개별 데이터 출력
        if not summary_df.empty:
            if group_by_col:
                fig_count = px.bar(
                    summary_df.reset_index(),
                    x=group_by_col,
                    y=["승용차(K)", "승합차(K)", "화물차(K)", "특수차(K)"],
                    title="차량 등록 대수 (천 단위 K)",
                    labels={"x": "지역", "y": "등록 대수 (K)"},
                    text_auto=".1f",
                    barmode="stack",
                    color_discrete_map={"승용차(K)": "blue", "승합차(K)": "green", "화물차(K)": "red", "특수차(K)": "purple"}
                )
                st.subheader("📊 차량 유형 대수 차트")
                st.plotly_chart(fig_count, use_container_width=True)
            else:  #특정 구 선택 시 해당 지역의 차량 대수 차트 출력
                st.subheader(f"📌 {year if year != '-' else '전체'}-{month if month != '-' else '전체'} {region} {district} 차량 등록 대수")

                #시군구 선택 시 차량 대수 차트 (세로 바 차트)
                melted_df = summary_df.reset_index().melt(id_vars=["district"], 
                                        value_vars=["승용차(K)", "승합차(K)", "화물차(K)", "특수차(K)"], 
                                        var_name="차량 유형", value_name="대수(K)")
                fig_district = px.bar(
                    melted_df,
                    x="차량 유형",
                    y="대수(K)",
                    text_auto=".1f",
                    title="차량 등록 대수 (천 단위 K)",
                    labels={"대수(K)": "등록 대수 (K)"},
                    color="차량 유형",
                    color_discrete_map={"승용차(K)": "blue", "승합차(K)": "green", "화물차(K)": "red", "특수차(K)": "purple"}
                )
                st.plotly_chart(fig_district, use_container_width=True)
        else:
            st.warning("❌ 선택한 조건에 해당하는 데이터가 없습니다.")

        st.subheader("📋 자동차 등록대수 시각화")
        #st.write(selected_year, selected_month, selected_region)
        before_map(df, selected_year, selected_month, selected_region, selected_type)



elif st.session_state.menu == "FAQ":
    st.title("자주 묻는 질문(FAQ)")
    args = {
            'host' : 'localhost',
            'user' : 'root',
            'password' : 'root1234',
            'port' : 3306,
            'database' : 'faq_db'
        }



    # 🔥 탭 생성
    #tabs = st.tabs(["기아", "현대"])

    # 🔥 기아 FAQ 검색 함수
    def search_faq_kia(keyword):
        conn = mysql.connector.connect(**args)
        cursor = conn.cursor()
        query = """
        SELECT category, question, answer 
        FROM faq_kia
        WHERE question LIKE %s
        """
        like_keyword = f"%{keyword}%"
        cursor.execute(query, ([like_keyword]))

        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    # 🔥 현대 FAQ 검색 함수
    def search_faq_hyundai(keyword):
        conn = mysql.connector.connect(**args)
        cursor = conn.cursor()
        query = """
        SELECT category, question, answer 
        FROM faq_hyundai
        WHERE question LIKE %s
        """
        like_keyword = f"%{keyword}%"
        cursor.execute(query, ([like_keyword]))

        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    # 초기 세션 상태 설정
    if "selected_tab" not in st.session_state:
        st.session_state["selected_tab"] = "기아"  # 기본값 설정

    # 버튼을 사용하여 탭처럼 동작하게 만듦
    col1, col2 = st.columns(2)  # 버튼을 두 개의 열로 나누기

    with col1:
        if st.button("🚗 기아"):
            st.session_state["selected_tab"] = "기아"

    with col2:
        if st.button("🚙 현대"):
            st.session_state["selected_tab"] = "현대"
    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;  /* 버튼을 화면 너비에 맞게 설정 */
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    # 선택된 탭에 맞는 내용 출력
    if st.session_state["selected_tab"] == "기아":
        st.header("🚗 기아")
        # 기아 관련 내용을 이곳에 추가합니다.
        st.write("기아 차량에 관한 정보를 이곳에 작성합니다.")

    elif st.session_state["selected_tab"] == "현대":
        st.header("🚙 현대")
        # 현대 관련 내용을 이곳에 추가합니다.
        st.write("현대 차량에 관한 정보를 이곳에 작성합니다.")

    # 🔥 검색 UI 및 검색 실행
    keyword = st.text_input('검색할 키워드를 입력하세요:', '')

    if keyword:
        st.write(f'검색어: {keyword}')

        # 🔥 현재 선택된 브랜드에 맞는 검색 실행
        if st.session_state["selected_tab"] == "기아":
            results = search_faq_kia(keyword)

            # 🔥 검색 결과 출력
            if results:
                st.subheader(f"검색 결과 ({len(results)}개)")
                for idx, (category, question, answer) in enumerate(results):
                    que = st.expander(f"{question}")
                    que.write(f"답변: {answer}")
            else:
                st.write("검색된 결과가 없습니다.")

        elif st.session_state["selected_tab"] == "현대":
            results = search_faq_hyundai(keyword)

            # 🔥 검색 결과 출력
            if results:
                st.subheader(f"검색 결과 ({len(results)}개)")
                for idx, (category, question, answer) in enumerate(results):
                    que = st.expander(f"**{category}** {question}")
                    que.write(f"답변: {answer}")
            else:
                st.write("검색된 결과가 없습니다.")



    else:
        st.write("검색어를 입력하고 'Enter' 키를 눌러 주세요.")

    # 🔍 현재 선택된 탭 디버깅용
