from Datapreprocessing import dataPreprocessing
# CSV 파일 불러와서 데이터 전처리
# 파일 경로 설정 (방법 1: raw string 사용)
file_path = r'D:\dev\CreditOnly\CreditOnly_PythonFlask\data'
# 나와 같은 직업군의 신용등급(시각화)
based_on_jobs = [
    "HAC_CD",  # 직업 구분 (1:급여소득자, 2:개인사업자, 3:연금소득자, 4:주부, 5:전문직, 7:프리랜서, 8:무직, 9:기타)
    "CB",  # NICE, KCB에서 제공하는 신용평가 등급(1~10등급)
]

def based_on_jobs_to_json():
    df = dataPreprocessing(file_path, based_on_jobs)
    df_json = df.to_json(orient='records', force_ascii=False)  # records 형태로 변환
    return df_json
