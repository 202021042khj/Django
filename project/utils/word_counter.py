import logging
import csv
import os

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 파일 핸들러 추가 (파일에 로그 기록)
file_handler = logging.FileHandler('debug.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def save_word_count(word, count):
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'word_counts.csv')

    # 로깅 사용
    logger.debug(f"File path: {file_path}")
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([word, count])

    # 로깅 사용
    logger.debug(f"Word count for '{word}' saved to {file_path}")
