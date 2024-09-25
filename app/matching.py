import polars as pl
from rapidfuzz import process
import json
import asyncio

    
async def fuzzy_match(entry) -> None:
    search_value = fetch_conf_name(entry)

    if search_value != "":
        conf_rank = (
            pl.read_csv("data/conf_n_journal_list.csv")
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
        conf_name = conf_info["title"].to_list()
        conf_tier = conf_info["tier"].to_list()
        if len(conf_name) == 0:
            conf_name = [""]
            conf_tier = [-1]
    else:
        conf_name = [""]
        conf_tier = [-1]
    
    fix_entry(entry, conf_name[0], conf_tier[0])
    

def fetch_conf_name(entry) -> str:
    if entry!=None and entry!={}: 
        if entry["conference"] != None:
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


# MAIN
def match_conferences(entries):
    for entry in entries:
        asyncio.run(fuzzy_match(entry))

    return json.dumps(entries, indent=4) #json形式で出力
