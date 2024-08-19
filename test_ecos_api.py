from PublicDataReader import Ecos
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 환경 변수에서 API 키를 가져옵니다.
EcosApiKey = os.getenv('ECOS_API_KEY')

def test_ecos_api():
    try:
        api = Ecos(EcosApiKey)
        df = api.get_statistic_word(용어='소비자물가지수')
        if df is not None and not df.empty:
            print("API 호출 성공")
            print(df)
        else:
            print("데이터가 비어 있습니다.")
    except Exception as e:
        print(f"API 호출 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_ecos_api()