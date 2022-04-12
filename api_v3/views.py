from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes
from rest_framework.views import APIView

import psycopg2
import os

from api_v3.serializers import seriliazePurchases,serializeUsage,serializeTowers


def connect():
    return psycopg2.connect(
        database=os.getenv("DBNAME"),
        user= os.getenv('DBUSER'),
        password=os.getenv('DBPASS'),
        host=os.getenv('DBHOST'),
        port=os.getenv("DBPORT")
    )

@api_view(['GET'])
def getTopPurchases(request,id):
    cursor = connect().cursor()
    query='''with res as (SELECT match_id,hero_id,localized_name, item_id,items.name,COUNT(*) FROM matches
INNER JOIN matches_players_details ON match_id = matches.id
INNER JOIN heroes ON heroes.id = hero_id 
LEFT JOIN purchase_logs ON match_player_detail_id = matches_players_details.id
INNER JOIN items ON item_id = items.id
WHERE match_id ={:} and ( matches.radiant_win = (player_slot BETWEEN 0 and 4))
GROUP BY match_id,hero_id,localized_name, item_id,items.name
)
SELECT * FROM (
	SELECT res.*,
	rank() OVER (
		PARTITION BY hero_id
		ORDER BY count DESC,name ASC
	) FROM res
) as res2
WHERE rank <=5
ORDER BY hero_id ASC,rank ASC'''.format(id)
    cursor.execute(query)

    return Response(seriliazePurchases(cursor.fetchall()))


@api_view(['GET'])
def getUsage(request,id):
    cursor = connect().cursor()
    query = '''with ability as (SELECT abilities.id,
				 abilities.name,
				 hero_id,
				 localized_name,
				 matches.radiant_win = (player_slot BETWEEN 0 and 4) as winner,
				 case when 10*FLOOR((time*100/duration)/10) < 101 then 10*FLOOR((time*100/duration)/10) || '-' || 10*FLOOR((time*100/duration)/10)+9
		 		 else '100-109'
				 end bucket,
				 COUNT(*)
				 FROM abilities
				 LEFT JOIN ability_upgrades ON abilities.id = ability_id
				 LEFT JOIN matches_players_details as mpd ON match_player_detail_id = mpd.id
				 LEFT JOIN heroes ON hero_id = heroes.id
				 LEFT JOIN matches ON match_id = matches.id
				 WHERE abilities.id = {:}
				 GROUP BY abilities.id, abilities.name, hero_id, localized_name,winner,bucket
				)
SELECT * FROM (SELECT ability.*,RANK() OVER (
	PARTITION BY hero_id,winner
	ORDER BY count DESC,bucket ASC
) FROM ability) as res
WHERE rank =1
ORDER BY hero_id ASC ,winner DESC'''.format(id)
    cursor.execute(query)
    return Response(serializeUsage(cursor.fetchall()))


@api_view(['GET'])
def getTowerKills(request):
    cursor = connect().cursor()
    query = '''with res as (SELECT hero_id,localized_name,match_id,subtype, time FROM heroes
LEFT JOIN matches_players_details as mpd ON hero_id = heroes.id
LEFT JOIN matches ON match_id = matches.id
LEFT JOIN game_objectives as go ON match_player_detail_id_1 = mpd.id
WHERE go.subtype = 'CHAT_MESSAGE_TOWER_KILL' and time <= duration
ORDER BY match_id ASC, time ASC)
SELECT hero_id,localized_name,max(seqnum) as sequence FROM (
select hero_id,localized_name,match_id,
       row_number() over (partition by hero_id,match_id, grp order by match_id ASC, time ASC) as seqnum
from (select res.*,
             (row_number() over (order by match_id ASC, time ASC) -
              row_number() over (partition by hero_id,match_id order by match_id ASC, time ASC)
             ) as grp
      from res
     ) as t
ORDER BY match_id ASC, time ASC
	) as ta
GROUP BY hero_id,localized_name
ORDER BY sequence DESC, localized_name ASC'''
    cursor.execute(query)
    return Response(serializeTowers(cursor.fetchall()))
