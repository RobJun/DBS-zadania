from requests import session
from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes
from rest_framework.views import APIView
from api_v4 import sa

from api_v4.models import MP_details, Matches, Patches, Players
from api_v2.serializers import serializePatches,serializePlayerExp,serializeObjectives,serializeAbilities
from api_v3.serializers import seriliazePurchases,serializeUsage,serializeTowers
from rest_framework import serializers
from django.db.models.functions import Cast,Extract,Lead,Round,Coalesce,Rank,Floor
from django.db.models.expressions import Window
from django.db import models
from django.db.models import F,Subquery,OuterRef,Value, Q,Count, Max,When,Case
from django_cte import With
from django.db.models.sql.constants import LOUTER

from api_v4.sa import Heroes, Objectives, Session
from sqlalchemy import select,Numeric,cast,extract,Integer,and_,Text
from sqlalchemy.orm  import aliased
from sqlalchemy.sql import func,case,desc
from . import sa

@api_view(['GET'])
def getPatches(req):
     session = Session()
     matches = select(sa.Matches.id,
                    sa.Matches.start_time,
                    func.round(cast(sa.Matches.duration, Numeric(10,2))/60,2).label('duration_minutes')
                    ).subquery()
     patches = select(sa.Patches.name,
                    cast(extract('EPOCH',sa.Patches.release_date),Integer).label('release_date'),
                    func.lead(
                          cast(extract('EPOCH',
                              sa.Patches.release_date),Integer),1).over(order_by='id').label('end_date')
                     ).subquery()
     fin = select(patches,matches.c.id,matches.c.duration_minutes).join(matches,
          and_(matches.c.start_time >= patches.c.release_date,  matches.c.start_time <= patches.c.end_date),
          isouter=True)
     print(str(fin))
     return Response(serializePatches(session.execute(fin).all()))

@api_view(['GET'])
def getGame_exp(req,id):
     session = Session()
     players = select(
          sa.Players.id,
          sa.Heroes.localized_name,
          func.round(cast(
               sa.Matches.duration,
               Numeric(10,2))/60,2).label('duration_minutes'),
          func.coalesce(sa.Players.nick,'unknown'),
          func.coalesce(sa.MP_details.xp_hero,0) +
          func.coalesce(sa.MP_details.xp_creep,0) + 
          func.coalesce(sa.MP_details.xp_other,0) + 
          func.coalesce(sa.MP_details.xp_roshan,0),
          sa.MP_details.level,
          sa.Matches.radiant_win == and_(sa.MP_details.player_slot >=0, sa.MP_details.player_slot <= 4),
          sa.Matches.id,
          ).select_from(sa.Players).\
          join(sa.MP_details).\
          join(sa.Matches).\
          join(sa.Heroes).\
          filter(sa.Players.id == id).order_by(sa.Matches.id)
     print(str(players))
     return Response(serializePlayerExp(session.execute(players).all()))

@api_view(['GET'])
def getObjectives(req,id):
     session = Session()
     players = select(
          sa.Players.id,
          func.coalesce(sa.Players.nick,'unknown'),
          sa.Heroes.localized_name,
          sa.Matches.id,
          func.coalesce(sa.Objectives.subtype,'NO_ACTION'),
          func.count(func.coalesce(sa.Objectives.subtype,'NO_ACTION'))

     ).select_from(sa.Players).\
     join(sa.MP_details).\
     join(sa.Matches).\
     join(sa.Heroes).\
     join(sa.Objectives,
          sa.Objectives.match_player_detail_id_1 == sa.MP_details.id,isouter=True).\
     group_by(sa.Players.id,
          func.coalesce(sa.Players.nick,'unknown'),
          sa.Heroes.localized_name,
          sa.Matches.id,
          sa.Objectives.subtype).filter(sa.Players.id == id).order_by(sa.Matches.id,sa.Heroes.localized_name)
     print(str(players))
     #
     #players = MP_details.objects.filter(player__id=id
     #).annotate(player_nick=Coalesce('player__nick',Value('unknown',output_field=models.TextField()))
     #).annotate(action=Coalesce('mpd1__subtype',Value('NO_ACTION',output_field=models.TextField()))
     #).values('match__id','player__id','player_nick','hero__localized_name','action').annotate(count=Count('action')).order_by('match__id','hero__localized_name')
     #
     return Response(serializeObjectives(session.execute(players).all()))

@api_view(['GET'])
def getAbilities(req,id):
     session = Session()
     players = select(
          sa.Players.id,
          func.coalesce(sa.Players.nick,'unknown'),
          sa.Heroes.localized_name,
          sa.Matches.id,
          sa.Abilities.name,
          func.count('*'),
          func.max(sa.Ability_upgrades.level)
     ).select_from(sa.Players).\
     join(sa.MP_details).\
     join(sa.Matches).\
     join(sa.Heroes).\
     join(sa.Ability_upgrades).\
     join(sa.Abilities).\
     group_by(
          sa.Players.id,
          func.coalesce(sa.Players.nick,'unknown'),
          sa.Heroes.localized_name,
          sa.Matches.id,
          sa.Abilities.name,
     ).filter(sa.Players.id==id).order_by(sa.Matches.id,sa.Abilities.name)
     print(str(players))
     #
     #players = MP_details.objects.filter(player__id=id
     #).annotate(player_nick=Coalesce('player__nick',Value('unknown',output_field=models.TextField()))
     #).values('match__id','player__id','player_nick','hero__localized_name','mpd__ability__name').annotate(upgrade_level=Max('mpd__level'), count=Count('mpd__ability__name')
     #).order_by('match__id','mpd__ability__name')

     #for p in players:
     #     print(p['match__id'],p['player__id'],p['player_nick'],p['hero__localized_name'],p['mpd__ability__name'],p['upgrade_level'],p['count'])
     #return Response(seriliazePurchases(players))
     return Response(serializeAbilities(session.execute(players).all()))

