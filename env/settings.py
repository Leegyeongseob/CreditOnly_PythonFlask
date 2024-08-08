import os
from dotenv import load_dotenv

load_dotenv()

ElasticsearchUrl = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
EcosApiKey = os.getenv('ECOS_API_KEY', '9M7CN1EZJCG7AJ0FYE3L')
DartApiKey = os.getenv('DART_API_KEY', '867e415360666e31086d898b5c4a77f0c71657ed')
