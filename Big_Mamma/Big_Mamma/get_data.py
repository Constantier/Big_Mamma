import pandas as pd
import requests
import os
import json

from googleapiclient import discovery
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def transfo_date_events(date,start=True):
    '''
    Retrun the start or end date of an event
    Take date as serie and start as bool
    If start = True -> Return the start date
    If start = False -> Return End date
    '''
    if '-' in date:
        date=date.split('-') #checking if there is one or two date
        for index,day in enumerate(date):
            if day.replace(' ','').isnumeric(): #if there is only a numeric value on the start date -> it is the same month
                date[index]=day + ' '.join(date[1].split(' ')[2:]) #concat the month and year from the end date
            elif len(day.split(' '))==3: #if the first date have a different month but no year (so 3 elements because there is a space first) it is the same year
                date[index]=day + ' '.join(date[1].split(' ')[3:])
    else :
        date=[date,date]
    if start:
        return date[0]
    return date[1]

def get_sports_event_europe(date_from,date_to):
    '''
    Return a dataframe with all sports events between date_from and date_to.

    The dates must be in the format : 'yyyy-mm-dd'

    Return the HTTP error code if there is an error
    '''

    url='https://api.allsportdb.com/v3/calendar'

    params={
        'dateFrom':date_from,
        'dateTo':date_to,
        'continentId':3
    }

    headers = {'Authorization': 'Bearer f704e05e-e81e-4e1f-bd78-b63b9837f7ef'}

    reponse=requests.get(url=url,headers=headers,params=params)

    if reponse.status_code!=200:
        return {'error':reponse.status_code}

    events_list=reponse.json()
    eur_events=[]
    for event in events_list:
        cities=[]
        for location in event['location']:
            for city in location['locations']:
                emoji=location.get('emoji','')
                cities.append(emoji+city['name'])

        emoji=event.get('emoji','')
        eur_events.append({
            'name':emoji+event['name'],
            'date':event['date'],
            'locations':cities
        })
    eur_events=pd.DataFrame(eur_events)
    eur_events['Start date']=eur_events.apply(lambda x:transfo_date_events(x['date'],start=True),axis=1)
    eur_events['End date']=eur_events.apply(lambda x:transfo_date_events(x['date'],start=False),axis=1)
    eur_events=eur_events.drop(columns=['date'])

    return eur_events

def get_data_sales(sheet, spreadsheet_id='1dYY5HU0h81NchR1xviaZF5HvCoS-rIY5ilgpVhFrE7U'):
    '''
    Return all the lines from column A to F in the sheet of the file 'ventes API'
    '''
    try : #Import GCP credentials from local computer or GitHub Secret
        credentials = Credentials.from_authorized_user_file('/Users/constantintalandier/Desktop/Le_Wagon/gcp/token.json', SCOPES)
    except:
        credentials=Credentials.from_authorized_user_info(json.loads(google_creds),SCOPES)

    service = discovery.build('sheets', 'v4', credentials=credentials)

    # The A1 notation of the values to retrieve.
    ranges = [f"'{sheet}'!A1:F"]

    # How values should be represented in the output.
    value_render_option = 'FORMATTED_VALUE'

    # How dates, times, and durations should be represented in the output.
    date_time_render_option = 'FORMATTED_STRING'

    request = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id,
                                                       ranges=ranges,
                                                       valueRenderOption=value_render_option,
                                                       dateTimeRenderOption=date_time_render_option)
    try :
        response = request.execute()
    except HttpError as error:
        return f'Error : {error}'

    return response['valueRanges'][0]['values']

if __name__=='__main__':
    print(get_sports_event_europe('2022-01-01','2022-01-30'))
    print(get_data_sales('Ventes'))
