'''
To include only trajectories within the square boundaries, datapoints outside these boundaries are deleted.
'''

import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon


def read_csv(file_path):
    # Read the CSV file into a DataFrame
    return pd.read_csv(file_path)

def create_polygon(points):
    # Create a polygon from given points
    return Polygon(points)

def filter_data(df, polygon):
    # Filter out rows where x or y is outside the polygon
    def is_within_polygon(row):
        point = Point(row['real_world_x'], row['real_world_y'])
        return polygon.contains(point)

    return df[df.apply(is_within_polygon, axis=1)]


def main(df, point_df):

    print('start creating df with removing points outside of place polygon')
    df_xy = point_df[['real_world_x', 'real_world_y']]

    points = list(df_xy.itertuples(index=False, name=None))
    
    # Create the polygon
    polygon = create_polygon(points)
    
    # Filter the data
    filtered_df = filter_data(df, polygon)

    print('df with removed points outside of place polygon created')

    return filtered_df


#points = [(1089570.16,6123193.04), (1089624.58,6123247.62), (1089677.42,6123194.94), (1089596.26,6123150.49)]  # Example points for the polygon

