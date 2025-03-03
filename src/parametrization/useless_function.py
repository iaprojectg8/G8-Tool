# def process_dataframes_zip(uploaded_file, extract_to):
#     """
#     Processes the uploaded zip file containing CSV files.
#     Args:
#         uploaded_file (BytesIO): The uploaded zip file.
#         extract_to (str): The directory to extract the files to.
#     """
            
#     if os.path.exists(extract_to):
#         shutil.rmtree(extract_to)
    
#     # Create the directory
#     os.makedirs(extract_to, exist_ok=True)
    
#     extract_csv_from_zip(uploaded_file, extract_to)
#     st.session_state.already_uploaded_file = uploaded_file

#     # This is a dataframe dictionary
#     st.session_state.dataframes = read_csv_files_from_directory(extract_to)
#     st.session_state.dataframes = put_date_as_index(dataframe_dict=st.session_state.dataframes)
#     st.session_state.building_indicator_df = st.session_state.dataframes[rd.choice(list(st.session_state.dataframes.keys()))]