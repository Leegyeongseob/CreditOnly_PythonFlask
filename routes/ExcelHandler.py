import pandas as pd
import os
from flask import jsonify
from elasticsearch import Elasticsearch
from routes.DataProcessor import CreateIndexIfNotExists, SafeEsBulk
import logging
from env.settings import ElasticsearchUrl

Logger = logging.getLogger(__name__)

Es = Elasticsearch([ElasticsearchUrl])

def IndexExcelData():
    try:
        excel_file_path = os.path.join(os.path.dirname(__file__), '../data/통계표_07180337.xlsx')
        df_excel = pd.read_excel(excel_file_path)

        # 필요에 따라 데이터 전처리 수행
        df_excel = df_excel.dropna()  # 예시: 결측값 제거

        CreateIndexIfNotExists('Statistics')
        Actions = [
            {
                "_index": "Statistics",
                "_source": row.to_dict()
            }
            for _, row in df_excel.iterrows()
        ]
        SafeEsBulk(Actions)

        Logger.info("Excel data indexed successfully")
        return jsonify({"message": "Excel data indexed successfully"}), 200
    except Exception as e:
        Logger.error(f"Error indexing Excel data: {str(e)}")
        return jsonify({"error": str(e)}), 500
