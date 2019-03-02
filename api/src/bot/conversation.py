import watson_developer_cloud
import pywapi
import datetime
import time
from scipy import stats
import numpy as np
from sklearn import datasets,linear_model
from pprint import pprint
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
from .models import BotContext, CropForcasting
from upaj.settings import logging as logger

# from sklearn.tree import

DATA_GOV_API = '579b464db66ec23bdd000001f4159aa056f849bb6c7922a7a5c2cc99'

conversation = watson_developer_cloud.ConversationV1(
    username='6c3fe2ff-40bd-4cc4-968a-a2d5f282e5ec',
    password='hWIJrde0H551',
    version='2018-03-08'
)

# Calculate the mean value of a list of numbers
def mean(values):
	return float(float(sum(values)) / float(len(values)))

# Calculate covariance between x and y
def covariance(x, mean_x, y, mean_y):
	covar = 0.0
	for i in range(len(x)):
		covar = covar + float(x[i] - mean_x) * float(y[i] - mean_y)
	return covar

# Calculate the variance of a list of numbers
def variance(values, xmean):
	return float(sum([float(x-xmean)**2 for x in values]))

# Calculate coefficients
def coefficients(X,Y):
	x_mean, y_mean = mean(X), mean(Y)
	b1 = covariance(X, x_mean, Y, y_mean) / variance(X, x_mean)
	b0 = y_mean - b1 * x_mean
	return [b0, b1]

# Simple linear regression algorithm
def simple_linear_regression(X,Y):
	b0, b1 = coefficients(X,Y)
	return [b0,b1]


def get_response(chat):

    ''' Calls the Watson API for responses'''

    workspace_id = '650f9948-7391-4a98-bf15-996caee0fb0a'
    response = conversation.message(workspace_id=workspace_id, input={'text': chat})
    return response

def valid_location(location):
    if location is None or location == '':
        return False
    return True

def smalltalk(query):
    init_talks = ["Hi","Hello","Hey"]
    if query in init_talks:
        return True
    return False

def helptalk(query):
    init_talks = ["help","help me","can you help me","help","reset"]
    if query in init_talks:
        return True
    return False

def chatDriver(query,location=None,user=None):
    if smalltalk(query) or helptalk(query):
        BotContext.set_context_from_session(user,"") 
    elif user is not None:
        ctx = BotContext.get_context_from_session(user)
        logger.debug(ctx)
        # Getting Context
        if ctx == "#new_location_weather":
            BotContext.set_context_from_session(user,"")
            query = "what is the Weather for " + query
        elif ctx == "#flow_crop_prediction_location":
            BotContext.set_context_from_session(user,"")
        elif ctx == "#minimum_support_price":
            BotContext.set_context_from_session(user,"")
            query = "What is minimum price for " + query
        elif ctx == "#pesticide":
            BotContext.set_context_from_session(user,"")
            query = "Pesticide for " + query
        elif ctx == "#cultivation":
            BotContext.set_context_from_session(user,"")
            query = "Cultivation techniques for " + query
    
    intents = []
    entities = []

    try:
        watson_replies = get_response(query)
        response = watson_replies.result
        # pprint(response)
    except:
        return_data = {}
        return_data["text"] = 'Sorry! Not available right now.'
        return_data["options"] = []
        return return_data

    logger.debug("response : ")
    logger.debug(response)
    #logger.debug(entities)

    for intent in response['intents']:
        intents.append(intent['intent'])

    for entity in response['entities']:
        entities.append(entity)

    if 'greetings' in intents:
        return greeting(response)

    if 'weather' in intents:
        return location_suggestions(entities,location)

    if 'cost' in intents:
        return minimum_support_price_prediction(response,user=user)

    if 'pesticide' in intents:
        return pesticide(entities)

    if 'goodbyes' in intents:
        return bye()

    if 'cultivation' in intents:
        return cultivation(response)

    if 'help' in intents:
        return helpme()

    if 'customer_support' in intents:
        return customer_support()

    # check for any flow that exists.
    #try:
    location = entities[0]['value']
    logger.debug("location")
    logger.debug(location)
    logger.debug(ctx)
    if valid_location(location) and ctx == "#flow_crop_prediction_location":
        logger.debug("oh yeah")
        BotContext.set_location_context_from_session(user,location,"#flow_crop_prediction_season")
        return crop_forecasting_season()
    #except:
    #    pass

    if 'crop_forecasting' in intents:
        return crop_forecasting(entities,location)

    data_return = {}
    data_return["text"] = response
    data_return = clear_flow(data_return)
    return data_return

# Functions are defined below

def customer_support():
    customer = {}
    customer["text"] = "You can call up Kisan Call Center (KCC) through a toll free number 1800-180-1551 for more information"
    customer["options"] = []
    return customer

def helpme():
    help_text = {}
    help_text["text"] = "I can help you with crop forcasting, pesticide suggestion, fertilizers, weather reports, suggestions to best practice for crop cultivation and much more."
    help_text["options"] = []
    return help_text

def bye():
    return response_encoder("It was a pleasure to help you.")

def cultivation(response):
    search = response['input']['text']
    base = "https://www.youtube.com/results?search_query="

    r = requests.get(base+search)
    soup = BeautifulSoup(r.text,'html.parser')
    vids = soup.findAll('a',attrs={'class':'yt-uix-tile-link'})

    video_link = []
    count = 0
    for v in vids:
        temp = 'https://www.youtube.com' + v['href']
        video_link.append(temp)
        if(count >= 3):
            break
        count+=1

    return_data = {}
    return_data["links"] = video_link
    return_data = clear_flow(return_data)
    return return_data

def rephrase(response):

    ''' asks user to rephrase itself'''

    return response_encoder("Did not understand! Please try again.")

def greeting(response):

    ''' returns greetings messages'''
    data = {}
    data["text"] = response['output']['text'][0] + '\n' + 'I can help you with crop forcasting, pesticide suggestion, fertilizers, weather reports, suggestions to best practice for crop cultivation and much more.'
    data["options"] = greeting_flow()
    return data

# flows defined for the greetings
def greeting_flow():
    flows = []
    flows.append({"key":"#flow_weather","value": "Weather"})
    flows.append({"key":"#flow_crop_prediction","value": "Crop Prediction"})
    flows.append({"key":"#flow_cost","value": "Minimum Support Price"})
    flows.append({"key":"#flow_pesticide","value": "Pesticide"})
    flows.append({"key":"#flow_cultivation","value": "Cultivation"})
    flows.append({"key":"#flow_support","value": "Customer Support"})
    return flows

def ask_location():
    data = {}
    data["text"] = "Please enter location ?"
    return data

