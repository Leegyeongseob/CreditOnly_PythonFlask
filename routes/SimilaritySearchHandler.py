import logging
from flask import jsonify, request
from elasticsearch import Elasticsearch
from env.settings import ElasticsearchUrl

# 로깅 설정
Logger = logging.getLogger(__name__)

# Elasticsearch 클라이언트 초기화
es = Elasticsearch([ElasticsearchUrl])

def SimilaritySearch():
    try:
        query_text = request.json.get('query')
        if not query_text:
            return jsonify({"error": "Query parameter is required"}), 400

        index_name = 'ecos_statistic_word'
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["WORD", "CONTENT^2"],  # CONTENT 필드에 가중치 부여
                    "fuzziness": "AUTO",
                    "type": "best_fields"  # 가장 일치하는 필드에 대해 검색 수행
                }
            }
        }
        response = es.search(index=index_name, body=query)
        return jsonify(response['hits']['hits']), 200

    except Exception as e:
        Logger.error(f"Error performing similarity search: {str(e)}")
        return jsonify({"error": str(e)}), 500