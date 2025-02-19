# Basic Tool imports
import requests
import os, sys
from time import sleep
from os import system, name


# Manditory for the time conversions
from datetime import timedelta

# Used to hide api keys and load environment variables
from dotenv import dotenv_values # Used for Secrets and other environment Variables

# Panda - Dataframe imports
import pandas as pd
# from scipy import stats
# from tqdm.auto import tqdm


'''
This script requires multiple libraries which may require more package installations.

Use: pip install -r requirements text to get started.


- https://www.raidbots.com/static/data/live/talents.json (Use this to find out talent builds)
'''


# Load Secrets
my_secrets = dotenv_values(".env")
wcl_api_key = my_secrets["wcl_api_key"] # loads warcraftlogs api info (make sure to set this information in the .env file)


# Start of Functions


# Clear terminal if on windows or linux systems
def clear():
   if name == 'nt':
      _ = system('cls')
   else:
      _ = system('clear')


# Timestamp -> Readable time.
def mill_conv(milliseconds):
   t = timedelta(milliseconds=int(milliseconds))
   minutes = t.seconds // 60
   seconds = t.seconds % 60
   if seconds < 10:
      seconds = f"0{seconds}"
   return f"{minutes}:{seconds}"


# Main Functions
def get_fight_id(url):
    fight_id = ""
    while fight_id == "":
        try:
            #print(f"Log Link: ", end="")
            fight_id = url.split("reports/")[1].split("#fight")[0]
        except IndexError:
            raise("error")
            sleep(5)
            clear()
    fight_data = requests.get("https://www.warcraftlogs.com/v1/report/fights/{}?fight=1&api_key={}".format(fight_id,wcl_api_key)).json()
    # Debug fight_data
    print("https://www.warcraftlogs.com/v1/report/fights/{}?fight=1&api_key={}".format(fight_id,wcl_api_key))
    names = []
    name2id = {}

   
    counter = 1
    clear()
    print(f"Blood DK's found within fightID: {fight_id}\n\n")
    
    # Check for all Blood DKs
    for friendly in fight_data["friendlies"]:
        if friendly["icon"] == "DeathKnight-Blood": # Using icon instead of class type to sort out only BDK.
            name2id[friendly["name"]] = friendly["id"]
            names.append(friendly["name"])
            print(f"{counter} - {friendly['name']}")
            counter += 1

    print(f"\n\nPlease select the BDK # you want to review:", end="")
    select_player = 1 #need to change this to check for a character enterd by the user, for now will assume 1 BDK in log, will not work for raid logs for now
    player_id = name2id[names[select_player-1]]
    player_name = names[select_player-1]

    return fight_data, fight_id, player_id, player_name


def process_fight_data(fight_data):
    clear()
    f_fights = []
    for friendly in fight_data["friendlies"]:
        if friendly["id"] == player_id:
            for f in friendly["fights"]:
                f_fights.append(f["id"])

    id2times = {}
    for fight in fight_data["fights"]:
        if fight["boss"] != 0:
            if fight["id"] in f_fights:
                print(fight["name"] + ": " + str(fight["id"]))

                id2times[fight["id"]] = {
                    "start_time": fight["start_time"],
                    "end_time": fight["end_time"],
                    "boss": fight["boss"],
                    "zoneName": fight["zoneName"]
                }

                if "keystoneLevel" in fight:
                    id2times[fight["id"]]["keystoneLevel"] = fight["keystoneLevel"]
                    if "completionTime" in fight:
                        id2times[fight["id"]]["completionTime"] = fight["completionTime"]
                    else:
                        id2times[fight["id"]]["completionTime"] = "Brick"

                else:
                    id2times[fight["id"]]["name"] = fight["name"]
                    id2times[fight["id"]]["kill"] = fight["kill"]

    return  id2times


