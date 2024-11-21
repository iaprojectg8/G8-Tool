# G8-Tool
It contains everything that could be used by collaborators regarding data analysis


## Features
- Chose climate variables
- Select a period of interest
- Select an interval cut
- Show variable mean month plot
- Show variables mean year evolution plot

## Install
You should install miniconda to not have any problem with the installation as it will contain everything you need and well separate from anything else that could interfer. Interence between packages is the most annoying problem when making installation.

## Environment

If you don't have miniconda install it, and set it up correctly.

1. Create your conda environment
```
conda create --name env_name python=3.12
```
2. Acitvate it
```
conda activate env_name
```

3. Install the needed packages
```
pip install -r requirements.txt     
```

## Launch the app
```
streamlit run General.py
```
