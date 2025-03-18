import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector 

#mysql과 연결
args = {
  'host' : 'localhost',
  'user' : 'root',
  'password' : 'Jmlee0507!',
  'port' : 3306,
  'database' : 'faq_db'
}
conn = mysql.connector.connect(**args)
cursor = conn.cursor() 

#기본 설정
st.set_page_config(page_title="등록 현황 대시보드", layout="wide")

#사이드 바
st.sidebar.title("📌 메뉴")
menu = st.sidebar.radio("이동할 페이지 선택", ["홈", "등록 현황 조회", "FAQ"])


#홈페이지
if menu == "홈":
    st.title("🚗 차량 등록 현황 시스템")
    st.write("연도별 및 지역별 차량 등록 현황 제공.")
    col1, col2 = st.columns(2)

    
#등록 현황 조회
elif menu == "등록 현황 조회":
    st.title("등록 현황 조회")
    col1, col2 = st.columns(2)
    

#FAQ <- 여기에 채워두기
elif menu == "FAQ":
    st.title("자주 묻는 질문(FAQ)")
    kia, hyundai = st.tabs(['기아','현대'])
    with kia:
        st.header("기아")
        #기아 데이터

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