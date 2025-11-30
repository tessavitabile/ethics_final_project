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

def get_air_quality_by_borough(air_quality_df, geo_lookup_df):
    air_quality_merged_df = pd.merge(air_quality_df, geo_lookup_df,
                                        left_on='geo_place_name', right_on='Name',
                                        how='inner')
    air_quality_merged_df['data_value_float'] = air_quality_merged_df['data_value'].astype(float)
    return air_quality_merged_df.groupby(['Borough', 'name', 'measure_info'])['data_value_float'].mean()

def get_air_quality_by_neighborhood(air_quality_df, geo_lookup_df):
    borough = input("Enter a NYC borough: ")
    pd.set_option('display.max_rows', None)
    air_quality_merged_df = pd.merge(air_quality_df, geo_lookup_df,
                                        left_on='geo_place_name', right_on='Name',
                                        how='inner')
    air_quality_merged_df['data_value_float'] = air_quality_merged_df['data_value'].astype(float)
    return air_quality_merged_df.loc[air_quality_merged_df['Borough']==borough].groupby(['geo_place_name', 'name', 'measure_info'])['data_value_float'].mean()
import pandas as pd

def get_asthma_data(file_path="data/asthma_ed_df.csv"):
    df = pd.read_csv(file_path)
    df["Estimated annual rate per 10,000"] = pd.to_numeric(df["Estimated annual rate per 10,000"], errors='coerce')
    df["Number"] = pd.to_numeric(df["Number"], errors='coerce')
    return df

def get_asthma_by_borough(asthma_df):
    borough_df = asthma_df.groupby("Borough")["Estimated annual rate per 10,000"].mean().reset_index()
    return borough_df

def get_asthma_by_neighborhood(asthma_df):
    neighborhood_df = asthma_df.groupby(["Geography", "Borough"])["Estimated annual rate per 10,000"].mean().reset_index()
    return neighborhood_df

def get_rent_by_neighborhood(rent_df):
    neighborhood_df = rent_df.groupby(["Geography", "Borough"])["Value"].mean().reset_index()
    return neighborhood_df
