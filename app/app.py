from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import asyncio
from dotenv import load_dotenv
import os
import threading
<<<<<<< HEAD:app/app.py
from src import scraping_main  # モジュールをインポート

from app import Localization
=======
sys.path.append('../')
from app import scraping_main
from config import Localization
>>>>>>> parent of fce2c0d ([WIP] file path 変更前):config/app.py

# gRPC サーバーをインポート
from app.grpc_server import serve as grpc_serve

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.environ.get("FRONT_API_URL")}})

@app.route("/")
def index():
    return "Welcome to ASEticle."

@app.route('/api/execute', methods=['GET'])
def execute_route():
    if request.args.get('params') is not None:
        params = request.args.get('params')
    else:
        return jsonify({"error": Localization.get('config.routes.bad_request')}), 400

    result = asyncio.run(scraping_main(params))

    return result

def run_flask():
    app.run(port=8080, debug=True)

if __name__ == "__main__":
    # Flask と gRPC のサーバーを同時に実行
    grpc_thread = threading.Thread(target=grpc_serve)
    grpc_thread.start()

    # run_flask()
