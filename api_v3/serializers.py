
from typing import Dict


def seriliazePurchases(data) -> Dict:
    if data == []:  return {}
    current_hero = None
    purchases = {"id" : data[0][0], "heroes" :[]}
    for row in data:
        if current_hero != row[1]:
            purchases["heroes"].append({"id": row[1], "name": row[2], "top_purchases": []})
            current_hero =  row[1]
        purchases["heroes"][-1]["top_purchases"].append({"id": row[3],"name": row[4],"count" : row[5]})
    return purchases



def serializeUsage(data)-> Dict:
    if data == []:  return {}
    usage = {"id": data[0][0],"name":data[0][1],"heroes" : []}
    current_hero = None
    for row in data:
        if current_hero != row[2]:
            usage["heroes"].append({"id": row[2],"name": row[3],"usage_winners" : {},"usage_loosers":{}})
            current_hero = row[2]
        if(row[4]): usage["heroes"][-1]["usage_winners"] = {"bucket" : row[5],"count" : row[6]}
        else: usage["heroes"][-1]["usage_loosers"] = {"bucket" : row[5],"count" : row[6]}

    return usage