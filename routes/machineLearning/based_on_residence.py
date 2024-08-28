from Datapreprocessing import dataPreprocessing
# CSV 파일 불러와서 데이터 전처리
# 파일 경로 설정 (방법 1: raw string 사용)
# file_path = r'D:\dev\CreditOnly\CreditOnly_PythonFlask\data'
#우분투 환경에서 경로설정
file_path = '/home/ubuntu/flask/data'
# 나와 같은 직업군의 신용등급(시각화)
based_on_residence = [
    "RES_ADD",  # 거주지 주소
    "CB"  # NICE, KCB에서 제공하는 신용평가 등급(1~10등급)
]

def based_on_residence_to_json():
    df = dataPreprocessing(file_path, based_on_residence)
    df_json = df.to_json(orient='records', force_ascii=False)  # records 형태로 변환
    return df_json