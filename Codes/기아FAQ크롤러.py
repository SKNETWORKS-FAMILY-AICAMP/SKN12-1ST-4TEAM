from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

url = 'https://www.kia.com/kr/customer-service/center/faq#none'
driver = webdriver.Chrome()
driver.get(url)
time.sleep(1)
total_button = driver.find_element(By.XPATH,'//*[@id="tab-list"]/li[2]/button')
total_button.click()
time.sleep(2)

questions,answers = [],[]
try:
    for i in range(1, 6):
        for j in range(1, 6):
           
            div_lists_url = '#accordion-specification > div'
            html = driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            div_lists =  soup.select(div_lists_url)
            for div in div_lists:
                title = div.find('span', class_= 'cmp-accordion__title')
                questions.append(title.text)
                answer_lists = div.find_all('p')
                temp = []
                for asnwer in answer_lists:
                    temp.append(asnwer.text.replace("\xa0", "").replace("\n",""))

                answers.append(temp)
            if j % 5 == 0:
                if i >=2: 
                    next_button = driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div/div/div[4]/div/button[2]')
                else:
                    next_button = driver.find_element(By.XPATH, '//*[@id="contents"]/div/div[3]/div/div/div[4]/div/button')
                next_button.click()
                time.sleep(1)
            elif i == 5 and j == 3 :
                break
            else : 
                normal_button = driver.find_element(By.XPATH, f'//*[@id="contents"]/div/div[3]/div/div/div[4]/div/ul/li[{j+1}]/a')
                normal_button.click()
                time.sleep(1)

except Exception as e:
    print(f'에러발생 : {e}')
finally: 
    driver.quit()

result = []
for q, a in zip(questions,answers):
    dict_result = {
        'category' :" ",
        'question' : q,
        'answer' : a}
    result.append(dict_result)

print (result)