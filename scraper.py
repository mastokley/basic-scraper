import requests
from bs4 import BeautifulSoup
import sys

INSPECTION_DOMAIN = 'http://info.kingcounty.gov'
INSPECTION_PATH = '/health/ehs/foodsafety/inspections/Results.aspx'
INSPECTION_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '98122',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'B',
}


def get_inspection_requests(**kwargs):
    params = INSPECTION_PARAMS
    for k, a in kwargs.items():
        if k in INSPECTION_PARAMS:
            params[k] = a
    response = requests.get('{}{}'.format(INSPECTION_DOMAIN, INSPECTION_PATH,),
                            params)
    bytes_content = sys.getsizeof(response)
    encoding = response.encoding
    response.raise_for_status()
    return response, bytes_content, encoding

# Write a load_inspection_page function which reads this file from disk and returns the content and encoding in the same way as the above function. Then you can switch between the two without altering the API. I’ll leave this exercise entirely to you.

def load_inspection_page():
    with io.open(filepath) as f:
        inspection_page = f.read


# with io.open('kc_health_data.html') as f:
#                html_doc = f.read()
#
# soup = BeautifulSoup(html_doc, 'html.parser')
#
# print(soup)
