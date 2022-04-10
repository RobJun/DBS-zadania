from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes
from rest_framework.views import APIView

import psycopg2
import os

from api_v3.serializers import seriliazePurchases


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
    query='''with res as (SELECT match_id,hero_id,localized_name, item_id,items.name,COUNT(*) FROM matches_players_details
INNER JOIN heroes ON heroes.id = hero_id 
LEFT JOIN purchase_logs ON match_player_detail_id = matches_players_details.id
INNER JOIN items ON item_id = items.id
WHERE match_id ={:}
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
def dummy(request):
    return Response({"dummy" : "dummy"})
