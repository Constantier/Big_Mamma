from Big_Mamma.get_data import get_sports_event_europe

def test_length_of_hello_world():
    assert type(get_sports_event_europe(date_from='2022-01-01',date_to='2022-01-02'))==list

if __name__ == '__main__':
    test_length_of_hello_world()
