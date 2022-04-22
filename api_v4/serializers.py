
from typing import Dict

def serializePatches(data) -> Dict:
    patches = []
    current_patch = ""
    for row in data:
        if current_patch != row.id:
            patches.append({"patch_version": row.name,"patch_start_date": row.patch_start_date, "patch_end_date": row.patch_end_date, "matches" : []})
            current_patch = row.id
        if(row.match_id == None and row.duration == None):
           continue
        patches[-1]["matches"].append({"match_id" : row.match_id, "duration" : row.duration})
    return {"patches":  patches}




def serializePlayerExp(data) -> Dict:
    if data == []:  return {}
    player_details = {"id" : data[0]['player__id'], "player_nick" : data[0]['player_nick'], "matches" : []}
    for row in data:
        player_details["matches"].append({"match_id": row['match__id'],
                                        "hero_localized_name": row['hero__localized_name'],
                                        "match_duration_minutes": row['duration_minutes'],
                                        "experiences_gained": row['experiences_gained'],
                                        "level_gained": row['level'],
                                        "winner": row['winner']})
    return player_details



def serializeObjectives(data) -> Dict:
    if data == []:  return {}
    current_match = None
    player_details = {"id" : data[0]['player__id'], "player_nick" : data[0]['player_nick'], "matches" : []}
    for row in data:
        if current_match != (row['match__id'],row['hero__localized_name']):
            player_details["matches"].append({"match_id": row['match__id'], "hero_localized_name": row['hero__localized_name'], "actions": []})
            current_match = (row['match__id'],row['hero__localized_name'])
        player_details["matches"][-1]["actions"].append({"hero_action": row['action'],"count": row['count']})
    return player_details



def serializeAbilities(data) -> Dict:
    if data == []:  return {}
    current_match = None
    player_details = {"id" : data[0]['player__id'], "player_nick" : data[0]['player_nick'], "matches" : []}
    for row in data:
        if current_match != (row['match__id'],row['hero__localized_name']):
            player_details["matches"].append({"match_id": row['match__id'], "hero_localized_name": row['hero__localized_name'], "abilities": []})
            current_match = (row['match__id'],row['hero__localized_name'])
        player_details["matches"][-1]["abilities"].append({"ability_name": row['mpd__ability__name'],"count": row['count'],"upgrade_level": row['upgrade_level']})
    return player_details