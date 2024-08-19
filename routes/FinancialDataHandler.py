import requests
from flask import jsonify, request
import logging
from elasticsearch import Elasticsearch, helpers
from env.settings import FinancialApiKeyEncoded, ElasticsearchUrl

Logger = logging.getLogger(__name__)
Es = Elasticsearch([ElasticsearchUrl])

def IndexAllFinancialData():
    try:
        # GET 요청에서 fncoNm 파라미터를 추출
        fncoNm = request.args.get('fncoNm', '')

        # API 요청 URL과 파라미터 설정
        url = 'http://apis.data.go.kr/1160100/service/GetFnCoBasiInfoService/getFnCoOutl'
        params = {
            'serviceKey': FinancialApiKeyEncoded,
            'pageNo': '1',
            'numOfRows': '1000',
            'resultType': 'json',
            'basDt': '20200408',
            'fncoNm': fncoNm
        }

        # 외부 API 호출
        response = requests.get(url, params=params)

        # 로깅 및 상태 코드 확인
        Logger.info(f"Response Status Code: {response.status_code}")
        Logger.info(f"Response Text: {response.text}")

        if response.status_code != 200:
            Logger.error(f"API request failed with status code {response.status_code}")
            return jsonify({"error": f"API request failed with status code {response.status_code}"}), 500

        # JSON 응답 처리
        try:
            response_data = response.json()
        except ValueError as e:
            Logger.error(f"JSON decoding failed: {str(e)}")
            Logger.error(f"Raw response text: {response.text}")
            return jsonify({"error": f"JSON decoding failed: {str(e)}"}), 500

        # 응답에서 필요한 데이터 추출
        items = response_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        if not items:
            Logger.warning("No items found in API response")
            return jsonify({"warning": "No items found in API response"}), 200

        # 데이터 필터링 및 매핑에 맞는 필드 확인
        actions = []
        for item in items:
            # 필요한 데이터 필드만 인덱싱
            doc = {
                "fncoNm": item.get("fncoNm", ""),
                "fncoAddr": item.get("fncoAddr", ""),
                "basDt": item.get("basDt", ""),
                # 추가로 필요한 필드를 여기에 추가하세요.
            }

            # 필수 필드 누락 여부를 확인
            if not doc["fncoNm"] or not doc["basDt"]:
                Logger.warning(f"Skipping document due to missing fields: {doc}")
                continue

            actions.append({
                "_index": "financial_data",
                "_source": doc
            })

        if actions:
            helpers.bulk(Es, actions)
            Logger.info(f"Indexed {len(actions)} documents successfully to financial_data index")
            return jsonify({"message": f"Indexed {len(actions)} documents successfully to financial_data index"}), 200
        else:
            Logger.warning("No valid items to index")
            return jsonify({"warning": "No valid items to index"}), 200

    except requests.RequestException as e:
        Logger.error(f"Request error: {str(e)}")
        return jsonify({"error": f"Request error: {str(e)}"}), 500
    except Exception as e:
        Logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
