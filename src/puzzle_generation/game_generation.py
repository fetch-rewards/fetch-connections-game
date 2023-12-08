import random
import json
import os

'''
Transforms the csv frost.csv into data.js (which has GAMES_TO_GENERATE number of games)

frost.csv was generated with the following query

select brands.logo_url, biz.name, brands.brand_code from 
FETCH_SERVICES_PROD.STAGING.brand_stage as brands
join FETCH_SERVICES_PROD.STAGING.business_stage as biz
on biz.id = brands.business_id
where brands.logo_url is not null and brands.hidden is null
limit 500

'''
WORDS_IN_CATEGORY = 4
CATEGORIES_IN_GAME = 4
GAMES_TO_GENERATE = 10

# generates a map of business to brand urls
def transform_csv(csv_file):
    output = {}
    file = open(csv_file, 'r')
    lines = file.readlines()

    for line in lines:
        pieces = line.split(',')
        brand_url = pieces[0]
        biz = pieces[1]

        if biz not in output:
            output[biz] = [brand_url]
        else:
            output[biz].append(brand_url)
    file.close()

    return output


# generates a list of games, where each game is an array of 4 biz-brand arrays
# does not allow the same business in a single game
def generate_games(biz_brands, num_games):
    games = []*num_games*CATEGORIES_IN_GAME

    game_count = 0
    while game_count < num_games:
        biz_in_game = set()
        while len(biz_in_game) < CATEGORIES_IN_GAME:
            biz = random.choice(list(biz_brands.keys()))
            brands = biz_brands[biz]
            if len(brands) >= CATEGORIES_IN_GAME and biz not in biz_in_game:
                game = [biz,random.sample(brands, WORDS_IN_CATEGORY)]
                games.append(game)
                biz_in_game.add(biz)
        game_count += 1
    return list(chunks(games,CATEGORIES_IN_GAME))

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def format_category(biz, brand_urls, diffuculty):
    category = {
        "category" : biz,
        "words": brand_urls,
        "difficulty": diffuculty,
    }
    return category

def format_output(games):
    game_out = []
    for game in games:
        game_arr = []
        difficulty = 1
        for category in game:
            game_arr.append(format_category(category[0], category[1], difficulty))
            difficulty += 1
        game_out.append(game_arr)

    rel_directory=os.path.relpath("src/lib","src/puzzle_generation")
    f = open(rel_directory+'/'+"data.js", 'w')
    f.write("export const CONNECTION_GAMES = ")
    f.write(json.dumps(game_out))
    f.write(";")
    f.close()

brand_map = transform_csv("frost.csv")
games = generate_games(brand_map, GAMES_TO_GENERATE)
format_output(games)