#국토교통부 자료 크롤링

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import time
import requests

# 결과 저장 리스트
result = []

url = 'https://stat.molit.go.kr/portal/cate/statView.do?hRsId=58&hFormId=5498&hSelectId=5498&hPoint=00&hAppr=1&hDivEng=&oFileName=&rFileName=&midpath=&sFormId=5498&sStart=201101&sEnd=201101&sStyleNum=2&settingRadio=xlsx'

# 웹드라이버 세팅
driver = webdriver.Chrome()
driver.get(url)
time.sleep(1)

month_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
for years in range(2011,2026):
    for months in month_list:
        if years == 2025 and months == "03" :
            break
        else :
            #검색 연월 세팅
            from_year_month= Select(driver.find_element(By.XPATH, '//*[@id="sStart"]') )
            from_year_month.select_by_value(f'{years}{months}')
            to_year_month = Select(driver.find_element(By.XPATH, '//*[@id="sEnd"]') )
            to_year_month.select_by_value(f'{years}{months}')
            radio_button = driver.find_element(By.XPATH,'//*[@id="main"]/div/div[2]/div[2]/div[3]/div/div[1]/div/button')
            radio_button.click()
            time.sleep(2)

            #데이터 셀렉터
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            div_list = soup.select("#sheet01-table > tbody > tr:nth-child(2) > td:nth-child(1) > div > div.GMPageOne > table > tbody")

            #지역구분 불러오기
            year = years
            month = months
            districts_list = []
            data_values=[]
            # year_month.extend(div_list[0].find_all(class_='GMClassReadOnly GMClassFocusedCell GMWrap0 GMText GMCell IBSheetFont0 HideCol0C1')[0].text.split('-'))
            regions = [item.text for item in div_list[0].find_all(class_='GMClassReadOnly GMWrap0 GMText GMCell IBSheetFont0 HideCol0C2')]
            districts_list = [item.text for item in div_list[0].find_all(class_='GMClassReadOnly GMWrap0 GMText GMCell IBSheetFont0 HideCol0C3')]

            # 디버깅용 상황 프린트
            print(f'{year}{months}Regions count:', len(regions))
            print(f'{year}{months}Districts count:', len(districts_list))

            #실 데이터 불러오기
            div_list = soup.select("#sheet01-table > tbody > tr:nth-child(2) > td:nth-child(2) > div > div.GMPageOne > table > tbody")
            tr_list = div_list[0].find_all('tr', class_='GMDataRow')
            for tr in tr_list:
                td_texts = [td.get_text(strip=True) for td in tr.find_all("td") if td.get_text(strip=True)]
                data_values.append(td_texts)

            # print(year_month)
            # print(regions)
            # print(districts_list)
            # print(data_values)


            # 컬럼 이름 설정
            columns = ["passenger_government", "passenger_private", "passenger_business", "passenger_total",
                       "van_government", "van_private", "van_business", "van_total",
                       "truck_government", "truck_private", "truck_business", "truck_total",
                       "special_government", "special_private", "special_business", "special_total",
                       "total_government", "total_private", " total_business", "total_all"]



            # 지역 및 행정구역 매핑
            region_idx = 0
            current_region = regions[region_idx]
            data_idx = 0

            for i, district in enumerate(districts_list):
                if data_idx >= len(data_values):
                    break

                row_dict = {
                    "record_month": f'{years}-{months}',
                    "region": current_region,
                    "district": district
                }
                row_dict.update(dict(zip(columns, data_values[data_idx])))
                result.append(row_dict)

                data_idx += 1

                # 2018년 10월 이후부터는 "계"가 시도의 마지막에 위치
                if year > 2018 or (year == 2018 and int(month) >= 10):
                    # "계"가 나온 후, 다음 지역으로 변경
                    if district == "계" and region_idx + 1 < len(regions):
                        region_idx += 1
                        current_region = regions[region_idx]
                else:
                    # 기존 방식: "계"가 나와도 바로 지역 변경 X
                    if district == "계":
                        continue

                    # 다음 행이 "계"일 경우, 그 다음 행부터 지역 변경
                    if i + 1 < len(districts_list) and districts_list[i + 1] == "계":
                        if region_idx + 1 < len(regions):
                            region_idx += 1
                            current_region = regions[region_idx]



import pandas as pd
df = pd.DataFrame(result)
df.to_excel("crawled_data.xlsx", index=False, engine="openpyxl")