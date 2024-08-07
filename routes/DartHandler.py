import requests
import zipfile
import io
from elasticsearch import Elasticsearch
from flask import request, jsonify
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 설정 파일 로드
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))

# Elasticsearch 클라이언트 생성
es = Elasticsearch([config['elasticsearch']['url']])

def index_data():
    try:
        dart_api_key = config['apis']['dart_api_key']
        corp_code = request.json.get('corp_code', '00126380')
        rcept_no = request.json.get('rcept_no', '20190401004781')
        reprt_code = request.json.get('reprt_code', '11011')

        # 회사 개황 정보 수집
        company_info_url = f'https://opendart.fss.or.kr/api/company.json?crtfc_key={dart_api_key}&corp_code={corp_code}'
        company_response = requests.get(company_info_url)
        company_response.raise_for_status()
        company_data = company_response.json()['list']

        # 회사 개황 정보 Elasticsearch 인덱싱
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(es.index, index='dart_company_info', body=company) for company in company_data]
            for future in futures:
                future.result()

        # 재무제표 원본파일(XBRL) 수집
        financial_statements_url = f'https://opendart.fss.or.kr/api/fnlttXbrl.xml?crtfc_key={dart_api_key}&rcept_no={rcept_no}&reprt_code={reprt_code}'
        financial_response = requests.get(financial_statements_url)
        financial_response.raise_for_status()

        # Zip 파일을 메모리에서 읽기
        with zipfile.ZipFile(io.BytesIO(financial_response.content)) as zip_file:
            zip_file.extractall(config['files']['xbrl_directory'])

        logger.info("DART data indexed successfully")
        return jsonify({"message": "DART data indexed successfully"}), 200
    except Exception as e:
        logger.error(f"Error indexing DART data: {str(e)}")
        return jsonify({"error": str(e)}), 500

