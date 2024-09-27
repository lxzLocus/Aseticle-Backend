import polars as pl
from rapidfuzz import process
import json
import asyncio
from datetime import datetime
    
async def fuzzy_match(entry) -> None:
    search_value = fetch_conf_name(entry)

    if search_value != "":
        conf_rank = (
            pl.read_csv("/app/data/conf_n_journal_list.csv")  # 修正: フルパスを指定
            .filter(
                (pl.col("title").str
                .contains(pl.col("title")
                .map_batches(lambda s: fuzzy_match_score(search_value, s)))
                ) |
                (pl.col("acronym").str
                .contains(pl.col("acronym")
                .map_batches(lambda s: fuzzy_match_score(search_value, s)))
                )
            )
            .select(["title", "tier"])
        )
        
        #変換
        conf_info = conf_rank.to_dict()
        conf_name = conf_info["title"]
        conf_tier = conf_info["tier"]
        if len(conf_name) == 0:
            conf_name = [""]
            conf_tier = [99]
    else:
        conf_name = [""]
        conf_tier = [99]
    
    fix_entry(entry, conf_name[0], conf_tier[0])
    

def fetch_conf_name(entry) -> str:
    if entry != None and entry != {}:
        if "conference" in entry and entry["conference"] != None:
            return entry["conference"]
    
    return ""

def fuzzy_match_score(search_value, series):
    ans = process.extractOne(search_value, series)
    if ans[1] < 90:
        return "hoge zxqjb"
    return ans[0]
    

def fix_entry(entry, fixed_conf_name, tier):
    # 引数のクエリに対して、(可能であれば)会議名の修正とtierデータを追加
    if fixed_conf_name != "":
        entry["conference"] = fixed_conf_name
    entry["tier"] = tier

def default_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

# MAIN
async def match_conferences(entries):
    tasks = [asyncio.create_task(fuzzy_match(entry)) for entry in entries]
    await asyncio.gather(*tasks)
    return json.dumps(entries, default=default_converter, indent=4)  # json形式で出力