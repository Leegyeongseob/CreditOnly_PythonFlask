from flask import Flask
from routes.BankOfKoreaHandler import index_data as index_bok_data
from routes.DartHandler import index_data as index_dart_data
from routes.Scheduler import start_scheduler

app = Flask(__name__)

# URL 엔드포인트 추가
app.add_url_rule('/api/elastic/bok', 'index_bok_data', index_bok_data, methods=['GET'])
app.add_url_rule('/api/elastic/dart', 'index_dart_data', index_dart_data, methods=['GET'])

if __name__ == '__main__':
    start_scheduler()
    app.run(port=5000, debug=True)
