# 나라지표 데이터 크롤링

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd

url = 'https://www.index.go.kr/unity/potal/eNara/sub/showStblGams3.do?stts_cd=125701&idx_cd=1257&freq=Y&period=N'

# 웹드라이버 세팅
driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)

#데이터 셀렉터
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
table_list = soup.select("#t_Table_125701 > tbody")
tr_list = table_list[0].find_all('tr')

# 디버깅용 확인
# print(table_list)
# print(tr_list)

data = []
for tr in tr_list:
    cleaned_data = [text.strip().replace("\xa0", " ") for text in tr.text.splitlines() if text.strip()]
    data.append(cleaned_data)

# print(data)

result = []
columns = ["division", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]
result = [dict(zip(columns, row)) for row in data]

print(result)
driver.quit()

import os
import pymysql
import pandas as pd

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
cursor.execute("CREATE DATABASE IF NOT EXISTS vehicle_chart;")
cursor.execute("USE vehicle_chart;")

#데이터 넣기
cursor.execute("""
CREATE TABLE IF NOT EXISTS car_registration_chart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    division VARCHAR(20),  -- 구분
    y_2015 FLOAT,
    y_2016 FLOAT,
    y_2017 FLOAT,
    y_2018 FLOAT,
    y_2019 FLOAT,
    y_2020 FLOAT,
    y_2021 FLOAT,
    y_2022 FLOAT,
    y_2023 FLOAT,
    y_2024 FLOAT);
    """
    )

insert_query = """
    INSERT INTO car_registration_chart
    (division, y_2015, y_2016, y_2017, y_2018, y_2019, y_2020, y_2021, y_2022, y_2023, y_2024)
    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
for row in result:
    division = row['division']
    values = [division]
    # '전년대비 증감비(%)' 행이면 모든 연도 데이터를 float, 아니면 int로 변환
    if division == '전년대비 증감비(%)':
        for year in ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]:
            values.append(float(row[year].replace(',', '')))
    else:
        for year in ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]:
            values.append(int(row[year].replace(',', '')))

    cursor.execute(insert_query, tuple(values))
    conn.commit()

cursor.close()
conn.close()
print("🚀 모든 데이터 삽입 완료!")