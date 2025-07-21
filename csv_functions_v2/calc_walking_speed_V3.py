'''
based on chatGPT. Prompt: Hi! I need a python script for the following task:
I have a .csv file that entails the location of multiple objects (humans) over a certain period of time. Each object is identified by "tracker_id". I need the speed of every object for every moment of the period. Write a script that:
-opens the .csv file
-adds a column for walkingspeed
-groups by tracker_id
-extracts information about location from the column centre_x and centre_y.
-calculated the speed at each specific moment
-adds the speed into the column
-merges the grouped tracker_ids
-saves the document as new csv

V3: adding automated extraction of relevant column numbers
Added Geodesic speed calculation instead of euclidean on Mercator
'''


import pandas as pd
import numpy as np
from pyproj import Transformer
from geopy.distance import geodesic



def main(df):

    print('start creating df with speed calculations')


    # Ensure the dataframe is sorted by tracker_id and timestamp
    df.sort_values(by=['tracker_id', 'time'], inplace=True)

    # Define transformer from EPSG:3857 to EPSG:4326
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

    # Apply transformation to each row
    df[['latitude', 'longitude']] = df.apply(
        lambda row: transformer.transform(row['real_world_x'], row['real_world_y']),
        axis=1, result_type='expand'
    )
    
    # Function to calculate the speed
    def compute_speed(df, header):

        array = df.to_numpy()

        x_position = header.index('latitude')
        y_position = header.index('longitude')
        time_position = header.index('time')
        speed_position = header.index('speed')


        i = 0
        while i < (array.shape[0])-1:
            point1 = (array[i][x_position], array[i][y_position])
            point2 = (array[i+1][x_position], array[i+1][y_position])
            speed = (geodesic(point1, point2).meters) / (array[i+1][time_position]-array[i][time_position])
            array[i][speed_position] = speed
            i = i+1
        return pd.DataFrame(array, columns = headers)
    

    # Apply speed calculation function to each group
    df['speed'] = 0
    headers = list(df)
    modified_df = df.groupby('tracker_id').apply(lambda group: compute_speed(group, headers))

    print('df with speed calculations calculated')
    return modified_df

    

