import json
from time import sleep
import requests # type: ignore
from pprint import pprint
from datetime import datetime

import secrets
from databases import *


# Function to make API call
def call_api(APIParams, game):
    url = f'https://euw1.api.riotgames.com/{game}/summoners/by-puuid/{APIParams}'
    pprint(url)
    response = requests.get(url)
    return response.json()

# Function to store results in MySQL
def store_result(result, game):

    # Convert the timestamp to datetime  >> 1722455759000
    timestamp = result['revisionDate'] / 1000 # Convert milliseconds to seconds 
    dt_object = datetime.fromtimestamp(timestamp)

    if game == 'lol':
        sql = "INSERT INTO lolsummoner (id, accountId, puuid, profileIconId, revisionDate, summonerLevel) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id = VALUES(id), accountId = VALUES(accountId), puuid = VALUES(puuid)"
    elif game == 'tft':
        sql = "INSERT INTO tftsummoner (id, accountId, puuid, profileIconId, revisionDate, summonerLevel) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id = VALUES(id), accountId = VALUES(accountId), puuid = VALUES(puuid)"
    else:
        print('Invalid game name')
        return
    values = (result['id'], result['accountId'], result['puuid'], result['profileIconId'], dt_object, result['summonerLevel'])
    print((sql, values))
    cursor.execute(sql, values)
    conn.commit()

# Iterate over each game / puuid in the Database and process it
query = "SELECT puuid FROM lolpuuids"
cursor = conn.cursor()
cursor.execute(query)
results=cursor.fetchall()

for element in results:
    element=''.join(element)
    APIParams = f'{element}?api_key={secrets.LOLheaders["X-Riot-Token"]}'
    result = call_api(APIParams, "lol/summoner/v4")
    pprint(result)
    store_result(result, "lol")

    sleep(1.0)

query = "SELECT puuid FROM tftpuuids"
cursor = conn.cursor()
cursor.execute(query)
results=cursor.fetchall()

for element in results:
    element=''.join(element)
    APIParams = f'{element}?api_key={secrets.TFTheaders["X-Riot-Token"]}'
    result = call_api(APIParams, "tft/summoner/v1")
    pprint(result)
    store_result(result, "tft")

    sleep(1.0)

# Close the database connection
conn.close()
