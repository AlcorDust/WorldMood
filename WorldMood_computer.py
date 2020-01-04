import serial
import urllib.request
import json
import datetime
import time
import csv
import time
import codecs

ser = serial.Serial('/dev/ttyUSB1', 9600)

app_id = "xxxxxxx"
app_secret = "xxxxxxxxxxxxxxxxxxxxxxxxx" 

page_ids = {"Europe": ['rainews.it', 'lemonde.fr', 'ihre.sz', 'elpais', 'fakt24pl'], "Asia": ['dailybangladeshpratidin', 'PeoplesDaily', 'expressnewspk', 'khaosod', 'TheJapanNews'], "Africa": ['newsofafrica', 'elkhabarnews', 'MoroccoWorldNews', 'SundayTimesZA'], "North America": ['cnnpolitics', 'NationalPost', 'wsj', 'nytimes'],"South America": ['correiobraziliense', 'BuenosAiresHeraldcom', 'ElObservadorUY', 'bolivianexpress'],"Russia": ['russianewsofficial'], "Oceania": ['7NewsAustralia', 'theaustralian', 'nzherald.co.nz'], "Middle East" : ['The.Daily.Outlook.Afghanistan', 'DailyNewsEgypt', 'hamshahri', 'IsraelTodayMagazine', 'aljazeera']}   
countries_led = {"Europe":"2", "Asia":"1", "Africa":"4", "North America":"6", "South America":"5", "Russia":"7", "Oceania":"0", "Middle East" : "3"}
color_reaction = {"wow":(0,255,0),"love":(255,0,255),"sad":(0,0,255),"angry":(255,0,0), "haha":(255,255,0)}

countries_mood = dict()
local_reactions_now = dict()

access_token = app_id + "|" + app_secret

def request_until_succeed(url):
    req = urllib.request.Request(url)
    success = False
    while success is False:
        try: 
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL %s: %s" % (url, datetime.datetime.now()))
            print("Retrying.")

    return response.read().decode(response.headers.get_content_charset())


def unicode_normalize(text):
    return text.translate({ 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22,
                            0xa0:0x20 })

def scrapeFacebookPageFeedStatus(page_id, access_token):

    num_processed = 0   
    scrape_starttime = datetime.datetime.now()

    #print("\nScraping %s Facebook Page: %s" % (page_id, scrape_starttime))

    statuses = getFacebookPageFeedData(page_id, access_token, 1)                    

    for status in statuses['data']:

        if 'reactions' in status:

            #print("Done! Status Processed in %s" % (datetime.datetime.now() - scrape_starttime))

            return processFacebookPageFeedStatus(page_id, status,              
                access_token)


def getFacebookPageFeedData(page_id, access_token, num_statuses):

    # Reactions parameters
    base = "https://graph.facebook.com/v2.6"
    node = "/%s/posts" % page_id 
    fields = "/?fields=message,link,created_time,type,name,id," + \
            "comments.limit(0).summary(true),shares,reactions" + \
            ".limit(0).summary(true)"
    parameters = "&limit=%s&access_token=%s" % (num_statuses, access_token)
    url = base + node + fields + parameters

    # retrieve data
    data = json.loads(request_until_succeed(url))

    return data

def processFacebookPageFeedStatus(page_id, status, access_token):

    status_id = status['id']
    status_message = '' if 'message' not in status.keys() else \
            unicode_normalize(status['message'])
    link_name = '' if 'name' not in status.keys() else \
            unicode_normalize(status['name'])
    status_type = status['type']
    status_link = '' if 'link' not in status.keys() else \
            unicode_normalize(status['link'])

    status_published = datetime.datetime.strptime(
            status['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + \
            datetime.timedelta(hours=-5) # EST
    status_published = status_published.strftime(
            '%Y-%m-%d %H:%M:%S') 

    num_reactions = 0 if 'reactions' not in status else \
            status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else \
            status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']

    def getReactionsForStatus(status_id, access_token):

        base = "https://graph.facebook.com/v2.6"
        node = "/%s" % status_id
        reactions = "/?fields=" \
                "reactions.type(LIKE).limit(0).summary(total_count).as(like)" \
                ",reactions.type(LOVE).limit(0).summary(total_count).as(love)" \
                ",reactions.type(WOW).limit(0).summary(total_count).as(wow)" \
                ",reactions.type(HAHA).limit(0).summary(total_count).as(haha)" \
                ",reactions.type(SAD).limit(0).summary(total_count).as(sad)" \
                ",reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
        parameters = "&access_token=%s" % access_token
        url = base + node + reactions + parameters

        # retrieve data
        data = json.loads(request_until_succeed(url))

        return data

    reactions = getReactionsForStatus(status_id, access_token) if \
            status_published > '2016-02-24 00:00:00' else {}

    num_likes = 0 if 'like' not in reactions else \
            reactions['like']['summary']['total_count']

    num_likes = num_reactions if status_published < '2016-02-24 00:00:00' \
            else num_likes

    def get_num_total_reactions(reaction_type, reactions):
        if reaction_type not in reactions:
            return 0
        else:
            return reactions[reaction_type]['summary']['total_count']

    num_loves = get_num_total_reactions('love', reactions)
    num_wows = get_num_total_reactions('wow', reactions)
    num_hahas = get_num_total_reactions('haha', reactions)
    num_sads = get_num_total_reactions('sad', reactions)
    num_angrys = get_num_total_reactions('angry', reactions)
    
    # Return a list of all processed data

    return [status_id, status_message, link_name, status_type, status_link,
            status_published, num_reactions, num_comments, num_shares,
            num_likes, num_loves, num_wows, num_hahas, num_sads, num_angrys]


if __name__ == '__main__':

    while(1):

        for country in page_ids.keys():
        
            print('\n' + country)

            local_reactions_now['love']=0
            local_reactions_now['wow']=0
            local_reactions_now['haha']=0
            local_reactions_now['sad']=0
            local_reactions_now['angry']=0

            for page_id in page_ids[country]:
            
                print('\t' + page_id)
                lista = scrapeFacebookPageFeedStatus(page_id, access_token)

                local_reactions_now['love']+=lista[10]
                local_reactions_now['wow']+=lista[11]
                local_reactions_now['haha']+=lista[12]
                local_reactions_now['sad']+=lista[13]
                local_reactions_now['angry']+=lista[14]

            for reaction in local_reactions_now.keys():

                print(reaction + ' : ' + str(local_reactions_now[reaction]))

            highest = max(local_reactions_now, key=lambda key: local_reactions_now[key])

            print(highest)
            print(color_reaction[highest])

            color_list = color_reaction[highest]

            payload = str(color_list[0]) + "," +  str(color_list[1]) + "," +  str(color_list[2]) + "," + countries_led[country] + ",&"

            #payload="0,0,255," + countries_led[country] + ",&"
            bytes = str.encode(payload)
            print(bytes)
            ser.write(bytes)

            

