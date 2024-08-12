import requests
from flask import jsonify, request
import logging
import xml.etree.ElementTree as ET
from env.settings import DartApiKey
from routes.DataProcessor import CreateIndexIfNotExists, SafeEsBulk

Logger = logging.getLogger(__name__)

def IndexDartData():
    try:
        # Content-Type 확인
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 400

        # 요청 데이터에서 고유번호(corp_code), 접수번호(rcept_no), 보고서 코드(reprt_code)를 가져옴
        CorpCode = request.json.get('corp_code')
        if not CorpCode:
            return jsonify({"error": "corp_code is required"}), 400

        RceptNo = request.json.get('rcept_no')
        ReprtCode = request.json.get('reprt_code')

        # 기업개황 API 호출
        CompanyInfoUrl = f'https://opendart.fss.or.kr/api/company.json?crtfc_key={DartApiKey}&corp_code={CorpCode}'
        CompanyResponse = requests.get(CompanyInfoUrl)

        if CompanyResponse.status_code != 200:
            Logger.error(f"Error fetching company info: {CompanyResponse.status_code}")
            return jsonify({"error": f"Failed to fetch company info, status code: {CompanyResponse.status_code}"}), 500

        CompanyData = CompanyResponse.json()
        if CompanyData['status'] != '000':
            Logger.error(f"No data found in response: {CompanyData['message']}")
            return jsonify({"error": f"No data found in response: {CompanyData['message']}"}), 500

        # Elasticsearch에 인덱싱
        CreateIndexIfNotExists('dart_company_info')
        Actions = [
            {
                "_index": "dart_company_info",
                "_source": {
                    "corp_code": CorpCode,
                    "corp_name": CompanyData.get("corp_name"),
                    "corp_name_eng": CompanyData.get("corp_name_eng"),
                    "stock_name": CompanyData.get("stock_name"),
                    "stock_code": CompanyData.get("stock_code"),
                    "ceo_nm": CompanyData.get("ceo_nm"),
                    "corp_cls": CompanyData.get("corp_cls"),
                    "jurir_no": CompanyData.get("jurir_no"),
                    "bizr_no": CompanyData.get("bizr_no"),
                    "adres": CompanyData.get("adres"),
                    "hm_url": CompanyData.get("hm_url"),
                    "ir_url": CompanyData.get("ir_url"),
                    "phn_no": CompanyData.get("phn_no"),
                    "fax_no": CompanyData.get("fax_no"),
                    "induty_code": CompanyData.get("induty_code"),
                    "est_dt": CompanyData.get("est_dt"),
                    "acc_mt": CompanyData.get("acc_mt")
                }
            }
        ]
        SafeEsBulk(Actions)

        Logger.info("DART company info indexed successfully")
        return jsonify({"message": "DART company info indexed successfully"}), 200

    except Exception as e:
        Logger.error(f"Error indexing DART data: {str(e)}")
        return jsonify({"error": str(e)}), 500

def ProcessXbrlFile(XbrlContent):
    try:
        Root = ET.fromstring(XbrlContent)

        # XBRL 파일에서 필요한 데이터 추출 (예: 재무제표)
        FinancialData = []
        for Element in Root.findall('.//YourElementTag'):  # Element tag는 실제 태그 이름으로 바꾸세요
            Data = {
                "field1": Element.find('YourSubElementTag1').text,  # 서브 태그도 실제 태그 이름으로 변경
                "field2": Element.find('YourSubElementTag2').text,
                # 필요한 다른 필드들 추가
            }
            FinancialData.append(Data)

        CreateIndexIfNotExists('dart_financial_data')
        Actions = [
            {
                "_index": "dart_financial_data",
                "_source": Data
            }
            for Data in FinancialData
        ]
        SafeEsBulk(Actions)

        Logger.info("XBRL file processed and data indexed successfully")
        return jsonify({"message": "XBRL file processed and data indexed successfully"}), 200
    except Exception as e:
        Logger.error(f"Error processing XBRL file: {str(e)}")
        raise

