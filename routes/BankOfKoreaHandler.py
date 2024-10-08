import os
from dotenv import load_dotenv
import logging
from PublicDataReader import Ecos
from elasticsearch import Elasticsearch, helpers
import pandas as pd

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 환경 변수를 설정합니다. 기본값도 제공합니다.
ElasticsearchUrl = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
EcosApiKey = os.getenv('ECOS_API_KEY', '9M7CN1EZJCG7AJ0FYE3L')

# Elasticsearch 클라이언트를 초기화합니다.
es = Elasticsearch([ElasticsearchUrl])

# 로깅을 설정합니다.
logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger(__name__)


def IndexBokData(keyword):
    try:
        Logger.info(f"Starting IndexBokData with keyword: {keyword}")

        # PublicDataReader를 사용하여 ECOS 데이터를 조회합니다.
        api = Ecos(EcosApiKey)
        Logger.info(f"ECOS API Key: {EcosApiKey}")  # API 키 확인 (주의: 실제 운영 환경에서는 로그에 API 키를 출력하지 마세요)

        df = api.get_statistic_word(용어=keyword)
        Logger.info(f"API response: {df}")

        if df is None or df.empty:
            Logger.warning(f"No data found for keyword: {keyword}")
            return {"error": "No data found for the given keyword"}, 404

        # 데이터프레임의 열 이름을 영어로 변경합니다.
        df = df.rename(columns={"용어": "WORD", "용어설명": "CONTENT"})
        Logger.info(f"Renamed columns: {df.columns}")

        # 인덱스 이름을 정의합니다.
        index_name = 'ecos_statistic_word'
        # 인덱스가 없다면 생성합니다.
        CreateIndexIfNotExists(index_name)

        # Elasticsearch에 데이터를 인덱싱하기 위한 액션을 생성합니다.
        actions = [
            {
                "_index": index_name,
                "_source": row.to_dict()
            }
            for _, row in df.iterrows()
        ]
        Logger.info(f"Created {len(actions)} actions for indexing")

        # 벌크 인덱싱을 수행합니다.
        SafeEsBulk(actions)

        Logger.info(f"{keyword} data indexed successfully")
        return {"message": f"{keyword} data indexed successfully"}, 200
    except Exception as e:
        Logger.error(f"Error indexing {keyword} data: {str(e)}")
        return {"error": str(e)}, 500

def CreateIndexIfNotExists(index_name):
    # 인덱스가 존재하지 않는 경우에만 생성합니다.
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
        # Elasticsearch에 벌크 연산을 수행합니다.
        success, failed = helpers.bulk(es, actions, stats_only=True)
        Logger.info(f"Bulk indexing: {success} succeeded, {failed} failed")
    except Exception as e:
        Logger.error(f"Error in Elasticsearch bulk operation: {str(e)}")
        raise