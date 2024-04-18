import requests
import json
from valid_params import REGIONS, URLS

# Rankings is the only url that requires a region
def get_data(url, region):
    """
    url: str
        The url to get the data from
    region: str
        The region to get the data from -- must be one of the regions in the locations.py file

    This method makes a request to the url and saves the data to a json file in the /data directory
    The url must be 
    """
    if not region and url == URLS[0]:
        raise ValueError("Rankings url requires a region")
    if url == URLS[0]:
        if region not in REGIONS:
            raise ValueError("Invalid region")
        url = url.replace(":region", region)
    
    response = requests.get(url)
    data = response.json()
    if url == URLS[0]:
        with open(f"../data/{region}_rankings.json", "w") as f:
            json.dump(data, f, indent=4)
    else:
        with open(f"../data/{url.split('/')[-1]}.json", "w") as f:
            json.dump(data, f, indent=4)

if __name__ == '__main__':
    for url in URLS:
        if url == URLS[0]:
            for region in REGIONS:
                get_data(url, region)
        else:
            get_data(url, None)

