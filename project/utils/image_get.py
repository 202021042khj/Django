from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_image_url(search_term):
    
    # WebDriver 설정
    chrome_options = Options()
    service = Service
    driver = webdriver.Chrome()

    image = None

    try:
        search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={search_term}"
        driver.get(search_url)
               
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img')))
        
       
        for _ in range(0):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 

       
        image_elements = driver.find_elements(By.CSS_SELECTOR, 'img')
        if image_elements:
            for image in image_elements[1:]:  
                image = image.get_attribute('src')
                if image and image.startswith('http'): 
                    print(f"이미지 URL: {image}")
                    break  
        else:
            print("이미지를 찾을 수 없습니다.")
    except Exception as e:
        print(f"이미지 추출 오류: {e}")
    finally:
        driver.quit()  

    return image

# 테스트
#image = get_image_url("puppies")
#print(image)
