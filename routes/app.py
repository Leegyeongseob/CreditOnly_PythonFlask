from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
from DataController import collect_data, preprocess_data
import logging
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask 애플리케이션 초기화
app = Flask(__name__)
# Flask 앱에 대해 Cross-Origin Resource Sharing (CORS)을 활성화합니다.
CORS(app)

# Elasticsearch 클라이언트 초기화
es = Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST', 'localhost'),
                     'port': int(os.getenv('ELASTICSEARCH_PORT', 9200))}])

# 백그라운드 작업을 처리하기 위한 스레드 풀 실행자
executor = ThreadPoolExecutor(max_workers=3)

# 데이터 수집 및 색인화를 위한 엔드포인트
@app.route('/collect', methods=['POST'])
def collect_and_index():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL이 필요합니다."}), 400

    try:
        # 비동기적으로 데이터 수집 및 처리
        future = executor.submit(collect_and_process_data, url)
        result = future.result()

        if result is None:
            return jsonify({"error": "데이터 수집 또는 처리에 실패했습니다."}), 400

        logger.info(f"{url}에서 데이터를 성공적으로 수집하고 색인화했습니다.")
        return jsonify({"message": "데이터 수집 및 처리가 시작되었습니다."}), 202
    except Exception as e:
        logger.error(f"collect_and_index에서 오류 발생: {str(e)}")
        return jsonify({"error": "내부 서버 오류"}), 500

# 데이터 수집 및 처리 함수
def collect_and_process_data(url):
    data = collect_data(url)
    if not data:
        return None

    processed_data = preprocess_data(data)

    # 처리된 각 데이터 항목을 색인화합니다.
    for item in processed_data:
        es.index(index='chatbot_data', body=item)

    return True

# 검색을 위한 엔드포인트
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "쿼리 매개변수가 필요합니다."}), 400

    try:
        result = es.search(index='chatbot_data', body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["cleaned_content", "original_content"]
                }
            },
            "highlight": {
                "fields": {
                    "cleaned_content": {},
                    "original_content": {}
                }
            }
        })

        logger.info(f"검색 쿼리 실행됨: {query}")
        return jsonify(result['hits']['hits']), 200
    except Exception as e:
        logger.error(f"검색 중 오류 발생: {str(e)}")
        return jsonify({"error": "내부 서버 오류"}), 500

# 건강 상태 확인을 위한 엔드포인트
@app.route('/health', methods=['GET'])
def health_check():
    if es.ping():
        return jsonify({"status": "건강함", "elasticsearch": "연결됨"}), 200
    else:
        return jsonify({"status": "건강하지 않음", "elasticsearch": "연결되지 않음"}), 503

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True', host='0.0.0.0')
