import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv


# ChromeDriver 경로 설정
chrome_options = Options()
service = Service
driver = webdriver.Chrome()

# 검색어 입력
search_term = ''  # 검색어로 수정
search_url = f'https://www.youtube.com/results?search_query={search_term}'

# CSV 파일 준비
csv_file = open('youtube_comments.csv', mode='w', newline='', encoding='utf-8')
writer = csv.writer(csv_file)
writer.writerow(['Video Title', 'Comment'])  # CSV 파일 헤더 작성

k = 1  # 크롤링할 영상 수

try:
    # YouTube 검색 결과 페이지 열기
    driver.get(search_url)
    time.sleep(5)  # 페이지 로딩 대기

    # 최상단 비디오를 3개 크롤링
    for i in range(k):
        # 비디오 클릭
        video = driver.find_elements(By.XPATH, '//*[@id="video-title"]')[i]
        video_title = video.text
        video.click()
        time.sleep(5)  # 비디오 페이지 로딩 대기

        # 처음 조금 스크롤
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(3)  # 댓글이 로드될 시간을 추가로 기다림

        # 댓글 섹션 스크롤하여 모든 댓글 로드
        scroll_pause_time = 2
        last_height = driver.execute_script("return document.documentElement.scrollHeight")

        while True:
            # 페이지 스크롤
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(scroll_pause_time)

            # 새로운 높이 얻기
            new_height = driver.execute_script("return document.documentElement.scrollHeight")

            # 스크롤이 더 이상 내려가지 않으면 종료
            if new_height == last_height:
                break
            last_height = new_height

        # 댓글 크롤링
        comments = driver.find_elements(By.XPATH, '//*[@id="content-text"]')

        for comment in comments:
            writer.writerow([video_title, comment.text])  # 비디오 제목과 댓글 작성

        # 뒤로가기
        driver.back()
        time.sleep(5)  # 페이지 로딩 대기

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    csv_file.close()  # CSV 파일 닫기
    driver.quit()
    print("댓글이 'youtube_comments.csv' 파일에 저장되었습니다.")
