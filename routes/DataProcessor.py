import xml.etree.ElementTree as ET
import pandas as pd

def preprocess_xml_data(xml_data, columns):
    """
    수집된 XML 데이터를 전처리하는 함수

    :param xml_data: XML 데이터
    :param columns: 추출할 컬럼 리스트
    :return: 전처리된 데이터 (DataFrame 형식)
    """
    root = ET.fromstring(xml_data)
    data = []
    for item in root.findall('.//row'):
        row = {col: item.find(col).text if item.find(col) is not None else None for col in columns}
        data.append(row)
    df = pd.DataFrame(data)
    df.dropna(inplace=True)
    return df
