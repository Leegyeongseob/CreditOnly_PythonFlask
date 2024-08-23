import pandas as pd
import numpy as np

# 머신러닝으로 신용등급 분류하기
def dataPreprocessing(file_path, required_columns):
    data = [
        "based_on_creditCard",
        "based_on_jobs",
        "based_on_jobs_and_loans",
        "based_on_residence",
        "machineLearningData"
    ]
    # CSV 파일 읽기
    df = pd.read_csv(file_path + "/저축은행 신용관련 익명데이터.csv", low_memory=False)

    # 선택한 컬럼으로 데이터프레임 필터링
    df = df[required_columns]
    # 데이터 확인 (처음 5행)
    print(df.head())

    # -999를 NaN으로 변환
    df = df.replace(-999, np.nan)

    # HAC_CD 컬럼이 존재하면 결측값을 9(기타)으로 대체
    if 'HAC_CD' in df.columns:
        df['HAC_CD'] = df['HAC_CD'].fillna(9)

    # CB 컬럼이 존재하면 중앙값으로 대체
    if 'CB' in df.columns:
        df['CB'] = df['CB'].fillna(df['CB'].median())
        # CB 열의 -1 값을 9(기타)으로 변경
        df['CB'] = df['CB'].replace(-1, 9)
        print("CB 열에서 -1 값을 9으로 변경했습니다.")

    # 나머지 수치형 컬럼들이 존재하면 평균값으로 대체
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        if col not in ['HAC_CD', 'CB'] and col in df.columns:
            df[col] = df[col].fillna(df[col].mean())

    # 문자열 데이터 타입의 열이 존재하면 처리
    string_columns = df.select_dtypes(include='object')
    for col in string_columns.columns:
        if col in df.columns:
            if col == 'RES_ADD':
                # RES_ADD 열은 문자열로 유지하고 결측치만 처리
                df[col] = df[col].fillna('Unknown')
            else:
                # 다른 문자열 열들에 대해서는 기존 로직 유지
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(9)

    # HAC_CD를 정수형으로 변환
    if 'HAC_CD' in df.columns:
        df['HAC_CD'] = df['HAC_CD'].astype(int)

    # 이상값 처리가 필요한 컬럼들
    outlier_columns = ['L22003100', 'LA1200017', 'LA1200018', 'LA1200019',
                       'LA1200020', 'LA1200021', 'LA6000005']

    for column in outlier_columns:
        if column in df.columns:
            # 값의 빈도 계산
            value_counts = df[column].value_counts()

            # 상위 10% 빈도의 값들을 '자주 나오는 값'으로 정의
            frequent_values = value_counts[value_counts > value_counts.quantile(0.9)].index

            # '자주 나오는 값'들의 평균과 표준편차 계산
            frequent_mean = df[df[column].isin(frequent_values)][column].mean()
            frequent_std = df[df[column].isin(frequent_values)][column].std()

            # '자주 나오는 값' 중 평균에서 3 표준편차 이상 벗어난 값을 이상값으로 간주
            outliers = frequent_values[(frequent_values > frequent_mean + 3 * frequent_std) |
                                       (frequent_values < frequent_mean - 3 * frequent_std)]

            # '자주 안 나오는 값'들의 평균 계산
            infrequent_mean = df[~df[column].isin(frequent_values)][column].mean()

            # 이상값을 '자주 안 나오는 값'들의 평균으로 대체
            df[column] = df[column].replace(outliers, infrequent_mean)

            # 음수값을 0으로 대체
            df[column] = df[column].clip(lower=0)

    # 결측치 처리 (최빈값으로 대체)
    for column in df.columns:
        if df[column].dtype == 'object':  # 범주형 변수
            df[column] = df[column].fillna(df[column].mode()[0])
        else:  # 수치형 변수
            df[column] = df[column].fillna(df[column].mode()[0])

    # 데이터 전처리 결과 확인
    dataCheck(df)
    return df

# 데이터 확인하기
def dataCheck(df):
    # 데이터프레임의 크기 출력
    print("Dataframe Shape: ", df.shape)

    # 데이터프레임의 기본 통계 정보 출력
    print("\nBasic Statistics:\n")
    print(df.describe(include='all'))

    # 각 열의 결측값 확인
    print("\nMissing Values:\n")
    print(df.isnull().sum())

    # 각 열의 데이터 유형 확인
    print("\nData Types:\n")
    print(df.dtypes)

    # 각 열의 고유값 수 확인
    print("\nUnique Values per Column:\n")
    for column in df.columns:
        print(f"{column}: {df[column].nunique()} unique values")

    # 데이터프레임의 첫 몇 개의 행 출력
    print("\nFirst Few Rows:\n")
    print(df.head())

# 결측치 확인하고 처리하기
def missingValueCheck(df):
    df.replace('*', pd.NA, inplace=True)  # * 문자열을 결측치로 변환
    # 결측치 개수와 비율 확인
    missing_info = df.isnull().sum()
    missing_percentage = (missing_info / len(df)) * 100
    missing_summary = pd.DataFrame({
        'Missing Values': missing_info,
        'Percentage': missing_percentage
    })

    print("결측치 확인하기")
    print(missing_summary)


# 결측치 확인하고 처리하기
def missingValuePrint(df):
     # 문자열 데이터 타입의 열만 선택
    string_columns = df.select_dtypes(include='object')

    #문자열 데이터 값들 출력
    for col in string_columns.columns:
        print(f"\n열: {col}")
        print(string_columns[col].to_list())  # 결측치를 포함하여 리스트로 출력


def cbValuePrint(df):
    # CB 열에서 -1 값의 개수와 비율 확인
    cb_neg_1_count = (df['CB'] == -1).sum()
    cb_neg_1_percentage = (cb_neg_1_count / len(df)) * 100

    print(f"CB 열에서 -1 값 개수: {cb_neg_1_count}")
    print(f"CB 열에서 -1 값 비율: {cb_neg_1_percentage:.2f}%")
