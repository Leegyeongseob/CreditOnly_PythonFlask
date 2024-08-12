import os
from dotenv import load_dotenv
import logging
from flask import Flask, request, jsonify
from PublicDataReader import Ecos
from elasticsearch import Elasticsearch, helpers
import requests
import pandas as pd

load_dotenv()

# 환경 변수 설정
ElasticsearchUrl = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
EcosApiKey = os.getenv('ECOS_API_KEY', '9M7CN1EZJCG7AJ0FYE3L')

# Elasticsearch 클라이언트 초기화
es = Elasticsearch([ElasticsearchUrl])

# 로깅 설정
logging.basicConfig(level=logging.INFO)
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
    except Exception as e:
        Logger.error(f"Error indexing BOK data: {str(e)}")

def IndexKeyStatistics():
    try:
        # 한국은행 KeyStatisticList API 호출
        url = f"https://ecos.bok.or.kr/api/KeyStatisticList/{EcosApiKey}/json/kr/1/10/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 데이터를 DataFrame으로 변환
        rows = data.get('KeyStatisticList', {}).get('row', [])
        if not rows:
            Logger.warning("No data found from KeyStatisticList API")
            return

        df = pd.DataFrame(rows)

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
    except Exception as e:
        Logger.error(f"Error indexing Key statistics data: {str(e)}")

def CreateIndexIfNotExists(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "mappings": {
                "properties": {
                    "WORD": {
                        "type": "text",
                        "analyzer": "nori_analyzer"
                    },
                    "CONTENT": {
                        "type": "text",
                        "analyzer": "nori_analyzer"
                    }
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "nori_analyzer": {
                            "type": "custom",
                            "tokenizer": "nori_tokenizer"
                        }
                    }
                }
            }
        })
        Logger.info(f"Created index: {index_name}")

def SafeEsBulk(actions):
    try:
        success, failed = helpers.bulk(es, actions, stats_only=True)
        Logger.info(f"Bulk indexing: {success} succeeded, {failed} failed")
    except Exception as e:
        Logger.error(f"Error in Elasticsearch bulk operation: {str(e)}")
        raise

def PreprocessXmlData(xml_data, columns):
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
    IndexBokData()
    return jsonify({"message": "BOK data indexing task started"}), 202

@app.route('/api/elastic/key_statistics', methods=['GET'])
def index_key_statistics():
    IndexKeyStatistics()
    return jsonify({"message": "Key statistics indexing task started"}), 202

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["STAT_NAME", "DATA_VALUE", "UNIT_NAME", "TIME"]
            }
        }
    }
    try:
        response = es.search(index="ecos_key_statistics", body=search_query)
        hits = response['hits']['hits']
        return jsonify([hit['_source'] for hit in hits]), 200
    except Exception as e:
        Logger.error(f"Error during search: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
