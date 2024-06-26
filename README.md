# ValorantData
*Final project for CS3435, Data Collection & Visualization by Colin Tiller / c0nD*

## Project Information
- The data was collected from [vlr.gg](https://www.vlr.gg) using an unofficial REST API which can be
found here: [vlrggapi](https://github.com/axsddlr/vlrggapi) -- with some additional web scraping (please change
 your user agent in the `data_collection/preprocess_data.py - expand_team_name` method if you'd like to run it yourself.)
- All the unprocessed json files, as well as the processed csv files can be found in the `data` directory

## Replicating Results
- Install the requirements via the following `requirements.txt`:
> pip3 install -r requirements.txt

*or with conda:*

> conda create --name <name> --file requirements.txt    
> conda activate <name>

After installing the necessary packages, you must first collect the data by running the `main()` methods in the following files in order (both files check the namespace for main, so you can just run the scripts normally):

1. `data_collection/request_api.py`
2. `data_collection/preprocess_data.py`  
*do note the `expand_team_name` method has a default user agent that may not work for you -- please provide your own in the default parameter passed to the method*

All visualizations and model results are replicable from the `performance_analysis.ipynb` and `team_modeling.ipynb` interactive Python notebooks in the `src` folder.