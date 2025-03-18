# 데이터베이스 업로드

import os
import pymysql
import pandas as pd
from tqdm import tqdm

args = {
  'host' : 'localhost',
  'user' : 'root',
  'password' : 'root1234',
  'port' : 3306,
  }

#MySQL 연결
conn = pymysql.connect(**args)
cursor = conn.cursor()


#데이터베이스 생성
cursor.execute("CREATE DATABASE IF NOT EXISTS vehicle_db;")
cursor.execute("USE vehicle_db;")

#테이블 생성 (없으면 생성)
cursor.execute("""
CREATE TABLE IF NOT EXISTS car_registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_month VARCHAR(7),  -- YYYY-MM 형식 (연월 정보)
    region VARCHAR(50),  -- 시도명
    district VARCHAR(50),  -- 시군구

    -- 승용 (관용, 자가용, 영업용, 합계)
    passenger_government INT,
    passenger_private INT,
    passenger_business INT,
    passenger_total INT,

    -- 승합 (관용, 자가용, 영업용, 합계)
    van_government INT,
    van_private INT,
    van_business INT,
    van_total INT,

    -- 화물 (관용, 자가용, 영업용, 합계)
    truck_government INT,
    truck_private INT,
    truck_business INT,
    truck_total INT,

    -- 특수 (관용, 자가용, 영업용, 합계)
    special_government INT,
    special_private INT,
    special_business INT,
    special_total INT,

    -- 총계 (관용, 자가용, 영업용, 합계)
    total_government INT,
    total_private INT,
    total_business INT,
    total_all INT
);
""")



#특정 폴더 내 모든 엑셀 파일 자동 검색
EXCEL_FOLDER = r"C:\vehicle_db"  # 엑셀 파일이 있는 폴더 경로
excel_files = [os.path.join(EXCEL_FOLDER, f) for f in os.listdir(EXCEL_FOLDER) if f.endswith(".xlsx")]


#데이터 삽입 함수
def insert_data_from_excel(file_path):
    df = pd.read_excel(file_path, sheet_name="Sheet1")  # 첫 번째 시트 읽기
    df.columns = df.columns.str.strip()
    # 📌 숫자 컬럼 변환 (쉼표 제거 후 정수형 변환)
    numeric_columns = df.columns[3:]  # 첫 3개 컬럼(record_month, region, district)은 제외
    for col in numeric_columns:
        df[col] = df[col].astype(str).str.replace(",", "", regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    #INSERT문 제작
    sql_columns = ", ".join([f"`{col}`" for col in df.columns])
    sql_placeholders = ", ".join(["%s"] * len(df.columns))

    sql = f"INSERT INTO car_registration ({sql_columns}) VALUES ({sql_placeholders})"

    #데이터 삽입
    with tqdm(total=len(df), desc=f"📥 Inserting {file_path}") as pbar:
        for _, row in df.iterrows():
            cursor.execute(sql, tuple(row))
            pbar.update(1)  # ✅ tqdm 진행률 업데이트
    conn.commit()
    print(f"✅ {file_path} 데이터 삽입 완료!")


#실행
for file in excel_files:
    insert_data_from_excel(file)

#연결 종료
cursor.close()
conn.close()
print("🚀 모든 데이터 삽입 완료!")
