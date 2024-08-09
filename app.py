import sys
import os
from flask import Flask
from flask_cors import CORS
import logging

# 현재 디렉토리의 부모 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.BankOfKoreaHandler import IndexBokData
from routes.DartHandler import IndexDartData
from routes.Scheduler import StartScheduler
from routes.CsvHandler import IndexCsvData
from routes.ExcelHandler import IndexExcelData
from routes.ElasticSearchHandler import GetEcosData, GetDartData

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

if __name__ == '__main__':
    StartScheduler()
    App.run(port=5000, debug=True)