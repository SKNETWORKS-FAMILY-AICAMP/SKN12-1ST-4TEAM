%%writefile app.py

import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px

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