# DBS zadania
## Zadanie 3 v2/...
### v2/patches/
``` sql
SELECT 
	name as patch_version,
	patch_start_date,
	patch_end_date,
	matches.id as match_id,
	ROUND((matches.duration::numeric / 60),2) as match_duration
    FROM (
	    SELECT name,
	    cast(extract(epoch from release_date) as integer) as patch_start_date,
        cast(extract(epoch from LEAD(release_date,1) OVER (ORDER BY name)) as integer) as patch_end_date
        FROM patches
	) as myquery 
    LEFT JOIN matches ON matches.start_time BETWEEN patch_start_date AND patch_end_date
    ORDER BY name;
```
### v2/players/{id}/game_exp/
``` sql
SELECT players.id,COALESCE(nick,'unknown') as player_nick,
    localized_name as hero_localized_name,
    ROUND((matches.duration::numeric / 60),2) as match_duration_minutes,
    COALESCE(xp_hero,0) + COALESCE(xp_creep,0)+ COALESCE(xp_other,0) + COALESCE(xp_roshan,0) as experiences_gained,
    level as level_gained,
    matches.radiant_win = (player_slot BETWEEN 0 and 4) as winner,
    match_id
    FROM players
    INNER JOIN matches_players_details ON players.id = player_id 
    INNER JOIN heroes ON heroes.id = hero_id
    INNER JOIN matches ON match_id = matches.id
    WHERE players.id = {id}
    ORDER BY match_id;
```
    
### v2/players/{id}/game_objectives/
```sql
SELECT players.id,COALESCE(nick,'unknown') as player_nick,localized_name as hero_localized_name,
	match_id,COALESCE(subtype,'NO_ACTION') as hero_action, COUNT(COALESCE(subtype,'NO_ACTION')) as count
    FROM players
   	INNER JOIN matches_players_details ON players.id = player_id
    INNER JOIN heroes ON heroes.id = hero_id
	INNER JOIN matches ON matches.id = match_id
	LEFT JOIN game_objectives ON match_player_detail_id_1 = matches_players_details.id
	WHERE players.id =  {id}
	GROUP BY  players.id,COALESCE(nick,'unknown'),localized_name,
	match_id,subtype
	ORDER BY match_id,localized_name;
```
### v2/players/{id}/abilities/
```sql
SELECT players.id, 
COALESCE(nick,'unknown') as player_nick,
localized_name as hero_localized_name,
match_id, abilities.name as ability_name,
COUNT(*) as count,
MAX(ability_upgrades.level) as upgrade_level
FROM players
INNER JOIN matches_players_details ON player_id = players.id
INNER JOIN heroes ON hero_id = heroes.id
INNER JOIN ability_upgrades ON match_player_detail_id = matches_players_details.id
INNER JOIN abilities ON abilities.id = ability_id
WHERE player_id = {id}
GROUP BY players.id, COALESCE(nick,'unknown'),localized_name,match_id, abilities.name
ORDER BY match_id, abilities.name
```
