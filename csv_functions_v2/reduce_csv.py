'''
This script reduces the complexity of a given df. while keeping as much relevant information as possible.
A classic approach would be to keep every xth datapoint and delete the others. 
The datapoints of the traces are not always constantly recorded. Some humans are detected not on every frame.
The approach for this script is therefore slightly different: First, the time column is rounded to .5 seconds
secondly, the first value is kept as a starting point. From here, the first value every xth seconds is kept as well
returns shortened df
'''
import pandas as pd


def subsample(group):
    start_time = group['time'].iloc[0]
    mask = ((group['time'] - start_time) % time).abs() < 1e-6  # Avoid float precision issues
    subsampled = group[mask]

    if len(subsampled) < 2:
        subsampled = pd.concat([subsampled, group.iloc[[-1]]])

    return subsampled.drop_duplicates(subset='time')




def filter_df(df, time) -> pd.DataFrame:

    # Ensure the DataFrame is sorted by 'tracker_id' and 'time'
    df = df.sort_values(by=['tracker_id', 'time'])

    # Apply the subsample function to each group
    df_subsampled = df.groupby('tracker_id', group_keys=False).apply(subsample)

    # Reset the index if necessary
    df_subsampled = df_subsampled.reset_index(drop=True)

    #print(df_subsampled)
    return df_subsampled


def main(df, time):

    if time % 0.5 == 0:
        print('start creating df with reducing trace lenght by factor', time)
        df['time'] = (df['time'] * 2).round() / 2

        filtered_df = filter_df(df, time)

        print('df with removed tracker_ids with less then ', time , 'entries created')
        return filtered_df
    else:
        print('Only values for "time" that can be divided by 0.5s are possible')