def flow_weather(location,user):
    if location is None:
        location = BotContext.get_location_from_session(user)
        if location is None:
            return ask_location()
    BotContext.set_location_from_session(user,location)
    return location_suggestions(None,city=location)

def clear_flow(return_data):
    return_data["options"] = [{"key":"#clear","value":"Anything else I can help you with ?"}]
    return return_data

def crop_forecasting_season():
    data = {}
    data["text"] = "Please choose one of the given season ?"
    data["options"] = [{"key":"#crop_forcasting_rabi","value":"Rabi"},{"key":"#crop_forcasting_kharif","value":"Kharif"},{"key":"#crop_forcasting_autumn","value":"Autumn"},{"key":"#crop_forcasting_wholeyear","value":"Whole Year"}] 
    return data

def ChatDriverFlow(query,location=None,user=None):
    if query == "#flow_weather":
        data = flow_weather(location,user)
        data["options"] = [{"key":"#new_location_weather","value":"For some other location ?"},{"key":"#clear","value":"No"}]
        return data
    if query == "#new_location_weather":
        BotContext.set_context_from_session(user,"#new_location_weather")
        return ask_location()
    if query == "#clear":
        BotContext.set_context_from_session(user,"")
        data = {}
        data["text"] = "Anything else I can help you with ?"
        data["options"] = greeting_flow()
        return data

    if query == "#flow_crop_prediction":
        location = BotContext.get_location_from_session(user)
        if valid_location(location):
            data = {}
            data["text"] = "Do you want Crop prediction for " + location + " ?"
            data["options"] = [{"key":"#flow_crop_prediction_location_yes","value":"Yes for " + str(location)},{"key":"#flow_crop_prediction_location_no","value":"No"}]
            return data
        else:
            BotContext.set_context_from_session(user,"#flow_crop_prediction_location")
            return ask_location()

    if query == "#flow_crop_prediction_location_no":
        BotContext.set_context_from_session(user,"#flow_crop_prediction_location")
        return ask_location()

    if query == "#flow_crop_prediction_location_yes":
        return crop_forecasting_season()

    if query == "#crop_forcasting_rabi":
        location = BotContext.get_location_from_session(user)
        if valid_location(location):
            return crop_forecasting_v2(user,location.lower(),"rabi")
        else:
            return chatDriver("#flow_crop_prediction",None,user=user)
    if query == "#crop_forcasting_kharif":
        location = BotContext.get_location_from_session(user)
        if valid_location(location):
            return crop_forecasting_v2(user,location.lower(),"kharif")
        else:
            return chatDriver("#flow_crop_prediction",None,user=user)

    if query == "#crop_forcasting_autumn":
        location = BotContext.get_location_from_session(user)
        if valid_location(location):
            return crop_forecasting_v2(user,location,"autumn")
        else:
            return chatDriver("#flow_crop_prediction",None,user=user)

    if query == "#crop_forcasting_wholeyear":
        location = BotContext.get_location_from_session(user)
        if valid_location(location):
            return crop_forecasting_v2(user,location,"whole year")
        else:
            return chatDriver("#flow_crop_prediction",None,user=user)

    if query == "#flow_cost":
        crop = BotContext.get_crop_from_session(user)
        data_return = {}
        if not (crop is None or crop == ''):
            data_return["text"] = "Do you want the Minimum support Price for crop " + crop + " ?"
            data_return["options"] = [{"key":"#msp_yes","value":"Yes"},{"key":"#msp_no_ask_crop","value":"No"}]
            return data_return
        else:
            data_return["text"] = "Please Tell me the crop name for which Minimumm price is required."
            data_return["options"] = []
            return data_return

    if query == "#msp_yes":
        crop = BotContext.get_crop_from_session(user)
        return minimum_support_price_prediction(None,crop)

    if query == "#msp_no_ask_crop":
        BotContext.set_context_from_session(user,"#minimum_support_price")
        data_return = {}
        data_return["text"] = "Please tell me the crop name for which Minimum Price is required."
        data_return["options"] = []
        return data_return

    if query == "#flow_pesticide":
        data_return = {}
        data_return["text"] = "Please tell me the name Disesase for which you need suggestions of pesticide to be used."
        data_return["options"] = []
        BotContext.set_context_from_session(user,"#pesticide")
        return data_return

    if query == "#flow_cultivation":
        data_return = {}
        data_return["text"] = "Some of the suggestions required for growing crops ?"
        data_return["options"] = []
        BotContext.set_context_from_session(user,"#cultivation")
        return data_return

    if query == "#flow_support":
        return customer_support()

    return helpme()

def weather(location_id):
    ''' returns weather conditions for a given location id '''
    weather_data = pywapi.get_weather_from_weather_com(location_id)
    print(weather_data)
    response = {}
    response['temperature'] = "Temperature : " + str(weather_data['current_conditions']['temperature']) + " C"
    response['humidity'] = "Humidity : " + str(weather_data['current_conditions']['humidity'])
    response['windspeed'] = "Wind Speed : " + str(weather_data['current_conditions']['wind']['speed'])

    return response

def location_suggestions(entities,city=None):

    ''' facilitates search of location '''
    # print(entities[0]["value"])

    try:
        location = entities[0]['value']
    except:
        location = city

    data_return = {}
    try:
        # data = pywapi.get_location_id(location)
        weather_data_url = 'https://api.openweathermap.org/data/2.5/weather?q=' + location + ',in&appid=c4ebee5432d574b968a2332bfa6ab6f4&units=metric'
        r = requests.get(weather_data_url)
        data = r.json()
        # print (data)
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        discription = data["weather"][0]["description"]
        response_text = "The current temperature for " + str(location) +" is " + str(temp) + "C and humidity is " + str(humidity) + "% " + "expecting a " + discription
        if ("clear sky" in discription.lower()):
            response_text += " No worries."
        elif ("clouds" in discription.lower()):
            response_text += ". Overcast might be there, take care for your crop."
        # print(response_text)
        data_return["text"] = response_text
        return data_return
    except:
        data_return["text"] = "Sorry! Couldn't find for your location"
        return data_return

    # if len(data) is 1:
    #     for loc_id, location in data.items():
    #         return response_encoder(weather(loc_id))
    # else:
    #     for loc_id, location in data.items():
    #         if 'India' in location:
    #             return response_encoder(weather(loc_id))
    #         else:
    #             print ('There are number quite a few location with similar set of name, please be specific')
    #             return response_encoder(data)

