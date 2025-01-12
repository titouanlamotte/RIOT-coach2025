import json
from time import sleep
import requests # type: ignore
from pprint import pprint
from datetime import datetime

import secrets
from databases import *


# Function to make API call
def call_api(APIParams, game):
    url = f'https://euw1.api.riotgames.com/{game}/{APIParams}'
    pprint(url)
    response = requests.get(url)
    sleep(1.5)
    return response.json()

# Function to store results in MySQL
def store_result(result, game):

    # Convert the timestamp to datetime  >> 1722455759000
    now = datetime.now() 
    now_without_milliseconds = now.replace(microsecond=0)
    #pprint(now_without_milliseconds)
    dt_object = datetime.fromtimestamp(now_without_milliseconds.timestamp())

    result = result[0]
    # Ensure all keys in the list exist in the result dict with empty string if not present, TFT and LOL leagues are slightly different but we want to store the same keys
    keys = ['puuid','leagueId','queueType','tier','ratedTier','rank','ratedRating','summonerId','leaguePoints','wins','losses','veteran','inactive','freshBlood','hotStreak']
    for key in keys: 
        if key not in result: 
            pprint(f'{key} not in result')
            result[key] = ''
        else:
            result[key] = str(result[key])

    if game == 'lol':
        sql = "INSERT INTO lolleague (coachRevisionDate,puuid,leagueId,queueType,tier,ratedTier,`rank`,ratedRating,summonerId,leaguePoints,wins,losses,veteran,`inactive`,freshBlood,hotStreak) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE coachRevisionDate = VALUES(coachRevisionDate), puuid = VALUES(puuid), summonerId = VALUES(summonerId), queueType = VALUES(queueType)"
    elif game == 'tft':
        sql = "INSERT INTO tftleague (coachRevisionDate,puuid,leagueId,queueType,tier,ratedTier,`rank`,ratedRating,summonerId,leaguePoints,wins,losses,veteran,`inactive`,freshBlood,hotStreak) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE coachRevisionDate = VALUES(coachRevisionDate), summonerId = VALUES(summonerId), queueType = VALUES(queueType)"
    else:
        print('Invalid game name')
        return
    values = (dt_object, result['puuid'], result['leagueId'], result['queueType'], result['tier'], result['rank'], result['ratedTier'], result['ratedRating'], result['summonerId'], result['leaguePoints'], result['wins'], result['losses'], result['veteran'], result['inactive'], result['freshBlood'], result['hotStreak'])
    print((sql, values))
    pprint(check_sql_string(sql, values))
    cursor.execute(sql, values)
    conn.commit()

# Iterate over each game / puuid in the Database and process it
query = "SELECT id FROM lolsummoner"
cursor = conn.cursor()
cursor.execute(query)
results=cursor.fetchall()

for element in results:
    element=''.join(element)
    APIParams = f'{element}?api_key={secrets.LOLheaders["X-Riot-Token"]}'
    result = call_api(APIParams, "lol/league/v4/entries/by-summoner")
    pprint(result)
    if result == []:
        continue
    else:
        store_result(result, "lol")

    

query = "SELECT id FROM tftsummoner"
cursor = conn.cursor()
cursor.execute(query)
results=cursor.fetchall()

for element in results:
    element=''.join(element)
    APIParams = f'{element}?api_key={secrets.TFTheaders["X-Riot-Token"]}'
    result = call_api(APIParams, "tft/league/v1/entries/by-summoner")
    pprint(result)
    if result == []:
        continue
    else:
        store_result(result, "tft")


# Close the database connection
conn.close()
