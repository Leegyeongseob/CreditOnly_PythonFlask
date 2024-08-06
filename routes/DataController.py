import requests
import re

# 데이터를 수집하는 함수
def collect_data(url):
    try:
        # 주어진 URL에서 데이터를 요청
        response = requests.get(url)
        # 요청이 성공했는지 확인
        response.raise_for_status()
        # JSON 형식으로 데이터를 반환
        return response.json()
    except requests.RequestException as e:
        # 요청 중 오류가 발생하면 오류 메시지를 출력하고 None을 반환
        print(f"Error collecting data: {e}")
        return None

# 데이터를 전처리하는 함수
def preprocess_data(data):
    preprocessed_data = []

    for item in data:
        # 항목에서 'content' 필드를 가져옴
        text = item.get('content', '')

        # 소문자로 변환
        text = text.lower()

        # 특수 문자를 제거 (숫자는 유지)
        text = re.sub(r'[^가-힣a-z0-9\s]', '', text)

        # 여러 개의 공백을 하나로 치환
        text = re.sub(r'\s+', ' ', text).strip()

        # 전처리된 항목을 딕셔너리로 생성
        preprocessed_item = {
            'id': item.get('id'),
            'cleaned_content': text,
            'original_content': item.get('content'),
        }

        # 전처리된 항목을 리스트에 추가
        preprocessed_data.append(preprocessed_item)

    # 전처리된 데이터 리스트를 반환
    return preprocessed_data
