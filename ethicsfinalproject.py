import  pandas as pd
from    sodapy import Socrata

def get_data_frame(id):
    client     = Socrata("data.cityofnewyork.us", None)
    data    = client.get(id)
    return pd.DataFrame.from_records(data)