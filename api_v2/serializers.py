

from typing import Dict


def serializePatches(data) -> Dict:
    patches = []
    current_patch = ""
    for row in data:
        if current_patch != row[0]:
            patches.append({"patch_version": row[0],"patch_start_date": float(row[1]), "patch_end_date": float(row[2]), "matches" : []})
            current_patch = row[0]
        if(row[3] == None and row[4] == None):
           continue
        patches[-1]["matches"].append({"match_id" : row[3], "duration" : row[4]})
    return {"patches":  patches}


def serializePlayerExp(data) -> Dict:
    if data == []:  return {}
    player_details = {"id" : data[0][0], "player_nick" : data[0][1], "matches" : []}
    for row in data:
        player_details["matches"].append({"match_id": row[7],
                                        "hero_localized_name": row[2],
                                        "match_duration_minutes": row[3],
                                        "experiences_gained": row[4],
                                        "level_gained": row[5],
                                        "winner": row[6]})
    return player_details


def serializeObjectives(data) -> Dict:
    if data == []:  return {}
    current_match = None
    player_details = {"id" : data[0][0], "player_nick" : data[0][1], "matches" : []}
    for row in data:
        if current_match != (row[3],row[2]):
            player_details["matches"].append({"match_id": row[3], "hero_localized_name": row[2], "actions": []})
            current_match = (row[3],row[2])
        player_details["matches"][-1]["actions"].append({"hero_action": row[4],"count": row[5]})
    return player_details

def serializeAbilities(data) -> Dict:
    if data == []:  return {}
    current_match = None
    player_details = {"id" : data[0][0], "player_nick" : data[0][1], "matches" : []}
    for row in data:
        if current_match != (row[3],row[2]):
            player_details["matches"].append({"match_id": row[3], "hero_localized_name": row[2], "abilities": []})
            current_match = (row[3],row[2])
        player_details["matches"][-1]["abilities"].append({"ability_name": row[4],"count": row[5],"upgrade_level": row[6]})
    return player_details