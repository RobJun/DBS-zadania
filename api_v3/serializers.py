
from typing import Dict


def seriliazePurchases(data) -> Dict:
    if data == []:  return {}
    current_hero = None
    player_details = {"id" : data[0][0], "heroes" :[]}
    for row in data:
        if current_hero != row[1]:
            player_details["heroes"].append({"id": row[1], "name": row[2], "top_purchases": []})
            current_hero =  row[1]
        player_details["heroes"][-1]["top_purchases"].append({"id": row[3],"name": row[4],"count" : row[5]})
    return player_details