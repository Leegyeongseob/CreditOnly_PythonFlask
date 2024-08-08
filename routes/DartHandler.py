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

        CompanyInfoUrl = f'https://opendart.fss.or.kr/api/company.json?crtfc_key={DartApiKey}&corp_code={CorpCode}'
        CompanyResponse = requests.get(CompanyInfoUrl)
        CompanyResponse.raise_for_status()
        CompanyData = CompanyResponse.json()['list']

        CreateIndexIfNotExists('DartCompanyInfo')
        Actions = [
            {
                "_index": "DartCompanyInfo",
                "_source": Company
            }
            for Company in CompanyData
        ]
        SafeEsBulk(Actions)

        FinancialStatementsUrl = f'https://opendart.fss.or.kr/api/fnlttXbrl.xml?crtfc_key={DartApiKey}&rcept_no={RceptNo}&reprt_code={ReprtCode}'
        FinancialResponse = requests.get(FinancialStatementsUrl)
        FinancialResponse.raise_for_status()

        # XBRL 파일 처리 로직 필요
        ProcessXbrlFile(FinancialResponse.content)

        Logger.info("DART data indexed successfully")
        return jsonify({"message": "DART data indexed successfully"}), 200
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

        CreateIndexIfNotExists('DartFinancialData')
        Actions = [
            {
                "_index": "DartFinancialData",
                "_source": Data
            }
            for Data in FinancialData
        ]
        SafeEsBulk(Actions)

        Logger.info("XBRL file processed and data indexed successfully")
    except Exception as e:
        Logger.error(f"Error processing XBRL file: {str(e)}")
        raise
