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
from shapely.ops import transform
from pyproj import Proj, Transformer, CRS
from geopy.distance import geodesic


def sliding_window(data, window_size):
            window_values = []
            for i in range(len(data)):
                window = data[max(0, i - window_size + 1): i + 1]
                window_values.append(round(window.median(), 4))
            return window_values


def main(df, moving_window, fps):

    print('start creating df with speed calculations')

    buffer_df = []

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
   
    def compute_speed(df, header, fps):
        """ df_xy = df[['real_world_x', 'real_world_y']]

        mercator_coords = list(df_xy.itertuples(index=False, name=None))

        # Step 4: Define the source (EPSG:3857) and target (EPSG:4326) CRS
        src_crs = CRS("EPSG:3857")
        dst_crs = CRS("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)

        # Step 5: Transform the coordinates from EPSG:3857 to EPSG:4326
        transformed_coords = [transformer.transform(x, y) for x, y in mercator_coords]

        #print(transformed_coords) """

        array = df.to_numpy()
        #print(array.shape)

        x_position = header.index('latitude')
        y_position = header.index('longitude')
        time_position = header.index('time')
        speed_position = header.index('speed')
        #print('x_position', x_position, y_position, speed_position)


        i = 0
        while i < (array.shape[0])-1:
            #print('for iterator i = ', i, ' it is ', array[i][17])
            #speed = np.sqrt(abs(array[i][x_position] - array[i+1][x_position])**2 + abs(array[i][y_position] - array[i+1][y_position])**2) / (1/fps)
            point1 = (array[i][x_position], array[i][y_position])
            point2 = (array[i+1][x_position], array[i+1][y_position])
            #print('point1:', point1, ' point2: ', point2)
            speed = (geodesic(point1, point2).meters) / (array[i+1][time_position]-array[i][time_position])
            #print('Speed is:', speed)
            array[i][speed_position] = speed
            i = i+1
        return pd.DataFrame(array, columns = headers)
    

    # Apply speed calculation function to each group
    df['speed'] = 0
    headers = list(df)
    #print(headers)
    df1 = df.groupby('tracker_id').apply(lambda group: compute_speed(group, headers, fps))

    # Reset index
    df1.reset_index(drop=True, inplace=True)

    for tracker_id, group in df1.groupby('tracker_id'):
        if moving_window > len(group):
            group['speed_sw'] = group['speed']
            #print('group ', tracker_id, ' skipped.')
            #modified_df.merge(group, how='right')
        
        else:
            group['speed_sw'] = sliding_window(group['speed'], moving_window)
            #print('group ', tracker_id, ' added.')
            #print(group.head())
            #modified_df.merge(group, how='right')
        buffer_df.append(group)
        


    # Concatenate all modified groups into a single DataFrame
    modified_df = pd.concat(buffer_df, ignore_index=True)
    
    print('df with speed calculations calculated')
    return modified_df

    

