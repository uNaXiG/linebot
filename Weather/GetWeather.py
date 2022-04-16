import datetime
import pandas as pd
import numpy as np
import requests
import csv
import os

token = 'CWB-BCB96261-D0F1-4364-9AE9-60E18831DDAA'
def Get_Raw_Data(dataID):    
    URL = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/' + dataID + '?Authorization=' + token + '&format=json'
    r = requests.get(URL)
    data = r.json()
    return data

def Parse_Json_location(data):
    col = ['locationName']
    df = pd.DataFrame(columns=col)
    data_dict = {}
    locations = data['records']['location']
    row = -1
    for location in locations:
        row += 1
        data_dict['locationName'] = location['locationName']
                
        parameters = location['parameter']
        for par in parameters:
            factor_Name = par['parameterName']
            data_dict[factor_Name] = par['parameterValue']
            
        for key in data_dict.keys():
            df.loc[row, key] = data_dict[key]
        
    return df

def Parse_Json_weather(data):
    col = ['城市名稱']
    df = pd.DataFrame(columns=col)
    data_dict = {}
    locations = data['records']['locations']
    row = -1
    j = 0
    for loc in locations:        
        #data_dict['locationsName'] = loc['locationsName']
        
        loca = loc['location']        
        for l in loca:
            row += 1
            data_dict['城市名稱'] = l['locationName']
            lis = l['weatherElement']
            for i in range(len(lis)):                
                lisTime = lis[i]['time']
                for j in range(len(lisTime)):
                    frameName = lis[i]['description']                    
                    lisEle = lisTime[1]['elementValue']
                    data_dict['開始時間'] = lisTime[0]['startTime']
                    data_dict['結束時間'] = lisTime[0]['endTime']
                    data_dict[frameName] = lisEle[0]['value']                        
            for key in data_dict.keys():
                df.loc[row, key] = data_dict[key]
        
        
            
    return df

if __name__ == "__main__":   
    
    path ="D:/LineBot/Weather/" + datetime.datetime.now().strftime('%Y_%m_%d') + "_data"
    if not os.path.exists(path):
        os.makedirs(path)
    
    #data_location = Get_Raw_Data('O-A0001-001')
    #df = Parse_Json_location(data_location)
    #save_file_name = path + '/{}_data.csv'.format(datetime.datetime.now().strftime('location_report'))
    #df.to_csv(save_file_name, encoding = '', index = False)
    
    data_weather = Get_Raw_Data('F-D0047-091')
    df = Parse_Json_weather(data_weather)
    save_file_name = path + '/{}_data.csv'.format(datetime.datetime.now().strftime('weather_report'))
    df.to_csv(save_file_name, encoding = '', index = False)