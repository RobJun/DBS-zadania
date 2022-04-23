from django.db import models
from django_cte import CTEManager


class Regions(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    class Meta:
        db_table='cluster_regions'
        managed=False

class Matches(models.Model):
    objects = CTEManager()
    id = models.IntegerField(primary_key=True)
    cluster_region = models.ForeignKey(Regions,on_delete=models.CASCADE)
    start_time = models.IntegerField()
    duration = models.IntegerField()
    tower_status_radiant = models.IntegerField()
    tower_status_dire = models.IntegerField()
    barracks_status_radiant = models.IntegerField()
    barracks_status_dire = models.IntegerField()
    first_blood_time = models.IntegerField()
    game_mode = models.IntegerField()
    radiant_win = models.BooleanField()
    negative_votes =  models.IntegerField()
    positive_votes =  models.IntegerField()
    class Meta:
        db_table='matches'
        managed=False


class Heroes(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    localized_name = models.TextField()
    class Meta:
        db_table='heroes'
        managed=False

class Players(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    nick = models.TextField()
    class Meta:
        db_table='players'
        managed=False


class Player_ratings(models.Model):
    id = models.IntegerField(primary_key=True)
    player = models.ForeignKey(Players,on_delete=models.CASCADE)
    total_wins = models.IntegerField()
    total_matches = models.IntegerField()
    trueskill_mu = models.DecimalField(max_digits=15,decimal_places=4)
    trueskill_sigma = models.DecimalField(max_digits=15,decimal_places=4)
    class Meta:
        db_table='player_ratings'
        managed=False


class Items(models.Model):
     id = models.IntegerField(primary_key=True)
     name = models.TextField()
     class Meta:
        db_table='items'
        managed=False


class MP_details(models.Model):
    class Meta:
        db_table='matches_players_details'
        managed=False
    objects = CTEManager()
    id = models.IntegerField(primary_key=True)
    match = models.ForeignKey(Matches,on_delete=models.CASCADE)
    player = models.ForeignKey(Players,on_delete=models.CASCADE)
    hero = models.ForeignKey(Heroes,on_delete=models.CASCADE)
    player_slot = models.IntegerField()
    gold = models.IntegerField()
    gold_spent = models.IntegerField()
    gold_per_min = models.IntegerField()
    xp_per_min = models.IntegerField()
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    denies = models.IntegerField()
    last_hits = models.IntegerField()
    stuns = models.IntegerField()
    hero_damage = models.IntegerField()
    item_1 = models.ForeignKey(Items,on_delete=models.CASCADE, db_column='item_id_1', related_name='item1')
    item_2 = models.ForeignKey(Items,on_delete=models.CASCADE, db_column='item_id_2', related_name='item2')
    item_3 = models.ForeignKey(Items,on_delete=models.CASCADE, db_column='item_id_3', related_name='item3')
    item_4 = models.ForeignKey(Items,on_delete=models.CASCADE, db_column='item_id_4', related_name='item4')
    item_5 = models.ForeignKey(Items,on_delete=models.CASCADE, db_column='item_id_5', related_name='item5')
    item_6 = models.ForeignKey(Items,on_delete=models.CASCADE, db_column='item_id_6', related_name='item6')
    level = models.IntegerField()
    leaver_status = models.IntegerField()
    xp_hero = models.IntegerField()
    xp_creep = models.IntegerField()
    xp_roshan = models.IntegerField()
    xp_other = models.IntegerField()
    gold_other = models.IntegerField()
    gold_death = models.IntegerField()
    gold_buyback = models.IntegerField()
    gold_abandon = models.IntegerField()
    gold_sell = models.IntegerField()
    gold_destroying_structure = models.IntegerField()
    gold_killing_heroes = models.IntegerField()
    gold_killing_creeps = models.IntegerField()
    gold_killing_roshan = models.IntegerField()
    gold_killing_couriers = models.IntegerField()


class Player_times(models.Model):
    id = models.IntegerField(primary_key=True)
    match_player_detail = models.ForeignKey(MP_details,on_delete=models.CASCADE)
    time = models.IntegerField()
    gold = models.IntegerField()
    lh = models.IntegerField()
    xp = models.IntegerField()
    class Meta:
        db_table='player_times'
        managed=False

class Purchase_logs(models.Model):
    id = models.IntegerField(primary_key=True)
    match_player_detail = models.ForeignKey(MP_details,on_delete=models.CASCADE, related_name='purchases')
    item = models.ForeignKey(Items,on_delete=models.CASCADE)
    time = models.IntegerField()
    class Meta:
        db_table='purchase_logs'
        managed=False

class Abilities(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    class Meta:
        db_table='abilities'
        managed=False

class Chats(models.Model):
    id = models.IntegerField(primary_key=True)
    match_player_detail = models.ForeignKey(MP_details,on_delete=models.CASCADE)
    message = models.TextField()
    time = models.IntegerField()
    nick = models.TextField()
    class Meta:
        db_table='chats'
        managed=False

class Objectives(models.Model):
    id = models.IntegerField(primary_key=True)
    match_player_detail_1 = models.ForeignKey(MP_details,on_delete=models.CASCADE,db_column='match_player_detail_id_1',related_name='mpd1')
    match_player_detail_2 = models.ForeignKey(MP_details,on_delete=models.CASCADE,db_column='match_player_detail_id_2', related_name='mpd2')
    key = models.IntegerField()
    subtype = models.TextField()
    team = models.IntegerField()
    time = models.IntegerField()
    value = models.IntegerField()
    slot = models.IntegerField()
    class Meta:
        db_table='game_objectives'
        managed=False

class Ability_upgrades(models.Model):
    id = models.IntegerField(primary_key=True)
    ability = models.ForeignKey(Abilities,on_delete=models.CASCADE)
    match_player_detail = models.ForeignKey(MP_details,on_delete=models.CASCADE, related_name='mpd')
    level = models.IntegerField()
    time = models.IntegerField()
    class Meta:
        db_table='ability_upgrades'
        managed=False

class Teamfights(models.Model):
    id = models.IntegerField(primary_key=True)
    match = models.ForeignKey(Matches,on_delete=models.CASCADE)
    start_teamfight = models.IntegerField()
    end_teamfight = models.IntegerField()
    last_death = models.IntegerField()
    deaths = models.IntegerField()
    class Meta:
        db_table='teamfights'
        managed=False

class Teamfights_players(models.Model):
    id = models.IntegerField(primary_key=True)
    teamfight = models.ForeignKey(Teamfights,on_delete=models.CASCADE)
    match_player_detail = models.ForeignKey(MP_details,on_delete=models.CASCADE)
    buyback = models.IntegerField()
    damage = models.IntegerField()
    deaths = models.IntegerField()
    gold_delta = models.IntegerField()
    xp_start = models.IntegerField()
    xp_end = models.IntegerField()
    class Meta:
        db_table='teamfights_players'
        managed=False

class Player_actions(models.Model):
    id = models.IntegerField(primary_key=True)
    match_player_detail = models.ForeignKey(MP_details,on_delete=models.CASCADE)
    none =  models.IntegerField(db_column='unit_order_none')
    move_to_position =  models.IntegerField(db_column='unit_order_move_to_position')
    move_to_target =  models.IntegerField(db_column='unit_order_move_to_target')
    attack_move =  models.IntegerField(db_column='unit_order_attack_move')
    attack_target =  models.IntegerField(db_column='unit_order_attack_target')
    cast_position =  models.IntegerField(db_column='unit_order_cast_position')
    cast_target =  models.IntegerField(db_column='unit_order_cast_target')
    cast_target_tree =  models.IntegerField(db_column='unit_order_cast_target_tree')
    cast_no_target =  models.IntegerField(db_column='unit_order_cast_no_target')
    cast_toggle =  models.IntegerField(db_column='unit_order_cast_toggle')
    hold_position =  models.IntegerField(db_column='unit_order_hold_position')
    train_ability =  models.IntegerField(db_column='unit_order_train_ability')
    drop_item =  models.IntegerField(db_column='unit_order_drop_item')
    give_item =  models.IntegerField(db_column='unit_order_give_item')
    pickup_item =  models.IntegerField(db_column='unit_order_pickup_item')
    pickup_rune =  models.IntegerField(db_column='unit_order_pickup_rune')
    purchase_item =  models.IntegerField(db_column='unit_order_purchase_item')
    sell_item =  models.IntegerField(db_column='unit_order_sell_item')
    disassemble_item =  models.IntegerField(db_column='unit_order_disassemble_item')
    move_item =  models.IntegerField(db_column='unit_order_move_item')
    cast_toggle_auto =  models.IntegerField(db_column='unit_order_cast_toggle_auto')
    stop =  models.IntegerField(db_column='unit_order_stop')
    buyback =  models.IntegerField(db_column='unit_order_buyback')
    glyph =  models.IntegerField(db_column='unit_order_glyph')
    eject_item_from_stash =  models.IntegerField(db_column='unit_order_eject_item_from_stash')
    cast_rune =  models.IntegerField(db_column='unit_order_cast_rune')
    ping_ability =  models.IntegerField(db_column='unit_order_ping_ability')
    move_to_direction =  models.IntegerField(db_column='unit_order_move_to_direction')
    class Meta:
        db_table='player_actions'
        managed=False
        
class Patches(models.Model):
    objects = CTEManager()
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    release_date = models.DateTimeField()
    class Meta:
        db_table='patches'
        managed=False

    
    