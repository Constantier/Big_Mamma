# Big Mamma data viz :pizza:

Welcome to the data Visualization exemple for Big Mamma sales in 2021.
It is a little front web page to see and filter sales of restaurants.
You can filter sales by dates, category or product and see european sports events that occured during the sales.

## Website :
You can visualize the web page on the adress : https://bigmammacta.herokuapp.com
If you want to see the code and run it locally, you can the **installation** section.

## How it work? :
The web page was made with **streamlit** and run a local package which is in charge of getting the from 2 sources:
- Google Sheet : [a google sheet](https://docs.google.com/spreadsheets/d/1dYY5HU0h81NchR1xviaZF5HvCoS-rIY5ilgpVhFrE7U/edit#gid=0) contain all the sales of 2021 and i use Google API to fetch it
- allsportdb : it is an API that give you sports events during a period and a region

The package contain 2 modules:
- get_data : set communication and request data from the 2 API
- data_base : in charge of building a SQL database stored in the data folder

When the webpage need to refresh data, it call the **generate_db** function from the **data_base** module. This is the main function that refresh the SQL database.

The database is then queried by the web app based on the filters selected by the user.
The graph is updated on every change to the filters.
To avoid latency from the **sports API**, the latter is queried **only when you hit the button 'Search Sports Events'**.

## Installation :
If you want to run it on your computer, you need to :
- Download the repo
- pip install all the packages in 'requirements.txt' -> pip install -r requirements.txt
- A Google Cloud Platform project with the API enabled. To create a project and enable an API, refer to Create a project and enable the [API](https://developers.google.com/workspace/guides/create-project)
- Authorization credentials for a desktop application. To learn how to create credentials for a desktop application, refer to [Create credentials](https://developers.google.com/workspace/guides/create-credentials).
- Download the json credentials file from google and put it in the folder './Big_Mamma/Big_Mamma/json'
- On the first 'Refresh Google sheet data', you will be prompt to grant access the app to your google sheets (in read-mode only, **use Chrome for beter compatibility**)
- Create an account on [AllSportDB](https://allsportdb.com)
- Activate an API key (only works with Standard plan)
- Create a file 'all_sport_db.json' in ./xBig_Mamma/Big_Mamma/json
- Write your API key on the format : {"key":"< your key >"}

You can then run the command : 'make streamit' to run the web app on your computer

Feel free to let me know if you encounter problem or find bugs :)

Bye!
