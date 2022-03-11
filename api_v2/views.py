from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view

import psycopg2
import os


'''SELECT 
	name as patch_version,
	patch_start_date,
	patch_end_date,
	matches.id as match_id,
	ROUND((matches.duration::numeric / 60),2)::float as match_duration
    FROM (
	    SELECT name,
	    cast(extract(epoch from release_date) as integer) as patch_start_date,
        cast(extract(epoch from LEAD(release_date,1) OVER (ORDER BY name)) as integer) as patch_end_date
        FROM patches
	) as myquery 
    LEFT JOIN matches ON matches.start_time BETWEEN patch_start_date AND patch_end_date
    ORDER BY name;'''


''''''

# OR
'''
SELECT subtab.id,nick,match_id,localized_name,
ROUND((matches.duration::numeric / 60),2)::float,
COALESCE(matches_players_details.xp_hero,0) + COALESCE(matches_players_details.xp_creep,0)+ COALESCE(matches_players_details.xp_other,0) + COALESCE(matches_players_details.xp_roshan,0) as exp_gained,
matches_players_details.level,
matches.radiant_win = (matches_players_details.player_slot BETWEEN 0 and 4) as winner
FROM (SELECT * FROM players WHERE id = $id) as subtab
INNER JOIN matches_players_details ON subtab.id = player_id
INNER JOIN heroes ON heroes.id = hero_id
INNER JOIN matches ON match_id = matches.id
'''


@api_view(['GET'])
def getPatches(request):
    
    conn = psycopg2.connect(
        database=os.getenv("DBNAME"),
        user= os.getenv('DBUSER'),
        password=os.getenv('DBPASS'),
        host=os.getenv('DBHOST'),
        port=os.getenv("DBPORT")
    )
    cursor = conn.cursor()
    raw_query = '''SELECT 
name as patch_version,
patch_start_date::float,
patch_end_date::float,
matches.id as match_id,
ROUND((matches.duration::numeric / 60),2)::float as match_duration
FROM (
	SELECT name,
	cast(extract(epoch from release_date) as integer) as patch_start_date,
    cast(extract(epoch from LEAD(release_date,1) OVER (ORDER BY name)) as integer) as patch_end_date
    FROM patches
	) as myquery 
INNER JOIN matches ON matches.start_time BETWEEN patch_start_date AND patch_end_date
ORDER BY name,match_id;'''
    cursor.execute(raw_query)
    patches = []
    current_patch = ""
    for row in cursor.fetchall():
        if current_patch != row[0]:
            patches.append({"patch_version": row[0],"patch_start_date": row[1], "patch_end_date": row[2], "matches" : []})
            current_patch = row[0]
        if(row[3] == None and row[4] == None):
            continue
        patches[-1]["matches"].append({"match_id" : row[3], "duration" : row[4]})
    
    return Response({"patches":  patches})


@api_view(['GET'])
def getGame_exp(request,id):

    conn = psycopg2.connect(
        database=os.getenv("DBNAME"),
        user= os.getenv('DBUSER'),
        password=os.getenv('DBPASS'),
        host=os.getenv('DBHOST'),
        port=os.getenv("DBPORT")
    )
    cursor = conn.cursor()
    raw_query = '''SELECT players.id,COALESCE(nick,'unknown') as player_nick,
    localized_name as hero_localized_name,
    ROUND((matches.duration::numeric / 60),2)::float as match_duration_minutes,
    COALESCE(xp_hero,0) + COALESCE(xp_creep,0)+ COALESCE(xp_other,0) + COALESCE(xp_roshan,0) as experiences_gained,
    level as level_gained,
    matches.radiant_win = (matches_players_details.player_slot BETWEEN 0 and 4) as winner,
    match_id
    FROM players
    LEFT JOIN matches_players_details ON players.id = player_id 
    LEFT JOIN heroes ON heroes.id = hero_id
    LEFT JOIN matches ON match_id = matches.id
    WHERE players.id =   {:}
	ORDER BY match_id;'''.format(id)
    cursor.execute(raw_query)
    rows = cursor.fetchall()
    if rows == []:  return Response({})
    player_details = {"id" : rows[0][0], "player_nick" : rows[0][1], "matches" : []}
    for row in rows:
        player_details["matches"].append({"match_id": row[7],
                                        "hero_localized_name": row[2],
                                        "match_duration_minutes": row[3],
                                        "experiences_gained": row[4],
                                        "level_gained": row[5],
                                        "winner": row[6]})
        
    return Response(player_details)

@api_view(['GET'])
def getObjectives(request, id):
    conn = psycopg2.connect(
        database=os.getenv("DBNAME"),
        user= os.getenv('DBUSER'),
        password=os.getenv('DBPASS'),
        host=os.getenv('DBHOST'),
        port=os.getenv("DBPORT")
    )
    cursor = conn.cursor()
    raw_query = '''SELECT players.id,COALESCE(nick,'unknown') as player_nick,localized_name as hero_localized_name,
	match_id,COALESCE(subtype,'NO_ACTION'), COUNT(COALESCE(subtype,'NO_ACTION'))
    FROM players
   	LEFT JOIN matches_players_details ON players.id = player_id
    LEFT JOIN heroes ON heroes.id = hero_id
	LEFT JOIN game_objectives ON match_player_detail_id_1 = matches_players_details.id
	WHERE players.id =  {:}
	GROUP BY  players.id,COALESCE(nick,'unknown'),localized_name,
	match_id,subtype
	ORDER BY match_id,localized_name;'''.format(id)
    cursor.execute(raw_query)
    rows = cursor.fetchall()
    if rows == []:  return Response({})
    current_match = None
    player_details = {"id" : rows[0][0], "player_nick" : rows[0][1], "matches" : []}
    for row in rows:
        if current_match != (row[3],row[2]):
            player_details["matches"].append({"match_id": row[3], "hero_localized_name": row[2], "actions": []})
            current_match = (row[3],row[2])
        player_details["matches"][-1]["actions"].append({"hero_action": row[4],"count": row[5]})
    return Response(player_details)


@api_view(['GET'])
def getAbilities(request, id):
    return Response({"id" : id})