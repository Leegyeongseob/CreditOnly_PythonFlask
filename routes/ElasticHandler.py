from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

class ElasticHandler:
    def __init__(self):
        # Elasticsearch 클라이언트를 초기화합니다.
        self.es = Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST'), 'port': os.getenv('ELASTICSEARCH_PORT')}])

    def index_data(self, index_name, doc_type, doc_id, body):
        """
        데이터를 Elasticsearch에 색인하는 메서드입니다.

        :param index_name: 색인 이름
        :param doc_type: 문서 유형
        :param doc_id: 문서 ID
        :param body: 문서 내용 (데이터)
        :return: Elasticsearch 색인 결과
        """
        return self.es.index(index=index_name, doc_type=doc_type, id=doc_id, body=body)

    def search(self, index_name, query):
        """
        Elasticsearch에서 검색을 수행하는 메서드입니다.

        :param index_name: 색인 이름
        :param query: 검색 쿼리
        :return: 검색 결과
        """
        return self.es.search(index=index_name, body=query)
