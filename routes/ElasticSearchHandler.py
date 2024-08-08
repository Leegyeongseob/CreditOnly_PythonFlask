from flask import jsonify, request
from elasticsearch import Elasticsearch
from env.settings import ElasticsearchUrl
import logging

Logger = logging.getLogger(__name__)

Es = Elasticsearch([ElasticsearchUrl])

def GetDataFromElasticsearch(index_name, query):
    try:
        response = Es.search(index=index_name, body=query)
        return response
    except Exception as e:
        Logger.error(f"Error retrieving data from Elasticsearch: {str(e)}")
        raise

def GetEcosData():
    try:
        index_name = 'EcosStatisticWord'
        query = {
            "query": {
                "match_all": {}
            }
        }
        response = GetDataFromElasticsearch(index_name, query)
        return jsonify(response), 200
    except Exception as e:
        Logger.error(f"Error retrieving data from Elasticsearch: {str(e)}")
        return jsonify({"error": str(e)}), 500

def GetDartData():
    try:
        index_name = 'DartCompanyInfo'
        query = {
            "query": {
                "match_all": {}
            }
        }
        response = GetDataFromElasticsearch(index_name, query)
        return jsonify(response), 200
    except Exception as e:
        Logger.error(f"Error retrieving data from Elasticsearch: {str(e)}")
        return jsonify({"error": str(e)}), 500
