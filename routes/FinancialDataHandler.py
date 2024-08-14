import requests
from flask import jsonify, request
import logging
from elasticsearch import Elasticsearch, helpers
from env.settings import FinancialApiKeyEncoded, ElasticsearchUrl

Logger = logging.getLogger(__name__)
Es = Elasticsearch([ElasticsearchUrl])

def IndexAllFinancialData():
    try:
        fncoNm = request.args.get('fncoNm', '')
        url = 'http://apis.data.go.kr/1160100/service/GetFnCoBasiInfoService/getFnCoOutl'
        params = {
            'serviceKey': FinancialApiKeyEncoded,
            'pageNo': '1',
            'numOfRows': '1000',
            'resultType': 'json',
            'basDt': '20200408',
            'fncoNm': fncoNm
        }

        response = requests.get(url, params=params)

        Logger.info(f"Response Status Code: {response.status_code}")
        Logger.info(f"Response Text: {response.text}")

        if response.status_code != 200:
            Logger.error(f"API request failed with status code {response.status_code}")
            return jsonify({"error": f"API request failed with status code {response.status_code}"}), 500

        try:
            response_data = response.json()
        except ValueError as e:
            Logger.error(f"JSON decoding failed: {str(e)}")
            return jsonify({"error": f"JSON decoding failed: {str(e)}"}), 500

        items = response_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        if not items:
            Logger.warning("No items found in API response")
            return jsonify({"warning": "No items found in API response"}), 200

        # Elasticsearch에 데이터 인덱싱 - 'financial_data' 인덱스 사용
        actions = [
            {
                "_index": "financial_data",
                "_source": item
            }
            for item in items
        ]
        helpers.bulk(Es, actions)

        Logger.info(f"Financial data indexed successfully to financial_data index")
        return jsonify({"message": "Financial data indexed successfully to financial_data index"}), 200

    except requests.RequestException as e:
        Logger.error(f"Request error: {str(e)}")
        return jsonify({"error": f"Request error: {str(e)}"}), 500
    except Exception as e:
        Logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500