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
INNER JOIN matches ON match_id = matches.id
INNER JOIN heroes ON hero_id = heroes.id
INNER JOIN ability_upgrades ON match_player_detail_id = matches_players_details.id
INNER JOIN abilities ON abilities.id = ability_id
WHERE player_id = {id}
GROUP BY players.id, COALESCE(nick,'unknown'),localized_name,match_id, abilities.name
ORDER BY match_id, abilities.name
```

## Zadanie 5 v3/...
### /v3/matches/{id}/top_purchases/
```sql
with res as (SELECT match_id,hero_id,localized_name, item_id,items.name,COUNT(*) FROM matches
INNER JOIN matches_players_details ON match_id = matches.id
INNER JOIN heroes ON heroes.id = hero_id 
LEFT JOIN purchase_logs ON match_player_detail_id = matches_players_details.id
INNER JOIN items ON item_id = items.id
WHERE match_id ={id} and ( matches.radiant_win = (player_slot BETWEEN 0 and 4))
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
ORDER BY hero_id ASC,rank ASC
```
### /v3/abilities/{id}/usage/
```sql
with ability as (SELECT abilities.id,
	abilities.name,
	hero_id,
	localized_name,
	matches.radiant_win = (player_slot BETWEEN 0 and 4) as winner,
	case when 10*FLOOR((time*100/duration)/10) < 101 then 10*FLOOR((time*100/duration)/10) || '-' || 10*FLOOR((time*100/duration)/10)+9
	else '100-109'
	end bucket,
	COUNT(*)
	FROM abilities
	INNER JOIN ability_upgrades ON abilities.id = ability_id
	LEFT JOIN matches_players_details as mpd ON match_player_detail_impd.id
	LEFT JOIN heroes ON hero_id = heroes.id
	LEFT JOIN matches ON match_id = matches.id
	WHERE abilities.id = {id}
	GROUP BY abilities.id, abilities.name, hero_localized_name,winner,bucket
	)
SELECT * FROM (SELECT ability.*,RANK() OVER (
	PARTITION BY hero_id,winner
	ORDER BY count DESC,bucket ASC
) FROM ability) as res
WHERE rank =1
ORDER BY hero_id ASC ,winner DESC
```
### /v3/statistics/tower_kills/
```sql
with res as (SELECT hero_id,localized_name,match_id,subtype, time FROM heroes
    LEFT JOIN matches_players_details as mpd ON hero_id = heroes.id
    LEFT JOIN matches ON match_id = matches.id
    LEFT JOIN game_objectives as go ON match_player_detail_id_1 = mpd.id
    WHERE go.subtype = 'CHAT_MESSAGE_TOWER_KILL' and time <= duration
    ORDER BY match_id ASC, time ASC)
SELECT hero_id,localized_name,max(seqnum) as sequence FROM (
    select hero_id,localized_name,match_id,
    row_number() over (partition by hero_id,match_id, poradie order by match_id ASC, time ASC) as seqnum
    from (select res.*,
             (row_number() over (order by match_id ASC, time ASC) -
              row_number() over (partition by hero_id,match_id order by match_id ASC, time ASC)
             ) as poradie
            from res ) as t
    ORDER BY match_id ASC, time ASC ) as ta
GROUP BY hero_id,localized_name
ORDER BY sequence DESC, localized_name ASC
```
