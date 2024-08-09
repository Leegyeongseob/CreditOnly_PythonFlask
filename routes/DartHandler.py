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

        CorpCode = request.json.get('corp_code', '00126380')
        RceptNo = request.json.get('rcept_no', '20190401004781')
        ReprtCode = request.json.get('reprt_code', '11011')

        # 기업개황 API 호출
        CompanyInfoUrl = f'https://opendart.fss.or.kr/api/company.json?crtfc_key={DartApiKey}&corp_code={CorpCode}'
        CompanyResponse = requests.get(CompanyInfoUrl)

        if CompanyResponse.status_code != 200:
            Logger.error(f"Error fetching company info: {CompanyResponse.status_code}")
            return jsonify({"error": f"Failed to fetch company info, status code: {CompanyResponse.status_code}"}), 500

        CompanyData = CompanyResponse.json()
        if CompanyData['status'] != '000':
            Logger.error(f"No data found in response: {CompanyData['message']}")
            return jsonify({"error": "No data found in response"}), 500

        CreateIndexIfNotExists('dart_company_info')
        Actions = [
            {
                "_index": "dart_company_info",
                "_source": CompanyData
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
        for Element in Root.findall('.//YourElementTag'):
            Data = {
                "field1": Element.find('YourSubElementTag1').text,
                "field2": Element.find('YourSubElementTag2').text,
                # 필요한 다른 필드들...
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
    except Exception as e:
        Logger.error(f"Error processing XBRL file: {str(e)}")
        raise
