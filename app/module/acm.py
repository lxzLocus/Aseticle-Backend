import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
from lxml import html
from datetime import datetime
from urllib.parse import quote
from dotenv import load_dotenv
import os

# 環境変数を読み込む
load_dotenv()

proxies = [
	os.getenv("PROXY1"),
    os.getenv("PROXY2")
]
proxy_index = 0

# プロキシを交互に選択する関数2
def get_next_proxy():
    global proxy_index
    proxy = proxies[proxy_index]
    proxy_index = (proxy_index + 1) % len(proxies)
    return f"http://{proxy}"

class WebScraper:

    def __init__(self, url):
        self.url = url

    async def fetch_page(self, session):
        proxy = get_next_proxy()
        async with session.get(self.url, proxy=proxy) as response:
            content = await response.text()
            soup = BeautifulSoup(content, "lxml")
            soup_str = str(soup)
            soup_bytes = bytes(soup_str, encoding="utf8")
            return html.fromstring(soup_bytes)

class SemanticApi:
    @classmethod
    async def fetch_metadata(cls, session, url):
        # URLエンコード
        encoded_url = quote(f"URL:{url}")
        paper_url = encoded_url.replace("#core-collateral-info", "")

        # ベースURL
        base_url = "https://api.semanticscholar.org/graph/v1/paper/"
        fields = "abstract,authors,citationCount,influentialCitationCount,venue,publicationVenue"
        
        full_url = f"{base_url}{paper_url}?fields={fields}"

        try:
            # 非同期リクエストを送信
            async with session.get(full_url) as response:
                res = await response.text()
                
                # JSONデータを解析
                res_json = json.loads(res)
                
                # 指定されたフィールドを抽出
                venue = res_json.get("venue")
                citation_count = res_json.get("citationCount")
                author_list = res_json.get("authors")
                if author_list:
                    author_names = [author["name"] for author in author_list]
                    authors=", ".join(author_names)
                else:
                    authors = None
                if res_json.get("abstract") and res_json.get("abstract") != "[]":
                    api_abs = res_json.get("abstract")
                else:
                    api_abs = None

            
                return venue, citation_count, authors, api_abs
        except:
            return None, None, None, None
        async with session.get(full_url) as response:
            res = await response.text()
            res_json = json.loads(res)
            
            venue = res_json.get("venue")
            citation_count = res_json.get("citationCount")
            author_list = res_json.get("authors")
            if author_list:
                author_names = [author["name"] for author in author_list]
                authors = ", ".join(author_names)
            else:
                authors = None
            if res_json.get("abstract") and res_json.get("abstract") != "[]":
                api_abs = res_json.get("abstract")
            else:
                api_abs = None
        
            return venue, citation_count, authors, api_abs


async def fetch_data(session, siteInfo):
    scraper = WebScraper(siteInfo["url"])
    acm_data = await scraper.fetch_page(session)
    venue, citation_count, authors, api_abs = await SemanticApi.fetch_metadata(session, siteInfo["url"])
    
    return siteInfo, acm_data, venue, citation_count, authors, api_abs