def pesticide(entities):

    ''' returns pesticide information '''
    no_query = 'I can help you with the pesticide for beetle, insect, blight, grasshopper and many more. For ex : best pesiticide for beetle, insect, blight etc'
    if len(entities) == 0 or 'values' in entities[0]:
        return_data = {}
        return_data["text"] = no_query
        return_data["options"] = []
        return return_data

    value = entities[0]['value']
    pesticide = pd.read_csv('csv_files/pesticides.csv')
    try:
        var = {}
        ad = "Shukla Agri Traders, Jabalpur market."
        data = pesticide.loc[pesticide['disease'] == value]
        var["text"] = "user this pesticide "  + data.iloc[0]['pesticide']
        var["text"] += " which you can purchase from " + ad
        var = clear_flow(var)
        return var
    except:
        data_return = {}
        data_return["text"] = "No data for the specified disease! Please try after some time."
        data_return = clear_flow(data_return)
        return data_return

def minimum_support_price_prediction(response,crop_name=None,user=None):

    ''' provides a predicted minimum support price '''

    if crop_name is None:
        try:
            crop = response['entities'][0]['value']
            BotContext.set_crop_from_session(user,crop)
        except:
            return_data = {}
            return_data["text"] = "Could not find crop name. Please specify the proper crop name alongside the query."
            return_data = clear_flow(return_data)
            return return_data
    else:
        crop = crop_name

    dataframe = pd.read_csv('csv_files/crops.csv')
    msp_cost = -1
    now = datetime.datetime.now()

    try:
        crop_price_history = dataframe.loc[dataframe['crop'] == crop]
    except:
        crop_price_history = []
        return 0

    crop_price_history = crop_price_history.drop(columns="crop")
    crop_price_history = pd.melt(crop_price_history, var_name='year', value_name='price')

    x = crop_price_history['year'].tolist()
    y = crop_price_history['price'].tolist()

    if len(crop_price_history) == 0:
        return response_encoder("No previous cost records found for the given crop.")

    x = np.array(x).astype(np.float)
    y = np.array(y).astype(np.float)

    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

    try:
        current_year = now.year
        predicition = current_year*slope + intercept

        if(predicition <= 0):
            output = str('Sorry! no prediction avialable')
        else:
            output = str('The minimum selling price of ' + crop + ' is expected to be \u20B9' +str(predicition.round()))
    except:
        output = str('Sorry! no prediction available')
    return_data = {}
    return_data["text"] = output
    return_data = clear_flow(return_data)
    return return_data

def crop_forecasting_v2(user,location,season):
    crop_forcastdb = CropForcasting.get_crop(location,season)
    if crop_forcastdb:
        crop = crop_forcastdb[0].crop
        crops = crop.split(",")
        output2 = []
        output2.append("List of possible crop which can be grown with there approximate production this season \n")
        for crp in crops:
            output2.append(crp)
        return_data["list"] = output2
        return_data = clear_flow(return_data)
        return return_data
    now = datetime.datetime.now()
    data = pd.read_csv('csv_files/crop_production.csv')
    data = data.values
    output2 = []
    
    if(True):
        # print (str(season).lower() + " " + str(location).lower())
        Crop = {}
        for i in range(1,len(data)):
            data[i][3] = str(data[i][3].lower())
            data[i][3] = data[i][3].strip()
            data[i][1] = str(data[i][1].lower())
            data[i][1] = data[i][1].strip()
            if(str(location.lower()) == data[i][1]  and season.lower() == data[i][3].lower()):
                try:
                    # setting each crop to its production in the year as a pair of production per unit km and year.
                    value = float(float(data[i][6])/float(data[i][5]))
                    year = int(data[i][2])
                    if(not data[i][4] in Crop):
                        Crop[data[i][4]] = [[value],[year]]
                    else:
                        Crop[data[i][4]][0].append(value)
                        Crop[data[i][4]][1].append(year)
                    # Production.append(float(data[i][6])/float(data[i][5]))
                    # Year.append(data[i][2])
                except:
                    continue
            # break
        predicted_crop = []
        # print ("Crop :",end=' ')
        # print (Crop)
        # logger.debug(Crop)
        for crop in Crop:
            Production = []
            Year = []
            Production = Crop[crop][0]
            Year = Crop[crop][1]    
            # try:
            # print (Year,Production)
            if len(Production) > 1:
                [b0,b1] = simple_linear_regression(Year,Production)
                current_year = now.year
                predicition = current_year*b1+b0
                if(float(predicition) == 0):
                    continue
                predicted_crop.append((predicition,crop))
            # except:
            #    continue
            # output1 += str(i + " " + str(predicition) + " ")
            #print (i + " " +str(predicition))
        # logger.debug(predicted_crop)
        predicted_crop.sort(reverse=True)
        cnt = 2
        index = 1
        # top five crops for production
        for i in range(len(predicted_crop)):
            cnt+=1
            if(cnt > 5):
                break
            if(predicted_crop[i][0] > 0):
                output2.append(str(index) + " " +predicted_crop[i][1] + " " + str(predicted_crop[i][0]) + " metric tonne/hectare \n")
                index+=1

    data_return = {}
    if (len(output2) == 0):
        data_return = {}
        data_return["text"] = "Not data found for the region"
    else:
        CropForcasting.set_crop(location.lower(),season.lower(),",".join(output2))
        output2.insert(0,"List of possible crop which can be grown with there approximate production this season \n")
        data_return["list"] = output2

    data_return = clear_flow(data_return)
    return data_return

def crop_forecasting(entities,loc,user=None):
    now = datetime.datetime.now()
    try:
        location = entities[0]['value']
    except:
        location = loc
        # return response_encoder("Please specify place alongside the query.")
    if(now.month >= 7 and now.month <= 10):
        season = 'kharif'
    elif(now.month >= 10 and now.month <= 11):
        season = 'autumn'
    elif((now.month >= 11 and now.month <= 12) or now.month <= 1):
        season = 'rabi'
    else:
        season = 'whole year'

    if valid_location(location):
        return crop_forecasting_v2(user,location,season)

    return ChatDriverFlow(query="#flow_crop_prediction",location=None,user=user)

def response_encoder(response):

    ''' encodes message to the proper format '''

    message = {}
    message['bubbles'] = 1
    message['text'] = []

    if type(response) == str:
        message['text'].append('<div class="message new"><figure class="avatar"><img src="../static/images/chathead.png" /></figure>' + response + '</div>')
    elif type(response) == dict:
        for key, value in response.items():
            message['text'].append('<div class="message new"><figure class="avatar"><img src="../static/images/chathead.png" /></figure>' + key + " : " + value + '</div>')
        message['bubbles'] = len(response)
    elif type(response) == list:
        for i in range(len(response)):
            if(i == 0):
                message['text'].append('<div class="message new"><figure class="avatar"><img src="../static/images/chathead.png" /></figure>' + response[i] + '</div>')    
            else:
                message['text'].append('<div class="message new"><figure class="avatar"><img src="../static/images/chathead.png" /></figure>' + str(i) + " : " + response[i] + '</div>')
        message['bubbles'] = len(response)
    print (message)
    return message


