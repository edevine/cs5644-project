# CS5644 Project
Final Project for CS 5644 Machine Learning with Big Data

## Quick Start
1. Download Taxi data from [www.nyc.gov/html/tlc/html/about/trip_record_data.shtml](http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml)
2. From the command line: run "preprocess-taxi-data.py" with two arguments: input directory, and output file
    e.g. `py preprocess-taxi-data.py taxi-data daily.csv`

## Borough Boundaries
1. Download geo-json file from [http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nybb/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson](http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nybb/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson) and save to 'geo-data/borough-boundaries.json'.
2. From the command line, run `py scrap/geo-map.py`
