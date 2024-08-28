from Datapreprocessing import dataPreprocessing
# CSV 파일 불러와서 데이터 전처리
# 파일 경로 설정 (방법 1: raw string 사용)
# file_path = r'D:\dev\CreditOnly\CreditOnly_PythonFlask\data'
#우분투 환경에서 경로설정
file_path = '/home/ubuntu/flask/data'
# 나와 같은 직업군의 신용등급(시각화)
based_on_jobs_and_loans = [
    "HAC_CD",  # 직업 구분 (1:급여소득자, 2:개인사업자, 3:연금소득자, 4:주부, 5:전문직, 7:프리랜서, 8:무직, 9:기타)
    "L00000001",  # 미상환 대출총건수
]

def based_on_jobs_and_loans_to_json():
    df = dataPreprocessing(file_path, based_on_jobs_and_loans)

    # "L00000001" 열 이름을 "Loan"으로 변경
    if "L00000001" in df.columns:
        df = df.rename(columns={"L00000001": "Loan"})


    df_json = df.to_json(orient='records', force_ascii=False)  # records 형태로 변환
    return df_json