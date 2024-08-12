import pandas as pd
import os
from flask import jsonify
from elasticsearch import Elasticsearch
from routes.DataProcessor import CreateIndexIfNotExists, SafeEsBulk
import logging
from env.settings import ElasticsearchUrl

Logger = logging.getLogger(__name__)

Es = Elasticsearch([ElasticsearchUrl])

def IndexCsvData():
    try:
        # 상대 경로로 csv 파일 경로 설정
        csv_file_path = r'D:\dev\CreditOnly\CreditOnly_python_flask\CreditOnly_PythonFlask\data\국민건강보험공단_건강보험 보험료 현황_20211231.csv'
        df_csv = pd.read_csv(csv_file_path, encoding='euc-kr')  # 필요한 인코딩으로 변경

        # 필요에 따라 데이터 전처리 수행
        df_csv = df_csv.dropna()  # 예시: 결측값 제거

        CreateIndexIfNotExists('HealthInsurance')
        Actions = [
            {
                "_index": "HealthInsurance",
                "_source": row.to_dict()
            }
            for _, row in df_csv.iterrows()
        ]
        SafeEsBulk(Actions)

        Logger.info("CSV data indexed successfully")
        return jsonify({"message": "CSV data indexed successfully"}), 200
    except Exception as e:
        Logger.error(f"Error indexing CSV data: {str(e)}")
        return jsonify({"error": str(e)}), 500
