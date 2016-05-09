import requests
from bs4 import BeautifulSoup
import sys
import io

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
INSPECTION_PAGE = 'inspection_page.html'


def get_inspection_page(**kwargs):
    """Return inspection page."""
    params = INSPECTION_PARAMS
    for k, a in kwargs.items():  # don't throw in params that don't belong
        if k in INSPECTION_PARAMS:
            params[k] = a
    response = requests.get('{}{}'.format(INSPECTION_DOMAIN, INSPECTION_PATH,),
                            params)
    encoding = response.encoding
    response.raise_for_status()
    return response.content, encoding


def write_inspection_page():
    """Write inspection page to file."""
    content = get_inspection_page()[0]
    with io.open(INSPECTION_PAGE, 'wb') as f:
        f.write(content)


def load_inspection_page():
    """Load inspection page."""
    with io.open(INSPECTION_PAGE) as f:
        inspection_page = f.read()
    return inspection_page, 'utf-8'



# with io.open('kc_health_data.html') as f:
#                html_doc = f.read()
#
# soup = BeautifulSoup(html_doc, 'html.parser')
#
# print(soup)
