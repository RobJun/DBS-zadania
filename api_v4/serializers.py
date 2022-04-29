
from typing import Dict

def serializeAbilities(data) -> Dict:
    if data.count() == 0:  return {}
    current_match = None
    player_details = {"id" : data[0]['player__id'], "player_nick" : data[0]['player_nick'], "matches" : []}
    for row in data:
        if current_match != (row['match__id'],row['hero__localized_name']):
            player_details["matches"].append({"match_id": row['match__id'], "hero_localized_name": row['hero__localized_name'], "abilities": []})
            current_match = (row['match__id'],row['hero__localized_name'])
        player_details["matches"][-1]["abilities"].append({"ability_name": row['mpd__ability__name'],"count": row['count'],"upgrade_level": row['upgrade_level']})
    return player_details


    
def seriliazePurchases(data) -> Dict:
    if data.count() == 0:  return {}
    current_hero = None
    purchases = {"id" : data[0]['M_match_id'], "heroes" :[]}
    for row in data:
        if current_hero != row['M_hero_id']:
            purchases["heroes"].append({"id": row['M_hero_id'], "name": row['M_hero_localized_name'], "top_purchases": []})
            current_hero =  row['M_hero_id']
        purchases["heroes"][-1]["top_purchases"].append({"id": row['M_item_id'],"name": row['M_item_name'],"count" : row['pur_count']})
    return purchases


def serializeUsage(data)-> Dict:
    if len(data) == 0:  return {}
    usage = {"id": data[0].ability_id,"name":data[0].name,"heroes" : []}
    current_hero = None
    for row in data:
        if current_hero != row.hero_id:
            usage["heroes"].append({"id": row.hero_id,"name": row.localized_name})
            current_hero = row.hero_id
        if(row.winner): usage["heroes"][-1]["usage_winners"] = {"bucket" : row.bucket,"count" : row.count}
        elif(not row.winner): usage["heroes"][-1]["usage_loosers"] = {"bucket" : row.bucket,"count" : row.count}

    return usage