StateDict = {
    'jammu and kashmir' : 1,
    'himachal pradesh' : 2,
    'punjab' : 3,
    'uttarakhand' : 4,
    'arunachal pradesh' : 5,
    'chandigarh' : 6,
    'sikkim' : 7,
    'haryana' : 8,
    'uttar pradesh' : 9,
    'assam' : 10,
    'nagaland' : 11,
    'meghalaya' : 12,
    'bihar' : 13,
    'manipur' : 14,
    'rajasthan' : 15,
    'tripura' : 16,
    'mizoram' : 17,
    'jharkhand' : 18,
    'west bengal' : 19,
    'madhya pradesh' : 20,
    'gujarat' : 21,
    'dadra and nagar haveli' : 22,
    'chhattisgarh' : 23,
    'odisha' : 24,
    'maharashtra' : 25,
    'telangana' : 26,
    'goa' : 27,
    'karnataka' : 28,
    'andhra pradesh' : 29,
    'puducherry' : 30,
    'andaman and nicobar islands' : 31,
    'tamil nadu' : 32,
    'kerala' : 33,
}


SeasonDict = {
    'Summer     ' : 1,
    'Whole Year ' : 2,
    'Kharif     ' : 3,
    'Autumn     ' : 4,
    'Winter     ' : 5,
    'Rabi       ' : 6,
}


