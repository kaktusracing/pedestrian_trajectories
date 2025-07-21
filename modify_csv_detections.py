
'''
V11: 2025-07-21
Function to modify raw trajectorz csv files. 
Process steps can be taken from the readme file or from the script.
User needs to modify:
-directory: directory of raw trajectory files. 
-output_directory: where to save modified trajectory files
-point_folder; includes the tranformation matrices for geotransformation. given in supplementary material
-place_coord_folder: inclues place polygons in real-world coordinates. given in supplementary material

If .tra files need to be created, uncomment function (line 118) and make sure to define right location within "create_trajectory_file_cluster"



'''

import pandas as pd
import os
import geopandas as gpd
import datetime


path = os.getcwd()
print(path)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.getcwd()
print(path)

from csv_functions_v2 import calc_walking_speed_V3
from csv_functions_v2 import calc_center
from csv_functions_v2 import calc_geo_df
from csv_functions_v2 import subsample_csv
from csv_functions_v2 import mask_coordinates_to_place
from csv_functions_v2 import create_trajectory_file_cluster
from csv_functions_v2 import reduce_csv


current_date = datetime.datetime.now().strftime("%Y-%m-%d")

#needs to be modified by user:
directory = "Demo/04.trajectory_raw/"
output_directory = "Demo/05.trajectory_results/"

point_folder = "Demo/07.geotransformation/points/"
place_coord_folder = "Demo/08.place_data/polygons/"


# Define modification properties
fps = 15 # Define the frame rate (frames per second)
resolution = 0.5 #[seconds] How many seconds between consecutive datapoints (for reducing complexity) Must be divisible by 0.5
window_size = 8 #size of window for moving average 
threshold = 30 #traces with less frames are deleted

#initialization
buffer_df = []
buffer_geo_df = []


#gets corresponding polygon for each trajectory file. matching is done by place id which needs 
#to be at the beginning of each file in the format: XX_placename.
def get_place_polygon(name):
    for file in os.listdir(place_coord_folder):
        filename = os.fsdecode(file)
        #print('visited_filename:', filename)
        if filename.endswith(".csv") and filename.startswith(name): 
            #print("filename place_polygon:", filename)
            # Read the CSV file into a DataFrame
            place_df = pd.read_csv(place_coord_folder + filename)
            return place_df


print("directory", directory)

#main function. walks through (sub)directories of given directory
for root, dirs, files in os.walk(directory):
    for name in files:
        filename = os.fsdecode(name)
        print("filename:", filename)
        if filename.endswith(".csv"): 

            # Read the CSV file into a DataFrame
            print("root ",root, "and dir ", dirs, "and filename: ", filename)
            place_name = filename[:3] #place_name is equal to place id +_ e.g. "04_"
            print('place_name:', place_name)
            df = pd.read_csv(root + '/' + filename)

            #first subfunction subsamples the df. Traces with less frames than threshold are deleted: 
            df = subsample_csv.main(df, threshold)

            if df.empty == True:
                print('Dataframe', filename, 'is empty')
                continue

            # get center of bounding boxes, time (based on fps) and applying a sliding window. It adds the columns center_x, center_y, time, sliding_window_x and sliding_window_y
            df = calc_center.main(df, window_size, fps)

            # get real world coordinates. Adds column real_world_xm real_world_y, real_world_sw_x and real_world_sw_y
            df = calc_geo_df.main(df,filename, window_size, point_folder)

            #mask place-polygone over place points (real_world coordinates): excludes data point outside the place boundaries
            place_df = get_place_polygon(place_name)

            df = mask_coordinates_to_place.main(df,place_df )

            #df traces with less frames than threshold are deleted: 
            df = subsample_csv.main(df, threshold)


            #catch empty csv files
            if df.empty == True:
                print('Dataframe', filename, 'is empty')
            
            else:

                #subsample the df: only include every x datapoint of each trace in the new df
                df = reduce_csv.main(df, resolution)

                #create .tra file --> activate when needed. Make sure to define output directory within function!
                #create_trajectory_file_cluster.main(df, filename)

                #Get geojson for every datapoint (no sliding window)
                gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['real_world_x'], df['real_world_y']), crs = 'EPSG:3857')
                gdf = gdf.to_crs('EPSG:4326')
            
                #Get geojson for every datapoint (sliding window)
                gdf_sw = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['real_world_sw_x'], df['real_world_sw_y']), crs = 'EPSG:3857')
                gdf_sw = gdf_sw.to_crs('EPSG:4326')

                folder_path = os.path.join(output_directory + "/Geojsons/")
                os.makedirs(folder_path, exist_ok=True)
                gdf.to_file(folder_path + filename[:-4] + ".geojson", 
                driver='GeoJSON')
                gdf_sw.to_file(folder_path + filename[:-4] + "_sw.geojson", 
                driver='GeoJSON')

                # get walking speed. Adds column 'speed' and 'speed_sw
                df = calc_walking_speed_V3.main(df)

                #Adds column 'number of people'
                df['nr_people'] = df.groupby('time')['time'].transform('count')

                #save file to given directory
                folder_path = os.path.join(output_directory + "/speed/" )
                os.makedirs(folder_path, exist_ok=True)
                df.to_csv(folder_path + filename[:-4] + "_speed.csv", index=False)

            continue
        else:
            continue





