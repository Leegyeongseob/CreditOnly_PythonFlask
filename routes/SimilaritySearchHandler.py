from flask import Flask, request, jsonify, Response
from elasticsearch import Elasticsearch
import json

app = Flask(__name__)
es = Elasticsearch("http://localhost:9200")

@app.route('/api/elastic/similarity_search', methods=['POST'])
def similarity_search():
    query_text = request.json.get('query')
    if not query_text:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        # Elasticsearch 검색 쿼리 실행
        response = es.search(index=["financial_data", "ecos_statistic_word", "dart_company_info"], body={
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["WORD", "CONTENT"],
                                "fuzziness": "AUTO"
                            }
                        },
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["corp_name"],
                                "fuzziness": "AUTO"
                            }
                        },
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["fncoNm"],
                                "fuzziness": "AUTO"
                            }
                        }
                    ]
                }
            }
        })

        # 결과 처리
        hits = response['hits']['hits']
        result = [
            {
                "index": hit["_index"],
                "score": hit["_score"],
                "source": hit['_source']
            } for hit in hits
        ]

        return Response(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype='application/json'
        )

    except Exception as e:
        # 일반적인 Exception으로 처리
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)