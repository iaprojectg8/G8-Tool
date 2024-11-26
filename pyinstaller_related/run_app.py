from streamlit.web import cli
import os
import shutil
import sys
import atexit



# In order to config Pyinstaller the right way, you should refer to this github 
# repo which tells exactly the step to follow:
# https://github.com/jvcss/PyInstallerStreamlit

def setup_temp_environment(temp_files, base_dir):
    """
    Set up the temporary environment by copying required files and folders
    from the extracted resources to the working directory.

    Args:
        temp_files (list of tuples): A list of tuples where each tuple contains
                                      the source file/folder path (from the packaged 
                                      application) and the destination path (in the 
                                      current working directory).
    """
    for src, dest in temp_files:
        src_path = os.path.join(base_dir, src)  # Construct full path for source
        
        # Check if the source path is a directory
        if os.path.isdir(src_path):
            if not os.path.exists(dest):  # Create the destination folder if not exists
                shutil.copytree(src_path, dest)
        # If it's a file, copy it directly to the destination
        elif os.path.isfile(src_path):
            shutil.copy2(src_path, dest)

def cleanup_temp_environment(temp_files):
    """
    Clean up the temporary environment by deleting the files and folders
    copied to the working directory after execution.

    Args:
        temp_files (list of tuples): A list of tuples where each tuple contains
                                      the source file/folder path (from the packaged 
                                      application) and the destination path (in the 
                                      current working directory).
    """
    try:
        for _, dest in temp_files:
            if os.path.isdir(dest):
                shutil.rmtree(dest, ignore_errors=True)  # Remove directories
            elif os.path.isfile(dest):
                os.remove(dest)  # Remove files
    except Exception as e:
        print(f"Error occurred during cleanup: {e}")

def main():

    if getattr(sys, 'frozen', False):
        """
        If the application is running as a PyInstaller bundle (frozen),
        extract the necessary files from the embedded package and set up 
        a temporary environment to access them.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
        meipass_path = sys._MEIPASS  # Path where PyInstaller extracts resources
        print(f"Extracted resources path: {meipass_path}")

        # List of files and folders to copy from the PyInstaller bundle to the working directory
        temp_files = [
            (os.path.join(meipass_path, 'General.py'), os.getcwd()),  # Copy General.py to current working directory
            (os.path.join(meipass_path, 'lib'), os.path.join(os.getcwd(), 'lib')),  # Copy lib folder
            (os.path.join(meipass_path, 'utils'), os.path.join(os.getcwd(), 'utils')),  # Copy utils folder
            (os.path.join(meipass_path, 'layouts'), os.path.join(os.getcwd(), 'layouts')),  # Copy layouts folder
            (os.path.join(meipass_path, 'pages'), os.path.join(os.getcwd(), 'pages')),  # Copy pages folder
            (os.path.join(meipass_path, '.streamlit'), os.path.join(os.getcwd(), '.streamlit')),  # Copy .streamlit folder
            (os.path.join(meipass_path, 'CSV_files'), os.path.join(os.getcwd(), 'CSV_files')),  # Copy CSV_files folder
        ]

        # Set up the temporary environment by copying necessary files/folders
        setup_temp_environment(temp_files, base_dir)

        # Register cleanup to be executed when the program ends
        atexit.register(lambda: cleanup_temp_environment(temp_files))

        # Run the main Streamlit application with specific arguments
    cli._main_run_clExplicit('General.py', is_hello=False, args=['run'])

if __name__ == "__main__":
    main()