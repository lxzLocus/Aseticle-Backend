import requests
import aiohttp
import sys
import os
from io import BytesIO
from PyPDF2 import PdfFileReader
from datetime import datetime
from urllib.parse import quote
from lxml import html
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) #追加
from config.localization import Localization

# 環境変数を読み込む
load_dotenv()

ARXIV_URL = "https://arxiv.org/"

# 環境変数からプロキシサーバリストを取得
proxies1 = [
	{"http": os.getenv("PROXY1"), "https": os.getenv("PROXY1")},
    {"http": os.getenv("PROXY2"), "https": os.getenv("PROXY2")}
]
proxies2 = [
	os.getenv("PROXY1"),
    os.getenv("PROXY2")
]
proxy_index = 0

ARXIV_URL = "https://arxiv.org/"

# プロキシを交互に選択する関数1
def get_next_proxy1():
    global proxy_index
    proxy = proxies1[proxy_index]
    proxy_index = (proxy_index + 1) % len(proxies1)
    return proxy

# プロキシを交互に選択する関数2
def get_next_proxy2():
    global proxy_index
    proxy = proxies2[proxy_index]
    proxy_index = (proxy_index + 1) % len(proxies2)
    return f"http://{proxy}"

class WebScraper:

    def __init__(self, url):
        self.url = url
        self.page_content = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def fetch_page(self):
        try:
            proxy = get_next_proxy1()
            response = requests.get(self.url, headers=self.headers, proxies=proxy)
            response.raise_for_status()
            self.page_content = response.content
        except requests.exceptions.HTTPError as err:
            print(Localization.get('app.module.arxiv.fetch.http_error') + {err})
        except Exception as e:
            print(Localization.get('app.module.arxiv.fetch.error') + {e})

    def extract_metadata(self):
        if not self.page_content:
            print(Localization.get('app.module.arxiv.extract.fetch_error'))
            return []

        # Extract using XPATH
        extractContent = html.fromstring(self.page_content)
        if not extractContent:
            print(Localization.get('app.module.arxiv.extract.not_found'))
            return []

        return extractContent

class PdfCounter:
    @classmethod
    async def fetch_pdf_pages(cls, url):
        pdf_url = url.replace("abs", "pdf")
        
        async with aiohttp.ClientSession() as session:
            try:
                proxy = get_next_proxy2()
                async with session.get(pdf_url, proxy=proxy) as response:
                    if response.status == 200:
                        pdf_data = await response.read()
                        pdf_file = BytesIO(pdf_data)
                        pdf_reader = PdfFileReader(pdf_file)
                        pages = pdf_reader.getNumPages()
                        return response.status, pages
                    else:
                        return response.status, None
            except Exception as e:
                print(f"Error fetching PDF: {e}")
                return 404, None

class SemanticApi:
    @classmethod
    async def fetch_semantic_api(cls, url):
        async with aiohttp.ClientSession() as session:
            base_url = "https://api.semanticscholar.org/graph/v1/paper/"
            encoded_url = quote(f"URL:{url}")
            fields = "citationCount,venue"
            
            async with session.get(
                f"{base_url}{encoded_url}?fields={fields}"
            ) as response:
                result = await response.json()

            if result:
                # Ensure venue and citationCount are fetched correctly
                venue = result.get("venue", None)
                citation_count = result.get("citationCount", None)
                return venue, citation_count
            else:
                return None, None

async def arxiv_execute(param):
    entries = []

    for item in param:
        
        #pdfの場合の処理
        if "/pdf/" in item["url"]:
            item["url"] = item["url"].replace("/pdf/", "/abs/")
        
        url = item["url"]
        relevant_no = item["relevant_no"]
        cite_num = item["cite_num"]
        scraper = WebScraper(url)
        scraper.fetch_page()

        metadata = scraper.extract_metadata()

        if metadata:
            # Retrieving contents from metadata
            title = metadata.xpath("//meta[@property='og:title']/@content")[0]
            authors = ", ".join(metadata.xpath("//div[@class='authors']/a/text()"))
            conference = metadata.get('publicationTitle', '')
            
            #######
            if metadata.xpath("//td[@class='tablecell comments mathjax']/text()"):
                conf_text = metadata.xpath("//td[@class='tablecell comments mathjax']/text()")[0]
                search_terms = ['Accepted by ', 'Accepted for ', 'Published as', 'accepted', 'publish']
            #######
                
            
            dateline = metadata.xpath("//div[@class='dateline']/text()")[0].strip()
            date_part = dateline.strip('[]').replace('Submitted on ', '')
            clean_date_part = date_part.split(' ')[0:3]
            clean_date_str = ' '.join(clean_date_part)
            date_obj = datetime.strptime(clean_date_str, '%d %b %Y')
            date = date_obj.strftime('%y%m%d')
            
            abstract = metadata.xpath("//meta[@property='og:description']/@content")[0]
            submitted = bool(metadata.xpath("//td[@class='tablecell comments mathjax']/text()"))
            
            status, pages = await PdfCounter.fetch_pdf_pages(url)
            venue, cite_num = await SemanticApi.fetch_semantic_api(url)
            
            new_entry = {
                "url": url,
                "title": title,
                "author": authors,
                "conference": venue,
                "pages": pages,
                "date": date,
                "abstract": abstract,
                "cite_num": cite_num,
                "submitted": submitted,
                "relevant_no": relevant_no,
            }
            entries.append(new_entry)

    return entries