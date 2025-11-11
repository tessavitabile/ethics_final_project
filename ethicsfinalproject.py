import  pandas as pd
from    sodapy import Socrata

def get_data_frame(id):
    client     = Socrata("data.cityofnewyork.us", None)
    data    = client.get(id)
    return pd.DataFrame.from_records(data)

def get_affordable_housing(affordable_housing_df):
    zip = input("Enter a NYC zipcode: ")
    print("Addresses of affordable housing in this zip code")
    return affordable_housing_df.loc[affordable_housing_df['postcode'] == zip, ['house_number', 'street_name', 'borough', 'postcode']]

def get_parks(parks_df):
    zip = input("Enter a NYC zipcode: ")
    print("\nAddresses of parks in this zip code")
    return parks_df.loc[parks_df['zipcode'] == zip, ['signname', 'address', 'borough', 'zipcode']]