CropsDict = {

    # Crops (0 - 12)

    'Bajra' : 1, 'Pearl Millet' : 1, 'Pearlmillet' : 1,
    'Rice' : 2, 'Chawal' : 2, 'Paddy' : 2,
    'Maize' : 3, 'Makka' : 3, 'Makai' : 3, 'Corn' : 3,
    'Wheat' : 4, 'Gayhoon' : 4, 'Gehu' : 4, 'Gehoon' : 4, 'Gehun' : 4,
    'Jowar' : 5, 'Jwar' : 5, 'Sorghum' : 5,
    'Korra' : 6, 'Foxtail Millet' : 6, 'Kangani' : 6, 'Kangni' : 6, 'Millet' : 6,

    'Ragi' : 7,
    'Raagi' : 7,
    'Finger Millet' : 7,

    'Samai' : 8,
    'Small millets' : 8,
    'Little Millet' : 8,
    'Minor Millet' : 8,
    'Sma' : 8,
    'Til' : 8,
    'Tilli' : 8,

    'Barley' : 9,
    'jau' : 9,
    'jo' : 9,

    'Total foodgrain' : 10,

    'Varagu' : 11,
    'Kodo Millet' : 11,
    'kodra' : 11,
    'Arikelu' : 11,

    'Other Cereals & Millets' : 12,

    # Spices (150 - 158)

    'Coriander' : 151,
    'Dhaniya' : 151,
    'Cilantro' : 151,

    'Dry ginger' : 152,

    'Black pepper' : 153,
    'Kaali Mirch' : 153,
    'Kaalimirch' : 153,
    'Kali Mirch' : 153,
    'Kalimirch' : 153,

    'Dry chillies' : 154,
    'Sookhi Mirch' : 154,
    'Sukhi Mirch' : 154,

    'Turmeric' : 155,
    'Haldi'  : 155,
    'Hardi' : 155,
    'Hardy' : 155,
    'Haldy' : 155,

    'Cardamom' : 156,
    'Caedamon' : 156,
    'Cardamum' : 156,
    'Chhoti Ilayachi' : 156,
    'Ilaychi' : 156,
    'Ilayachi' : 156,

    'Garlic' : 157,
    'Lehsun' : 157,
    'Lahsun' : 157,

    'Ginger' : 158,
    'Adrak' : 158,

    # Unsorted (200 - )

    'Sannhamp' : 200,

    'Khesari' : 201,

    'Guar seed' : 202,

    'Jobster' : 203,

    'Perilla' : 204,

    'Lab-Lab' : 205,

    # Oil Seeds (20 - 32)

    'Sesamum' : 21,
    'Sesame' : 21,
    'Benne' : 21,

    'Linseed' : 22,
    'Flax' : 22,
    'Teesi' : 22,
    'Alsi' : 22,

    'Safflower' : 23,
    'Kusum' : 23,

    'Soyabean' : 24,
    'Soybean' : 24,

    'Citrus Fruit' : 25,

    'Groundnut' : 26,
    'Peanut' : 26,
    'Moong Fali' : 26,
    'Moongfali' : 26,
    'Mung Fali' : 26,
    'Mungfali' : 26,

    'Castor seed' : 27,
    'Arandi' : 27,
    'arandi' : 27,
    'Leri'  : 27,
    'Ledi' : 27,

    'other oilseeds' : 28,

    'Sunflower' : 29,
    'Soorajmukhi' : 29,
    'Surajmukhi' : 29,

    'Oilseeds total' : 30,

    'Niger seed' : 31,
    'Nigerseed' : 31,
    'Thisel' : 31,
    'Nyger' : 31,
    'Kalaunji' : 31,
    'Ram Til' : 31,
    'Ramtil' : 31,

    'Rapeseed &Mustard' : 32,
    'Rape' : 32,
    'Sarso' : 32,
    'Mustard' : 32,
    'Rapeseed' : 32,

    # Pulses (40 - 53)

    'other misc. pulses' : 41,

    'Gram' : 41,
    'Chana' : 41,

    'Horse-gram' : 42,
    'Kala chana' : 42,
    'Kulthi' : 42,
    'Kulthi Daal' : 42,

    'Other Kharif pulses' : 43,

    'Moong(Green Gram)' : 44,
    'Moong' : 44,
    'Moongbean' : 44,
    'Moong Bean' : 44,
    'Green Gram': 44,

    'Urad' : 45,
    'Black Gram' : 45,
    'Blackgram' : 45,

    'Arhar/Tur' : 46,
    'Arhar' : 46,
    'Tur' : 46,
    'Toor' : 46,
    'Pigeon Pea' : 46,
    'Pigeonpea' : 46,

    'Pulses total' : 47,

    'Masoor' : 48,
    'Lentil' : 48,

    'Rajmash Kholar' : 49,
    'Rajma' : 49,
    'Kidney Beans' : 49,
    'Kidneybeans' : 49,

    'Other  Rabi pulses' : 50,

    'Peas & beans (Pulses)' : 51,

    'Ricebean (nagadal)' : 52,

    'Moth' : 53,
    'Matbean' : 53,
    'Mat Bean' : 53,
    'Matki' : 53,
    'Dew Bean' : 53,

    # Dry Fruits (120 - 121)

    'Cashewnut' : 120,
    'Cashew' : 120,
    'Kaju' : 120,
    'Cashewnut Processed' : 120,
    'Cashewnut Raw' : 120,

    'Other Dry Fruit' : 121,

    # Cash Crops (130 - 137)

    'Cotton(lint)' : 130,
    'Kapas' : 130,

    'Sugarcane' : 131,
    'Ganna' : 131,
    'Ookh' : 131,
    'ookh' : 131,
    'Eekh':  131,
    'Ikh' : 131,

    'Tobacco' : 132,
    'Tambaku' : 132,
    'Tamakhu' : 132,
    'Tambakhu' : 132,

    'Jute & mesta' : 133,
    'Jute' : 133,
    'Mesta' : 133,

    'other fibres' : 134,


    'Rubber' : 135,
    'Caoutchouc' : 135,

    'Tea' : 136,
    'Chai' : 136,

    'Coffee' : 137,

    # Vegetables (60 - 86)

    'Other Vegetables' : 60,

    'Peas  (vegetable)' : 61,

    'Potato' : 62,
    'Aloo' : 62,
    'Alu' : 62,
    'Aaloo' : 62,
    'Aalu' : 62,

    'Beans & Mutter(Vegetable)' : 63,

    'Brinjal' : 64,
    'Baigan' : 64,

    'Cucumber' : 65,
    'Kheera' : 65,

    'Onion' : 66,
    'Pyaaj' : 66,
    'Pyaaz' : 66,
    'Pyaj' : 66,
    'Pyaz' : 66,

    'Sweet potato' : 67,
    'Kanna' : 67,
    'Shakarkand' : 67,

    'Tapioca' : 68,
    'Cassava' : 68,

    'Cowpea(Lobia)' : 69,
    'Cowpea' : 69,
    'Lobia'  : 69,
    'Boda' : 69,
    'Bodi' : 69,

    'Bhindi' : 70,
    'Ladyfinger' : 70,
    'Lady Finger' : 70,

    'Cabbage' : 71,
    'Pattagobhi' : 71,
    'Bandgobhi' : 71,

    'Redish' : 72,
    'Radish' : 72,
    'Mooli' : 72,

    'Bottle Gourd' : 73,
    'Lauki' : 73,
    'Loki' : 73,

    'Snak Guard' : 74,
    'Snakeguord' : 74,
    'Snake Guord' : 74,
    'Padaval' : 74,
    'Nenua' : 74,

    'Cauliflower' : 75,
    'Gobhi' : 75,
    'Phoolgobhi' : 75,
    'Fool Gobhi' : 75,

    'Colocosia' : 76,
    'Taro' : 76,
    'Aalukee' : 76,

    'Asgard' : 77,
    'Ash Gourd' : 77,
    'Ass Gaurd' : 77,
    'Petha' : 77,

    'Beet Root' : 78,
    'Beetroot' : 78,
    'Chukandar' : 78,
    'Chookandar' : 78,

    'Ribed Guard' : 79,

    'Yam' : 80,
    'Ratalu' : 80,

    'Turnip' : 81,
    'Shalajam' : 81,
    'Shalagam' : 81,
    'Shalgam' : 81,

    'Bitter Gourd' : 82,
    'Karela' : 82,

    'Bean' : 83,
    'Beans' : 83,
    'Phaliyan' : 83,
    'Phaliyaan' : 83,
    'Faliyan' : 83,
    'Sem' : 83,
    'saem' : 83,

    'Drum Stick' : 84,
    'Sahjan' : 84,
    'Saijan' : 84,

    'Pump Kin' : 85,
    'Pumpkin' : 85,
    'Kaddu' : 85,
    'Kadua' : 85,

    'Carrot' : 86,
    'Gajar' : 86,
    'Gazar' : 86,
    'Gaajar' : 86,

    # Fruits (90 - 113)

    'Arcanut (Processed)' : 90,
    'Arecanut (Processed)' : 90,
    'Atcanut (Raw)' : 90,
    'Atcanut (Raw)' : 90,
    'Arecanut' : 90,
    'Betelnut' : 90,
    'Betel Nut' : 90,
    'Supari' : 90,
    'Supadi' : 90,

    'Mango' : 91,
    'Aam' : 91,

    'Orange' : 92,
    'Santara' : 92,

    'Water Melon' : 93,
    'Watermelon' : 93,

    'Apple' : 94,
    'Seb' : 94,

    'Peach' : 95,
    'Adu' : 95,
    'Aadu' : 95,
    'Aaru' : 95,

    'Pear' : 96,
    'Rahila' : 96,

    'Plums' : 97,
    'Aalo Bukhara' : 97,
    'Alu Bukhara' : 97,

    'Other Citrus Fruit' : 98,

    'Litchi' : 99,

    'Papaya' : 100,
    'Papita' : 100,
    'Papeeta' : 100,

    'Ber' : 101,
    'Gooseberry' : 101,
    'Goose Berry' : 101,

    'Tomato' : 102,
    'Tamatar' : 103,

    'Other Fresh Fruits' : 104,

    'Pome Fruit' : 105,

    'Pineapple' : 106,

    'Banana' : 107,
    'Kela' : 107,

    'Coconut ' : 108,
    'Nariyal' : 108,
    'Nariyal' : 108,


    'Lemon' : 109,
    'Nimbu' : 109,
    'Neebu' : 109,

    'Pome Granet' : 110,
    'Pomegranate' : 110,

    'Sapota' : 111,
    'Sapodilla' : 111,
    'Cheekoo' : 111,
    'Chiku' : 111,
    'Chico' : 111,
    'Naseberry' : 111,

    'Grapes' : 112,
    'Angoor' : 112,

    'Jack Fruit' : 113,
    'Kathal' : 113,
    'Kathar' : 113,
    'Katahal' : 113,
    'Katahar' : 113,
}

