import  pandas as pd
from    sodapy import Socrata
import json
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd
from shapely.geometry import shape

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
    
def get_rent_data(file_path="data/rent_df.csv"):
    df = pd.read_csv(file_path)
    return df

def get_rent_by_borough(rent_df):
    neighborhood_df = rent_df.groupby(["Geography", "Borough"])["Value"].mean().reset_index()
    return neighborhood_df

def get_rent_by_neighborhood(rent_df):
    neighborhood_df = rent_df.groupby(["Geography", "Borough"])["Value"].mean().reset_index()
    return neighborhood_df

def get_air_quality_table():
    data = {
        "Borough": ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island", "Healthy Standard"],
        "PM2.5 (µg/m³)": [7.6, 7.3, 7.8, 7.2, 6.8, "< 12"],
        "NO₂ (ppb)": [16.0, 17.4, 18.8, 15.2, 13.9, "< 53"],
        "O₃ (ppb)": [32.7, 36.4, 30.4, 37.1, 34.3, "< 70"],
    }
    air_quality_table = pd.DataFrame(data)
    return air_quality_table

def get_heat_map(zip_codes_df, parks_by_zip):
    zip_codes_df = zip_codes_df.dropna(subset=['the_geom'])

    #Convert 'the_geom' (dict with 'coordinates' and 'type') to shapely shapes
    zip_codes_df['geometry'] = zip_codes_df['the_geom'].apply(shape)

    #Create GeoDataFrame
    zip_codes_gdf = gpd.GeoDataFrame(zip_codes_df, geometry='geometry', crs="EPSG:4326")

    #Merge park counts and zipcodes Geodata
    zip_parks_gdf = zip_codes_gdf.merge(
        parks_by_zip,
        left_on='modzcta',
        right_on='zipcode',
        how='left'
    )

    #Set zip codes with no parks to 0
    zip_parks_gdf['Number of Parks'] = zip_parks_gdf['Number of Parks'].fillna(0)

    #Heat Map
    fig = px.choropleth_mapbox(
        zip_parks_gdf,
        geojson=json.loads(zip_parks_gdf.to_json()),
        locations="modzcta",
        featureidkey="properties.modzcta",
        color="Number of Parks",
        color_continuous_scale="YlGn",
        hover_name="modzcta",
        hover_data={"Number of Parks": True},
        mapbox_style="carto-positron",
        zoom=8.8,
        center={"lat": 40.7, "lon": -74},
        opacity=0.5,
    )
    return fig

def get_borough_summary(rent_df, asthma_df, parks_df):
    rent_borough = rent_df.groupby("Borough")['Value'].mean().reset_index()
    rent_borough.rename(columns={'Borough':'borough'}, inplace=True)
    rent_borough.rename(columns={'Value': 'Average Percentage of Households Spending >30% on Rent'}, inplace=True)

    asthma_borough = asthma_df.groupby("Borough")['Estimated annual rate per 10,000'].mean().reset_index()
    asthma_borough.rename(columns={'Borough':'borough'}, inplace=True)
    asthma_borough.rename(columns={'Estimated annual rate per 10,000': 'Estimated annual rate of Asthma ED Visits per 10,000'}, inplace=True)

    borough_map = {'M': 'Manhattan','B': 'Brooklyn','Q': 'Queens','X': 'Bronx','R': 'Staten Island'}
    parks_df['borough'] = parks_df['borough'].map(borough_map)
    parks_borough = parks_df.groupby('borough').size().reset_index(name='Number of Parks')

    borough_summary = pd.merge(rent_borough, asthma_borough, on="borough")
    borough_summary = pd.merge(borough_summary, parks_borough, on="borough")
    borough_summary.style.background_gradient(cmap='Blues', subset=['Average Percentage of Households Spending >30% on Rent', 'Estimated annual rate of Asthma ED Visits per 10,000', 'Number of Parks'])
    return borough_summary
