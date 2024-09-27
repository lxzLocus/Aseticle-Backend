from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import asyncio
from dotenv import load_dotenv
import os
import sys
sys.path.append('/app/app')
from googlescholar_searcher import scraping_main # type: ignore
sys.path.append('/app/config')
from config import Localization

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

if __name__ == "__main__":
	app.run(port=8080, debug=True)