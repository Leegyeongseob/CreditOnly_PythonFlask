import io
import logging
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser

import pandas as pd
import requests
from elasticsearch import Elasticsearch
from flask import Flask, request, jsonify

# Flask 애플리케이션 생성
app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 설정 파일 로드
config = ConfigParser()
config.read('config.ini')

# Elasticsearch 클라이언트 생성
es = Elasticsearch([config['elasticsearch']['url']])

def preprocess_xml_data(xml_data, columns):
    """
    수집된 XML 데이터를 전처리하는 함수

    :param xml_data: XML 데이터
    :param columns: 추출할 컬럼 리스트
    :return: 전처리된 데이터 (DataFrame 형식)
    """
    root = ET.fromstring(xml_data)
    data = []
    for item in root.findall('.//row'):
        row = {col: item.find(col).text if item.find(col) is not None else None for col in columns}
        data.append(row)
    df = pd.DataFrame(data)
    df.dropna(inplace=True)
    return df

@app.route('/index_data', methods=['POST'])
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

@app.route('/index_dart', methods=['POST'])
def index_dart():
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

@app.route('/search', methods=['GET'])
def search():
    try:
        query = request.args.get('q')
        index = request.args.get('index', 'ecos_statistic_word')
        result = es.search(index=index, body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["*"]
                }
            }
        })
        return jsonify(result['hits']['hits'])
    except Exception as e:
        logger.error(f"Error searching data: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
