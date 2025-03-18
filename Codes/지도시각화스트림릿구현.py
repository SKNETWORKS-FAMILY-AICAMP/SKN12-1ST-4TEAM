%%writefile streamlit_test.py
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from project1_map import get_shp, sido_map, sgg_map, before_map
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
    st.session_state["update"] = False  # 데이터 갱신 여부

# ---- 사이드바 ----
st.sidebar.title("메뉴")
menu = st.sidebar.radio("이동할 페이지를 선택하세요", ["홈", "등록 현황 조회", "FAQ"])

# ---- 홈 페이지 ----
if menu == "홈":
    st.title("차량 등록 현황 시스템")
    st.write("이 시스템은 연도별 및 지역별 차량 등록 현황을 제공합니다.")

# ---- 등록 현황 조회 ----
elif menu == "등록 현황 조회":
    st.title("등록 현황 조회")

    # 🔹 선택 상자 배치 + 조회 버튼 추가
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 0.5])

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

    with col5:
        if st.button("조회"):  # 조회 버튼 클릭 시 세션 상태 업데이트
            st.session_state["region"] = selected_region
            st.session_state["district"] = selected_district
            st.session_state["year"] = selected_year
            st.session_state["month"] = selected_month
            st.session_state["update"] = True  # 데이터 갱신 여부 설정

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
        before_map(df, selected_year, selected_month, region = selected_region)

#FAQ <- 여기에 채워두기
elif menu == "FAQ":
    st.title("자주 묻는 질문(FAQ)")
    kia, hyundai = st.tabs(['기아','현대'])
    args = {
        'host' : 'localhost',
        'user' : 'root',
        'password' : 'root1234',
        'port' : 3306,
        'database' : 'faq_db'
    }
    with kia:
        st.header("기아")
        #기아 데이터
        def search_faq(keyword):
            conn = mysql.connector.connect(**args)
            cursor = conn.cursor()
            query = """
            SELECT question, answer 
            FROM faq_db.faq_kia
            WHERE question LIKE %s
            """
            like_keyword = f"%{keyword}%"
            cursor.execute(query, ([like_keyword]))
            
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return results


    with hyundai:
        st.header("현대")
        def search_faq(keyword):
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
        
        # Streamlit UI 구성
        def main():
            keyword = st.text_input('검색할 키워드를 입력하세요:', '')
            if keyword:
                st.write(f'검색어: {keyword}')
                # 검색 결과 가져오기
                results = search_faq(keyword)
                if results:
                    st.subheader(f"검색 결과 ({len(results)}개)")
                    for idx, (category,question,answer) in enumerate(results):
                        que = st.expander(f"**{category}** {question}")
                        que.write(f"**답변**: {answer}")
                else:
                    st.write("검색된 결과가 없습니다.")
            else:
                st.write("검색어를 입력하고 'Enter' 키를 눌러 주세요.")
                
    if __name__ == '__main__':
        main()
