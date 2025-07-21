'''
Function to:
-add center coordinates for each bounding box
-calculate a moving average 

'''
import pandas as pd





def main(df, window_size, fps):

    print('start creating df with center points and moving window')

    buffer_df = []

    # Sort based on tracker_id
    df.sort_values(by=['tracker_id', 'frame_index'], inplace=True)

    # Add column for center point in x
    df['center_x'] = (df['x_min'] + df['x_max']) / 2
    df['center_x'] = df['center_x'].round(4)

    # Add column for center point in y
    df['center_y'] = (df['y_min'] + df['y_max']) / 2
    df['center_y'] = df['center_y'].round(4)

    # Calculate the time based on frame_index and frame rate
    df['time'] = df['frame_index'] / fps    


    for tracker_id, group in df.groupby('tracker_id'):
        #if trajectory is shorter than window_size, don't apply moving average
        if window_size > len(group):
            group['sliding_window_x'] = group['center_x']
            group['sliding_window_y'] = group['center_y']
        
        else:
            group['sliding_window_x'] = group['center_x'].rolling(window=window_size, min_periods=1).median().round(4)
            group['sliding_window_y'] = group['center_y'].rolling(window=window_size, min_periods=1).median().round(4)
            #print('group ', tracker_id, ' added.')

        buffer_df.append(group)
        

    # Concatenate all modified groups into a single DataFrame
    modified_df = pd.concat(buffer_df, ignore_index=True)

    print('df with center points and moving window created')
    return modified_df
