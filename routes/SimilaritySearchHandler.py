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

        indices = ['ecos_statistic_word', 'dart_company_info', 'financial_data']  # 검색할 인덱스들
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["WORD", "CONTENT^2"],  # 모든 인덱스의 관련 필드를 포함
                    "fuzziness": "AUTO",
                    "type": "best_fields"
                }
            }
        }

        response = es.search(index=",".join(indices), body=query)
        return jsonify(response['hits']['hits']), 200

    except Exception as e:
        Logger.error(f"Error performing similarity search: {str(e)}")
        return jsonify({"error": str(e)}), 500
