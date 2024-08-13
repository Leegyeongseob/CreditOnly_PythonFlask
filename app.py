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
from routes.FinancialDataHandler import IndexAllFinancialData  # 금융회사 데이터 핸들러 추가
from routes.machineLearning.based_on_creditCard import based_on_creditCard_to_json #신용카드 개설에 따른 신용등급(시각화)
from routes.machineLearning.based_on_jobs import based_on_jobs_to_json # 나와 같은 직업군의 신용등급(시각화)
from routes.machineLearning.based_on_jobs_and_loans import based_on_jobs_and_loans_to_json #대출에 따른 신용등급(시각화)
from routes.machineLearning.based_on_residence import based_on_residence_to_json #거주지역에 따른 신용등급(시각화)




logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

App = Flask(__name__)

# CORS 설정을 추가하여 모든 도메인에서의 요청을 허용합니다.
CORS(App)

App.add_url_rule('/api/elastic/bok', 'IndexBokData', IndexBokData, methods=['GET'])
App.add_url_rule('/api/elastic/dart', 'IndexDartData', IndexDartData, methods=['POST'])
App.add_url_rule('/api/elastic/csv', 'IndexCsvData', IndexCsvData, methods=['GET'])
App.add_url_rule('/api/elastic/excel', 'IndexExcelData', IndexExcelData, methods=['GET'])
App.add_url_rule('/api/elastic/get_ecos', 'GetEcosData', GetEcosData, methods=['GET'])
App.add_url_rule('/api/elastic/get_dart', 'GetDartData', GetDartData, methods=['GET'])
App.add_url_rule('/api/elastic/similarity_search', 'SimilaritySearch', SimilaritySearch, methods=['POST'])
App.add_url_rule('/api/elastic/financial_company', 'IndexAllFinancialData', IndexAllFinancialData, methods=['GET'])

# 각각의 데이터 시각화 관련 핸들러에 고유한 URL을 설정합니다.
App.add_url_rule('/evaluation/credit_card', 'based_on_creditCard_to_json', based_on_creditCard_to_json, methods=['GET'])
App.add_url_rule('/evaluation/jobs', 'based_on_jobs_to_json', based_on_jobs_to_json, methods=['GET'])
App.add_url_rule('/evaluation/jobs_and_loans', 'based_on_jobs_and_loans_to_json', based_on_jobs_and_loans_to_json, methods=['GET'])
App.add_url_rule('/evaluation/residence', 'based_on_residence_to_json', based_on_residence_to_json, methods=['GET'])



if __name__ == '__main__':
    StartScheduler()
    App.run(port=5000, debug=True)