def get_event_data(id2times,player_id,fight_id,wcl_api_key,fightNBR):
    # Select Fight
    print("\n\n\nWhat log # would you like to check: ", end="")
    f_id = int(fightNBR);
    clear()   
    encounter = id2times[f_id]["boss"]
    zone_name = id2times[f_id]["zoneName"]
    start_time = id2times[f_id]["start_time"]
    end_time = id2times[f_id]["end_time"]
    if "keystoneLevel" in id2times[f_id]:
        keystone_level = id2times[f_id]["keystoneLevel"]

    if "completionTime" in id2times[f_id]:
        keyStats = "";
        if id2times[f_id]["completionTime"] == "Brick":
            timer = "Bricked"
            keyStats += (f"Player: {player_name}") + "\n";
            keyStats += (f"Key: {zone_name} +{keystone_level}") + "\n";
            keyStats += (f"Run Time: {timer}") + "\n";
        else:       
            timer = mill_conv(int(id2times[f_id]["completionTime"]))
            keyStats += (f"Player: {player_name}") + "\n";
            keyStats += (f"Key: {zone_name} +{keystone_level}") + "\n";
            keyStats += (f"Run Time: {timer}") + "\n";
        if keystone_level:
            excel_format = f"{player_name} - {zone_name} +{keystone_level}.xlsx"
    else:
        timer = mill_conv(end_time - start_time)
        boss_name = id2times[f_id]["name"]
        #need to implement the above changes for keyPlayer so output works in raid, in TODO 3
        # This section will do a check if the raid boss was killed or not. Leave this in incase you wish to change excel naming.
        if id2times[f_id]["kill"] == True:
            print(f"Player: {player_name}")
            print(f"Raid: {zone_name}")
            print(f"Boss: {boss_name}")
            print(f"Kill Time: {timer}")
            excel_format = f"{player_name} - {zone_name.split(',')[0]} - {boss_name.split(',')[0]}.xlsx"
        else:
            print(f"Player: {player_name}")
            print(f"Raid: {zone_name}")
            print(f"Boss: {boss_name}")
            print(f"Wiped @: {timer}")
            excel_format = f"{player_name} - {zone_name.split(',')[0]} - {boss_name.split(',')[0]}.xlsx"
    print(f"\n\n")

    event_data = requests.get("https://www.warcraftlogs.com/v1/report/events/{}?encounter={}&start={}&end={}&sourceid={}&api_key={}".format(fight_id, encounter, start_time, end_time, player_id, wcl_api_key)).json()
    # Debug event data
    #print(f"https://www.warcraftlogs.com/v1/report/events/{fight_id}?encounter={encounter}&start={start_time}&end={end_time}&sourceid={player_id}&api_key={wcl_api_key}")
    return  event_data, start_time, end_time, excel_format , keyStats


### Functions to Process DS information

# Gathers Death Strike info
def get_ds_info(event_data, start_time):
    ds_list = []
    for event in event_data["events"]:
        try:
            if event["ability"]["name"] == "Death Strike":
                if event["type"] == "heal":
                    if event["classResources"][0]["max"] != 0: #This filters heals on your dancing rune weapon
                        try:
                            overheal = event["overheal"]
                        except KeyError:
                            overheal = 0

                        millisec=event["timestamp"]-start_time
                        timer = mill_conv(millisec)


                        ds_list.append({
                            "timestamp": event["timestamp"],
                            "humantime": f"{timer}",
                            "amount": event["amount"],
                            "overheal": overheal,
                            "runic_power": event["classResources"][0]["amount"],
                            "hitPoints": event["hitPoints"],
                            "maxHitPoints": event["maxHitPoints"],
                            "absorb": event["absorb"]
                        })
        except KeyError:
            pass

 
    return ds_list


# Gathers Blood Shield info
def get_bs_info(event_data, start_time):
    bs_list = []
    for event in event_data["events"]:
        try:
            if event["ability"]["guid"] == 77535: #77535 is Blood Shield
                if event["type"] == "refreshbuff":

                        millisec=event["timestamp"]-start_time
                        timer = mill_conv(millisec)


                        bs_list.append({
                            "timestamp": event["timestamp"],
                            "humantime": f"{timer}",
                            "absorb": event["absorb"],
                            "type": event["type"]
                        })
        except KeyError:
            pass
        try:
            if event["ability"]["guid"] == 77535:
                if event["type"] == "applybuff":

                        millisec=event["timestamp"]-start_time
                        timer = mill_conv(millisec)


                        bs_list.append({
                            "timestamp": event["timestamp"],
                            "humantime": f"{timer}",
                            "absorb": event["absorb"],
                            "type": event["type"]
                        })
        except KeyError:
            pass
    # This command sorts the list to to make sure timestamps are in order
    sorted_list = sorted(bs_list, key=lambda x: (x["timestamp"]))
    return sorted_list


# gather player stats
def get_stats_info(event_data, stat):
    stat_info = []
    for event in event_data["events"]:
        try:
            if event["type"] == "combatantinfo":  # Vampiric Blood

                stat_info.append({
                    "stamina": event[stat]
                })
        except KeyError:
            pass

 
    return stat_info



# gather player buff information
'''
types (1 = applybuff, 2 = refreshbuff, 3 = removebuff,)

Buff GUID list
vampiric blood = 55255

'''
def get_buff_info(event_data, start_time, buff_guid, buff_type):
    buff_info = []
    if buff_type == 1:
        buff_type = "applybuff"
    if buff_type == 2:
        buff_type = "refreshbuff"
    if buff_type == 3:
        buff_type = "removebuff"
    for event in event_data["events"]:
        try:
            if event["ability"]["guid"] == buff_guid:
                if event["type"] == buff_type:

                    millisec=event["timestamp"]-start_time
                    # Saved for providing over all time a buff is up functionality
                    timer = mill_conv(millisec)

                    buff_info.append({
                        "timestamp": event["timestamp"],
                        # "humantime": f"timer",
                    })
        except KeyError:
            pass
 
    return buff_info


