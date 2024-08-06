from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()

class ElasticHandler:
    def __init__(self):
        self.es = Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST'), 'port': os.getenv('ELASTICSEARCH_PORT')}])

    def index_data(self, index_name, doc_type, doc_id, body):
        return self.es.index(index=index_name, doc_type=doc_type, id=doc_id, body=body)

    def search(self, index_name, query):
        return self.es.search(index=index_name, body=query)