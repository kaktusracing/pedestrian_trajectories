'''
This function applies georeferencing on a given dataframe. Needs a corresponding point file for homography.

'''

import pandas as pd
import os
import numpy as np
import cv2
import geopandas as gpd
import numpy as np


def get_reference_matr(place_id, tar_resolution, folder):

    #print('Looking for matrix for ID Nr. ', place_id)

    for file in os.listdir(folder):
        filename = os.fsdecode(file)
        #print("filename for matrix: ", filename[:3])
        if place_id in filename[:3]:
            reference = pd.read_csv(os.path.join(folder, filename), comment='#', encoding='latin1')

            #reference points where extracted using different resolutions. Trajectory files are all given in HD pixel coordinates.
            #It therefore needs to be ensured that the reference points are tranformed to the same resolution. Matching based on resolution 
            #in filename of point file.

            if 'HD' in filename and not 'QHD+'or'FHD' or 'QHD' or 'UHD' or 'HD+' in filename:
                 scaled_ref = rescale_matrix(reference, (1280,720), tar_resolution)
            if 'FHD' in filename:
                 scaled_ref = rescale_matrix(reference, (1920, 1080), tar_resolution)
            if 'QHD' in filename and 'QHD+' not in filename:
                 scaled_ref = rescale_matrix(reference, (2560, 1440), tar_resolution)
            if 'UHD' in filename:
                 scaled_ref = rescale_matrix(reference, (3840, 2160), tar_resolution)
            if 'QHD+' in filename:
                 scaled_ref = rescale_matrix(reference, (2688, 1520), tar_resolution)
            if 'HD+' in filename and 'QHD+' not in filename:
                 scaled_ref = rescale_matrix(reference, (1280, 1024), tar_resolution)
                            
            h, _ = get_proj_matrix(scaled_ref)
            return h
        else:
            #print('Matrix for ID Nr. ', place_id, 'not found')
            continue


#function to rescale point file.
def rescale_matrix(df, old_res, target_resolution):
    # Calculate scale factors
    new_res= target_resolution
    scale_x = new_res[0] / old_res[0]
    scale_y = new_res[1] / old_res[1]
    
    # Scale coordinates
    df['sourceX'] = df['sourceX'] * scale_x
    df['sourceY'] = df['sourceY'] * scale_y
    
    return df
     

#function to create homography matrix from rescales point file
def get_proj_matrix(ref):
    '''
    pts_src and pts_dst are numpy arrays of points

    in source and destination images.

    '''
    pts_src = np.array([(x,y) for x,y in zip(ref['sourceX'], -1*ref['sourceY'])])

    pts_dst  = np.array([(x,y) for x,y in zip(ref['mapX'], ref['mapY'])])

    h, status = cv2.findHomography(pts_src, pts_dst)

    return h, status


# Function to apply homography
def apply_homography(x, y, H):
    pixel_coords = np.array([x, y, 1.0])
    real_world_coords = H @ pixel_coords
    real_world_coords /= real_world_coords[2]  # normalize by the third coordinate
    return real_world_coords[0], real_world_coords[1]




def main(df, filename, window_size, folder):

    print('start creating df with real-world coordinates')
    geo_df = df    
    buffer_geo_df = []

    # Initialize new columns for real-world coordinates
    geo_df['real_world_x'] = 0.0
    geo_df['real_world_y'] = 0.0

    #define target resolution:
    if '480p' in filename:
            tar_res = (640, 480)
    else:
            tar_res = (1280, 720)

    #get homography for specific place:
    homography = get_reference_matr(filename[:3], tar_res, folder)

    # Apply the homography to each row
    for index, row in geo_df.iterrows():
        real_world_x, real_world_y = apply_homography(row['center_x'], row['y_max'], homography)
        geo_df.at[index, 'real_world_x'] = real_world_x
        geo_df.at[index, 'real_world_y'] = real_world_y


    #apply moving window
    for tracker_id, group in geo_df.groupby('tracker_id'):
        if window_size > len(group):
            group['real_world_sw_x'] = group['real_world_x']
            group['real_world_sw_y'] = group['real_world_y']
            #print('group ', tracker_id, ' skipped.')
        
        else:
            group['real_world_sw_x'] = group['real_world_x'].rolling(window=window_size, min_periods=1).median().round(4)
            group['real_world_sw_y'] = group['real_world_y'].rolling(window=window_size, min_periods=1).median().round(4)
            #print('group ', tracker_id, ' added.')
        buffer_geo_df.append(group)


    # Concatenate all modified groups into a single DataFrame
    modified_geo_df = pd.concat(buffer_geo_df, ignore_index=True)

    print('df with real-world coordinates created')
    return modified_geo_df