DistDict = {'NICOBARS': 0, 'NORTH AND MIDDLE ANDAMAN': 1, 'SOUTH ANDAMANS': 2, 'ANANTAPUR': 3, 'CHITTOOR': 4, 'EAST GODAVARI': 5, 'GUNTUR': 6, 'KADAPA': 7, 'KRISHNA': 8, 'KURNOOL': 9, 'PRAKASAM': 10, 'SPSR NELLORE': 11, 'SRIKAKULAM': 12, 'VISAKHAPATANAM': 13, 'VIZIANAGARAM': 14, 'WEST GODAVARI': 15, 'ANJAW': 16, 'CHANGLANG': 17, 'DIBANG VALLEY': 18, 'EAST KAMENG': 19, 'EAST SIANG': 20, 'KURUNG KUMEY': 21, 'LOHIT': 22, 'LONGDING': 23, 'LOWER DIBANG VALLEY': 24, 'LOWER SUBANSIRI': 25, 'NAMSAI': 26, 'PAPUM PARE': 27, 'TAWANG': 28, 'TIRAP': 29, 'UPPER SIANG': 30, 'UPPER SUBANSIRI': 31, 'WEST KAMENG': 32, 'WEST SIANG': 33, 'BAKSA': 34, 'BARPETA': 35, 'BONGAIGAON': 36, 'CACHAR': 37, 'CHIRANG': 38, 'DARRANG': 39, 'DHEMAJI': 40, 'DHUBRI': 41, 'DIBRUGARH': 42, 'DIMA HASAO': 43, 'GOALPARA': 44, 'GOLAGHAT': 45, 'HAILAKANDI': 46, 'JORHAT': 47, 'KAMRUP': 48, 'KAMRUP METRO': 49, 'KARBI ANGLONG': 50, 'KARIMGANJ': 51, 'KOKRAJHAR': 52, 'LAKHIMPUR': 53, 'MARIGAON': 54, 'NAGAON': 55, 'NALBARI': 56, 'SIVASAGAR': 57, 'SONITPUR': 58, 'TINSUKIA': 59, 'UDALGURI': 60, 'ARARIA': 61, 'ARWAL': 62, 'AURANGABAD': 63, 'BANKA': 64, 'BEGUSARAI': 65, 'BHAGALPUR': 66, 'BHOJPUR': 67, 'BUXAR': 68, 'DARBHANGA': 69, 'GAYA': 70, 'GOPALGANJ': 71, 'JAMUI': 72, 'JEHANABAD': 73, 'KAIMUR (BHABUA)': 74, 'KATIHAR': 75, 'KHAGARIA': 76, 'KISHANGANJ': 77, 'LAKHISARAI': 78, 'MADHEPURA': 79, 'MADHUBANI': 80, 'MUNGER': 81, 'MUZAFFARPUR': 82, 'NALANDA': 83, 'NAWADA': 84, 'PASHCHIM CHAMPARAN': 85, 'PATNA': 86, 'PURBI CHAMPARAN': 87, 'PURNIA': 88, 'ROHTAS': 89, 'SAHARSA': 90, 'SAMASTIPUR': 91, 'SARAN': 92, 'SHEIKHPURA': 93, 'SHEOHAR': 94, 'SITAMARHI': 95, 'SIWAN': 96, 'SUPAUL': 97, 'VAISHALI': 98, 'CHANDIGARH': 99, 'BALOD': 100, 'BALODA BAZAR': 101, 'BALRAMPUR': 102, 'BASTAR': 103, 'BEMETARA': 104, 'BIJAPUR': 105, 'BILASPUR': 106, 'DANTEWADA': 107, 'DHAMTARI': 108, 'DURG': 109, 'GARIYABAND': 110, 'JANJGIR-CHAMPA': 111, 'JASHPUR': 112, 'KABIRDHAM': 113, 'KANKER': 114, 'KONDAGAON': 115, 'KORBA': 116, 'KOREA': 117, 'MAHASAMUND': 118, 'MUNGELI': 119, 'NARAYANPUR': 120, 'RAIGARH': 121, 'RAIPUR': 122, 'RAJNANDGAON': 123, 'SUKMA': 124, 'SURAJPUR': 125, 'SURGUJA': 126, 'DADRA AND NAGAR HAVELI': 127, 'NORTH GOA': 128, 'SOUTH GOA': 129, 'AHMADABAD': 130, 'AMRELI': 131, 'ANAND': 132, 'BANAS KANTHA': 133, 'BHARUCH': 134, 'BHAVNAGAR': 135, 'DANG': 136, 'DOHAD': 137, 'GANDHINAGAR': 138, 'JAMNAGAR': 139, 'JUNAGADH': 140, 'KACHCHH': 141, 'KHEDA': 142, 'MAHESANA': 143, 'NARMADA': 144, 'NAVSARI': 145, 'PANCH MAHALS': 146, 'PATAN': 147, 'PORBANDAR': 148, 'RAJKOT': 149, 'SABAR KANTHA': 150, 'SURAT': 151, 'SURENDRANAGAR': 152, 'TAPI': 153, 'VADODARA': 154, 'VALSAD': 155, 'AMBALA': 156, 'BHIWANI': 157, 'FARIDABAD': 158, 'FATEHABAD': 159, 'GURGAON': 160, 'HISAR': 161, 'JHAJJAR': 162, 'JIND': 163, 'KAITHAL': 164, 'KARNAL': 165, 'KURUKSHETRA': 166, 'MAHENDRAGARH': 167, 'MEWAT': 168, 'PALWAL': 169, 'PANCHKULA': 170, 'PANIPAT': 171, 'REWARI': 172, 'ROHTAK': 173, 'SIRSA': 174, 'SONIPAT': 175, 'YAMUNANAGAR': 176, 'CHAMBA': 177, 'HAMIRPUR': 178, 'KANGRA': 179, 'KINNAUR': 180, 'KULLU': 181, 'LAHUL AND SPITI': 182, 'MANDI': 183, 'SHIMLA': 184, 'SIRMAUR': 185, 'SOLAN': 186, 'UNA': 187, 'ANANTNAG': 188, 'BADGAM': 189, 'BANDIPORA': 190, 'BARAMULLA': 191, 'DODA': 192, 'GANDERBAL': 193, 'JAMMU': 194, 'KARGIL': 195, 'KATHUA': 196, 'KISHTWAR': 197, 'KULGAM': 198, 'KUPWARA': 199, 'LEH LADAKH': 200, 'POONCH': 201, 'PULWAMA': 202, 'RAJAURI': 203, 'RAMBAN': 204, 'REASI': 205, 'SAMBA': 206, 'SHOPIAN': 207, 'SRINAGAR': 208, 'UDHAMPUR': 209, 'BOKARO': 210, 'CHATRA': 211, 'DEOGHAR': 212, 'DHANBAD': 213, 'DUMKA': 214, 'EAST SINGHBUM': 215, 'GARHWA': 216, 'GIRIDIH': 217, 'GODDA': 218, 'GUMLA': 219, 'HAZARIBAGH': 220, 'JAMTARA': 221, 'KHUNTI': 222, 'KODERMA': 223, 'LATEHAR': 224, 'LOHARDAGA': 225, 'PAKUR': 226, 'PALAMU': 227, 'RAMGARH': 228, 'RANCHI': 229, 'SAHEBGANJ': 230, 'SARAIKELA KHARSAWAN': 231, 'SIMDEGA': 232, 'WEST SINGHBHUM': 233, 'BAGALKOT': 234, 'BANGALORE RURAL': 235, 'BELGAUM': 236, 'BELLARY': 237, 'BENGALURU URBAN': 238, 'BIDAR': 239, 'CHAMARAJANAGAR': 240, 'CHIKBALLAPUR': 241, 'CHIKMAGALUR': 242, 'CHITRADURGA': 243, 'DAKSHIN KANNAD': 244, 'DAVANGERE': 245, 'DHARWAD': 246, 'GADAG': 247, 'GULBARGA': 248, 'HASSAN': 249, 'HAVERI': 250, 'KODAGU': 251, 'KOLAR': 252, 'KOPPAL': 253, 'MANDYA': 254, 'MYSORE': 255, 'RAICHUR': 256, 'RAMANAGARA': 257, 'SHIMOGA': 258, 'TUMKUR': 259, 'UDUPI': 260, 'UTTAR KANNAD': 261, 'YADGIR': 262, 'ALAPPUZHA': 263, 'ERNAKULAM': 264, 'IDUKKI': 265, 'KANNUR': 266, 'KASARAGOD': 267, 'KOLLAM': 268, 'KOTTAYAM': 269, 'KOZHIKODE': 270, 'MALAPPURAM': 271, 'PALAKKAD': 272, 'PATHANAMTHITTA': 273, 'THIRUVANANTHAPURAM': 274, 'THRISSUR': 275, 'WAYANAD': 276, 'AGAR MALWA': 277, 'ALIRAJPUR': 278, 'ANUPPUR': 279, 'ASHOKNAGAR': 280, 'BALAGHAT': 281, 'BARWANI': 282, 'BETUL': 283, 'BHIND': 284, 'BHOPAL': 285, 'BURHANPUR': 286, 'CHHATARPUR': 287, 'CHHINDWARA': 288, 'DAMOH': 289, 'DATIA': 290, 'DEWAS': 291, 'DHAR': 292, 'DINDORI': 293, 'GUNA': 294, 'GWALIOR': 295, 'HARDA': 296, 'HOSHANGABAD': 297, 'INDORE': 298, 'JABALPUR': 299, 'JHABUA': 300, 'KATNI': 301, 'KHANDWA': 302, 'KHARGONE': 303, 'MANDLA': 304, 'MANDSAUR': 305, 'MORENA': 306, 'NARSINGHPUR': 307, 'NEEMUCH': 308, 'PANNA': 309, 'RAISEN': 310, 'RAJGARH': 311, 'RATLAM': 312, 'REWA': 313, 'SAGAR': 314, 'SATNA': 315, 'SEHORE': 316, 'SEONI': 317, 'SHAHDOL': 318, 'SHAJAPUR': 319, 'SHEOPUR': 320, 'SHIVPURI': 321, 'SIDHI': 322, 'SINGRAULI': 323, 'TIKAMGARH': 324, 'UJJAIN': 325, 'UMARIA': 326, 'VIDISHA': 327, 'AHMEDNAGAR': 328, 'AKOLA': 329, 'AMRAVATI': 330, 'BEED': 331, 'BHANDARA': 332, 'BULDHANA': 333, 'CHANDRAPUR': 334, 'DHULE': 335, 'GADCHIROLI': 336, 'GONDIA': 337, 'HINGOLI': 338, 'JALGAON': 339, 'JALNA': 340, 'KOLHAPUR': 341, 'LATUR': 342, 'NAGPUR': 343, 'NANDED': 344, 'NANDURBAR': 345, 'NASHIK': 346, 'OSMANABAD': 347, 'PALGHAR': 348, 'PARBHANI': 349, 'PUNE': 350, 'RAIGAD': 351, 'RATNAGIRI': 352, 'SANGLI': 353, 'SATARA': 354, 'SINDHUDURG': 355, 'SOLAPUR': 356, 'THANE': 357, 'WARDHA': 358, 'WASHIM': 359, 'YAVATMAL': 360, 'BISHNUPUR': 361, 'CHANDEL': 362, 'CHURACHANDPUR': 363, 'IMPHAL EAST': 364, 'IMPHAL WEST': 365, 'SENAPATI': 366, 'TAMENGLONG': 367, 'THOUBAL': 368, 'UKHRUL': 369, 'EAST GARO HILLS': 370, 'EAST JAINTIA HILLS': 371, 'EAST KHASI HILLS': 372, 'NORTH GARO HILLS': 373, 'RI BHOI': 374, 'SOUTH GARO HILLS': 375, 'SOUTH WEST GARO HILLS': 376, 'SOUTH WEST KHASI HILLS': 377, 'WEST GARO HILLS': 378, 'WEST JAINTIA HILLS': 379, 'WEST KHASI HILLS': 380, 'AIZAWL': 381, 'CHAMPHAI': 382, 'KOLASIB': 383, 'LAWNGTLAI': 384, 'LUNGLEI': 385, 'MAMIT': 386, 'SAIHA': 387, 'SERCHHIP': 388, 'DIMAPUR': 389, 'KIPHIRE': 390, 'KOHIMA': 391, 'LONGLENG': 392, 'MOKOKCHUNG': 393, 'MON': 394, 'PEREN': 395, 'PHEK': 396, 'TUENSANG': 397, 'WOKHA': 398, 'ZUNHEBOTO': 399, 'ANUGUL': 400, 'BALANGIR': 401, 'BALESHWAR': 402, 'BARGARH': 403, 'BHADRAK': 404, 'BOUDH': 405, 'CUTTACK': 406, 'DEOGARH': 407, 'DHENKANAL': 408, 'GAJAPATI': 409, 'GANJAM': 410, 'JAGATSINGHAPUR': 411, 'JAJAPUR': 412, 'JHARSUGUDA': 413, 'KALAHANDI': 414, 'KANDHAMAL': 415, 'KENDRAPARA': 416, 'KENDUJHAR': 417, 'KHORDHA': 418, 'KORAPUT': 419, 'MALKANGIRI': 420, 'MAYURBHANJ': 421, 'NABARANGPUR': 422, 'NAYAGARH': 423, 'NUAPADA': 424, 'PURI': 425, 'RAYAGADA': 426, 'SAMBALPUR': 427, 'SONEPUR': 428, 'SUNDARGARH': 429, 'KARAIKAL': 430, 'MAHE': 431, 'PONDICHERRY': 432, 'YANAM': 433, 'AMRITSAR': 434, 'BARNALA': 435, 'BATHINDA': 436, 'FARIDKOT': 437, 'FATEHGARH SAHIB': 438, 'FAZILKA': 439, 'FIROZEPUR': 440, 'GURDASPUR': 441, 'HOSHIARPUR': 442, 'JALANDHAR': 443, 'KAPURTHALA': 444, 'LUDHIANA': 445, 'MANSA': 446, 'MOGA': 447, 'MUKTSAR': 448, 'NAWANSHAHR': 449, 'PATHANKOT': 450, 'PATIALA': 451, 'RUPNAGAR': 452, 'S.A.S NAGAR': 453, 'SANGRUR': 454, 'TARN TARAN': 455, 'AJMER': 456, 'ALWAR': 457, 'BANSWARA': 458, 'BARAN': 459, 'BARMER': 460, 'BHARATPUR': 461, 'BHILWARA': 462, 'BIKANER': 463, 'BUNDI': 464, 'CHITTORGARH': 465, 'CHURU': 466, 'DAUSA': 467, 'DHOLPUR': 468, 'DUNGARPUR': 469, 'GANGANAGAR': 470, 'HANUMANGARH': 471, 'JAIPUR': 472, 'JAISALMER': 473, 'JALORE': 474, 'JHALAWAR': 475, 'JHUNJHUNU': 476, 'JODHPUR': 477, 'KARAULI': 478, 'KOTA': 479, 'NAGAUR': 480, 'PALI': 481, 'PRATAPGARH': 482, 'RAJSAMAND': 483, 'SAWAI MADHOPUR': 484, 'SIKAR': 485, 'SIROHI': 486, 'TONK': 487, 'UDAIPUR': 488, 'EAST DISTRICT': 489, 'NORTH DISTRICT': 490, 'SOUTH DISTRICT': 491, 'WEST DISTRICT': 492, 'ARIYALUR': 493, 'COIMBATORE': 494, 'CUDDALORE': 495, 'DHARMAPURI': 496, 'DINDIGUL': 497, 'ERODE': 498, 'KANCHIPURAM': 499, 'KANNIYAKUMARI': 500, 'KARUR': 501, 'KRISHNAGIRI': 502, 'MADURAI': 503, 'NAGAPATTINAM': 504, 'NAMAKKAL': 505, 'PERAMBALUR': 506, 'PUDUKKOTTAI': 507, 'RAMANATHAPURAM': 508, 'SALEM': 509, 'SIVAGANGA': 510, 'THANJAVUR': 511, 'THE NILGIRIS': 512, 'THENI': 513, 'THIRUVALLUR': 514, 'THIRUVARUR': 515, 'TIRUCHIRAPPALLI': 516, 'TIRUNELVELI': 517, 'TIRUPPUR': 518, 'TIRUVANNAMALAI': 519, 'TUTICORIN': 520, 'VELLORE': 521, 'VILLUPURAM': 522, 'VIRUDHUNAGAR': 523, 'ADILABAD': 524, 'HYDERABAD': 525, 'KARIMNAGAR': 526, 'KHAMMAM': 527, 'MAHBUBNAGAR': 528, 'MEDAK': 529, 'NALGONDA': 530, 'NIZAMABAD': 531, 'RANGAREDDI': 532, 'WARANGAL': 533, 'DHALAI': 534, 'GOMATI': 535, 'KHOWAI': 536, 'NORTH TRIPURA': 537, 'SEPAHIJALA': 538, 'SOUTH TRIPURA': 539, 'UNAKOTI': 540, 'WEST TRIPURA': 541, 'AGRA': 542, 'ALIGARH': 543, 'ALLAHABAD': 544, 'AMBEDKAR NAGAR': 545, 'AMETHI': 546, 'AMROHA': 547, 'AURAIYA': 548, 'AZAMGARH': 549, 'BAGHPAT': 550, 'BAHRAICH': 551, 'BALLIA': 552, 'BANDA': 553, 'BARABANKI': 554, 'BAREILLY': 555, 'BASTI': 556, 'BIJNOR': 557, 'BUDAUN': 558, 'BULANDSHAHR': 559, 'CHANDAULI': 560, 'CHITRAKOOT': 561, 'DEORIA': 562, 'ETAH': 563, 'ETAWAH': 564, 'FAIZABAD': 565, 'FARRUKHABAD': 566, 'FATEHPUR': 567, 'FIROZABAD': 568, 'GAUTAM BUDDHA NAGAR': 569, 'GHAZIABAD': 570, 'GHAZIPUR': 571, 'GONDA': 572, 'GORAKHPUR': 573, 'HAPUR': 574, 'HARDOI': 575, 'HATHRAS': 576, 'JALAUN': 577, 'JAUNPUR': 578, 'JHANSI': 579, 'KANNAUJ': 580, 'KANPUR DEHAT': 581, 'KANPUR NAGAR': 582, 'KASGANJ': 583, 'KAUSHAMBI': 584, 'KHERI': 585, 'KUSHI NAGAR': 586, 'LALITPUR': 587, 'LUCKNOW': 588, 'MAHARAJGANJ': 589, 'MAHOBA': 590, 'MAINPURI': 591, 'MATHURA': 592, 'MAU': 593, 'MEERUT': 594, 'MIRZAPUR': 595, 'MORADABAD': 596, 'MUZAFFARNAGAR': 597, 'PILIBHIT': 598, 'RAE BARELI': 599, 'RAMPUR': 600, 'SAHARANPUR': 601, 'SAMBHAL': 602, 'SANT KABEER NAGAR': 603, 'SANT RAVIDAS NAGAR': 604, 'SHAHJAHANPUR': 605, 'SHAMLI': 606, 'SHRAVASTI': 607, 'SIDDHARTH NAGAR': 608, 'SITAPUR': 609, 'SONBHADRA': 610, 'SULTANPUR': 611, 'UNNAO': 612, 'VARANASI': 613, 'ALMORA': 614, 'BAGESHWAR': 615, 'CHAMOLI': 616, 'CHAMPAWAT': 617, 'DEHRADUN': 618, 'HARIDWAR': 619, 'NAINITAL': 620, 'PAURI GARHWAL': 621, 'PITHORAGARH': 622, 'RUDRA PRAYAG': 623, 'TEHRI GARHWAL': 624, 'UDAM SINGH NAGAR': 625, 'UTTAR KASHI': 626, '24 PARAGANAS NORTH': 627, '24 PARAGANAS SOUTH': 628, 'BANKURA': 629, 'BARDHAMAN': 630, 'BIRBHUM': 631, 'COOCHBEHAR': 632, 'DARJEELING': 633, 'DINAJPUR DAKSHIN': 634, 'DINAJPUR UTTAR': 635, 'HOOGHLY': 636, 'HOWRAH': 637, 'JALPAIGURI': 638, 'MALDAH': 639, 'MEDINIPUR EAST': 640, 'MEDINIPUR WEST': 641, 'MURSHIDABAD': 642, 'NADIA': 643, 'PURULIA': 644}
