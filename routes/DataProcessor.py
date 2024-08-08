import pandas as pd
import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import TransportError
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from env.settings import ElasticsearchUrl

Logger = logging.getLogger(__name__)

Es = Elasticsearch([ElasticsearchUrl])

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
    }
}

def CreateIndexIfNotExists(IndexName):
    if not Es.indices.exists(index=IndexName):
        Es.indices.create(index=IndexName, body={"mappings": Mappings[IndexName]})
        Logger.info(f"Created index: {IndexName}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def SafeEsBulk(Actions):
    try:
        helpers.bulk(Es, Actions)
    except TransportError as e:
        Logger.error(f"Error in Elasticsearch bulk operation: {str(e)}")
        raise

def ValidateXmlData(Df):
    if Df.empty:
        raise ValueError("XML data is empty after processing")
    if Df['STAT_NAME'].isnull().any() or Df['STAT_CODE'].isnull().any():
        raise ValueError("Missing required fields in XML data")
    return Df

def PreprocessXmlData(XmlData, Columns):
    Root = ET.fromstring(XmlData)
    Data = []
    for Item in Root.findall('.//row'):
        Row = {Col: Item.find(Col).text if Item.find(Col) is not None else None for Col in Columns}
        Data.append(Row)
    Df = pd.DataFrame(Data)
    Df.dropna(inplace=True)
    return ValidateXmlData(Df)
