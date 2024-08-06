import requests
import re


def collect_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error collecting data: {e}")
        return None


def preprocess_data(data):
    preprocessed_data = []

    for item in data:
        text = item.get('content', '')

        # 소문자 변환
        text = text.lower()

        # 특수 문자 제거 (숫자는 유지)
        text = re.sub(r'[^가-힣a-z0-9\s]', '', text)

        # 여러 개의 공백을 하나로 치환
        text = re.sub(r'\s+', ' ', text).strip()

        preprocessed_item = {
            'id': item.get('id'),
            'cleaned_content': text,
            'original_content': item.get('content'),
        }

        preprocessed_data.append(preprocessed_item)

    return preprocessed_data