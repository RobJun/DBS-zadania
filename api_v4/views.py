from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes
from rest_framework.views import APIView

from api_v4.models import MP_details, Matches, Patches, Players


from rest_framework import serializers
from django.db.models.functions import Cast,Extract,Lead,Round,Coalesce
from django.db.models.expressions import Window
from django.db import models
from django.db.models import F,Subquery,OuterRef,Value, Q,Count, Max
from django_cte import With
from django.db.models.sql.constants import LOUTER

from api_v4.serializers import serializeObjectives, serializePatches, serializePlayerExp,serializeAbilities


@api_view(['GET'])
def getPatches(req):
     cte = With(
          Matches.objects.annotate(duration_decimal=Cast('duration',output_field=models.DecimalField(max_digits=15,decimal_places=4)))\
           .annotate(duration_minutes=Round(F('duration_decimal')/60,precision=2)).values('id','duration_minutes','start_time')
     )

     matches = cte.join(Patches.objects.annotate(patch_start_date=Extract('release_date','epoch')).annotate(patch_end_date=Subquery(
               Patches.objects.annotate(end_date=Extract('release_date','epoch')).filter(id=OuterRef('id')+1).values('end_date')[:1]
          )),patch_start_date__lte=cte.col.start_time,patch_end_date__gte=cte.col.start_time,_join_type=LOUTER).with_cte(cte)\
          .annotate(match_id=cte.col.id,duration=cte.col.duration_minutes).order_by('name')
     print(matches.query)
     return Response(serializePatches(matches))

@api_view(['GET'])
def getGame_exp(req,id):
     players = MP_details.objects.annotate(player_nick=Coalesce('player__nick',Value('unknown',output_field=models.TextField()))
               ).annotate(experiences_gained= Coalesce('xp_hero',Value(0)) + Coalesce('xp_creep',Value(0)) + Coalesce('xp_other',Value(0)) +  Coalesce('xp_roshan',Value(0))
               ).annotate(duration_decimal=Cast('match__duration',output_field=models.DecimalField(max_digits=15,decimal_places=4))
               ).annotate(duration_minutes=Round(F('duration_decimal')/60,precision=2)
               ).annotate(winnerT=models.ExpressionWrapper(
                    Q(player_slot__gte = 0,player_slot__lte=4),
                    output_field=models.BooleanField()
               )).annotate(
                    winner=models.ExpressionWrapper(
                    Q(winnerT=F('match__radiant_win')),
                    output_field=models.BooleanField()
               )
               ).filter(player__id=id).order_by('match__id')\
               .values('player__id','player_nick','duration_minutes','hero__localized_name','experiences_gained','level','winner','match__id')
     return Response(serializePlayerExp(players))

@api_view(['GET'])
def getObjectives(req,id):
     players = MP_details.objects.filter(player__id=id
     ).annotate(player_nick=Coalesce('player__nick',Value('unknown',output_field=models.TextField()))
     ).annotate(action=Coalesce('mpd1__subtype',Value('NO_ACTION',output_field=models.TextField()))
     ).values('match__id','player__id','player_nick','hero__localized_name','action').annotate(count=Count('action')).order_by('match__id','hero__localized_name')

     return Response(serializeObjectives(players))

@api_view(['GET'])
def getAbilities(req,id):
     players = MP_details.objects.filter(player__id=id
     ).annotate(player_nick=Coalesce('player__nick',Value('unknown',output_field=models.TextField()))
     ).values('match__id','player__id','player_nick','hero__localized_name','mpd__ability__name').annotate(upgrade_level=Max('mpd__level'), count=Count('mpd__ability__name')
     ).order_by('match__id','mpd__ability__name')

     for p in players:
          print(p['match__id'],p['player__id'],p['player_nick'],p['hero__localized_name'],p['mpd__ability__name'],p['upgrade_level'],p['count'])
     return Response(serializeAbilities(players))

@api_view(['GET'])
def getTopPurchases(req,id):
     return Response({})

@api_view(['GET'])
def getUsage(req,id):
     return Response({})

@api_view(['GET'])
def getTowerKills(req):
     return Response({})