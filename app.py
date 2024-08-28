import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from functools import wraps
import jwt
# 현재 디렉토리의 부모 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routes', 'machineLearning'))

from routes.BankOfKoreaHandler import IndexBokData
from routes.DartHandler import IndexDartData
from routes.Scheduler import StartScheduler
from routes.CsvHandler import IndexCsvData
from routes.ExcelHandler import IndexExcelData
from routes.ElasticSearchHandler import GetEcosData, GetDartData
from routes.SimilaritySearchHandler import similarity_search
from routes.FinancialDataHandler import IndexAllFinancialData
from routes.machineLearning.based_on_creditCard import based_on_creditCard_to_json
from routes.machineLearning.based_on_jobs import based_on_jobs_to_json
from routes.machineLearning.based_on_jobs_and_loans import based_on_jobs_and_loans_to_json
from routes.machineLearning.based_on_residence import based_on_residence_to_json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://www.creditonly.store"}})


# JWT 시크릿 키 (실제 운영 환경에서는 환경 변수 등으로 안전하게 관리해야 합니다)
JWT_SECRET_KEY = "1q2w3e4r!@#!!23456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            # 여기에서 필요한 경우 추가적인 사용자 검증 로직을 넣을 수 있습니다.
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.errorhandler(Exception)
def handle_error(error):
    message = str(error)
    status_code = 500
    if hasattr(error, 'code'):
        status_code = error.code
    return jsonify({"error": message}), status_code

# 경제 관련 데이터
@app.route('/api/elastic/ecos', methods=['GET'])
@token_required
def index_bok_data():
    return IndexBokData()

@app.route('/api/elastic/economic/financial_data', methods=['GET'])
@token_required
def index_all_financial_data():
    return IndexAllFinancialData()

# 기업 관련 데이터
@app.route('/api/elastic/company/dart', methods=['POST'])
@token_required
def index_dart_data():
    return IndexDartData()

@app.route('/api/elastic/company/get_dart', methods=['GET'])
@token_required
def get_dart_data():
    return GetDartData()

# 데이터 유사도 검색
@app.route('/api/elastic/similarity_search', methods=['POST'])
@token_required
def similarity_search_route():
    return similarity_search()

# 데이터 인덱싱
@app.route('/api/elastic/csv', methods=['GET'])
@token_required
def index_csv_data():
    return IndexCsvData()

@app.route('/api/elastic/excel', methods=['GET'])
@token_required
def index_excel_data():
    return IndexExcelData()

# 데이터 시각화
@app.route('/evaluation/credit_card', methods=['GET'])
@token_required
def credit_card_evaluation():
    return based_on_creditCard_to_json()

@app.route('/evaluation/jobs', methods=['GET'])
@token_required
def jobs_evaluation():
    return based_on_jobs_to_json()

@app.route('/evaluation/jobs_and_loans', methods=['GET'])
@token_required
def jobs_and_loans_evaluation():
    return based_on_jobs_and_loans_to_json()

# 로깅 추가

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/evaluation/residence', methods=['GET'])
@token_required
def residence_evaluation():
    return based_on_residence_to_json()

# 신용평가 데이터 받아오는 부분
@app.route('/creditInput', methods=['POST'])
@token_required
def credit_input():
    data = request.json
    # 여기에 신용평가 로직을 구현하세요
    return jsonify({"message": "Credit input received successfully"}), 200

if __name__ == '__main__':
    StartScheduler()
    logger.info('Starting Flask application')
    app.run(host='0.0.0.0', port=5000)