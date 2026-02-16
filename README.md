# CAP5771-project

## Repo structure
Base directory containing python scripts and Jupyter notebooks containing milestone code, 'diary/' containing diary entries recording the data science process,
'data' directory containing csv datasets and the database (empty directory may need to be created before downloading datasets), 'data/nutrients' directory containing 
the usda nutrition dataset csv files

## Generating DB
- create an empty 'data' directory with an empty 'nutrients' subdirectory
- download the 'Branded' csv dataset at https://fdc.nal.usda.gov/download-datasets and put the extracted files in the 'data/nutrients' directory
- download the Walmart prices csv dataset at https://www.kaggle.com/datasets/thedevastator/product-prices-and-sizes-from-walmart-grocery and put it in the 'data' directory
- run the 'db_setup.py' script
- a 'nutrition.db' file should be created in the 'data' directory, if not, ensure that all three booleans at the top of the setup script are set to True and all csvs
are in the correct locations

## Running the Jupyter Notebook
- see above 'Generating DB' section to generate the database used
- ensure all requirements in 'requirements.txt' are met
- open 'milestone1.ipynb', 'Restart' the notebook if available, then 'Run All' to run all cells
- if you wish to run them individually, the first code cell is necessary to run others and the last cell closes the database