import pandas as pd
import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch, helpers
import logging
from env.settings import ElasticsearchUrl

# 로깅 설정
Logger = logging.getLogger(__name__)

# Elasticsearch 클라이언트 초기화
es = Elasticsearch([ElasticsearchUrl])

# 인덱스 매핑 정의
Mappings = {
    "EcosStatisticWord": {
        "properties": {
            "STAT_NAME": {"type": "keyword"},
            "STAT_CODE": {"type": "keyword"}
        }
    },
    "DartCompanyInfo": {
        "properties": {
            "corp_code": {"type": "keyword"},
            "corp_name": {"type": "text"},
            "stock_code": {"type": "keyword"},
            "modify_date": {"type": "date"}
        }
    },
    "FinancialCompany": {
        "properties": {
            "fncoNm": {"type": "text"},
            "fncoType": {"type": "text"},
            "fncoAddr": {"type": "text"},
            "basDt": {"type": "date"}
        }
    }
}

def createIndexIfNotExists(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        print(f"Index {index_name} created.")

def safeEsBulk(actions):
    try:
        helpers.bulk(es, actions)
    except Exception as e:
        print(f"Error in Elasticsearch bulk operation: {str(e)}")
        raise

def validateXmlData(df):
    if df.empty:
        raise ValueError("XML data is empty after processing")
    if df['STAT_NAME'].isnull().any() or df['STAT_CODE'].isnull().any():
        raise ValueError("Missing required fields in XML data")
    return df

def preprocessXmlData(xml_data, columns):
    root = ET.fromstring(xml_data)
    data = []
    for item in root.findall('.//row'):
        row = {col: item.find(col).text if item.find(col) is not None else None for col in columns}
        data.append(row)
    df = pd.DataFrame(data)
    df.dropna(inplace=True)
    return validateXmlData(df)

def validateJsonData(df):
    if df.empty:
        raise ValueError("JSON data is empty after processing")
    # 검증을 위한 추가 로직
    return df

def preprocessJsonData(json_data, columns):
    data = []
    for item in json_data:
        row = {col: item.get(col) for col in columns}
        data.append(row)
    df = pd.DataFrame(data)
    df.dropna(inplace=True)
    return validateJsonData(df)

def indexDataToElasticsearch(index_name, data):
    actions = [
        {
            "_index": index_name,
            "_source": item
        }
        for item in data
    ]
    safeEsBulk(actions)
