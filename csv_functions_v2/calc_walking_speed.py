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

'''


import pandas as pd
import numpy as np
#import argparse


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
    
    # Function to calculate the speed
   
    def compute_speed(df, header, fps):
        array = df.to_numpy()
        #print(array.shape)

        x_position = header.index('real_world_sw_x')
        y_position = header.index('real_world_sw_y')
        speed_position = header.index('speed')
        #print('x_position', x_position, y_position, speed_position)


        i = 0
        while i < (array.shape[0])-1:
            #print('for iterator i = ', i, ' it is ', array[i][17])
            speed = np.sqrt(abs(array[i][x_position] - array[i+1][x_position])**2 + abs(array[i][y_position] - array[i+1][y_position])**2) / (1/fps)
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



""" if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('--df', type=pd.DataFrame, required=True, help='full dataframe')
    parser.add_argument('--fps', type=int, required=True, help='fps of dataframe')
    parser.add_argument('--moving_window', type=int, required=True, help='size of moving window to smooth speed and mitigate outliers')

    args = parser.parse_args()
    main(args) """
    

