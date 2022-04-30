from Big_Mamma.get_data import get_sports_event_europe
from Big_Mamma.get_data import get_data_sales
import pandas as pd

def test_type_sports_event():
    print('Testing sport API function')
    assert type(get_sports_event_europe(date_from='2022-01-01',date_to='2022-01-02'))==type(pd.DataFrame())

def test_type_google_api():
    print('Testing google sheet API')
    assert type(get_data_sales('Vente'))==list

if __name__ == '__main__':
    test_type_sports_event()
    test_type_google_api()
