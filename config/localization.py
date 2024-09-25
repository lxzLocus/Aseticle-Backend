import yaml
import os

class Localization:
	_data = None

	@classmethod
	def load(cls, file_path):
		with open(file_path, 'r', encoding='utf-8') as file:
			cls._data = yaml.safe_load(file)

	@classmethod
	def get(cls, key, default=None):
		if cls._data is None:
			raise ValueError("Localization data not loaded.")
		keys = key.split('.')
		data = cls._data
		for k in keys:
			data = data.get(k, default)
			if data is default:
				break
		return data

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'locales', 'ja.yml')
Localization.load(file_path)