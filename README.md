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
**v4/patches/**:
```sql
SELECT  anon_1.name,
        anon_1.release_date,
        anon_1.end_date,
        anon_2.id,
        anon_2.duration_minutes 
FROM (SELECT patches.name AS name,
             CAST(EXTRACT(EPOCH FROM patches.release_date) AS INTEGER) AS release_date,
             lead(CAST(EXTRACT(EPOCH FROM patches.release_date) AS INTEGER),1)
             OVER (ORDER BY patches.id) AS end_date
    FROM patches) AS anon_1
LEFT OUTER JOIN (SELECT matches.id AS id,
                        matches.start_time AS start_time,
                        round(CAST(matches.duration AS NUMERIC(10, 2)) / 60, 2) AS duration_minutes
                FROM matches) AS anon_2 
                ON anon_2.start_time >= anon_1.release_date AND anon_2.start_time <= anon_1.end_date
ORDER BY anon_1.name
```

EXPLAIN ANALYZE: 

| v2 | v4 |
|---|---|
| Nested Loop Left Join  (cost=1.59..18559.98 rows=105556 width=76)   (actual time=1895.107..19172.753 rows=50005 loops=1) | Sort  (cost=27631.27..27895.16   rows=105556 width=76) (actual time=19837.977..20315.626 rows=50005 loops=1) |
|     Join Filter: ((matches.start_time >= ((date_part('epoch'::text,   patches.release_date))::integer)) AND (matches.start_time <=   ((date_part('epoch'::text, lead(patches.release_date, 1) OVER   (?)))::integer))) |   Sort Key: patches.name |
|     Rows Removed by Join Filter: 900000 |   Sort Method: quicksort  Memory: 5443kB |
|     ->  WindowAgg  (cost=1.59..2.12 rows=19 width=40) (actual   time=0.556..1.522 rows=19 loops=1) |   ->  Nested Loop Left Join  (cost=1.59..18823.87 rows=105556 width=76)   (actual time=1961.855..19329.063 rows=50005 loops=1) |
|           ->  Sort  (cost=1.59..1.64 rows=19 width=40) (actual   time=0.476..0.703 rows=19 loops=1) |         Join Filter:   ((matches.start_time >= ((date_part('epoch'::text,   patches.release_date))::integer)) AND (matches.start_time <=   (lead((date_part('epoch'::text, patches.release_date))::integer, 1) OVER (?)))) |
|               Sort Key: patches.name |         Rows Removed by Join   Filter: 900000 |
|               Sort Method: quicksort  Memory: 25kB |         ->  WindowAgg    (cost=1.59..2.12 rows=19 width=44) (actual time=0.758..1.682 rows=19   loops=1) |
|               ->  Seq Scan on patches  (cost=0.00..1.19 rows=19 width=40) (actual   time=0.026..0.235 rows=19 loops=1) |               ->  Sort    (cost=1.59..1.64 rows=19 width=44) (actual time=0.616..0.829 rows=19   loops=1) |
|     ->  Materialize  (cost=0.00..1266.00 rows=50000 width=12)   (actual time=0.014..512.108 rows=50000 loops=19) |                     Sort Key:   patches.id |
|           ->  Seq Scan on matches  (cost=0.00..1016.00 rows=50000 width=12)   (actual time=0.021..479.129 rows=50000 loops=1) |                     Sort Method:   quicksort  Memory: 26kB |
| Planning Time: 0.211 ms |                     ->  Seq Scan on patches  (cost=0.00..1.19 rows=19 width=44) (actual   time=0.027..0.307 rows=19 loops=1) |
| Execution Time: 19644.461 ms |         ->  Materialize    (cost=0.00..1266.00 rows=50000 width=12) (actual time=0.012..515.989   rows=50000 loops=19) |
|  |               ->  Seq Scan on matches  (cost=0.00..1016.00 rows=50000 width=12)   (actual time=0.024..497.689 rows=50000 loops=1) |
|  | Planning Time: 0.306 ms |
|  | Execution Time: 20778.369 ms |

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
**v4/players/{id}/game_exp/**:
```sql
SELECT	players.id,
		coalesce(players.nick, 'unknown') AS coalesce_1,
		heroes.localized_name, round(CAST(matches.duration AS NUMERIC(10, 2)) /  60, 2) AS duration_minutes,
		coalesce(matches_players_details.xp_hero, 0)+ 
		coalesce(matches_players_details.xp_creep,0) + 
		coalesce(matches_players_details.xp_other, 0) + 
		coalesce(matches_players_details.xp_roshan, 0) AS anon_1,
		matches_players_details.level, 
		matches.radiant_win = (matches_players_details.player_slot >= 0 AND matches_players_details.player_slot <= 4) AS anon_2,
		matches.id AS id_1
FROM players 
JOIN matches_players_details ON players.id = matches_players_details.player_id 
JOIN matches ON matches.id = matches_players_details.match_id 
JOIN heroes ON heroes.id = matches_players_details.hero_id
WHERE players.id = {id}
```
EXPLAIN ANALYZE: 

| v2 | v4 |
|---|---|
| Gather Merge  (cost=14228.08..14229.14 rows=9 width=91)   (actual time=23.092..25.945 rows=13 loops=1) | Gather Merge    (cost=14228.08..14229.15 rows=9 width=91) (actual time=30.853..33.917   rows=13 loops=1) |
|     Workers Planned: 3 |   Workers Planned: 3 |
|     Workers Launched: 3 |   Workers Launched: 3 |
|     ->  Sort  (cost=13228.04..13228.04 rows=3 width=91)   (actual time=18.315..18.375 rows=3 loops=4) |   ->  Sort    (cost=13228.04..13228.05 rows=3 width=91) (actual time=24.445..24.503   rows=3 loops=4) |
|           Sort Key: matches_players_details.match_id |         Sort Key: matches.id |
|           Sort Method: quicksort  Memory:   25kB |         Sort Method: quicksort  Memory: 25kB |
|           Worker 0:  Sort Method:   quicksort  Memory: 25kB |         Worker 0:  Sort Method: quicksort  Memory: 25kB |
|           Worker 1:  Sort Method:   quicksort  Memory: 25kB |         Worker 1:  Sort Method: quicksort  Memory: 25kB |
|           Worker 2:  Sort Method:   quicksort  Memory: 25kB |         Worker 2:  Sort Method: quicksort  Memory: 25kB |
|           ->  Nested Loop  (cost=4.25..13228.01 rows=3 width=91)   (actual time=7.986..18.216 rows=3 loops=4) |         ->  Hash Join    (cost=4.25..13228.02 rows=3 width=91) (actual time=11.414..24.323   rows=3 loops=4) |
|               ->  Hash Join    (cost=3.96..13203.02 rows=3 width=53) (actual time=7.898..17.954   rows=3 loops=4) |               Hash Cond:   (matches_players_details.hero_id = heroes.id) |
|                     Hash Cond:   (matches_players_details.hero_id = heroes.id) |               ->  Nested Loop    (cost=0.71..13224.39 rows=3 width=52) (actual time=8.125..20.947   rows=3 loops=4) |
|                     ->  Nested Loop    (cost=0.42..13199.47 rows=3 width=47) (actual time=5.374..15.365   rows=3 loops=4) |                     ->  Nested Loop    (cost=0.42..13199.47 rows=3 width=47) (actual time=8.028..20.475   rows=3 loops=4) |
|                           ->  Parallel Seq Scan on   matches_players_details    (cost=0.00..13174.13 rows=3 width=36) (actual time=5.302..15.100   rows=3 loops=4) |                             ->  Parallel Seq Scan on   matches_players_details    (cost=0.00..13174.13 rows=3 width=36) (actual time=7.639..19.818   rows=3 loops=4) |
|                                 Filter:   (player_id = 14944) |                                   Filter: (player_id = 14944) |
|                                 Rows Removed   by Filter: 124997 |                                   Rows Removed by Filter: 124997 |
|                           ->  Index Scan using players_pk on players  (cost=0.42..8.44 rows=1 width=15) (actual   time=0.019..0.035 rows=1 loops=13) |                             ->  Index Scan using   players_pk on players  (cost=0.42..8.44   rows=1 width=15) (actual time=0.119..0.136 rows=1 loops=13) |
|                                 Index Cond:   (id = 14944) |                                   Index Cond: (id = 14944) |
|                     ->  Hash    (cost=2.13..2.13 rows=113 width=14) (actual time=2.350..2.359 rows=113   loops=4) |                     ->  Index Scan using matches_pk on matches  (cost=0.29..8.31 rows=1 width=9) (actual   time=0.098..0.101 rows=1 loops=13) |
|                           Buckets: 1024  Batches: 1    Memory Usage: 14kB |                           Index   Cond: (id = matches_players_details.match_id) |
|                           ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.041..1.179 rows=113 loops=4) |               ->  Hash    (cost=2.13..2.13 rows=113 width=14) (actual time=3.060..3.075 rows=113   loops=4) |
|               ->  Index Scan using matches_pk on matches  (cost=0.29..8.31 rows=1 width=9) (actual   time=0.031..0.034 rows=1 loops=13) |                     Buckets:   1024  Batches: 1  Memory Usage: 14kB |
|                     Index Cond: (id =   matches_players_details.match_id) |                     ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.059..1.530 rows=113 loops=4) |
| Planning Time: 0.678 ms | Planning Time: 0.700 ms |
| Execution Time: 26.385 ms | Execution Time: 34.403 ms |
    
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
**v4/players/{id}/game_objectives/**:
```sql
SELECT 	players.id,
		coalesce(players.nick, 'unknown') AS coalesce_1,
		heroes.localized_name, matches.id AS id_1,
		coalesce(game_objectives.subtype, 'NO_ACTION') AS coalesce_3,
		count(coalesce(game_objectives.subtype, 'NO_ACTION')) AS count_1
FROM players 
JOIN matches_players_details ON players.id = matches_players_details.player_id
JOIN matches ON matches.id = matches_players_details.match_id
JOIN heroes ON heroes.id = matches_players_details.hero_id
LEFT OUTER JOIN game_objectives ON game_objectives.match_player_detail_id_1 = matches_players_details.id
WHERE players.id = {id}
GROUP BY players.id, coalesce(players.nick, 'unknown'), heroes.localized_name, matches.id, game_objectives.subtype
ORDER BY matches.id, heroes.localized_name
```
EXPLAIN ANALYZE: 

| v2 | v4 |
|---|---|
| GroupAggregate  (cost=34801.70..34802.33 rows=23 width=114)   (actual time=7513.863..7514.763 rows=16 loops=1) | GroupAggregate    (cost=34801.70..34802.33 rows=23 width=114) (actual   time=7454.434..7454.947 rows=16 loops=1) |
|     Group Key: matches_players_details.match_id, heroes.localized_name,   players.id, (COALESCE(players.nick, 'unknown'::text)),   game_objectives.subtype |   Group Key: matches.id,   heroes.localized_name, players.id, (COALESCE(players.nick, 'unknown'::text)),   game_objectives.subtype |
|     ->  Sort  (cost=34801.70..34801.76 rows=23 width=74)   (actual time=7513.784..7514.097 rows=18 loops=1) |   ->  Sort    (cost=34801.70..34801.76 rows=23 width=74) (actual   time=7454.372..7454.548 rows=18 loops=1) |
|           Sort Key: matches_players_details.match_id, heroes.localized_name,   (COALESCE(players.nick, 'unknown'::text)), game_objectives.subtype |         Sort Key: matches.id,   heroes.localized_name, (COALESCE(players.nick, 'unknown'::text)),   game_objectives.subtype |
|           Sort Method: quicksort  Memory:   26kB |         Sort Method: quicksort  Memory: 26kB |
|           ->  Nested Loop  (cost=21591.84..34801.18 rows=23 width=74)   (actual time=7510.033..7513.400 rows=18 loops=1) |         ->  Nested Loop    (cost=21591.84..34801.18 rows=23 width=74) (actual   time=7434.720..7454.124 rows=18 loops=1) |
|               ->  Index Scan using players_pk on players  (cost=0.42..8.44 rows=1 width=15) (actual   time=0.024..0.059 rows=1 loops=1) |               ->  Index Scan using players_pk on players  (cost=0.42..8.44 rows=1 width=15) (actual   time=0.023..0.047 rows=1 loops=1) |
|                     Index Cond: (id = 14944) |                     Index Cond: (id   = 14944) |
|               ->  Gather    (cost=21591.42..34792.51 rows=23 width=42) (actual   time=7509.968..7515.322 rows=18 loops=1) |               ->  Gather    (cost=21591.42..34792.51 rows=23 width=42) (actual   time=7434.663..7456.554 rows=18 loops=1) |
|                     Workers Planned: 3 |                     Workers   Planned: 3 |
|                     Workers Launched: 3 |                     Workers   Launched: 3 |
|                     ->  Parallel Hash Left Join  (cost=20591.42..33790.21 rows=7 width=42)   (actual time=7495.008..7506.354 rows=4 loops=4) |                     ->  Parallel Hash Left Join  (cost=20591.42..33790.21 rows=7 width=42)   (actual time=7436.704..7446.161 rows=4 loops=4) |
|                           Hash Cond:   (matches_players_details.id = game_objectives.match_player_detail_id_1) |                           Hash   Cond: (matches_players_details.id = game_objectives.match_player_detail_id_1) |
|                           ->  Nested Loop    (cost=3.83..13202.60 rows=3 width=22) (actual time=12.317..23.002   rows=3 loops=4) |                             ->  Hash Join  (cost=3.83..13202.60 rows=3 width=22)   (actual time=10.949..20.289 rows=3 loops=4) |
|                                 ->  Hash Join    (cost=3.54..13177.68 rows=3 width=22) (actual time=12.172..22.641   rows=3 loops=4) |                                   Hash Cond: (matches_players_details.hero_id = heroes.id) |
|                                       Hash   Cond: (matches_players_details.hero_id = heroes.id) |                                   ->  Nested Loop  (cost=0.29..13199.05 rows=3 width=16)   (actual time=9.103..18.374 rows=3 loops=4) |
|                                         ->  Parallel Seq Scan on   matches_players_details    (cost=0.00..13174.13 rows=3 width=16) (actual time=8.760..19.138   rows=3 loops=4) |                                         ->  Parallel Seq Scan on   matches_players_details    (cost=0.00..13174.13 rows=3 width=16) (actual time=8.995..18.078   rows=3 loops=4) |
|                                               Filter: (player_id = 14944) |                                               Filter: (player_id = 14944) |
|                                               Rows Removed by Filter: 124997 |                                               Rows Removed by Filter: 124997 |
|                                         ->  Hash  (cost=2.13..2.13 rows=113 width=14) (actual   time=3.294..3.306 rows=113 loops=4) |                                         ->  Index Only Scan using   matches_pk on matches  (cost=0.29..8.31   rows=1 width=4) (actual time=0.043..0.045 rows=1 loops=13) |
|                                               Buckets: 1024  Batches: 1  Memory Usage: 14kB |                                               Index Cond: (id = matches_players_details.match_id) |
|                                               ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.067..1.654 rows=113 loops=4) |                                               Heap Fetches: 13 |
|                                 ->  Index Only Scan using matches_pk on   matches  (cost=0.29..8.31 rows=1   width=4) (actual time=0.052..0.058 rows=1 loops=13) |                                   ->  Hash  (cost=2.13..2.13 rows=113 width=14) (actual   time=2.359..2.368 rows=113 loops=3) |
|                                       Index   Cond: (id = matches_players_details.match_id) |                                         Buckets: 1024  Batches: 1  Memory Usage: 14kB |
|                                       Heap   Fetches: 13 |                                         ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.034..1.173 rows=113 loops=3) |
|                           ->  Parallel Hash  (cost=15856.15..15856.15 rows=378515   width=28) (actual time=7479.741..7479.754 rows=293349 loops=4) |                             ->  Parallel Hash  (cost=15856.15..15856.15 rows=378515   width=28) (actual time=7422.618..7422.627 rows=293349 loops=4) |
|                                 Buckets:   2097152  Batches: 1  Memory Usage: 60736kB |                                   Buckets: 2097152  Batches:   1  Memory Usage: 60736kB |
|                                 ->  Parallel Seq Scan on game_objectives  (cost=0.00..15856.15 rows=378515 width=28)   (actual time=0.046..3734.978 rows=293349 loops=4) |                                   ->  Parallel Seq Scan on   game_objectives  (cost=0.00..15856.15   rows=378515 width=28) (actual time=0.039..3712.187 rows=293349 loops=4) |
| Planning Time: 1.064 ms | Planning Time: 0.990 ms |
| Execution Time: 7518.312 ms | Execution Time: 7458.503 ms |

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
**v4/players/{id}/abilities/**:
```sql
SELECT 	players.id, coalesce(players.nick, 'unknown') AS coalesce_1,
		heroes.localized_name, matches.id AS id_1, abilities.name, 
		count('*') AS count_1, max(ability_upgrades.level) AS max_1
FROM players 
JOIN matches_players_details ON players.id = matches_players_details.player_id
JOIN matches ON matches.id = matches_players_details.match_id
JOIN heroes ON heroes.id = matches_players_details.hero_id
JOIN ability_upgrades ON matches_players_details.id = ability_upgrades.match_player_detail_id
JOIN abilities ON abilities.id = ability_upgrades.ability_id
WHERE players.id = {id}
GROUP BY players.id, coalesce(players.nick, 'unknown'), heroes.localized_name, matches.id, abilities.name
ORDER BY matches.id, abilities.name
```
EXPLAIN ANALYZE: 

| v2 | v4 |
|---|---|
| GroupAggregate  (cost=99756.31..99761.68 rows=179 width=84)   (actual time=37871.333..37876.685 rows=63 loops=1) | GroupAggregate    (cost=99756.31..99761.68 rows=179 width=84) (actual   time=37535.070..37541.843 rows=63 loops=1) |
|     Group Key: matches_players_details.match_id, abilities.name,   players.id, (COALESCE(players.nick, 'unknown'::text)), heroes.localized_name |   Group Key: matches.id,   abilities.name, players.id, (COALESCE(players.nick, 'unknown'::text)),   heroes.localized_name |
|     ->  Sort  (cost=99756.31..99756.76 rows=179 width=76)   (actual time=37871.253..37873.536 rows=239 loops=1) |   ->  Sort    (cost=99756.31..99756.76 rows=179 width=76) (actual   time=37534.953..37537.780 rows=239 loops=1) |
|           Sort Key: matches_players_details.match_id, abilities.name,   (COALESCE(players.nick, 'unknown'::text)), heroes.localized_name |         Sort Key: matches.id,   abilities.name, (COALESCE(players.nick, 'unknown'::text)),   heroes.localized_name |
|           Sort Method: quicksort  Memory:   49kB |         Sort Method: quicksort  Memory: 49kB |
|           ->  Nested Loop  (cost=14178.69..99749.61 rows=179 width=76)   (actual time=13726.150..37868.555 rows=239 loops=1) |         ->  Nested Loop    (cost=14178.69..99749.61 rows=179 width=76) (actual   time=12862.709..37531.750 rows=239 loops=1) |
|               ->  Index Scan using players_pk on players  (cost=0.42..8.44 rows=1 width=15) (actual   time=0.021..0.052 rows=1 loops=1) |               ->  Index Scan using players_pk on players  (cost=0.42..8.44 rows=1 width=15) (actual   time=0.020..0.046 rows=1 loops=1) |
|                     Index Cond: (id = 14944) |                     Index Cond: (id   = 14944) |
|               ->  Gather    (cost=14178.27..99739.38 rows=179 width=44) (actual   time=13726.090..37863.854 rows=239 loops=1) |               ->  Gather    (cost=14178.27..99739.38 rows=179 width=44) (actual   time=12862.656..37526.399 rows=239 loops=1) |
|                     Workers Planned: 4 |                     Workers   Planned: 4 |
|                     Workers Launched: 4 |                     Workers   Launched: 4 |
|                     ->  Nested Loop    (cost=13178.27..98721.48 rows=45 width=44) (actual   time=14338.682..37861.469 rows=48 loops=5) |                     ->  Nested Loop    (cost=13178.27..98721.48 rows=45 width=44) (actual   time=18427.203..37523.101 rows=48 loops=5) |
|                           ->  Hash Join    (cost=13178.00..98708.32 rows=45 width=26) (actual   time=14338.588..37859.194 rows=48 loops=5) |                             ->  Hash Join  (cost=13178.00..98708.32 rows=45 width=26)   (actual time=18427.124..37520.641 rows=48 loops=5) |
|                                 Hash Cond:   (matches_players_details.hero_id = heroes.id) |                                   Hash Cond: (matches_players_details.hero_id = heroes.id) |
|                                 ->  Nested Loop    (cost=13174.46..98704.66 rows=45 width=20) (actual   time=14336.023..37855.654 rows=48 loops=5) |                                   ->  Nested Loop  (cost=13174.46..98704.66 rows=45 width=20)   (actual time=18424.070..37516.505 rows=48 loops=5) |
|                                         ->  Parallel Hash Join  (cost=13174.17..98330.82 rows=45 width=20)   (actual time=14335.835..37853.182 rows=48 loops=5) |                                         ->  Parallel Hash Join  (cost=13174.17..98330.82 rows=45 width=20)   (actual time=18423.928..37513.881 rows=48 loops=5) |
|                                               Hash Cond: (ability_upgrades.match_player_detail_id =   matches_players_details.id) |                                               Hash Cond: (ability_upgrades.match_player_detail_id =   matches_players_details.id) |
|                                               ->  Parallel Seq Scan on   ability_upgrades  (cost=0.00..79290.00   rows=2234900 width=12) (actual time=0.019..18819.861 rows=1787920 loops=5) |                                               ->  Parallel Seq Scan on   ability_upgrades  (cost=0.00..79290.00   rows=2234900 width=12) (actual time=0.024..18626.064 rows=1787920 loops=5) |
|                                               ->  Parallel Hash  (cost=13174.13..13174.13 rows=3 width=16)   (actual time=13.053..13.063 rows=3 loops=5) |                                               ->  Parallel Hash  (cost=13174.13..13174.13 rows=3 width=16)   (actual time=13.981..13.991 rows=3 loops=5) |
|                                                     Buckets: 1024  Batches: 1  Memory Usage: 168kB |                                                     Buckets: 1024  Batches: 1  Memory Usage: 168kB |
|                                                     ->  Parallel Seq Scan on   matches_players_details    (cost=0.00..13174.13 rows=3 width=16) (actual time=4.374..12.873   rows=3 loops=5) |                                                     ->  Parallel Seq Scan on   matches_players_details    (cost=0.00..13174.13 rows=3 width=16) (actual time=4.347..13.829   rows=3 loops=5) |
|                                                           Filter: (player_id = 14944) |                                                           Filter: (player_id = 14944) |
|                                                           Rows Removed by Filter: 99997 |                                                           Rows Removed by Filter: 99997 |
|                                         ->  Index Only Scan using   matches_pk on matches  (cost=0.29..8.31   rows=1 width=4) (actual time=0.019..0.019 rows=1 loops=239) |                                         ->  Index Only Scan using   matches_pk on matches  (cost=0.29..8.31   rows=1 width=4) (actual time=0.019..0.020 rows=1 loops=239) |
|                                               Index Cond: (id = matches_players_details.match_id) |                                               Index Cond: (id = matches_players_details.match_id) |
|                                               Heap Fetches: 239 |                                               Heap Fetches: 239 |
|                                 ->  Hash    (cost=2.13..2.13 rows=113 width=14) (actual time=2.439..2.448 rows=113   loops=5) |                                   ->  Hash  (cost=2.13..2.13 rows=113 width=14) (actual   time=2.908..2.918 rows=113 loops=5) |
|                                         Buckets: 1024  Batches: 1  Memory Usage: 14kB |                                         Buckets: 1024  Batches: 1  Memory Usage: 14kB |
|                                         ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.036..1.210 rows=113 loops=5) |                                         ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.050..1.469 rows=113 loops=5) |
|                           ->  Index Scan using abilities_pk on   abilities  (cost=0.28..0.29 rows=1   width=26) (actual time=0.015..0.016 rows=1 loops=239) |                             ->  Index Scan using   abilities_pk on abilities    (cost=0.28..0.29 rows=1 width=26) (actual time=0.016..0.017 rows=1   loops=239) |
|                                 Index Cond:   (id = ability_upgrades.ability_id) |                                   Index Cond: (id = ability_upgrades.ability_id) |
| Planning Time: 1.338 ms | Planning Time: 1.208 ms |
| Execution Time: 37877.971 ms | Execution Time: 37543.124 ms |

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
**v4/matches/{id}/top_purchases/**:
```sql
SELECT 	anon_1.id, 
		anon_1.id_1, 
		anon_1.localized_name, 
		anon_1.id_2, anon_1.name, 
		anon_1.count_1, anon_1.rank 
FROM (SELECT 	anon_2.id AS id,
	  			anon_2.id_1 AS id_1,
	  			anon_2.localized_name AS localized_name,
	  			anon_2.id_2 AS id_2, anon_2.name AS name, 
	  			anon_2.count_1 AS count_1,
	  			rank() 
	  			OVER (PARTITION BY anon_2.id_1 
					  ORDER BY anon_2.count_1 DESC, anon_2.name)
	 			AS rank
		FROM (
			SELECT matches.id AS id,
					heroes.id AS id_1, heroes.localized_name AS localized_name,
					items.id AS id_2, items.name AS name,
					count('*') AS count_1
			FROM matches 
			JOIN matches_players_details ON matches.id = matches_players_details.match_id
			JOIN heroes ON heroes.id = matches_players_details.hero_id
			JOIN purchase_logs ON matches_players_details.id = purchase_logs.match_player_detail_id
			JOIN items ON items.id = purchase_logs.item_id
			WHERE matches.id = {id} AND 
			matches.radiant_win = (matches_players_details.player_slot >= 0 AND matches_players_details.player_slot <= 4) 
			GROUP BY matches.id, heroes.id, heroes.localized_name, items.id, items.name)
	  		AS anon_2) 
		AS anon_1
WHERE anon_1.rank < 6 
ORDER BY anon_1.id_1, anon_1.rank
```
EXPLAIN ANALYZE: 

| v3 	| v4 	|
|---	|---	|
| Sort    (cost=156859.95..156860.10 rows=61 width=52) (actual   time=99198.697..99199.122 rows=25 loops=1) 	| Sort  (cost=156858.80..156858.95   rows=61 width=52) (actual time=116250.463..116250.827 rows=25 loops=1) 	|
|     Sort Key: res2.hero_id, res2.rank 	|   Sort Key: anon_1.id_1,   anon_1.rank 	|
|     Sort Method: quicksort  Memory:   27kB 	|   Sort Method: quicksort  Memory: 27kB 	|
|     ->  Subquery Scan on   res2  (cost=156851.77..156858.14   rows=61 width=52) (actual time=99190.014..99198.251 rows=25 loops=1) 	|   ->  Subquery Scan on anon_1  (cost=156850.62..156856.99 rows=61   width=52) (actual time=116243.350..116250.058 rows=25 loops=1) 	|
|           Filter: (res2.rank <= 5) 	|         Filter: (anon_1.rank <   6) 	|
|           Rows Removed by Filter: 88 	|         Rows Removed by Filter: 88 	|
|           ->  WindowAgg  (cost=156851.77..156855.87 rows=182   width=52) (actual time=99189.986..99195.973 rows=113 loops=1) 	|         ->  WindowAgg    (cost=156850.62..156854.72 rows=182 width=52) (actual   time=116243.323..116248.154 rows=113 loops=1) 	|
|               ->  Sort    (cost=156851.77..156852.23 rows=182 width=44) (actual   time=99189.888..99191.774 rows=113 loops=1) 	|               ->  Sort    (cost=156850.62..156851.08 rows=182 width=44) (actual   time=116243.247..116244.736 rows=113 loops=1) 	|
|                     Sort Key: res.hero_id,   res.count DESC, res.name 	|                     Sort Key:   anon_2.id_1, anon_2.count_1 DESC, anon_2.name 	|
|                     Sort Method:   quicksort  Memory: 34kB 	|                     Sort Method:   quicksort  Memory: 34kB 	|
|                     ->  Subquery Scan on res  (cost=156815.36..156844.94 rows=182   width=44) (actual time=99173.497..99187.760 rows=113 loops=1) 	|                     ->  Subquery Scan on anon_2  (cost=156815.36..156843.79 rows=182   width=44) (actual time=116235.357..116241.999 rows=113 loops=1) 	|
|                           ->  Finalize GroupAggregate  (cost=156815.36..156843.12 rows=182   width=44) (actual time=99173.471..99184.008 rows=113 loops=1) 	|                             ->  Finalize   GroupAggregate    (cost=156815.36..156841.97 rows=182 width=44) (actual   time=116235.311..116239.712 rows=113 loops=1) 	|
|                                 Group Key:   matches_players_details.match_id, matches_players_details.hero_id,   heroes.localized_name, purchase_logs.item_id, items.name 	|                                   Group Key: matches.id, heroes.id, items.id 	|
|                                 ->  Gather Merge  (cost=156815.36..156838.54 rows=184   width=44) (actual time=99173.389..99179.916 rows=114 loops=1) 	|                                   ->  Gather Merge  (cost=156815.36..156838.31 rows=184   width=44) (actual time=116235.243..116237.393 rows=114 loops=1) 	|
|                                       Workers   Planned: 4 	|                                         Workers Planned: 4 	|
|                                       Workers   Launched: 4 	|                                         Workers Launched: 3 	|
|                                         ->  Partial   GroupAggregate    (cost=155815.30..155816.57 rows=46 width=44) (actual   time=99162.678..99163.997 rows=23 loops=5) 	|                                         ->  Partial   GroupAggregate    (cost=155815.30..155816.34 rows=46 width=44) (actual   time=116228.126..116230.221 rows=28 loops=4) 	|
|                                               Group Key: matches_players_details.match_id,   matches_players_details.hero_id, heroes.localized_name,   purchase_logs.item_id, items.name 	|                                               Group Key: matches.id, heroes.id, items.id 	|
|                                               ->  Sort  (cost=155815.30..155815.42 rows=46   width=36) (actual time=99162.625..99163.103 rows=38 loops=5) 	|                                               ->  Sort  (cost=155815.30..155815.42 rows=46   width=36) (actual time=116228.059..116228.831 rows=47 loops=4) 	|
|                                                     Sort Key: matches_players_details.hero_id, heroes.localized_name,   purchase_logs.item_id, items.name 	|                                                     Sort Key: heroes.id, items.id 	|
|                                                     Sort Method: quicksort  Memory:   31kB 	|                                                     Sort Method: quicksort  Memory:   25kB 	|
|                                                     Worker 0:  Sort Method:   quicksort  Memory: 25kB 	|                                                     Worker 0:  Sort Method:   quicksort  Memory: 25kB 	|
|                                                     Worker 1:  Sort Method:   quicksort  Memory: 25kB 	|                                                     Worker 1:  Sort Method:   quicksort  Memory: 33kB 	|
|                                                     Worker 2:  Sort Method:   quicksort  Memory: 33kB 	|                                                     Worker 2:  Sort Method:   quicksort  Memory: 31kB 	|
|                                                     Worker 3:  Sort Method:   quicksort  Memory: 25kB 	|                                                     ->  Nested Loop  (cost=36.48..155814.03 rows=46 width=36)   (actual time=86179.464..116227.401 rows=47 loops=4) 	|
|                                                     ->  Nested Loop  (cost=36.48..155814.03 rows=46 width=36)   (actual time=74782.068..99162.089 rows=38 loops=5) 	|                                                           ->  Hash Join  (cost=36.34..155806.44 rows=46 width=22)   (actual time=86179.369..116224.972 rows=47 loops=4) 	|
|                                                           ->  Hash Join  (cost=36.34..155806.44 rows=46 width=22)   (actual time=74781.994..99160.216 rows=38 loops=5) 	|                                                                 Hash Cond: (matches_players_details.hero_id = heroes.id) 	|
|                                                                 Hash Cond: (matches_players_details.hero_id = heroes.id) 	|                                                                 ->  Hash Join  (cost=32.79..155802.78 rows=46 width=12)   (actual time=86175.839..116220.381 rows=47 loops=4) 	|
|                                                                 ->  Hash Join  (cost=32.79..155802.78 rows=46 width=12)   (actual time=74778.519..99155.931 rows=38 loops=5) 	|                                                                       Hash Cond: (((matches_players_details.player_slot >= 0) AND   (matches_players_details.player_slot <= 4)) = matches.radiant_win) 	|
|                                                                       Hash Cond: (((matches_players_details.player_slot >= 0) AND   (matches_players_details.player_slot <= 4)) = matches.radiant_win) 	|                                                                       ->  Hash Join  (cost=24.47..155793.58 rows=91 width=16)   (actual time=71149.696..116218.681 rows=88 loops=4) 	|
|                                                                       ->  Hash Join  (cost=24.47..155793.58 rows=91 width=16)   (actual time=62586.837..99153.894 rows=71 loops=5) 	|                                                                             Hash Cond: (purchase_logs.match_player_detail_id =   matches_players_details.id) 	|
|                                                                             Hash Cond: (purchase_logs.match_player_detail_id =   matches_players_details.id) 	|                                                                             ->  Parallel Seq Scan on   purchase_logs  (cost=0.00..143829.36 rows=4548436   width=8) (actual time=0.025..58197.265 rows=4548436 loops=4) 	|
|                                                                             ->  Parallel Seq Scan on   purchase_logs  (cost=0.00..143829.36 rows=4548436   width=8) (actual time=0.028..49710.940 rows=3638749 loops=5) 	|                                                                             ->  Hash  (cost=24.35..24.35 rows=10 width=16)   (actual time=0.382..0.395 rows=10 loops=4) 	|
|                                                                             ->  Hash  (cost=24.35..24.35 rows=10 width=16)   (actual time=0.411..0.423 rows=10 loops=5) 	|                                                                                   Buckets: 1024  Batches: 1  Memory Usage: 9kB 	|
|                                                                                   Buckets: 1024  Batches: 1  Memory Usage: 9kB 	|                                                                                   ->  Index Scan using   idx_match_id_player_id on matches_players_details  (cost=0.42..24.35 rows=10 width=16) (actual   time=0.060..0.220 rows=10 loops=4) 	|
|                                                                                   ->  Index Scan using   idx_match_id_player_id on matches_players_details  (cost=0.42..24.35 rows=10 width=16) (actual   time=0.056..0.222 rows=10 loops=5) 	|                                                                                         Index Cond: (match_id = 21421) 	|
|                                                                                         Index Cond: (match_id = 21421) 	|                                                                       ->  Hash  (cost=8.31..8.31 rows=1 width=5) (actual   time=0.112..0.125 rows=1 loops=4) 	|
|                                                                       ->  Hash  (cost=8.31..8.31 rows=1 width=5) (actual   time=0.199..0.211 rows=1 loops=5) 	|                                                                             Buckets: 1024  Batches: 1  Memory Usage: 9kB 	|
|                                                                             Buckets: 1024  Batches: 1  Memory Usage: 9kB 	|                                                                             ->  Index Scan using   matches_pk on matches  (cost=0.29..8.31   rows=1 width=5) (actual time=0.040..0.073 rows=1 loops=4) 	|
|                                                                             ->  Index Scan using   matches_pk on matches  (cost=0.29..8.31   rows=1 width=5) (actual time=0.123..0.151 rows=1 loops=5) 	|                                                                                   Index Cond: (id = 21421) 	|
|                                                                                   Index Cond: (id = 21421) 	|                                                                 ->  Hash  (cost=2.13..2.13 rows=113 width=14) (actual   time=3.437..3.457 rows=113 loops=4) 	|
|                                                                 ->  Hash  (cost=2.13..2.13 rows=113 width=14) (actual   time=3.375..3.387 rows=113 loops=5) 	|                                                                       Buckets: 1024  Batches: 1  Memory Usage: 14kB 	|
|                                                                       Buckets: 1024  Batches: 1  Memory Usage: 14kB 	|                                                                       ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.037..1.651 rows=113 loops=4) 	|
|                                                                       ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.037..1.688 rows=113 loops=5) 	|                                                           ->  Index Scan using items_pk   on items  (cost=0.15..0.17 rows=1   width=18) (actual time=0.016..0.016 rows=1 loops=188) 	|
|                                                           ->  Index Scan using items_pk   on items  (cost=0.15..0.17 rows=1   width=18) (actual time=0.015..0.015 rows=1 loops=188) 	|                                                                 Index Cond: (id = purchase_logs.item_id) 	|
|                                                                 Index Cond: (id = purchase_logs.item_id) 	| Planning Time: 1.902 ms 	|
| Planning Time: 1.419 ms 	| Execution Time: 116252.293 ms 	|
| Execution Time: 99200.597 ms 	|  	|

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
				 LEFT JOIN matches_players_details as mpd ON match_player_detail_id = mpd.id
				 LEFT JOIN heroes ON hero_id = heroes.id
				 LEFT JOIN matches ON match_id = matches.id
				 WHERE abilities.id = {id}
				 GROUP BY abilities.id, abilities.name, hero_id, localized_name,winner,bucket
				)
SELECT * FROM (SELECT ability.*,RANK() OVER (
	PARTITION BY hero_id,winner
	ORDER BY count DESC,bucket ASC
) FROM ability) as res
WHERE rank =1
ORDER BY hero_id ASC ,winner DESC
```
**v4/abilities/{id}/usage/**:
```sql
SELECT 	anon_1.id, anon_1.name, anon_1.hero_id,
		anon_1.localized_name, anon_1.winner, 
		anon_1.bucket, anon_1.count_1, anon_1.rank 
FROM (SELECT 	anon_2.id AS id, anon_2.name AS name, 
	  			anon_2.hero_id AS hero_id, anon_2.localized_name AS localized_name,
	  			anon_2.winner AS winner, anon_2.bucket AS bucket, anon_2.count_1 AS count_1,
	  			rank() OVER (
					PARTITION BY anon_2.hero_id, anon_2.winner 
					ORDER BY anon_2.count_1 DESC, anon_2.bucket ASC
				) AS rank
		FROM (SELECT 	abilities.id AS id, abilities.name AS name,
			  			heroes.id AS hero_id, heroes.localized_name AS localized_name,
			  			matches.radiant_win = (matches_players_details.player_slot >= 0 AND matches_players_details.player_slot <= 4) AS winner,
			  			CASE WHEN (10 * floor(((ability_upgrades.time * 100) / matches.duration) / 10) < 101) 
			  			THEN CAST(10 * floor(((ability_upgrades.time * 100) / matches.duration) / 10) AS TEXT) || '-' || CAST(10 * floor(((ability_upgrades.time * 100) / matches.duration) / 10) + 9 AS TEXT) 
			  			ELSE '100-109' END AS bucket, count('*') AS count_1
			FROM abilities 
			JOIN ability_upgrades ON abilities.id = ability_upgrades.ability_id
			JOIN matches_players_details ON matches_players_details.id = ability_upgrades.match_player_detail_id
			JOIN heroes ON heroes.id = matches_players_details.hero_id
			JOIN matches ON matches.id = matches_players_details.match_id
			WHERE abilities.id = {id}
			GROUP BY abilities.id, abilities.name, heroes.id, heroes.localized_name, matches.radiant_win = (matches_players_details.player_slot >= 0 AND matches_players_details.player_slot <= 4), bucket
		) AS anon_2
	)AS anon_1
WHERE anon_1.rank = 1 ORDER BY anon_1.hero_id, anon_1.winner
```
EXPLAIN ANALYZE: 

| v3 	| v4 	|
|---	|---	|
| Sort    (cost=117794.32..117794.79 rows=191 width=89) (actual   time=4814.046..4814.084 rows=3 loops=1) 	| Subquery Scan on anon_1    (cost=116261.40..117691.72 rows=191 width=89) (actual   time=4777.808..4778.706 rows=3 loops=1) 	|
|     Sort Key: res.hero_id, res.winner DESC 	|   Filter: (anon_1.rank = 1) 	|
|     Sort Method: quicksort  Memory:   25kB 	|   Rows Removed by Filter: 20 	|
|     ->  Subquery Scan on res  (cost=116356.75..117787.08 rows=191   width=89) (actual time=4813.029..4813.993 rows=3 loops=1) 	|   ->  WindowAgg    (cost=116261.40..117214.95 rows=38142 width=89) (actual   time=4777.786..4778.440 rows=23 loops=1) 	|
|           Filter: (res.rank = 1) 	|         ->  Sort    (cost=116261.40..116356.75 rows=38142 width=81) (actual   time=4777.727..4777.944 rows=23 loops=1) 	|
|           Rows Removed by Filter: 20 	|               Sort Key:   anon_2.hero_id, anon_2.winner, anon_2.count_1 DESC, anon_2.bucket 	|
|           ->  WindowAgg  (cost=116356.75..117310.30 rows=38142   width=89) (actual time=4813.009..4813.713 rows=23 loops=1) 	|               Sort Method:   quicksort  Memory: 28kB 	|
|               ->  Sort    (cost=116356.75..116452.11 rows=38142 width=81) (actual   time=4812.930..4813.153 rows=23 loops=1) 	|               ->  Subquery Scan on anon_2  (cost=109830.83..113358.97 rows=38142   width=81) (actual time=4776.514..4777.451 rows=23 loops=1) 	|
|                     Sort Key:   ability.hero_id, ability.winner, ability.count DESC, ability.bucket 	|                     ->  HashAggregate  (cost=109830.83..112977.55 rows=38142   width=81) (actual time=4776.477..4777.004 rows=23 loops=1) 	|
|                     Sort Method:   quicksort  Memory: 28kB 	|                           Group   Key: abilities.id, heroes.id, (matches.radiant_win =   ((matches_players_details.player_slot >= 0) AND   (matches_players_details.player_slot <= 4))), CASE WHEN (('10'::double   precision * floor(((((ability_upgrades."time" * 100) /   matches.duration) / 10))::double precision)) < '101'::double precision)   THEN (((('10'::double precision * floor(((((ability_upgrades."time"   * 100) / matches.duration) / 10))::double precision)))::text \|\|'-'::text) \|\|   ((('10'::double precision * floor(((((ability_upgrades."time" *   100) / matches.duration) / 10))::double precision)) + '9'::double   precision))::text) ELSE '100-109'::text END 	|
|                     ->  Subquery Scan on ability  (cost=109926.19..113454.32 rows=38142   width=81) (actual time=4811.743..4812.651 rows=23 loops=1) 	|                             ->  Nested Loop  (cost=17431.85..109354.06 rows=38142   width=73) (actual time=3243.987..4380.320 rows=37068 loops=1) 	|
|                           ->  HashAggregate  (cost=109926.19..113072.90 rows=38142   width=81) (actual time=4811.722..4812.195 rows=23 loops=1) 	|                                   ->  Index Scan using   abilities_pk on abilities    (cost=0.28..8.29 rows=1 width=26) (actual time=0.028..0.050 rows=1   loops=1) 	|
|                                 Group Key:   abilities.id, mpd.hero_id, heroes.localized_name, (matches.radiant_win =   ((mpd.player_slot >= 0) AND (mpd.player_slot <= 4))), CASE WHEN   (('10'::double precision * floor(((((ability_upgrades."time" * 100)   / matches.duration) / 10))::double precision)) < '101'::double precision)   THEN (((('10'::double precision * floor(((((ability_upgrades."time"   * 100) / matches.duration) / 10))::double precision)))::text \|\| '-'::text) \|\|   ((('10'::double precision * floor(((((ability_upgrades."time" *   100) / matches.duration) / 10))::double precision)) + '9'::double   precision))::text) ELSE '100-109'::text END 	|                                         Index Cond: (id = 5004) 	|
|                                 ->  Nested Loop    (cost=17431.85..109354.06 rows=38142 width=73) (actual   time=3247.232..4406.329 rows=37068 loops=1) 	|                                   ->  Gather  (cost=17431.57..106199.05 rows=38142   width=31) (actual time=3243.896..3613.117 rows=37068 loops=1) 	|
|                                         ->  Index Scan using   abilities_pk on abilities    (cost=0.28..8.29 rows=1 width=26) (actual time=0.020..0.047 rows=1   loops=1) 	|                                         Workers Planned: 4 	|
|                                               Index Cond: (id = 5004) 	|                                         Workers Launched: 4 	|
|                                         ->  Gather  (cost=17431.57..106199.05 rows=38142   width=31) (actual time=3247.162..3639.277 rows=37068 loops=1) 	|                                         ->  Hash Join  (cost=16431.57..101384.85 rows=9536   width=31) (actual time=3239.019..3938.768 rows=7414 loops=5) 	|
|                                               Workers Planned: 4 	|                                               Hash Cond: (matches_players_details.match_id = matches.id) 	|
|                                               Workers Launched: 4 	|                                               ->  Hash Join  (cost=14790.57..99718.82 rows=9536   width=30) (actual time=2133.579..2683.397 rows=7414 loops=5) 	|
|                                               ->  Hash Left Join  (cost=16431.57..101384.85 rows=9536   width=31) (actual time=3261.015..3972.477 rows=7414 loops=5) 	|                                                     Hash Cond: (matches_players_details.hero_id = heroes.id) 	|
|                                                     Hash Cond: (mpd.match_id = matches.id) 	|                                                     ->  Parallel Hash Join  (cost=14787.03..99689.31 rows=9536   width=20) (actual time=2131.127..2529.937 rows=7414 loops=5) 	|
|                                                     ->  Hash Left Join  (cost=14790.57..99718.82 rows=9536   width=30) (actual time=2219.375..2776.965 rows=7414 loops=5) 	|                                                           Hash Cond: (ability_upgrades.match_player_detail_id =   matches_players_details.id) 	|
|                                                           Hash Cond: (mpd.hero_id = heroes.id) 	|                                                           ->  Parallel Seq Scan on   ability_upgrades  (cost=0.00..84877.25   rows=9536 width=12) (actual time=0.104..241.039 rows=7414 loops=5) 	|
|                                                           ->  Parallel Hash Left   Join  (cost=14787.03..99689.31   rows=9536 width=20) (actual time=2216.211..2621.700 rows=7414 loops=5) 	|                                                                 Filter: (ability_id = 5004) 	|
|                                                                 Hash Cond: (ability_upgrades.match_player_detail_id = mpd.id) 	|                                                                 Rows Removed by Filter: 1780506 	|
|                                                                 ->  Parallel Seq Scan on   ability_upgrades  (cost=0.00..84877.25   rows=9536 width=12) (actual time=0.115..244.272 rows=7414 loops=5) 	|                                                           ->  Parallel Hash  (cost=12770.90..12770.90 rows=161290   width=16) (actual time=2130.389..2130.399 rows=100000 loops=5) 	|
|                                                                       Filter: (ability_id = 5004) 	|                                                                 Buckets: 524288  Batches: 1  Memory Usage: 27648kB 	|
|                                                                       Rows Removed by Filter: 1780506 	|                                                                 ->  Parallel Seq Scan on   matches_players_details    (cost=0.00..12770.90 rows=161290 width=16) (actual   time=0.021..1054.887 rows=100000 loops=5) 	|
|                                                                 ->  Parallel Hash  (cost=12770.90..12770.90 rows=161290   width=16) (actual time=2215.345..2215.355 rows=100000 loops=5) 	|                                                     ->  Hash  (cost=2.13..2.13 rows=113 width=14) (actual   time=2.364..2.373 rows=113 loops=5) 	|
|                                                                       Buckets: 524288  Batches: 1  Memory Usage: 27648kB 	|                                                           Buckets: 1024  Batches: 1  Memory Usage: 14kB 	|
|                                                                       ->  Parallel Seq Scan on   matches_players_details mpd    (cost=0.00..12770.90 rows=161290 width=16) (actual   time=0.022..1095.625 rows=100000 loops=5) 	|                                                           ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.041..1.189 rows=113 loops=5) 	|
|                                                           ->  Hash  (cost=2.13..2.13 rows=113 width=14) (actual   time=3.074..3.083 rows=113 loops=5) 	|                                               ->  Hash  (cost=1016.00..1016.00 rows=50000 width=9)   (actual time=1104.962..1104.970 rows=50000 loops=5) 	|
|                                                                 Buckets: 1024  Batches: 1  Memory Usage: 14kB 	|                                                     Buckets: 65536  Batches: 1  Memory Usage: 2661kB 	|
|                                                                 ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.050..1.570 rows=113 loops=5) 	|                                                     ->  Seq Scan on matches  (cost=0.00..1016.00 rows=50000 width=9)   (actual time=0.029..549.698 rows=50000 loops=5) 	|
|                                                     ->  Hash  (cost=1016.00..1016.00 rows=50000 width=9)   (actual time=1041.190..1041.199 rows=50000 loops=5) 	| Planning Time: 1.158 ms 	|
|                                                           Buckets: 65536  Batches: 1  Memory Usage: 2661kB 	| Execution Time: 4780.712 ms 	|
|                                                           ->  Seq Scan on matches  (cost=0.00..1016.00 rows=50000 width=9)   (actual time=0.039..519.201 rows=50000 loops=5) 	|  	|
| Planning Time: 1.160 ms 	|  	|
| Execution Time: 4816.004 ms 	|  	|


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
**v4/statistics/tower_kills/**:
```sql
SELECT anon_1.hero_id, anon_1.localized_name, max(anon_1.seq) AS sequence 
FROM (
	SELECT anon_2.hero_id AS hero_id, anon_2.localized_name AS localized_name,
	row_number() OVER (
		PARTITION BY anon_2.hero_id, anon_2.match_id, anon_2.poradie
		ORDER BY anon_2.match_id, anon_2.time) AS seq
	FROM (SELECT anon_3.hero_id AS hero_id, anon_3.localized_name AS localized_name,
		  anon_3.match_id AS match_id, anon_3.time AS time,
		  row_number() OVER (ORDER BY anon_3.match_id, anon_3.time) - 
		  row_number() OVER (
			  PARTITION BY anon_3.hero_id, anon_3.match_id
			  ORDER BY anon_3.match_id, anon_3.time) AS poradie
		FROM (SELECT heroes.id AS hero_id, heroes.localized_name AS localized_name,
			  matches_players_details.match_id AS match_id, game_objectives.time AS time
			FROM heroes 
			LEFT OUTER JOIN matches_players_details ON heroes.id = matches_players_details.hero_id 
			JOIN matches ON matches.id = matches_players_details.match_id 
			JOIN game_objectives ON matches_players_details.id = game_objectives.match_player_detail_id_1
			WHERE game_objectives.subtype = 'CHAT_MESSAGE_TOWER_KILL' AND game_objectives.time <= matches.duration) 
		  AS anon_3)
	AS anon_2) 
	AS anon_1 
GROUP BY anon_1.hero_id, anon_1.localized_name
ORDER BY sequence DESC, anon_1.localized_name ASC
```
EXPLAIN ANALYZE: 

| v3 | v4 |
|---|---|
| Sort    (cost=188463.02..188999.19 rows=214467 width=22) (actual   time=112857.305..112858.305 rows=110 loops=1) | Sort  (cost=158524.18..159078.22   rows=221615 width=22) (actual time=122080.883..122081.958 rows=110 loops=1) |
|     Sort Key: (max((row_number() OVER (?)))) DESC, t.localized_name |   Sort Key: (max((row_number() OVER   (?)))) DESC, anon_2.localized_name |
|     Sort Method: quicksort  Memory:   33kB |   Sort Method: quicksort  Memory: 33kB |
|     ->  HashAggregate  (cost=167326.87..169471.54 rows=214467   width=22) (actual time=112854.173..112856.146 rows=110 loops=1) |   ->  HashAggregate  (cost=136631.17..138847.32 rows=221615   width=22) (actual time=122076.693..122079.619 rows=110 loops=1) |
|           Group Key: t.hero_id, t.localized_name |         Group Key: anon_2.hero_id,   anon_2.localized_name |
|           ->  Sort  (cost=163037.53..163573.70 rows=214467   width=38) (actual time=103465.079..108003.413 rows=475701 loops=1) |         ->  WindowAgg    (cost=126658.49..132752.91 rows=221615 width=38) (actual   time=102413.295..117098.075 rows=475701 loops=1) |
|               Sort Key: t.match_id,   t."time" |               ->  Sort    (cost=126658.49..127212.53 rows=221615 width=30) (actual   time=102413.230..107047.620 rows=475701 loops=1) |
|               Sort Method: quicksort  Memory: 52156kB |                     Sort Key:   anon_2.hero_id, anon_2.match_id, anon_2.poradie, anon_2."time" |
|               ->  WindowAgg    (cost=138148.21..144046.06 rows=214467 width=38) (actual   time=83807.600..98407.995 rows=475701 loops=1) |                     Sort Method:   quicksort  Memory: 49453kB |
|                     ->  Sort    (cost=138148.21..138684.38 rows=214467 width=30) (actual   time=83807.540..88410.524 rows=475701 loops=1) |                     ->  Subquery Scan on anon_2  (cost=99779.15..106981.64 rows=221615   width=30) (actual time=73642.961..97315.988 rows=475701 loops=1) |
|                           Sort Key:   t.hero_id, t.match_id, t.poradie, t."time" |                             ->  WindowAgg  (cost=99779.15..104765.49 rows=221615   width=30) (actual time=73642.941..88116.398 rows=475701 loops=1) |
|                           Sort Method:   quicksort  Memory: 49453kB |                                   ->  Sort  (cost=99779.15..100333.19 rows=221615   width=30) (actual time=73642.877..78267.157 rows=475701 loops=1) |
|                           ->  Subquery Scan on t  (cost=112186.56..119156.74 rows=214467   width=30) (actual time=55462.325..78792.109 rows=475701 loops=1) |                                         Sort Key: matches_players_details.match_id,   game_objectives."time" |
|                                 ->  WindowAgg    (cost=112186.56..117012.07 rows=214467 width=62) (actual   time=55462.302..69738.912 rows=475701 loops=1) |                                         Sort Method: quicksort  Memory:   49453kB |
|                                         ->  Sort  (cost=112186.56..112722.73 rows=214467   width=30) (actual time=55462.238..60019.158 rows=475701 loops=1) |                                         ->  WindowAgg  (cost=74561.91..80102.29 rows=221615   width=30) (actual time=54221.203..68677.629 rows=475701 loops=1) |
|                                               Sort Key: res.match_id, res."time" |                                               ->  Sort  (cost=74561.91..75115.95 rows=221615   width=22) (actual time=54221.097..58824.209 rows=475701 loops=1) |
|                                               Sort Method: quicksort  Memory:   49453kB |                                                     Sort Key: heroes.id, matches_players_details.match_id,   game_objectives."time" |
|                                               ->  WindowAgg  (cost=87833.41..93195.08 rows=214467   width=30) (actual time=36236.494..50563.155 rows=475701 loops=1) |                                                     Sort Method: quicksort  Memory:   49386kB |
|                                                     ->  Sort  (cost=87833.41..88369.57 rows=214467   width=22) (actual time=36236.420..40789.217 rows=475701 loops=1) |                                                     ->  Hash Join  (cost=24052.54..54885.06 rows=221615   width=22) (actual time=11079.810..48946.832 rows=475701 loops=1) |
|                                                           Sort Key: res.hero_id, res.match_id, res."time" |                                                           Hash Cond: (matches_players_details.hero_id = heroes.id) |
|                                                           Sort Method: quicksort  Memory:   49386kB |                                                           ->  Hash Join  (cost=24049.00..54277.96 rows=221615   width=12) (actual time=11077.416..39386.018 rows=475701 loops=1) |
|                                                           ->  Subquery Scan on res  (cost=41318.66..68841.93 rows=214467   width=22) (actual time=14960.521..31204.584 rows=475701 loops=1) |                                                                 Hash Cond: (matches_players_details.match_id = matches.id) |
|                                                                 ->  Gather Merge  (cost=41318.66..66697.26 rows=214467   width=54) (actual time=14960.500..22019.008 rows=475701 loops=1) |                                                                 Join Filter: (game_objectives."time" <= matches.duration) |
|                                                                       Workers Planned: 3 |                                                                 Rows Removed by Join Filter: 9 |
|                                                                       Workers Launched: 3 |                                                                 ->  Hash Join  (cost=22408.00..50891.68 rows=664846   width=12) (actual time=10077.154..28827.294 rows=475710 loops=1) |
|                                                                       ->  Sort  (cost=40318.62..40497.35 rows=71489   width=54) (actual time=14951.665..16179.916 rows=118925 loops=4) |                                                                       Hash Cond: (game_objectives.match_player_detail_id_1 =   matches_players_details.id) |
|                                                                             Sort Key: mpd.match_id, go."time" |                                                                       ->  Seq Scan on   game_objectives  (cost=0.00..26738.45   rows=664846 width=8) (actual time=0.082..7135.590 rows=663032 loops=1) |
|                                                                             Sort Method: quicksort  Memory:   12310kB |                                                                             Filter: (subtype = 'CHAT_MESSAGE_TOWER_KILL'::text) |
|                                                                             Worker 0:  Sort Method:   quicksort  Memory: 12369kB |                                                                             Rows Removed by Filter: 510364 |
|                                                                             Worker 1:  Sort Method:   quicksort  Memory: 12430kB |                                                                       ->  Hash  (cost=16158.00..16158.00 rows=500000   width=12) (actual time=10075.534..10075.543 rows=500000 loops=1) |
|                                                                             Worker 2:  Sort Method:   quicksort  Memory: 12278kB |                                                                             Buckets: 524288  Batches: 1  Memory Usage: 25581kB |
|                                                                             ->  Hash Join  (cost=16431.57..34554.67 rows=71489   width=54) (actual time=3856.257..13636.800 rows=118925 loops=4) |                                                                             ->  Seq Scan on   matches_players_details    (cost=0.00..16158.00 rows=500000 width=12) (actual   time=0.026..4998.848 rows=500000 loops=1) |
|                                                                                   Hash Cond: (mpd.hero_id = heroes.id) |                                                                 ->  Hash  (cost=1016.00..1016.00 rows=50000 width=8)   (actual time=1000.017..1000.026 rows=50000 loops=1) |
|                                                                                   ->  Hash Join  (cost=16428.03..34356.42 rows=71489 width=12)   (actual time=3853.763..11158.532 rows=118925 loops=4) |                                                                       Buckets: 65536  Batches: 1  Memory Usage: 2466kB |
|                                                                                         Hash Cond: (mpd.match_id = matches.id) |                                                                       ->  Seq Scan on matches  (cost=0.00..1016.00 rows=50000 width=8)   (actual time=0.029..500.422 rows=50000 loops=1) |
|                                                                                         Join Filter: (go."time" <= matches.duration) |                                                           ->  Hash  (cost=2.13..2.13 rows=113 width=14) (actual   time=2.348..2.357 rows=113 loops=1) |
|                                                                                         Rows Removed by Join Filter: 2 |                                                                 Buckets: 1024  Batches: 1  Memory Usage: 14kB |
|                                                                                         ->  Parallel Hash Join  (cost=14787.03..32152.44 rows=214466   width=12) (actual time=2775.239..7602.610 rows=118928 loops=4) |                                                                 ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.023..1.171 rows=113 loops=1) |
|                                                                                               Hash Cond: (go.match_player_detail_id_1 = mpd.id) | Planning Time: 1.224 ms |
|                                                                                               ->  Parallel Seq Scan on   game_objectives go  (cost=0.00..16802.44   rows=214466 width=8) (actual time=0.027..1833.601 rows=165758 loops=4) | Execution Time: 122099.066 ms |
|                                                                                                     Filter: (subtype = 'CHAT_MESSAGE_TOWER_KILL'::text) |  |
|                                                                                                     Rows Removed by Filter: 127591 |  |
|                                                                                               ->  Parallel Hash  (cost=12770.90..12770.90 rows=161290   width=12) (actual time=2774.446..2774.457 rows=125000 loops=4) |  |
|                                                                                                     Buckets: 524288  Batches: 1  Memory Usage: 27648kB |  |
|                                                                                                     ->  Parallel Seq Scan on   matches_players_details mpd    (cost=0.00..12770.90 rows=161290 width=12) (actual   time=0.019..1374.543 rows=125000 loops=4) |  |
|                                                                                         ->  Hash  (cost=1016.00..1016.00 rows=50000 width=8)   (actual time=1078.068..1078.078 rows=50000 loops=4) |  |
|                                                                                               Buckets: 65536  Batches: 1  Memory Usage: 2466kB |  |
|                                                                                               ->  Seq Scan on matches  (cost=0.00..1016.00 rows=50000 width=8)   (actual time=0.038..536.976 rows=50000 loops=4) |  |
|                                                                                   ->  Hash  (cost=2.13..2.13 rows=113 width=14) (actual   time=2.376..2.387 rows=113 loops=4) |  |
|                                                                                         Buckets: 1024  Batches: 1  Memory Usage: 14kB |  |
|                                                                                         ->  Seq Scan on heroes  (cost=0.00..2.13 rows=113 width=14) (actual   time=0.028..1.201 rows=113 loops=4) |  |
| Planning Time: 1.206 ms |  |
| Execution Time: 112862.472 ms |  |


