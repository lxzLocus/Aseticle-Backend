import requests
import json
import re
from datetime import datetime
import aiohttp
from urllib.parse import quote
import sys
import os  # 追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))  # 追加
from config.localization import Localization

IEEE_URL = "https://ieeexplore.ieee.org/"

class WebScraper:
    """This class is used to retrieve a web page from a specified URL and extract metadata from the page content.

    Attributes:
        url (str): URL of the web page to be scraped.
        page_content (bytes): Content of pages.
        headers (dict): Header used for HTTP requests.

    Method:
        fetch_page(): Retrieve the page from the specified URL.
        extract_metadata(): Extract metadata from the retrieved page content.
    """

    def __init__(self, url):
        self.url = url
        self.page_content = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def fetch_page(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            self.page_content = response.content
        except requests.exceptions.HTTPError as err:
            print(Localization.get('app.module.ieee.fetch.http_error') + {err})
        except Exception as e:
            print(Localization.get('app.module.ieee.fetch.error') + {e})

    def extract_metadata(self):
        if not self.page_content:
            print(Localization.get('app.module.ieee.extract.fetch_error'))
            return []

        # Extracting JavaScript objects
        match = re.search(r'xplGlobal\.document\.metadata\s*=\s*({.*?});', self.page_content.decode('utf-8'), re.DOTALL)
        if not match:
            print(Localization.get('app.module.ieee.extract.not_found'))
            return []

        metadata_json = match.group(1)

        # JavaScript objects converted to JSON object
        try:
            metadata = json.loads(metadata_json)
        except json.JSONDecodeError as e:
            print(Localization.get('app.module.ieee.extract.json_error') + {e})
            return []

        return metadata

class CiteNum:
    @classmethod
    async def fetch_cite_num(cls, title):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.semanticscholar.org/graph/v1/paper/search/match?query={quote(title)}",
            ) as response:
                try:
                    result = await response.json()
                except:
                    return None

                if "data" in result and isinstance(result["data"], list) and len(result["data"]) > 0:
                    paper_id = result["data"][0]["paperId"]

                    # paperIdから被引用数を取得
                    async with session.post(
                        'https://api.semanticscholar.org/graph/v1/paper/batch',
                        params={'fields': 'referenceCount,citationCount,title'},
                        json={"ids": [paper_id]}
                    ) as citation_response:
                        citation_data = await citation_response.json()
                    return citation_data[0].get("citationCount")
                else:
                    return None

async def ieee_execute(param):
    entries = []

    for item in param:
        url = item["url"]
        relevant_no = item["relevant_no"]
        scraper = WebScraper(url)
        scraper.fetch_page()

        metadata = scraper.extract_metadata()

        if metadata:
            # Retrieving contents from metadata
            title = metadata.get('displayDocTitle', '')
            meta_authors = metadata.get('authors', [])
            authors = ", ".join([author['name'] for author in meta_authors]) if meta_authors else None
            conference = metadata.get('publicationTitle', '')
            if not conference:
                conference = metadata.get('publisher', '')
            
            # 日付のフォーマット修正
            meta_date = metadata.get('insertDate', '')
            if meta_date:
                try:
                    date = datetime.strptime(meta_date, "%d %B %Y")
                except ValueError:
                    date = None
            else:
                date = None
            
            abstract = metadata.get('abstract', '')

            # Semantic Scholar APIで引用数を取得
            cite_num = await CiteNum.fetch_cite_num(title)

            # エントリ作成
            new_entry = {
                "url": url,
                "title": title,
                "author": authors,
                "conference": conference,
                "pages": None,  # IEEEのページ数情報がないため、Noneに設定
                "date": date,
                "abstract": abstract,
                "cite_num": cite_num,
                "submitted": True,
                "relevant_no": relevant_no,
            }
            entries.append(new_entry)

    return entries
