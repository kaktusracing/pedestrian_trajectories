'''
subsamples each trajectory: trajectories shorter than given frame threshold are deleted.
'''
import pandas as pd


def filter_tracker_ids(df, threshold) -> pd.DataFrame:
    # Count the number of rows for each unique 'tracker_id'
    tracker_counts = df['tracker_id'].value_counts()
    
    # Filter out 'tracker_id's with counts below the threshold
    valid_tracker_ids = tracker_counts[tracker_counts >= threshold].index
    non_valid_tracker_ids = tracker_counts[tracker_counts < threshold].index
    print('This ids are excluded: ', non_valid_tracker_ids)
    
    # Filter the original DataFrame to keep only valid 'tracker_id's
    filtered_df = df[df['tracker_id'].isin(valid_tracker_ids)]
    
    return filtered_df


def main(df, threshold):
    print('start creating df with removing tracker_ids with less then ', threshold , 'entries')

    filtered_df = filter_tracker_ids(df, threshold)

    print('df with removed tracker_ids with less then ', threshold , 'entries created')
    return filtered_df