# Big Mamma Package
This package is used to fetch data from 2 API:
- Google Sheet : [a google sheet](https://docs.google.com/spreadsheets/d/1dYY5HU0h81NchR1xviaZF5HvCoS-rIY5ilgpVhFrE7U/edit#gid=0) contain all the sales of 2021 and i use Google API to fetch it
- allsportdb : it is an API that give you sports events during a period and a region

The package contain 2 modules:
- get_data : set communication and request data from the 2 API
- data_base : in charge of updating a SQL database with the sales. This DB is stored in the data folder

**update_db** is the main function from the **data_base** module. It refresh the SQL database with sales.
**get_sports_event_europe** in the **get_data** module is the function to query the sport API

It requires a few setup:
- pip install all the packages in 'requirements.txt' -> pip install -r requirements.txt
- A Google Cloud Platform project with the API enabled. To create a project and enable an API, refer to Create a project and enable the [API](https://developers.google.com/workspace/guides/create-project)
- Authorization credentials for a desktop application. To learn how to create credentials for a desktop application, refer to [Create credentials](https://developers.google.com/workspace/guides/create-credentials).
- Download the json credentials file from google and put it in the folder './Big_Mamma/json'
- On the first 'Refresh Google sheet data', you will be prompt to grant access the app to your google sheets (in read-mode only)
- Create an account on [AllSportDB](https://allsportdb.com)
- Activate an API key (only works with Standard plan)
- Create a file 'all_sport_db.json' in ./Big_Mamma/json
- Write your API key on the format : {"key":"< your key >"}
