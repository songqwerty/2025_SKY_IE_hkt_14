import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class crawling:
    def __init__(self, email, password, key_word):
        
        self.email = email
        self.password = password
        if isinstance(key_word, (list, tuple)):
            self.key_word = ', '.join(key_word)
        else:
            self.key_word = key_word
        chrome_options = Options()
        chrome_options.add_argument("--disable-popup-blocking")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.results = []
        self.sort = [] 
        self.check_set_me = ['대학 글쓰기 1','대학영어 1','대학영어 2: 말하기','대학영어 2: 글쓰기','고급영어 : 산문','고급영어 : 문화와 사회','고급영어 : 발표','고급영어 : 영화','고급영어 : 연극','고급영어 : 학술작문','고급영어 :  문학']
        self.check_set_ma = ['물리학 1','화학 1','생물학 1', '수학 1', '컴퓨터의 개념 및 실습']
        self.check_credit_me = [2]+10*[3]
        self.check_credit_ma = [3,3,3,2,3]
        self.check_sweet_me = [7.7414,6.3696]+2*[6.3623]+7*[6.2773]; self.check_sweet_ma = [6.0247,6.315,6.3878,8.0,5.6487]
    

    def login(self):
        try:
            self.driver.get("https://www.snulife.com/login")
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            username_input.clear()
            username_input.send_keys(self.email)
            
            password_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="current-password"]'))
            )
            password_input.clear()
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.ENTER)
            
            # 로그인 성공 시 URL이 바뀌는 것을 명시적으로 기다림
            self.wait.until(EC.url_changes("https://www.snulife.com/login"))
            print("로그인 성공")
            return True
        # 3️⃣ 예외 상황을 더 명확하게 처리
        except TimeoutException:
            print("로그인 페이지 요소를 찾지 못했습니다.")
            return False
        except Exception as e:
            print(f"로그인 중 알 수 없는 오류 발생: {e}")
            return False


    def _get_texts_retry(self, by, sel, attempts=3, pause=0.2):
        for _ in range(attempts):
            try:
                elems = self.driver.find_elements(by, sel)
                return [e.text.strip() for e in elems if e.text and e.text.strip()]
            except StaleElementReferenceException:
                time.sleep(pause)
        return []
        
        
    def sorting(self):
        memorize = {'국어국문학과','중어중문학과','영어영문학과','불어불문학과','독어독문학과','노어노문학과','서어서문학과','언어학과','아시아언어문명학부','역사학부','고고미술사학과','종교학과','미학과','식물생산과학부','산림과학부','식품·동물생명공학부','응용생물화학부','조경·지역시스템공학부','바이오시스템·소재학부','지리학과','사회복지학과','스마트시스템과학과'}
        math = {'건설환경공학부','기계공학부','재료공학부','전기·정보공학부','컴퓨터공학부','화학생물공학부','건축학과','산업공학과','에너지자원공학과','원자핵공학과','조선해양공학과','항공우주공학과','수리과학부','통계학과','물리천문학부','화학부','생명과학부','지구환경과학부'}
        logic = {'농경제사회학부','철학과', '정치외교학부','경제학부','사회학과','인류학과','심리학과','언론정보학과'}
    
        category_sets = {
            'memorize': set(memorize),
            'math': set(math),
            'logic': set(logic)
        }
        all_majors = memorize.union(math, logic)
        
        key_words = [word.strip() for word in self.key_word.split(',')]
        final_lists = {'memorize': [], 'math': [], 'logic': [], 'unknown': []}
        
        for word in key_words:
            if word in self.check_set_me:
                final_lists['memorize'].append(word)
            elif word in self.check_set_ma:
                final_lists['math'].append(word)
            else:
                self.driver.get(f"https://www.snulife.com/lecture/search/?keyword={word}&filter=ti")
     
                # 동적으로 변하는 클래스 이름 대신, 고유한 href 속성을 포함하는 a 태그를 기다립니다.
                lecture_block_selector = 'a[href*="/lecture/view/evaluation/"]'
                
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, lecture_block_selector))
                    )
                except TimeoutException:
                    final_lists['unknown'].append(word)
                    continue
        
                while True:
                    try:
                        more_btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='더보기']]"))
                        )
                        self.driver.execute_script("arguments[0].click();", more_btn)
                        time.sleep(0.5)
                    except TimeoutException:
                        break
                
                major_list = []
       
                lecture_blocks = self.driver.find_elements(By.CSS_SELECTOR, lecture_block_selector)
                
                normalized_word = word.replace(" ", "")
        
                for block in lecture_blocks:
                    try:
                        title_element = block.find_element(By.CLASS_NAME, "css-1l86g47")
                        normalized_title = title_element.text.strip().replace(" ", "")
        
                        if normalized_word in normalized_title:
                            info_spans = block.find_elements(By.CSS_SELECTOR, "div.css-149zld span")
                            for span in info_spans:
                                potential_major = span.text.strip()
                                if potential_major in all_majors:
                                    major_list.append(potential_major)
                                    break
                    except NoSuchElementException:
                        continue
        
                dominant_category = 'unknown'
                if major_list:
                    local_counts = {'memorize': 0, 'math': 0, 'logic': 0}
                    for major in major_list:
                        if major in category_sets['memorize']:
                            local_counts['memorize'] += 1
                        elif major in category_sets['math']:
                            local_counts['math'] += 1
                        elif major in category_sets['logic']:
                            local_counts['logic'] += 1
                    
                    if any(count > 0 for count in local_counts.values()):
                        dominant_category = max(local_counts, key=local_counts.get)
        
                final_lists[dominant_category].append(word)
    
        self.sort = [item for category in ['memorize', 'math', 'logic', 'unknown'] for item in final_lists[category]]
        return final_lists


    def subject_credit(self):
        if not self.sort:
            print("먼저 sorting() 메서드를 실행하여 과목을 분류해주세요.")
            return []
            
        credit_sub = []
        for word in self.sort:
            if word in self.check_set_me:
                index_me = self.check_set_me.index(word)
                credit_sub.append(self.check_credit_me[index_me])
            elif word in self.check_set_ma:
                index_ma = self.check_set_ma.index(word)
                credit_sub.append(self.check_credit_ma[index_ma])
            else:
                try:
                    self.driver.get(f"https://www.snulife.com/lecture/search/?keyword={word}&filter=ti")
                    
                    link_xpath = f"//div[contains(@class, 'css-1l86g47') and text()='{word}']/ancestor::a"
                    lecture_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, link_xpath)))
                    
                    self.driver.execute_script("arguments[0].click();", lecture_link)
                    
                    self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[text()='학점']")))
                    
                    xpath_selector = "//div[text()='학점']/following-sibling::div"
                    credit_element = self.driver.find_element(By.XPATH, xpath_selector)
                    credit_number = credit_element.text.strip()
                    credit_sub.append(credit_number)
                
                except TimeoutException:
                    print(f"'{word}' 과목의 학점 정보를 찾는 데 실패했습니다. 리스트에 'N/A'를 추가합니다.")
                    credit_sub.append('N/A') 
                except Exception as e:
                    print(f"'{word}' 과목 처리 중 오류 발생: {e}")
                    credit_sub.append('Error')
        return credit_sub
    
    def crawl_start(self):
        if not self.sort:
            print("오류: sorting() 메서드를 먼저 호출하여 과목을 분류해야 합니다.")
            return []
    
        sweet = []
        print("\n과목별 당도 점수 크롤링을 시작합니다.")
        for word in self.sort:
            print(f"'{word}' 과목 처리 중...")
            if word in self.check_set_me:
                index2_me = self.check_set_me.index(word)
                sweet.append(self.check_sweet_me[index2_me])
            elif word in self.check_set_ma:
                index2_ma = self.check_set_ma.index(word)
                sweet.append(self.check_sweet_ma[index2_ma])
            else:
                self.driver.get(f"https://www.snulife.com/lecture/search/?keyword={word}&filter=ti")
                
                try:
                    self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-1l86g47")))
                except TimeoutException:
                    print(f"'{word}' 과목 검색 결과를 찾을 수 없습니다.")
                    sweet.append(np.nan)
                    continue 
                
                while True:
                    try:
                        more_btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='더보기']]"))
                        )
                        self.driver.execute_script("arguments[0].click();", more_btn)
                        time.sleep(0.5) 
                    except TimeoutException:
                        break
                
                title_elements = self.driver.find_elements(By.CLASS_NAME, "css-1l86g47")
                target_titles = [e for e in title_elements if e.text.strip() == word]
                
                n_list = []
                n2_list = []
    
                for i in range(len(target_titles)):
                    # StaleElementReferenceException 방지를 위해 항상 요소를 새로고침
                    title_elements_refresh = self.driver.find_elements(By.CLASS_NAME, "css-1l86g47")
                    titles_refresh = [e for e in title_elements_refresh if e.text.strip() == word]
                    
                    if i >= len(titles_refresh):
                        break
                
                    anchor = titles_refresh[i]
                    try:
                        # 상세 페이지로 이동
                        self.driver.execute_script("arguments[0].click();", anchor)
                        self.wait.until(EC.staleness_of(anchor))
                    except:
                        continue 
                
                    try:
                        # 1. 강의평 구역(css-9ootue)이 나타날 때까지 기다림
                        self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-9ootue")))
                        
                        # 2. 강의평이 있다면, 당도 점수를 스크래핑
                        texts = self._get_texts_retry(By.CLASS_NAME, "css-9ootue", attempts=3, pause=0.2)
                        sweetness_scores = []
                        for text in texts:
                            if text.startswith("당도"):
                                parts = text.split()
                                for part in parts:
                                    if part.isdigit():
                                        sweetness_scores.append(int(part))
                        if sweetness_scores:
                            n_list.append(np.sum(sweetness_scores))
                            n2_list.append(len(sweetness_scores))
                            
                    except TimeoutException:
                        pass
                        
                    finally:
                        self.driver.back()
                        self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-1l86g47")))
        
                if n_list and n2_list:
                    a = np.sum(n_list)
                    b = np.sum(n2_list)
                    result = np.round(a / b, 4) if b > 0 else np.nan
                else:
                    result = np.nan
                    
                sweet.append(result)
        print(f"'{word}' 과목 당도: {result}")
        
        print("\n모든 과목의 당도 점수 크롤링 완료.")
        return sweet

    def close(self):
        if self.driver:
            self.driver.quit()