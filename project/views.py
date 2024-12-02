import csv
import os
import time
import requests
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib import messages
from django.http import JsonResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from .models import Product
from django.conf import settings
from django.http import HttpResponse

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from project.utils.image_get import get_image_url

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        order = self.request.GET.get("order", "like")  # 기본값은 "like"
        view_mode = self.request.GET.get("view", "list")  # 기본값은 "list"
        
        if order == "like":
            return Product.objects.order_by("-like")  # 좋아요 수 내림차순
        elif order == "dislike":
            return Product.objects.order_by("-dislike")  # 싫어요 수 내림차순
        elif order == "alphabetical":
            return Product.objects.order_by("name")  # 이름 기준 오름차순
        else:
            return Product.objects.all()  # 기본적으로 모든 제품 가져오기

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_view'] = self.request.GET.get("view", "list")  # 현재 뷰 모드를 템플릿에 전달
        return context

def product_search(request):
    query = request.GET.get('q', '')  # 검색어를 가져옴
    products = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'project/product_search.html', {'products': products, 'query': query})


def youtube_comment_crawler(request):
    search_term = request.GET.get('q', '')  # URL의 검색어(q) 파라미터를 가져옴
    if not search_term:
        return JsonResponse({'error': '검색어가 제공되지 않았습니다.'})

    # ChromeDriver 경로 설정
    chrome_options = Options()
    service = Service
    driver = webdriver.Chrome()

    # 검색어 입력
    search_url = f'https://www.youtube.com/results?search_query={search_term}'
    csv_file_path = '/Users/khj/github/Django/project/data/youtube_comments.csv'

    # CSV 파일 준비
    csv_file = open(csv_file_path, mode='w', newline='', encoding='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(['Video Title', 'Comment'])  # CSV 파일 헤더 작성

    k = 3 #크롤링할 영상 수

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


    # 1. CSV 파일 로드
    data = pd.read_csv(csv_file_path)
    data.columns = ['video_title', 'comment']

    # 2. NaN 값을 빈 문자열로 대체하고, 카테고리 정의 및 라벨링
    data['comment'] = data['comment'].fillna('')  # NaN 값을 빈 문자열로 대체
    data['label'] = data['comment'].apply(lambda x: 1 if '좋다' in x or '훌륭하다' in x else 0)  # 긍정(1), 부정(0)으로 간단히 구분

    # 3. 텍스트 전처리
    tokenizer = Tokenizer(num_words=10000, oov_token="<OOV>")
    tokenizer.fit_on_texts(data['comment'])
    sequences = tokenizer.texts_to_sequences(data['comment'])
    padded = pad_sequences(sequences, maxlen=100, padding='post', truncating='post')

    # 4. 학습 및 테스트 데이터셋 분리
    X_train, X_test, y_train, y_test = train_test_split(padded, data['label'], test_size=0.2, random_state=42)

    # 5. RNN 모델 구축
    model = Sequential([
        Embedding(10000, 64, input_length=100),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')
    ])

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # 6. 모델 훈련
    history = model.fit(X_train, y_train, epochs=30, validation_data=(X_test, y_test), batch_size=16)

    # 평가 및 결과 출력
    y_pred = (model.predict(X_test) > 0.5).astype("int32")

    # labels=[0, 1]을 추가하여 '부정', '긍정' 두 클래스를 모두 인식하게 합니다.
    print(classification_report(y_test, y_pred, target_names=['부정', '긍정'], labels=[0, 1]))

    # 8. 카테고리 비율 계산
    data['prediction'] = (model.predict(padded) > 0.5).astype("int32")
    positive_comments = data[data['prediction'] == 1]
    negative_comments = data[data['prediction'] == 0]
    pos_ratio = len(positive_comments) / len(data) * 100
    neg_ratio = len(negative_comments) / len(data) * 100

    # 각 카테고리에 대한 비율 계산 및 표시
    categories = ['내구성', '완성도', '디자인', '긍정', '부정']
    category_counts = {category: sum(data['comment'].str.contains(category)) for category in categories}
    total_comments = len(data)
    category_ratios = {category: (count / total_comments) * 100 for category, count in category_counts.items()}

    image = get_image_url(search_term)

    # 수정된 부분: 결과를 products.csv에 저장
    products_csv_path = '/Users/khj/github/Django/project/data/products.csv'
    with open(products_csv_path, mode='a', newline='', encoding='utf-8') as products_csv:
        writer = csv.writer(products_csv)
        # 헤더 추가 (필요하면 조건문으로 처음 실행 시에만 추가하도록 수정 가능)
        writer.writerow(['Search Term', 'Positive Ratio', 'Negative Ratio', 'Category', 'Ratio', 'image'])
        # 데이터 저장
        writer.writerow([search_term, f"{pos_ratio:.2f}%", f"{neg_ratio:.2f}%", '', '', image])
        for category, ratio in category_ratios.items():
            writer.writerow([search_term, '', '', category, f"{ratio:.2f}%"])

    print("결과가 'products.csv' 파일에 저장되었습니다.")

    

    return redirect('product_list')

    




def process_local_csv(request):
    if request.method == "POST":
        # 로컬에 저장된 CSV 파일 경로
        csv_path = '/Users/khj/github/Django/project/data/products.csv' 

        # 파일 존재 여부 확인
        if not os.path.exists(csv_path):
            messages.error(request, "CSV file does not exist.")
            return redirect(request.path)

        # CSV 파일 읽기
        with open(csv_path, mode='r', encoding='utf-8') as file:
            io_string = csv.reader(file)
            
            # 첫 줄이 헤더라면 건너뜀
            next(io_string, None)
            
            for row in io_string:
                try:
                    # CSV 파일의 열 순서가 모델 필드와 일치한다고 가정
                    Product.objects.create(
                        name=row[0],
                        like=int(row[1]),
                        dislike=int(row[2]),
                        keyword=row[3],
                    )
                except Exception as e:
                    messages.error(request, f"Error in row: {row} - {str(e)}")
                    continue

        messages.success(request, "New product data has been processed successfully!")
        return redirect('product_list')

    return render(request, 'upload_local_csv.html')
