import os
from dotenv import load_dotenv

load_dotenv()

ElasticsearchUrl = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
EcosApiKey = os.getenv('ECOS_API_KEY', '9M7CN1EZJCG7AJ0FYE3L')
DartApiKey = os.getenv('DART_API_KEY', '867e415360666e31086d898b5c4a77f0c71657ed')

# 금융 API 키 추가 (인코딩된 버전)
FinancialApiKeyEncoded = os.getenv('FINANCIAL_API_KEY_ENCODED', '3XcjkXtX6QxklSxdLcR5LS2vtIDSFGVNOHwIG94dfCA14IuC8g7veVLpKGDxuVz3QtoLRl6iwWYMi76t3MxySQ%3D%3D')

# 금융 API 키 추가 (디코딩된 버전)
FinancialApiKeyDecoded = os.getenv('FINANCIAL_API_KEY_DECODED', '3XcjkXtX6QxklSxdLcR5LS2vtIDSFGVNOHwIG94dfCA14IuC8g7veVLpKGDxuVz3QtoLRl6iwWYMi76t3MxySQ==')