from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view

import psycopg2
import os
# Create your views here.

@api_view(['GET'])
def getData(request):
    
    conn = psycopg2.connect(
        database=os.getenv("DBNAME"),
        user= os.getenv('DBUSER'),
        password=os.getenv('DBPASS'),
        host=os.getenv('DBHOST'),
        port=os.getenv("DBPORT")
    )
    cursor = conn.cursor()
    raw_query = "SELECT VERSION();"
    cursor.execute(raw_query)
    version = cursor.fetchall()
    raw_query = "SELECT pg_database_size('dota2')/1024/1024 as dota2_db_size;"
    cursor.execute(raw_query)
    size = cursor.fetchall()
    return Response({"pgsql": {"version": "{:s}".format(version[0][0]), "dota2_db_size" : size[0][0]}})
