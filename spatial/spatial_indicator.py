from utils.imports import *


def extract_csv_from_zip(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def read_csv_files_from_directory(directory):

    # L'utilisation de glob est surement plus approprié dans ce genre de cas
    extracted_dir_name = os.listdir(directory)[0]
    extracted_dir_path = os.path.join(directory, extracted_dir_name)
    
    # Just to manage different zip file structures
    if os.path.isfile(extracted_dir_path):
        extracted_dir_path = directory

    csv_files = [f for f in os.listdir(extracted_dir_path) if f.endswith('.csv')]
    dataframes = {}
    for file in csv_files:
        file_path = os.path.join(extracted_dir_path, file)
        dataframes[file] = pd.read_csv(file_path)
    get_min_and_max_year(dataframes)
    return dataframes

def get_min_and_max_year(dataframes:dict):
    df = copy(dataframes[list(dataframes.keys())[0]])
    df["date"] = pd.to_datetime(df["date"])
    min_year = df['date'].min().year
    max_year = df['date'].max().year
    st.session_state.min_year = min_year
    st.session_state.max_year = max_year

def extract_coordinates(dataframes):
    coordinates = []
    for df in dataframes.values():
        if not df.empty:
            lat, lon = df.iloc[0][['lat', 'lon']]
            coordinates.append((lat, lon))
    gdf = gpd.GeoDataFrame(coordinates, columns=['lat', 'lon'])
    gdf['geometry'] = gdf.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
    return gdf


def make_zone_average(dataframes:dict):
    # Open all the files with glob and put it in a list of dataframes

    # Step 2: Combine all datasets
    combined_df = pd.concat(dataframes.values(), ignore_index=False)
    mean_df = combined_df.groupby(combined_df.index).mean()
    st.session_state.all_df_mean = mean_df



def put_date_as_index(dataframe_dict:dict):
    for key, df in dataframe_dict.items():
        print(df.index)
        df['date'] = pd.to_datetime(df['date'])  # Ensure the 'date' column is in datetime format
        df.set_index('date', inplace=True)  # Set the 'date' column as the index
        dataframe_dict[key] = df
    return dataframe_dict