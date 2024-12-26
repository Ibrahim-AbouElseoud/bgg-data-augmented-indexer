from requests_cache.core import CachedSession
from boardgamegeek import BGGClient
from boardgamegeek import BGGChoose
from boardgamegeek import BGGApiError
import csv
import sys
import time
import jellyfish
import logging
# import pkg_resources #required for pyinstaller but not required to run from source code


bgg = BGGClient()
rows_list=[]

def setup_logger(name, log_file, level=logging.INFO,enable_console=True):
    file_formatter=logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    file_handler = logging.FileHandler(log_file,'w','utf-8')        
    file_handler.setFormatter(file_formatter)

    logger = logging.getLogger(name)

    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    logger.setLevel(level)
    logger.addHandler(file_handler)
    
    return logger

log = setup_logger('logger', 'bgg_csv_indexer.log')


def read_csv(file="games.csv"):
    """Read CSV, Must have fields: Game,Owned by"""
    try:
        with open(file,encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row_data = {}
            for row in reader:
                row_data['Game']=row['Game']
                row_data['Owned by']=row['Owned by']
                rows_list.append(row_data)
                row_data = {}
        
        log.info("CSV Input Loaded Successfully from "+ file)
        
    except Exception as e:
        log.error("Error in opening file, error: "+str(e))
        log.error("Terminating program")
        sys.exit()

def find(game_name,find_error_counter):
    log.info("Processing game: "+str(game_name))
    try:
    #try getting game directly
        return bgg.game(game_name,choose=BGGChoose.BEST_RANK) 
    except Exception as e:
        log.warning("Can't find game directly, this is the error: "+str(e))
    # Can't find so will search by name
    try:
        log.info("Will try searching for the game on bgg by name: "+game_name)
        games = bgg.search(game_name)
        max_simi=0
        max_game=None
        log.info("Number of returned games: "+str(len(games))+" for query: "+game_name)
        for game in games:
            #use jaro_winkler_similarity to get closest name
            curr_simi=jellyfish.jaro_winkler_similarity(game_name,game.name)
            log.info("Game: "+game.name+" id: "+str(game.id)+" jaro_winkler_similarity: "+str(curr_simi))
            if curr_simi>max_simi:
                max_simi=curr_simi
                max_game=game

        if max_game is not None:
            log.info("Most matching game returned: "+str(max_game.name)+" for query name: "+game_name)
            max_game=bgg.game(game_id=max_game.id) #get game object not thingie 
    except BGGApiError:
        if find_error_counter < 4:
             find_error_counter += 1
             find(game_name,find_error_counter)
        else:
            log.error("Api call failing, will not try again, have tried 4 times already, skipping game "+game_name)  
            return None
        

    return max_game

def get_attributes(game):
    game_dict=dict()
    game_dict["bggName"] = game.name
    game_dict["url"] = "https://boardgamegeek.com/boardgame/"+str(game.id)
    game_dict["minTime"] = game.min_playing_time
    game_dict["maxTime"] = game.max_playing_time
    game_dict["complexity"] = game.rating_average_weight
    game_dict["minPlayers"] = game.min_players
    game_dict["maxPlayers"] = game.max_players
    game_dict["mechanics"] = game.mechanics
    game_dict["categories"] = game.categories
    game_dict["isExpansion"] = game.expansion
    game_dict["rating"] = game.rating_average
    game_dict["rank"] = game.bgg_rank
    game_dict["year"] = game.year
    print("Game attributes:",game_dict)
    log.info("Game attributes: "+str(game_dict))
    return game_dict

def write_csv(game_dict_list,file_name="boardgames_indexed.csv"):
    log.info("Writing CSV with "+str(len(game_dict_list))+" games")
    # csv header
    fieldnames = ['game', 'owner','bggName','minPlayers','maxPlayers','complexity','rating','rank','minTime','maxTime','isExpansion','year','categories','mechanics','url']
    with open(file_name, 'w', encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(game_dict_list)

def main():
    game_dict_list=[]
    for row in rows_list:
        game_dict=dict()
        isSkip=False
        game_name=row['Game']
        try:
            if game_name == None or game_name.strip() == "":
                continue
            else:
                game=find(row['Game'].strip(),0)
                if(game is None):
                    log.info("No entry found for game name: "+game_name+"...skipping...")
                    isSkip=True
            if not isSkip:
                game_dict = get_attributes(game)
        
        except Exception as e:
            log.error("Exception happened while processing game "+game_name+" so will skip, exception: "+e)
        
        game_dict['game']=row['Game']
        game_dict['owner']=row['Owned by']
        game_dict_list.append(game_dict)
    
    write_csv(game_dict_list)



if __name__ == "__main__":
    start_time = time.time()
    # Get the CSV file path
    file_path = input("Please enter the path of the CSV file: ")
    read_csv(file_path)
    main()
    log.info("Elapsed Time: --- %s seconds ---" % (time.time() - start_time))

