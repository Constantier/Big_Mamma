import os
import json
import requests
import pandas as pd

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
PATH=os.path.dirname(__file__)

def transfo_date_events(date, start=True):
    """
    Retrun the start or end date of a sport event
    Take date as serie and start as bool
    If start = True -> Return the start date
    If start = False -> Return End date
    """
    if "-" in date:
        # checking if there is one or two date
        date = date.split("-")
        for index, day in enumerate(date):

            # if there is only a numeric value on the start date -> it is the same month
            if day.replace(" ", "").isnumeric():
                # concat the month and year from the end date
                date[index] = day + " ".join(date[1].split(" ")[2:])

            # if the first date have a different month but no year (so 3 elements because there is a space first) it is the same year
            elif (len(day.split(" ")) == 3):
                date[index] = day + " ".join(date[1].split(" ")[3:])
    else:
        date = [date, date]
    if start:
        return date[0]
    return date[1]


def get_sports_event_europe(date_from, date_to):
    """
    Return a dataframe with all sports events between date_from and date_to.

    The dates must be in the format : 'yyyy-mm-dd'

    Return the HTTP error code if there is an error
    """
    #getting API key for all_sport_db
    json_path=os.path.join(os.path.join(PATH,'json'),'all_sport_db.json')
    if not os.path.exists(json_path):
        return pd.DataFrame({"error": "No file 'all_sport_db.json' found, please create it. Refer to the main README.md"},index=[0])

    with open(json_path) as file:
        api_key=json.load(file)['key']

    #Params for API requests
    url = "https://api.allsportdb.com/v3/calendar"
    params = {"dateFrom": date_from, "dateTo": date_to, "continentId": 3}
    headers = {"Authorization": f"Bearer {api_key}"}

    #API request
    reponse = requests.get(url=url, headers=headers, params=params)

    if reponse.status_code != 200:
        return pd.DataFrame({"error": reponse.status_code},index=[0])

    # if the request went well, take the json
    events_list = reponse.json()
    eur_events = []

    for event in events_list:
        cities = []
        #searching all cities for each event
        for location in event["location"]:
            for city in location["locations"]:
                emoji = location.get("emoji", "")
                cities.append(emoji + city["name"])

        emoji = event.get("emoji", "")
        eur_events.append(
            {"name": emoji + event["name"], "date": event["date"], "locations": cities}
        )
    # if there are events during the periode, we transform the dates into 2 columns
    eur_events = pd.DataFrame(eur_events)
    if not eur_events.empty:
        #adding column of start date and end date
        eur_events["Start date"] = eur_events.apply(
            lambda x: transfo_date_events(x["date"], start=True), axis=1
        )
        eur_events["End date"] = eur_events.apply(
            lambda x: transfo_date_events(x["date"], start=False), axis=1
        )
        #remove the column with the 2 dates
        eur_events = eur_events.drop(columns=["date"])

    return eur_events

def get_creds():
    '''
    return the token needed to use google sheet API. Use 'token.json' if it exist.
    Otherwise use the 'credentials.json' stored in the dir 'gcp' to create 'token.json'.
    '''
    #setting all the paths to the 2 google auth files
    gcp_path=os.path.join(PATH,'json')
    token_path=os.path.join(gcp_path,'token.json')
    credentals_path=os.path.join(gcp_path,'credentials.json')

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentals_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_data_sales(
    sheet, spreadsheet_id="1dYY5HU0h81NchR1xviaZF5HvCoS-rIY5ilgpVhFrE7U"
):
    """
    Return all the lines from column A to F in the sheet 'sheet' of the spreadsheet id 'spreadsheet_id'
    """
    credentials=get_creds()

    service = discovery.build("sheets", "v4", credentials=credentials)

    # fetching all values of the sheet
    ranges = [f"'{sheet}'!A1:F"]

    # How values should be represented in the output.
    value_render_option = "FORMATTED_VALUE"

    # How dates, times, and durations should be represented in the output.
    date_time_render_option = "FORMATTED_STRING"

    request = (
        service.spreadsheets()
        .values()
        .batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=ranges,
            valueRenderOption=value_render_option,
            dateTimeRenderOption=date_time_render_option,
        )
    )
    try:
        response = request.execute()
    except HttpError as error:
        return [f"Error : {error}"]

    return response["valueRanges"][0]["values"]


if __name__ == "__main__":
    print(get_sports_event_europe("2022-01-01", "2022-01-30"))
    print(get_data_sales("Ventes"))
