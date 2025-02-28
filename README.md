## Tick Surveillance Visualization

The visualization is available at: https://huggingface.co/spaces/xrusnack/Tick-Surveillance-Visualization

## Motivation 
The intention was to create a visualization that would allow to see the trends in the mean number of ticks collected at specific locations throughout the years, as well as the proportion of positively tested ticks for the specific bacteria (B. burgdorferi, A.phagocytophilum, B. microti, B. miyamotoi).

## Dataset 
The dataset contains information about the collection and testing of blacklegged tick nymphs over a 15-year period (from 2008 to 2022) in the months of May to September, in the New York State (consisting of 62 autonomous regions – counties). The collection took place at various locations in the selected counties. The study areas were selected based on several factors - the intention was to pick locations where the public could spend time hiking, hunting, or camping. Ticks were captured by coming into contact with a piece of cloth that was dragged along the ground and after surrounding vegetation.

The data preprocessing and exploratory analysis are documented in the tick_surveillance_project.ipynb file. 

## Technology
The app is implemented in python using plotly and Dash.

## Sources
The dataset is available at https://health.data.ny.gov/Health/Deer-Tick-Surveillance-Nymphs-May-to-Sept-excludin/kibp-u2ip/data

The used geojson file can be found here https://github.com/codeforgermany/click_that_hood/blob/main/public/data/new-york-counties.geojson