# Get vampiric Blood Data
def is_vb_active(ds_timestamp, vb_start, vb_end):
    for i in range(len(vb_start)):
        if ds_timestamp in range(vb_start[i]["timestamp"], vb_end[i]["timestamp"]):
            vb_end.append({"timestamp": end_time})

            return 1
    else:

            return 0


# Death Strike processing & dataframe management
def check_deathstrike(end_time, deathstrike_data, bloodshield_data, player_stam, vb_start, vb_end , keyStats):
    df_list = []
    index = 0
    for _ in range(len(vb_start)):
        if len(vb_start) > len(vb_end):
            vb_end.append({"timestamp": end_time})
    for info in deathstrike_data:
        rp = info['runic_power'] /10
        hp_before = info['hitPoints'] - info['amount']
        hp_per_before = round(hp_before / info['maxHitPoints'] *100, 1)
        hp_per_after = round(info['hitPoints'] / info['maxHitPoints'] *100, 1)
        per_healed = round(hp_per_after - hp_per_before,1)
        overhealing = round(info['overheal'] / info['maxHitPoints'] *100, 1)
        '''
        - This function is turned off as it wasn't requested in this version of the script but used later. Feel free to use it as you want.
        '''
        # Check to see if bloodshield is new or refreshed 
        # if bloodshield_data[index]['type'] == "applybuff":
        #     buff_type = "Apply"
        # if bloodshield_data[index]['type'] == "refreshbuff":
        #     buff_type = "Refresh"

        # Check if vamp blood is active during DS
        vamp_blood = is_vb_active(info["timestamp"],vb_start, vb_end)
        if vamp_blood == 0:
            vb_active = False
            # BS percentage of health
            bs_per = round(bloodshield_data[index]["absorb"] / info['maxHitPoints'] *100,1)
        if vamp_blood == 1:
            vb_active = True
            # Checks to adjust max hitpoint to the pre VB amount
            bs_per = round(bloodshield_data[index]["absorb"] / (info['maxHitPoints']/1.3) *100,1)
            minus_vb_hitpoints = round(info['maxHitPoints']/1.3)

        df_list.append({
            "timestamp": info['humantime'],
            "amount": info["amount"],
            "overheal": info["overheal"],
            "runic_power": rp,
            "hitPoints": info["hitPoints"],
            "maxHitPoints": info["maxHitPoints"],
            "BS_absorb": bloodshield_data[index]["absorb"],
            "hitPointsBefore": hp_before,
            "healthPbefore": hp_per_before,
            "healthPafter": hp_per_after,
            "VB_Active": vb_active
        })

        index += 1

    #df = pd.DataFrame(df_list)
    #df.index = df.index + 1 # starts the list at 1 not 0 
    #pd.options.display.max_rows = None
    #print(df)
    return(keyStats , df_list)

    '''
    print(f"\n\nWould you like to write this to a file? (y)es / (n)o: ", end="")
    if input()[0].lower() == "y" :
        try:
            os.makedirs("Sheets")
        except FileExistsError:
            pass
        with pd.ExcelWriter(f"./Sheets/{excel_format}") as writer:
            df.to_excel(writer)
        print(f"File successfully written to: ./Sheets/{excel_format}")
        sleep(3)
    #'''

###################
# Start of script #
###################

def main(url , fightNBR):

    clear()

    keep_running = True
    use_same_log = False

    while keep_running == True:
        
        # Gather all data
        if use_same_log == False:
            global fight_data,fight_id,player_id,player_name
            fight_data,fight_id,player_id,player_name = get_fight_id(url)
        else:
            print(fight_id)
        id2times = process_fight_data(fight_data)

        global event_data,start_time,end_time,excel_format,keyStats

        event_data,start_time,end_time,excel_format,keyStats  = get_event_data(id2times,player_id,fight_id,wcl_api_key,fightNBR)
        deathstrike_data = get_ds_info(event_data, start_time)
        bloodshield_data = get_bs_info(event_data, start_time)
        player_stats = get_stats_info(event_data, "stamina")
        player_stam = player_stats[0]["stamina"]*20



        # Vampiric Blood data
        vb_start = get_buff_info(event_data, start_time, 55233, 1)
        vb_end = get_buff_info(event_data, start_time, 55233, 3)

        # Run the DS script
        check_deathstrike(end_time, deathstrike_data, bloodshield_data, player_stam, vb_start, vb_end , keyStats)
        return(check_deathstrike(end_time, deathstrike_data, bloodshield_data, player_stam, vb_start, vb_end , keyStats) , id2times) #apart of TODO 1

        clear()
        keep_running = False
        '''
        print(f"Would you like to check another log? (y)es / (n)o:", end="")
        if input()[0].lower() == "y" :
            clear()
            print(f"Would you like to use the same log? (y)es / (n)o:", end="")
            if input()[0].lower() == "y" :
                use_same_log = True
                continue
            else:
                use_same_log = False
        else:
            clear()
            keep_running = False
        #'''
