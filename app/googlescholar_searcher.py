from module.acm import acm_execute
from module.arxiv import arxiv_execute
from module.ieee import ieee_execute
import asyncio
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()
# SerpApiのAPIキーを環境変数から取得
api_keys = [value for key, value in os.environ.items() if key.startswith("SERP_APIKEY")]

query ="machine+learning"

# 指定されたドメインのみを許可
allowed_domains = ["https://dl.acm.org/", "https://arxiv.org/", "https://ieeexplore.ieee.org/", "https://www.sciencedirect.com/"]
# 04
async def fetch_results(session, query, start, index):

    for api_key in api_keys:
        params = {
            "engine": "google_scholar",
            "q": query,
            "start": start,
            "api_key": api_key,
            "num": 20
        }
    
        async with session.get("https://serpapi.com/search?", params=params) as response:
            result = await response.json()
            if response.status != 200:#'error' in result and 'Rate limit reached' in result['error']:
                print(f"APIキー {api_key} の使用中にエラーが発生しました。次のAPIキーを試します。")
            else:
                return (index, result)

    raise Exception("すべてのAPIキーが回数制限に達しました")

# 03
async def search_googlescholar(query):
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for i in range(3):
            start = i * 20
            tasks.append(fetch_results(session, query, start, i))
        
        results = await asyncio.gather(*tasks)
        # インデックスでソートして順序を保つ
        results.sort(key=lambda x: x[0])  
        
        url_list = []
        cite_num_list = [] # cite_num（被引用数: apiでいうtotal）とrelevant_noを格納する辞書
        for _, result in results:
            for entry in result.get("organic_results", []):
                link = entry.get("link") 
                cited_by = entry.get('inline_links', {}).get('cited_by', {})
                cite_num = cited_by.get('total')

                if link:
                    # 指定されたドメインのURLのみをリストに追加し、/pdf/を含まない
                    if any(domain in link for domain in allowed_domains) and '/pdf/' not in link:
                        url_list.append(link)
                        cite_num_list.append(cite_num)
        
        # 辞書型のリストを作成
        all_array = [{"url": url, "relevant_no": index} for index, url in enumerate(url_list)]
        cite_num_list = [{"citation_count": cite_count, "relevant_no": index} for index, cite_count in enumerate(cite_num_list)]
        await update_cite_num(all_array, cite_num_list)
        # リストを分ける
        acm_array = [entry for entry in all_array if allowed_domains[0] in entry["url"]]
        arxiv_array = [entry for entry in all_array if allowed_domains[1] in entry["url"]]
        ieee_array = [entry for entry in all_array if allowed_domains[2] in entry["url"]]
        sciencedirect_array = [entry for entry in all_array if allowed_domains[3] in entry["url"]]
        
        return acm_array, arxiv_array, ieee_array, sciencedirect_array, cite_num_list


#05
#被引用数を上書きする処理（all_data:各サイトのスクレイピング処理の返り値を配列にまとめたもの,new_cite:APIによって取得した被引用数と関連度を格納した配列）
#all_dataの関連度とnew_citeの関連度が同じならcite_numを上書きする
async def update_cite_num(all_data, new_cite):
    await asyncio.sleep(0)  # 非同期処理をシミュレート
    for update in new_cite:
        for data in all_data:
            # データがリストの場合
            if isinstance(data, list):
                for item in data:
                    if item['relevant_no'] == update['relevant_no']:
                        item['cite_num'] = update['citation_count']
            # データが辞書の場合
            elif isinstance(data, dict):
                if data['relevant_no'] == update['relevant_no']:
                    data['cite_num'] = update['citation_count']

#02
async def scraping_main(query):
    acm, arxiv, ieee, sciencedirect ,citation_count= await search_googlescholar(query) #テスト用、実装時に消す　acm_test,arxiv_test, ieee_test, sciencedirect_test ,citation_count_test
    result = []
    result.append(await acm_execute(acm))
    result.append(await arxiv_execute(arxiv))
    result.append(await ieee_execute(ieee))

    await update_cite_num(result, citation_count) #被引用数の上書き処理
    print("all_data",result)

    #matchingを呼び出す処理を付け加える
    return result

# #テスト用
# if __name__ == "__main__":
#     query = "fuzzing"
#     asyncio.run(scraping_main(query))