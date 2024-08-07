import requests
import pandas as pd
from elasticsearch import Elasticsearch
from flask import jsonify
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from DataProcessor import preprocess_xml_data

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
        # 한국은행 API 데이터 수집
        ecos_api_key = config['apis']['ecos_api_key']
        url = f"https://ecos.bok.or.kr/api/StatisticWord/{ecos_api_key}/xml/kr/1/10/소비자동향지수"
        response = requests.get(url)
        response.raise_for_status()
        xml_data = response.content

        # XML 데이터 전처리
        columns = ['STAT_NAME', 'STAT_CODE']
        df_xml = preprocess_xml_data(xml_data, columns)

        # XML 데이터 Elasticsearch 인덱싱
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(es.index, index='ecos_statistic_word', body=row.to_dict()) for _, row in df_xml.iterrows()]
            for future in futures:
                future.result()

        # CSV 파일 데이터 수집
        csv_file_path = config['files']['health_insurance_csv']
        df_csv = pd.read_csv(csv_file_path)

        # CSV 데이터 Elasticsearch 인덱싱
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(es.index, index='health_insurance', body=row.to_dict()) for _, row in df_csv.iterrows()]
            for future in futures:
                future.result()

        logger.info("Data indexed successfully")
        return jsonify({"message": "Data indexed successfully"}), 200
    except Exception as e:
        logger.error(f"Error indexing data: {str(e)}")
        return jsonify({"error": str(e)}), 500
