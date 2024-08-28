# 데이터를 train, test 셋으로 분리하기
from Datapreprocessing import dataPreprocessing
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import GridSearchCV
import time


# CSV 파일 불러와서 데이터 전처리
# 파일 경로 설정 (방법 1: raw string 사용)
# file_path = r'D:\dev\CreditOnly\CreditOnly_PythonFlask\data'

# 우분투 환경에서 경로
file_path = '/home/ubuntu/flask/data'
# 필요로 하는 속성의 데이터만 뽑아서 csv로 만들기
required_columns = [
    "HAC_CD",  # 직업 구분 (1:급여소득자, 2:개인사업자, 3:연금소득자, 4:주부, 5:전문직, 7:프리랜서, 8:무직, 9:기타) -> 시각화와 머신러닝에 사용
    "CB",  # NICE, KCB에서 제공하는 신용평가 등급(1~10등급) -> 머신러닝 결과에 사용
    "C00000052",  # 최근5년내 미해지 신용개설 총 건수,varchar2(20) - 머신러닝에 사용, 시각화에 사용.
    "CA1200001",  # 최근1년내신용카드개설기관수,varchar2(20) - 머신러닝에 사용
    "CA2400001",  # 최근2년내신용카드개설기관수,varchar2(20) - 머신러닝에 사용
    "CA3600001",  # 최근3년내신용카드개설기관수,varchar2(20) - 머신러닝에 사용
    # 직업에 따른 미상환 대출 건수 시각화에 사용.
    "L22002700",  # 최근3개월내 500만원미만 미상환 대출총건수,varchar2(20) - 머신러닝에 사용
    "L22002800",  # 최근3개월내 1000만원미만 미상환 대출총건수,varchar2(20) - 머신러닝에 사용
    "L22002900",  # 최근6개월내 500만원미만 미상환 대출총건수,varchar2(20) - 머신러닝에 사용
    "L22003000",  # 최근6개월내 1000만원미만 미상환 대출총건수,varchar2(20) - 머신러닝에 사용
    "L22003100",  # 최근1년내 500만원미만 미상환 대출총건수,varchar2(20) - 머신러닝에 사용
    "L22003200",  # 최근1년내 1000만원미만 미상환 대출총건수,varchar2(20) - 머신러닝에 사용
    "LA1200017",  # 최근12개월내 대출 경험 총 건수(계좌상태 대위변제),varchar2(20) - 머신러닝에 사용
    "LA1200018",  # 최근12개월내 대출 경험 총 건수(계좌상태 상각),varchar2(20) - 머신러닝에 사용
    "LA1200019",  # 최근12개월내 대출 경험 총 건수(계좌상태 매각),varchar2(20) - 머신러닝에 사용
    "LA1200020",  # 최근12개월내 대출 경험 총 건수(계좌상태 채무재조정),varchar2(20) - 머신러닝에 사용
    "LA1200021",  # 최근12개월내 대출 경험 총 건수(계좌상태 파산),varchar2(20) - 머신러닝에 사용
    "LA1200022",  # 최근12개월내 대출 경험 총 건수(계좌상태 기한이익상실),varchar2(20) - 머신러닝에 사용
    "LA6000005",  # 최근12개월내 대출 경험 총 건수(계좌상태 양도해지 - 머신러닝에 사용
    "L00000001",  # 미상환 대출총건수 - 머신러닝에 사용, 시각화에 사용.
]
def trainTestSplit(df):
    # 타겟 변수와 특성 분리
    X = df.drop('CB', axis=1)
    y = df['CB']

    # 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test



# XGBoost 모델 하이퍼파라미터 튜닝 함수
def tune_xgboost(X_train, y_train):
    param_grid = {
        'n_estimators': [50, 150, 250, 500],
        'max_depth': [3, 6, 9, 12],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.7, 0.8, 0.9, 1.0],
        'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
        'gamma': [0, 0.1, 0.2, 0.5],
        'min_child_weight': [1, 5, 10]
    }

    model = xgb.XGBClassifier(objective='multi:softprob', eval_metric='mlogloss')

    # n_jobs를 1로 설정하여 병렬 처리 비활성화
    grid_search = GridSearchCV(model, param_grid, cv=3, scoring='accuracy', n_jobs=1, verbose=2)

    start_time = time.time()
    print("하이퍼파라미터 튜닝 시작...")
    grid_search.fit(X_train, y_train)
    end_time = time.time()
    elapsed_time = end_time - start_time

    print("최적 하이퍼파라미터:", grid_search.best_params_)
    print("최고 정확도:", grid_search.best_score_)
    print(f"튜닝 소요 시간: {elapsed_time:.2f}초")

    return grid_search.best_estimator_


def train_xgboost_optimized(X_train, X_test, y_train, y_test):
    best_model = tune_xgboost(X_train, y_train)

    start_time = time.time()
    print("최종 모델 학습 중...")

    # eval_metric 매개변수를 제거하고 eval_set만 사용
    best_model.fit(X_train, y_train,
                   eval_set=[(X_train, y_train), (X_test, y_test)],
                   verbose=True)

    end_time = time.time()
    elapsed_time = end_time - start_time

    y_pred = best_model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=1)
    cm = confusion_matrix(y_test, y_pred)

    try:
        roc_auc = roc_auc_score(y_test, best_model.predict_proba(X_test), multi_class='ovr')
    except:
        roc_auc = "ROC AUC score cannot be computed for this model"

    print(f"\n모델 학습 소요 시간: {elapsed_time:.2f}초")
    print("모델 정확도:", accuracy)
    print("분류 리포트:\n", report)
    print("혼동 행렬:\n", cm)
    print("ROC AUC 스코어:", roc_auc)

    return best_model


# 데이터 전처리
processedDf = dataPreprocessing(file_path, required_columns)

# train, test 데이터 분리
X_train, X_test, y_train, y_test = trainTestSplit(processedDf)

# XGBoost 모델 학습 및 평가 실행
train_xgboost_optimized(X_train, X_test, y_train, y_test)