async def load_site_contents(siteData):
    entries = []
    async with aiohttp.ClientSession() as session:
        try:
            tasks = [fetch_data(session, siteInfo) for siteInfo in siteData]
            results = await asyncio.gather(*tasks)
            
            for siteInfo, acm_data, venue, citetion_count, authors, api_abs in results:
                # Title
                title = acm_data.xpath("//meta[@property='og:title']/@content")[0]
                
                # Author
                # author = acm_data.xpath("span[contains(@property, 'givenName')]/text()")
                
                # Conference 
                if acm_data.xpath("//*[@id='skip-to-main-content']/main/article/header/div/div[4]/div[1]/a/text()"):
                    conf_explain = acm_data.xpath("//*[@id='skip-to-main-content']/main/article/header/div/div[4]/div[1]/a/text()")[0]
                    conf_text = conf_explain.split()[0]
                    if venue:   #要確認
                        conference = venue
                    else:
                        conference = conf_text  
                else:
                    conference = None
                
                # Pages
                if acm_data.xpath("//*[@id='skip-to-main-content']/main/article/header/div/div[4]/div[3]/span[1]/text()")[0]:
                    start_page = int(acm_data.xpath("//*[@id='skip-to-main-content']/main/article/header/div/div[4]/div[3]/span[1]/text()")[0])
                    end_page = int(acm_data.xpath("//*[@id='skip-to-main-content']/main/article/header/div/div[4]/div[3]/span[2]/text()")[0])
                    pages = pages = end_page - start_page + 1
                else:
                    pages = None
                
                # Date
                dateline = acm_data.xpath("//*[@id='skip-to-main-content']/main/article/header/div/div[5]/span[2]/text()")[0].strip()
                date_obj = datetime.strptime(dateline, '%d %B %Y')
                date = date_obj.strftime('%Y%m%d')
                
                # Abstract
                if api_abs:
                    abstract = api_abs
                elif acm_data.xpath("//*[@id='abstract']/div/text()"):
                    abstract=acm_data.xpath("//*[@id='abstract']/div/text()")
                else:
                    abstract = None
                
                # Cite num 要確認
                cite_num = citetion_count
                
                # Submitted ACMは常にtrue
                submitted = True
        except:
            title = None
            authors = None
            conference = None
            pages = None
            date = None
            abstract = None
            cite_num = None
            submitted = None
            
        # エントリーを追加する
        add_entry(siteInfo["url"], title, authors, conference, pages, date, abstract, cite_num, submitted, siteInfo["relevant_no"])


# エントリーを追加する関数
def add_entry(url, title, author, conference, pages, date, abstract, cite_num, submitted, relevant_no):
    global entries
    new_entry = {
        "url": url,
        "title": title,
        "author": author,
        "conference": conference,
        "pages": pages,
        "date": date,
        "abstract": abstract,
        "cite_num": cite_num,
        "submitted": submitted,
        "relevant_no": relevant_no,
    }
    entries.append(new_entry)


#MAIN
def load_acm_contents(siteData):
    asyncio.run(load_site_contents(siteData))

        tasks = [fetch_data(session, siteInfo) for siteInfo in siteData]
        results = await asyncio.gather(*tasks)
        
        for siteInfo, acm_data, venue, citation_count, authors, api_abs in results:
            title = acm_data.xpath("//meta[@property='og:title']/@content")[0]
            
            try:
                conf_explain = acm_data.xpath("//*[@id='skip-to-main-content']/main/article/header/div/div[4]/div[1]/a/text()")[0]
                conf_text = conf_explain.split()[0]
                conference = venue if venue else conf_text
            except:
                conference = None
            
            try:
                start_page = int(acm_data.xpath('//span[@property="pageStart"]/text()')[0])
                end_page = int(acm_data.xpath('//span[@property="pageEnd"]/text()')[0])
                pages = end_page - start_page + 1
            except:
                pages = None
            
            dateline = acm_data.xpath("//*[@id='skip-to-main-content']/main/article/header/div/div[5]/span[2]/text()")[0].strip()
            date_obj = datetime.strptime(dateline, '%d %B %Y')
            date = date_obj.strftime('%Y%m%d')
            
            abstract = api_abs if api_abs else (acm_data.xpath("//*[@id='abstract']/div/text()") or [None])[0]
            
            cite_num = citation_count
            submitted = True
            
            new_entry = {
                "url": siteInfo["url"],
                "title": title,
                "author": authors,
                "conference": conference,
                "pages": pages,
                "date": date,
                "abstract": abstract,
                "cite_num": cite_num,
                "submitted": submitted,
                "relevant_no": siteInfo["relevant_no"],
            }
            entries.append(new_entry)
    
    return entries

async def acm_execute(siteData):
    entries = await load_site_contents(siteData)
    return entries
