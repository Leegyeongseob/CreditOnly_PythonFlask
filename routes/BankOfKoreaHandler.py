import os
from dotenv import load_dotenv
import logging
from flask import Flask, request, jsonify
from PublicDataReader import Ecos
from elasticsearch import Elasticsearch, helpers
import requests

load_dotenv()

# 환경 변수 설정
ElasticsearchUrl = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
EcosApiKey = os.getenv('ECOS_API_KEY', '9M7CN1EZJCG7AJ0FYE3L')

# Elasticsearch 클라이언트 초기화
es = Elasticsearch([ElasticsearchUrl])

# 로깅 설정
Logger = logging.getLogger(__name__)

app = Flask(__name__)

def IndexBokData():
    try:
        # PublicDataReader를 사용하여 ECOS 데이터 조회
        api = Ecos(EcosApiKey)
        df = api.get_statistic_word(용어="소비자동향지수")

        # 데이터프레임의 열 이름을 올바르게 설정
        df = df.rename(columns={"용어": "WORD", "용어설명": "CONTENT"})

        # 인덱스 생성 (존재하지 않는 경우)
        index_name = 'ecos_statistic_word'
        CreateIndexIfNotExists(index_name)

        # Elasticsearch에 데이터 인덱싱
        actions = [
            {
                "_index": index_name,
                "_source": row.to_dict()
            }
            for _, row in df.iterrows()
        ]
        SafeEsBulk(actions)

        Logger.info("BOK data indexed successfully")
        return jsonify({"message": "BOK data indexed successfully"}), 200
    except Exception as e:
        Logger.error(f"Error indexing BOK data: {str(e)}")
        return jsonify({"error": str(e)}), 500


def IndexKeyStatistics():
    try:
        # 한국은행 KeyStatisticList API 호출
        url = f"https://ecos.bok.or.kr/api/KeyStatisticList/{EcosApiKey}/xml/kr/1/10/"
        response = requests.get(url)
        response.raise_for_status()
        xml_data = response.content

        # XML 데이터를 Elasticsearch에 인덱싱할 수 있는 구조로 변환
        df = PreprocessXmlData(xml_data, ['STAT_NAME', 'STAT_CODE', 'DATA_VALUE', 'UNIT_NAME', 'TIME'])

        # 인덱스 생성 (존재하지 않는 경우)
        index_name = 'ecos_key_statistics'
        CreateIndexIfNotExists(index_name)

        # Elasticsearch에 데이터 인덱싱
        actions = [
            {
                "_index": index_name,
                "_source": row.to_dict()
            }
            for _, row in df.iterrows()
        ]
        SafeEsBulk(actions)

        Logger.info("Key statistics data indexed successfully")
        return jsonify({"message": "Key statistics data indexed successfully"}), 200
    except Exception as e:
        Logger.error(f"Error indexing Key statistics data: {str(e)}")
        return jsonify({"error": str(e)}), 500

def CreateIndexIfNotExists(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "mappings": {
                "properties": {
                    "WORD": {"type": "text"},
                    "CONTENT": {"type": "text"},
                    "STAT_NAME": {"type": "text"},
                    "STAT_CODE": {"type": "text"},
                    "DATA_VALUE": {"type": "float"},
                    "UNIT_NAME": {"type": "text"},
                    "TIME": {"type": "date"}
                }
            }
        })
        Logger.info(f"Created index: {index_name}")

def SafeEsBulk(actions):
    try:
        helpers.bulk(es, actions)
    except Exception as e:
        Logger.error(f"Error in Elasticsearch bulk operation: {str(e)}")
        raise

def PreprocessXmlData(xml_data, columns):
    # XML 데이터를 DataFrame으로 변환하는 함수
    # XML 데이터를 pandas DataFrame으로 변환하여 반환하는 기능
    # 각 XML 노드의 데이터를 필요한 컬럼에 맞추어 추출하여 DataFrame을 생성합니다.
    import pandas as pd
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_data)
    data = []
    for item in root.findall('.//row'):
        row = {col: item.find(col).text if item.find(col) is not None else None for col in columns}
        data.append(row)
    df = pd.DataFrame(data)
    return df

@app.route('/api/elastic/bok', methods=['GET'])
def index_bok_data():
    return IndexBokData()

@app.route('/api/elastic/key_statistics', methods=['GET'])
def index_key_statistics():
    return IndexKeyStatistics()

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["WORD", "CONTENT", "STAT_NAME"]
            }
        }
    }
    try:
        response = es.search(index="ecos_statistic_word", body=search_query)
        hits = response['hits']['hits']
        return jsonify([hit['_source'] for hit in hits]), 200
    except Exception as e:
        Logger.error(f"Error during search: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
