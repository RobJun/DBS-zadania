import api_v4.models
from sqlalchemy.orm import sessionmaker

Regions = api_v4.models.Regions.sa
Matches = api_v4.models.Matches.sa
Heroes = api_v4.models.Heroes.sa
Players = api_v4.models.Players.sa
Player_ratings = api_v4.models.Player_ratings.sa
Items = api_v4.models.Items.sa
MP_details = api_v4.models.MP_details.sa
Player_times = api_v4.models.Player_times.sa
Purchase_logs = api_v4.models.Purchase_logs.sa
Abilities = api_v4.models.Abilities.sa
Chats = api_v4.models.Chats.sa
Objectives = api_v4.models.Objectives.sa
Ability_upgrades = api_v4.models.Ability_upgrades.sa
Teamfigths = api_v4.models.Teamfights.sa
Teamfights_players = api_v4.models.Teamfights_players.sa
Player_action = api_v4.models.Player_actions.sa
Patches = api_v4.models.Patches.sa


def Session():
    from aldjemy.core import get_engine
    engine = get_engine(alias='primary')
    #engine = get_engine()
    _Session = sessionmaker(bind=engine)
    return _Session()