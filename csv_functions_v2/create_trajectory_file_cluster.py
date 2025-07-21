'''
Create a .tra file from the dataframe. Store it at given location
'''

import pandas as pd


def transform_csv_to_trajectory_format(df, output_file):

    # Initialize the list to store trajectories
    trajectories = []
    index = 0

    tracker_ids = df['tracker_id'].unique()

    # Process each tracker ID
    for tracker_id in tracker_ids:
        traj_data = df[df['tracker_id'] == tracker_id][['real_world_sw_x', 'real_world_sw_y']].values
        num_vectors = traj_data.shape[0]
        trajectory = [index] + [num_vectors] + traj_data.flatten().tolist()
        trajectories.append(trajectory)
        index += 1
    
    
    # Define the dimension and number of trajectories
    dim_tra = 2
    num_tra = len(trajectories)
    
    # Write the formatted data to the output file
    with open(output_file, "w") as f:
        f.write(f"{dim_tra}\n")
        f.write(f"{num_tra}\n")
        for traj in trajectories:
            f.write(" ".join(map(str, traj)) + "\n")

    print("Trajectory file created successfully.")



def main(df, filename):

    output_file = "04.Trajectory_results/Trajectory_files/" + filename[:-4] + ".tra" 
    transform_csv_to_trajectory_format(df, output_file)
