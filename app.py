import sys
import os
from flask import Flask
from flask_cors import CORS
import logging

# 현재 디렉토리의 부모 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routes', 'machineLearning'))

from routes.BankOfKoreaHandler import IndexBokData
from routes.DartHandler import IndexDartData
from routes.Scheduler import StartScheduler
from routes.CsvHandler import IndexCsvData
from routes.ExcelHandler import IndexExcelData
from routes.ElasticSearchHandler import GetEcosData, GetDartData
from routes.SimilaritySearchHandler import SimilaritySearch
from routes.FinancialDataHandler import IndexAllFinancialData
from routes.machineLearning.based_on_creditCard import based_on_creditCard_to_json
from routes.machineLearning.based_on_jobs import based_on_jobs_to_json
from routes.machineLearning.based_on_jobs_and_loans import based_on_jobs_and_loans_to_json
from routes.machineLearning.based_on_residence import based_on_residence_to_json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

App = Flask(__name__)

# CORS 설정을 추가하여 모든 도메인에서의 요청을 허용합니다.
CORS(App)

# 경제 관련 데이터
App.add_url_rule('/api/elastic/ecos', 'IndexBokData', IndexBokData, methods=['GET'])
App.add_url_rule('/api/elastic/economic/financial_data', 'IndexAllFinancialData', IndexAllFinancialData, methods=['GET'])

# 기업 관련 데이터
App.add_url_rule('/api/elastic/company/dart', 'IndexDartData', IndexDartData, methods=['POST'])
App.add_url_rule('/api/elastic/company/get_dart', 'GetDartData', GetDartData, methods=['GET'])

# 데이터 유사도 검색
App.add_url_rule('/api/elastic/similarity_search', 'SimilaritySearch', SimilaritySearch, methods=['POST'])

# 데이터 인덱싱
App.add_url_rule('/api/elastic/csv', 'IndexCsvData', IndexCsvData, methods=['GET'])
App.add_url_rule('/api/elastic/excel', 'IndexExcelData', IndexExcelData, methods=['GET'])

# 데이터 시각화
App.add_url_rule('/evaluation/credit_card', 'based_on_creditCard_to_json', based_on_creditCard_to_json, methods=['GET'])
App.add_url_rule('/evaluation/jobs', 'based_on_jobs_to_json', based_on_jobs_to_json, methods=['GET'])
App.add_url_rule('/evaluation/jobs_and_loans', 'based_on_jobs_and_loans_to_json', based_on_jobs_and_loans_to_json, methods=['GET'])
App.add_url_rule('/evaluation/residence', 'based_on_residence_to_json', based_on_residence_to_json, methods=['GET'])

if __name__ == '__main__':
    StartScheduler()
    App.run(port=5000, debug=True)