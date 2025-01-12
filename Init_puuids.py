import json
from time import sleep
import requests # type: ignore
from pprint import pprint

import secrets
from databases import *

# Load JSON data
with open('init.json') as f:
    data = json.load(f)

# Function to make API call
def call_api(APIParams):
    url = f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{APIParams}'
    pprint(url)
    response = requests.get(url)
    return response.json()

# Function to store results in MySQL
def store_result(result, game):
    if game == 'lol':
        sql = "INSERT INTO lolpuuids (puuid, gameName, tagLine) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE  puuid = VALUES(puuid)"
    elif game == 'tft':
        sql = "INSERT INTO tftpuuids (puuid, gameName, tagLine) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE  puuid = VALUES(puuid)"
    else:
        print('Invalid game name')
        return
    values = (result['puuid'], result['gameName'], result['tagLine'])
    print((sql, values))
    cursor.execute(sql, values)
    conn.commit()

# Iterate over each element in the JSON array and process it
for element in data:
    pprint(element)

    APIParams = f'{element["gameName"]}/{element["tagLine"]}?api_key={secrets.LOLheaders["X-Riot-Token"]}'
    result = call_api(APIParams)
    pprint(result)
    store_result(result, "lol")

    APIParams = f'{element["gameName"]}/{element["tagLine"]}?api_key={secrets.TFTheaders["X-Riot-Token"]}'
    result = call_api(APIParams)
    pprint(result)
    store_result(result, "tft")

    sleep(0.5)

# Close the database connection
conn.close()