#Todo
@api_view(['GET'])
def getTopPurchases(req,id):
     session = Session()
     purchases = select(
          sa.Matches.id,
          sa.Heroes.id,
          sa.Heroes.localized_name,
          sa.Items.id,
          sa.Items.name,
          func.count('*')
     ).select_from(sa.Matches).\
     join(sa.MP_details).\
     join(sa.Heroes).\
     join(sa.Purchase_logs).\
     join(sa.Items).\
     filter(and_(sa.Matches.id == id, 
          sa.Matches.radiant_win == and_(sa.MP_details.player_slot >=0,
                                         sa.MP_details.player_slot <= 4))
     ).group_by(
          sa.Matches.id,
          sa.Heroes.id,
          sa.Heroes.localized_name,
          sa.Items.id,
          sa.Items.name,
     ).subquery()
     print(str(purchases))

     rankPurchases = select(purchases, 
          func.rank().over(
               partition_by=purchases.c.id_1,
               order_by=[purchases.c.count.desc(),purchases.c.name]
          ).label('rank')
     ).subquery()
     print(str(rankPurchases))

     topPurchases = select(
          rankPurchases
     ).filter(rankPurchases.c.rank < 6).order_by(rankPurchases.c.id_1,rankPurchases.c.rank)
     return Response(seriliazePurchases(session.execute(topPurchases).all()))

@api_view(['GET'])
def getUsage(req,id):
     session = Session()
     totalUsage = select(
          sa.Abilities.id,
          sa.Abilities.name,
          sa.Heroes.id.label('hero_id'),
          sa.Heroes.localized_name,
          (sa.Matches.radiant_win == and_(sa.MP_details.player_slot >=0, sa.MP_details.player_slot <= 4)).label('winner'),
          case(
               (10*func.floor((sa.Ability_upgrades.time*100/sa.Matches.duration)/10) < 101,
                              (cast((10*func.floor((sa.Ability_upgrades.time*100/sa.Matches.duration)/10)),Text)+"-"+
                              (cast(10*func.floor((sa.Ability_upgrades.time*100/sa.Matches.duration)/10) + 9,Text)))
               ),
               else_='100-109'
          ).label('bucket'),
          func.count('*')
     ).select_from(sa.Abilities).\
     join(sa.Ability_upgrades).\
     join(sa.MP_details).\
     join(sa.Heroes).\
     join(sa.Matches).filter(sa.Abilities.id==id).group_by(
          sa.Abilities.id,
          sa.Abilities.name,
          sa.Heroes.id,
          sa.Heroes.localized_name,
          sa.Matches.radiant_win == and_(sa.MP_details.player_slot >=0, sa.MP_details.player_slot <= 4),
          'bucket'
     ).subquery()
     print(str(totalUsage))
     usage = select(
          totalUsage,func.rank().over(
               partition_by=[totalUsage.c.hero_id,totalUsage.c.winner],
               order_by=[totalUsage.c.count.desc(),totalUsage.c.bucket.asc()]
          ).label('rank')
     ).subquery()
     UsageNum1 = select(
          usage
     ).filter(usage.c.rank == 1).order_by(usage.c.hero_id,usage.c.winner)
     return Response(serializeUsage(session.execute(UsageNum1).all()))

@api_view(['GET'])
def getTowerKills(req):
     session = Session()
     towers = select(
          sa.Heroes.id.label('hero_id'),
          sa.Heroes.localized_name,
          sa.MP_details.match_id.label('match_id'),
          sa.Objectives.time
     ).select_from(sa.Heroes).\
     join(sa.MP_details,isouter=True).\
     join(sa.Matches).\
     join(sa.Objectives,sa.MP_details.id == sa.Objectives.match_player_detail_id_1).\
     filter(and_(
          sa.Objectives.subtype == 'CHAT_MESSAGE_TOWER_KILL',
          sa.Objectives.time <= sa.Matches.duration
          )
     ).subquery()

     rankTowers = select(
          towers,
          (func.row_number().over(
               order_by=[towers.c.match_id,towers.c.time]
          ) - func.row_number().over(
               partition_by=[towers.c.hero_id,towers.c.match_id],
               order_by=[towers.c.match_id,towers.c.time]
          )
          ).label('poradie')
     ).subquery()

     rankedTowers = select(
          rankTowers.c.hero_id,
          rankTowers.c.localized_name,
          func.row_number().over(
               partition_by=[rankTowers.c.hero_id,rankTowers.c.match_id,rankTowers.c.poradie],
               order_by=[rankTowers.c.match_id,rankTowers.c.time]
          ).label('seq')
     )

     finTowers = select(
          rankedTowers.c.hero_id,
          rankedTowers.c.localized_name,
          func.max(rankedTowers.c.seq).label('sequence')
     ).group_by(
          rankedTowers.c.hero_id,
          rankedTowers.c.localized_name
     ).order_by(
          desc('sequence'),
          rankedTowers.c.localized_name.asc()
     )

     return Response(serializeTowers(session.execute(finTowers).all()))