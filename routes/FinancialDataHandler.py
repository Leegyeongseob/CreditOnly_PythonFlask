import os
import requests
from flask import jsonify, request
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

es = Elasticsearch([os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')])


def IndexAllFinancialData():
    try:
        url = 'http://apis.data.go.kr/1160100/service/GetFnCoBasiInfoService/getFnCoOutl'

        # 요청에서 파라미터 가져오기 (기본값 설정)
        page_no = request.args.get('pageNo', '1')
        rows_per_page = request.args.get('numOfRows', '100')
        base_date = request.args.get('basDt', '20230630')
        company_name = request.args.get('fncoNm', '')

        params = {
            'serviceKey': os.getenv('FINANCIAL_API_KEY_ENCODED'),
            'pageNo': page_no,
            'numOfRows': rows_per_page,
            'resultType': 'json',
            'basDt': base_date
        }

        if company_name:
            params['fncoNm'] = company_name

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        total_count = data.get('response', {}).get('body', {}).get('totalCount', 0)

        if not items:
            return jsonify({"message": "No data found"}), 404

        # Elasticsearch에 데이터 인덱싱
        for item in items:
            es.index(index='financial_company', body=item)

        return jsonify({
            "message": f"Indexed {len(items)} financial company records",
            "total_count": total_count,
            "current_page": page_no,
            "rows_per_page": rows_per_page
        }), 200

    except requests.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500