from src.utils.imports import *
from src.request.cmip6_requests import *
from src.utils.variables import EMPTY_REQUEST_FOLDER, NC_FILE_DIR, CSV_FILE_DIR, CSV_ZIPPED

@pytest.fixture
def sample_shapefile(tmp_path):
    # Create a sample shapefile for testing
    gdf = gpd.GeoDataFrame({
        'geometry': [gpd.points_from_xy([0], [0])]
    })
    shapefile_path = tmp_path / "sample.shp"
    gdf.to_file(shapefile_path)
    return shapefile_path

def test_process_shapefile(sample_shapefile, mocker):
    mocker.patch('src.request.cmip6_requests.get_shapefile_path', return_value=sample_shapefile)
    mocker.patch('src.request.cmip6_requests.shapefile_into_gdf', return_value=gpd.read_file(sample_shapefile))
    mocker.patch('src.request.cmip6_requests.manage_buffer', return_value=gpd.read_file(sample_shapefile))
    selected_shape_folder = [sample_shapefile]
    zip_folder = os.path.dirname(sample_shapefile)
    default_buffer_distance = 0.2
    combined_gdf, gdf_list = process_shapefile(selected_shape_folder, zip_folder, default_buffer_distance)
    assert isinstance(combined_gdf, gpd.GeoDataFrame)
    assert isinstance(gdf_list, list)

def test_make_empty_request_for_each_gdf(mocker):
    mocker.patch('src.request.cmip6_requests.make_empty_request', return_value=pd.DataFrame({'lat': [0], 'lon': [0]}))
    gdf_list = [gpd.GeoDataFrame({'geometry': [gpd.points_from_xy([0], [0])]}, crs="EPSG:4326")]
    empty_request_gdf = make_empty_request_for_each_gdf(gdf_list)
    assert isinstance(empty_request_gdf, pd.DataFrame)
    assert not empty_request_gdf.empty

def test_make_empty_request(mocker):
    mocker.patch('src.request.cmip6_requests.requests.get', return_value=mock.Mock(status_code=200, content=b''))
    mocker.patch('src.request.cmip6_requests.open_empty_request_df', return_value=pd.DataFrame({'lat': [0], 'lon': [0]}))
    bounds = (-10, -10, 10, 10)
    gdf = make_empty_request(bounds)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert not gdf.empty

def test_make_whole_request(mocker):
    mocker.patch('src.request.cmip6_requests.widget_init_beginner', return_value=([], '', '', '', []))
    mocker.patch('src.request.cmip6_requests.reset_directory')
    mocker.patch('src.request.cmip6_requests.request_loop')
    mocker.patch('src.request.cmip6_requests.nc_files_processing')
    bounds = (-10, -10, 10, 10)
    make_whole_request(bounds)
    assert True  # If no exception is raised, the test passes

def test_request_loop(mocker):
    mocker.patch('src.request.cmip6_requests.make_year_request')
    mocker.patch('src.request.cmip6_requests.initialize_progress_bar', return_value=(0, 0))
    mocker.patch('src.request.cmip6_requests.update_progress_bar', return_value=(0, 0))
    selected_variables = ['pr']
    selected_model = 'CNRM-ESM2-1'
    ssp_list = ['ssp585']
    experiment = 'r1i1p1f2'
    years_list = [[2015]]
    bounds = (-10, -10, 10, 10)
    nc_folder = NC_FILE_DIR
    request_loop(selected_variables, selected_model, ssp_list, experiment, years_list, bounds, nc_folder)
    make_year_request.assert_called_once_with('pr', 'CNRM-ESM2-1', 'ssp585', 'r1i1p1f2', bounds, 2015, nc_folder)

def test_make_year_request(mocker):
    mocker.patch('src.request.cmip6_requests.requests.get', return_value=mock.Mock(status_code=200, content=b''))
    bounds = (-10, -10, 10, 10)
    make_year_request('pr', 'CNRM-ESM2-1', 'ssp585', 'r1i1p1f2', bounds, 2015, NC_FILE_DIR)
    assert os.path.exists(os.path.join(NC_FILE_DIR, '2015_pr_ssp585.nc'))

def test_nc_files_processing(mocker, tmp_path):
    mocker.patch('src.request.cmip6_requests.open_nc_files_in_df', return_value=pd.DataFrame({'lat': [0], 'lon': [0]}))
    mocker.patch('src.request.cmip6_requests.convert_variable_units', return_value=pd.DataFrame({'lat': [0], 'lon': [0]}))
    mocker.patch('src.request.cmip6_requests.restructure_data_and_save_into_csv')
    mocker.patch('src.request.cmip6_requests.create_zip_and_save')
    nc_file_dir = tmp_path / "nc_files"
    nc_file_dir.mkdir()
    csv_file_dir = tmp_path / "csv_files"
    csv_zipped_dir = tmp_path / "csv_zipped"
    ssp_list = ['ssp585']
    nc_files_processing(nc_file_dir, csv_file_dir, csv_zipped_dir, ssp_list)
    open_nc_files_in_df.assert_called_once_with(nc_file_dir, mock.ANY, 'ssp585')
    convert_variable_units.assert_called_once_with(mock.ANY)
    restructure_data_and_save_into_csv.assert_called_once_with(mock.ANY, csv_file_dir)
    create_zip_and_save.assert_called_once_with(csv_file_dir, csv_zipped_dir, 'ssp585', mock.ANY)