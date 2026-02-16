# CAP5771-project

## Repo structure
Base directory containing python scripts and Jupyter notebooks containing milestone code, 'diary/' containing diary entries recording the data science process,
'data' directory containing CSV datasets and the database (empty directory may need to be created before downloading datasets), 'data/nutrients' directory containing 
the USDA nutrition dataset CSV files

## Generating DB
- In the 'data' directory create an empty 'nutrients' subdirectory
- download the 'Branded' CSV dataset at https://fdc.nal.usda.gov/download-datasets and put the extracted files in the 'data/nutrients' directory
- download the Walmart prices CSV dataset at https://www.kaggle.com/datasets/thedevastator/product-prices-and-sizes-from-walmart-grocery and put it in the 'data' directory
- run the 'db_setup.py' script
- a 'nutrition.db' file should be created in the 'data' directory, if not, ensure that all three booleans at the top of the setup script are set to True and all CSVs
are in the correct locations

We currently provide a 'scraped_wf_data.csv' due to the amount of time it takes to scrape the Whole Foods website.
If you would like to generate this yourself, you will need to run 'whole-foods-scraper.py.'
This requires some slight configuration to run, since it creates a new Firefox profile in the project directory by default.

If you do not wish to run this, you can skip the next section.

### Running the Whole Foods Scraper
After installing dependencies from requirements.txt (`python -m pip install -r requirements.txt`), open 'whole-foods-scraper.py' in a text editor.
Set the string in the `FIREFOX_INSTALL_LOC` constant to the absolute path of an installation of Firefox.
Selenium will detect the installation for actual scraping, but this is necessary to run the subprocess to generate a portable profile in the project directory.

The script will pull searchable items and zip codes from the target of `ITEM_SEARCHES_FILE` and `ZIP_CODES_FILE`, respectively.
In our use, we generated `ITEM_SEARCHES_FILE` from the description column of the Walmart dataset.
This file is read as a CSV, with the only column specified at the top being 'description'.
If you write your own searches, ensure each search is on its own line, with the very first being 'description'.
`ZIP_CODES_FILE` is simply a newline delimited list of zip codes to pull data from.

The script will perform all searches in the range `[SEARCH_OFFSET, MAX_ITEM_SEARCHES_PER_ZIP_CODE]` for each zip code.
You can modify bounds as you see fit by modifying those constants.

## Running the Jupyter Notebook
- see above 'Generating DB' section to generate the database used
- ensure all requirements in 'requirements.txt' are met
- open 'milestone1.ipynb', 'Restart' the notebook if available, then 'Run All' to run all cells
- if you wish to run them individually, the first code cell is necessary to run others and the last cell closes the database