import requests
from flask import jsonify
import logging
from env.settings import EcosApiKey
from routes.DataProcessor import CreateIndexIfNotExists, SafeEsBulk, PreprocessXmlData

Logger = logging.getLogger(__name__)

def IndexBokData():
    try:
        Url = f"https://ecos.bok.or.kr/api/StatisticWord/{EcosApiKey}/xml/kr/1/10/소비자동향지수"
        Response = requests.get(Url)
        Response.raise_for_status()
        XmlData = Response.content

        Columns = ['STAT_NAME', 'STAT_CODE']
        DfXml = PreprocessXmlData(XmlData, Columns)

        CreateIndexIfNotExists('EcosStatisticWord')
        Actions = [
            {
                "_index": "EcosStatisticWord",
                "_source": Row.to_dict()
            }
            for _, Row in DfXml.iterrows()
        ]
        SafeEsBulk(Actions)

        Logger.info("BOK data indexed successfully")
        return jsonify({"message": "BOK data indexed successfully"}), 200
    except Exception as e:
        Logger.error(f"Error indexing BOK data: {str(e)}")
        return jsonify({"error": str(e)}), 500
