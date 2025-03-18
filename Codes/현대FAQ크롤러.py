from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

#Chrome 실행
driver = webdriver.Chrome()
driver.get("https://www.hyundai.com/kr/ko/e/customer/center/faq")
time.sleep(2)

def move_to_first_page(driver):
    """카테고리 이동 후 1페이지 버튼 클릭"""
    try:
        first_page_button_xpath = '//*[@id="app"]/div[3]/section/div[2]/div/div[2]/section/div/div[3]/div[2]/div/ul/li[1]/button'
        first_page_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, first_page_button_xpath))
        )
        driver.execute_script("arguments[0].click();", first_page_button)
        time.sleep(2)  # 페이지 로딩 대기
        print("[페이지 리셋] 첫 페이지로 이동 완료")
    except Exception as e:
        print(f"[경고] 첫 페이지 버튼을 찾을 수 없음: {e}")

def faq_crawling(driver,cate_num):
        #카테고리 버튼 
        category_button_xpath = f'//*[@id="app"]/div[3]/section/div[2]/div/div[2]/section/div/div[1]/div[1]/ul/li[{cate_num}]/button'
        category_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, category_button_xpath)))
        #카테고리 버튼이 보이도록 스크롤 (화면 중앙 정렬)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", category_button)
        time.sleep(1)
    
        #카테고리 버튼 클릭 가능할 때까지 대기 후 클릭
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, category_button_xpath)))
        driver.execute_script("arguments[0].click();", category_button)
        time.sleep(2)

        # 카테고리 이동 후 첫 페이지로 강제 이동
        move_to_first_page(driver)
    
        try:
            category_list = []
            question_list = []
            answer_list = []
            scraped_questions = set() #이미 크롤링한 질문 저장

            page = 1 #현재 페이지

            while True:  # 페이지 끝날 때까지 반복
                print(f"[카테고리 {cate_num}] - {page} 페이지 크롤링 중...")
    
                # 현재 페이지의 HTML 가져오기
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
            
                #페이지 내 질문 목록 가져오기
                div_lists_url = '#app > div.contant-area > section > div.l-container-body > div > div.l-contents-mid > section > div > div:nth-child(3) > div.list-wrap > div'
                div_lists =  soup.select(div_lists_url)

                temp_questions = [] #이번 페이지에서 가져온 질문들
                
                for div in div_lists:
                    category = div.find('span',class_='list-category').text.strip()
                    title = div.find('span', class_= 'list-content').text.strip()

                    temp_questions.append(title)
                    category_list.append(category)
                    question_list.append(title)

                    #이미 크롤링한 질문이면, 중복 판단 -> 크롤링 중단
                    if title in scraped_questions:
                        print(f"[중복 감지] '{title}' 이미 크롤링된 질문 → 마지막 페이지로 판단")
                        return category_list, question_list, answer_list

                if len(temp_questions) == 0:
                    print(f"[카테고리 {cate_num}] 게시물 없음, 다음 카테고리 이동")
                    return category_list, question_list, answer_list

                # 새로 가져온 질문 저장
                scraped_questions.update(temp_questions)
                    
                #답변 버튼 리스트 가져오기
                buttons = driver.find_elements(By.CLASS_NAME, 'list-title')
            
                for button in buttons:        
                    #답변 버튼이 보이도록 스크롤 (화면 중앙 정렬)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(1)
            
                    #답변 버튼 클릭 가능할 때까지 대기 후 클릭
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "list-title")))
                    time.sleep(1)
        
                    # ActionChains로 버튼 강제 클릭
                    actions = ActionChains(driver)
                    actions.move_to_element(button).click().perform()
                    time.sleep(2)
            
                    # 클릭 후 숨겨진 답변 내용 가져오기
                    hidden_content = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'conts')))
                    WebDriverWait(driver, 10).until(lambda driver: hidden_content.is_displayed())
                    time.sleep(1)
                    answer_list.append(hidden_content.text.strip().replace('\n',' '))

                # 페이지네이션 확인 (다음 페이지 버튼)
                try:
                    next_button = driver.find_element(By.CLASS_NAME, "btn-next")
                    if "disabled" in next_button.get_attribute("class"):  # 비활성화 상태면 마지막 페이지
                        print(f"[카테고리 {cate_num}] 마지막 페이지 ({page}) 도달, 다음 카테고리 이동")
                        return category_list, question_list, answer_list
                    else:
                        next_button.click()
                        time.sleep(2)  # 페이지 로딩 대기
                        page += 1
                except:
                    print(f"[카테고리 {cate_num}] 다음 페이지 버튼 없음, 마지막 페이지로 판단")
                    return category_list, question_list, answer_list
        
        except Exception as e:
            print("오류 발생:", e)
            return category_list, question_list, answer_list #예외 발생 시 빈 리스트 반환

        # 결과 출력
        for c,q,a in zip(category_list,question_list,answer_list):
            print(f'카테고리: {c}')
            print(f'질문 : {q}')
            print(f'답변 : {a}')
            print('='*100)
            
        return category_list, question_list, answer_list


#전체 데이터를 담을 리스트
total_categories = []
total_questions = []
total_answers = []

#카테고리 1부터 9까지 반복
for i in range(1,10):
    category_list, question_list, answer_list = faq_crawling(driver, i)
    total_categories.append(category_list)
    total_questions.append(question_list)
    total_answers.append(answer_list)
    print(f'카테고리 {i} 크롤링 완료')
driver.quit()
