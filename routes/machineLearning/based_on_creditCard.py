from Datapreprocessing import dataPreprocessing
# CSV 파일 불러와서 데이터 전처리
# 파일 경로 설정 (방법 1: raw string 사용)
# file_path = r'D:\dev\CreditOnly\CreditOnly_PythonFlask\data'
#우분투 환경에서 경로설정
file_path = '/home/ubuntu/flask/data'
# 나와 같은 직업군의 신용등급(시각화)
based_on_creditCard = [
    "C00000052",  # 최근5년내 미해지 신용개설 총 건수,varchar2(20)
    "CA1200001",  # 최근1년내신용카드개설기관수,varchar2(20)
    "CA2400001",  # 최근2년내신용카드개설기관수,varchar2(20)
    "CA3600001",  # 최근3년내신용카드개설기관수,varchar2(20)
    "CB",  # NICE, KCB에서 제공하는 신용평가 등급(1~10등급)
]

def based_on_creditCard_to_json():
    df = dataPreprocessing(file_path, based_on_creditCard)
    df_json = df.to_json(orient='records', force_ascii=False)  # records 형태로 변환
    return df_json