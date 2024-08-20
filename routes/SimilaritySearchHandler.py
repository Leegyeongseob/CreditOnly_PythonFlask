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

    # Query Elasticsearch
    response = es.search(index=["financial_data", "ecos_statistic_word", "dart_company_info"], body={
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["WORD", "CONTENT", "corp_name", "fncoNm"],
                "fuzziness": "AUTO"
            }
        }
    })

    # Corrected response
    return Response(
        json.dumps(response['hits']['hits'], ensure_ascii=False),
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(port=5000, debug=True)
