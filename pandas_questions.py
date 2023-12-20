"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions = regions.rename(
         columns={'code': 'region_code',  'name': 'name_reg'})
    regions_and_departments = pd.merge(
        departments[['region_code', 'code', 'name']],
        regions[['region_code', 'name_reg']],
        on='region_code',
        how='left'
    )
    print(regions_and_departments.columns)
    regions_and_departments.columns = ['code_reg', 'code_dep', 'name_dep',
                                       'name_reg']
    regions_and_departments.insert(1, 'name_reg_new',
                                   regions_and_departments['name_reg'])
    regions_and_departments = regions_and_departments.drop(columns='name_reg')
    regions_and_departments = regions_and_departments.rename(
         columns={'name_reg_new': 'name_reg'})
    regions_and_departments.iloc[0:9, 2] = pd.Series(
         ['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum[referendum['Department code'].isin(
         regions_and_departments['code_dep'].values)]
    referendum.columns = ['Department code', 'Department name',
                          'Town code', 'Town name', 'Registered',
                          'Abstentions', 'Null', 'Choice A', 'Choice B']

    referendum_and_areas = pd.merge(referendum, regions_and_departments,
                                    left_on='Department code', 
                                    right_on='code_dep')
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    results = referendum_and_areas[['code_reg', 'Registered', 'Abstentions',
                                    'Null', 'Choice A',
                                    'Choice B']].groupby('code_reg').sum()
    print(results)
    rename = referendum_and_areas[['name_reg', 'code_reg']].set_index(
        'code_reg')
    rename = rename.drop_duplicates()
    print(rename)
    results = pd.concat([results, rename], axis=1)
    result_by_regions = results
    return result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map.
        The results should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file('data/regions.geojson')
    print(geo_data.columns)
    merged_data = geo_data.merge(referendum_result_by_regions,
                                                                left_on='code',
                                                                right_on='code_reg')
    merged_data['ratio'] = merged_data['Choice A'] / (
            merged_data['Choice A'] + merged_data['Choice B'])
    merged_data.plot(column='ratio')
    return merged_data


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
