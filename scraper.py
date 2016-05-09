import requests
from bs4 import BeautifulSoup
import sys
import io
import re
import json
from pprint import pprint

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
GEOCODE_API_URL = 'http://maps.googleapis.com/maps/api/geocode/json'


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


def parse_source(html, encoding='utf-8'):
    """Return soup object for given html file."""
    return BeautifulSoup(html, 'html.parser', from_encoding=encoding)


def extract_data_listings(html):
    pattern = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=pattern)


def has_two_tds(element):
    is_row = element.name == 'tr'
    children = element.find_all('td', recursive=False)
    has_two_children = len(children) == 2
    return is_row and has_two_children


def clean_data(data):
    try:
        return re.sub(r'^\s*|\s*$|:|^\- ', '', data.string)
    except (AttributeError, TypeError):
        return ''


def extract_restaurant_metadata(element):
    metadata_rows = element.find('table').find_all(has_two_tds,
                                                   recursive=False)
    rdata = {}
    current_label = ''
    for row in metadata_rows:
        key_cell, value_cell = row.find_all('td', recursive=False)
        new_label = clean_data(key_cell)
        if new_label:
            current_label = new_label
        rdata.setdefault(current_label, []).append(clean_data(value_cell))
    return rdata


def is_inspection_row(element):
    is_row = element.name == 'tr'
    if not is_row:
        return False
    cells = element.find_all('td', recursive=False)
    has_four = len(cells) == 4
    this_text = clean_data(cells[0]).lower()
    contains_word = 'inspection' in this_text
    does_not_start = not this_text.startswith('inspection')
    return is_row and has_four and contains_word and does_not_start


def extract_score_data(element):
    inspection_rows = element.find_all(is_inspection_row)
    samples = len(inspection_rows)
    total = high_score = average = 0
    for row in inspection_rows:
        string_value = clean_data(row.find_all('td')[2])
        try:
            int_value = int(string_value)
        except (ValueError, TypeError):
            samples -= 1
        else:
            total += int_value
            high_score = int_value if int_value > high_score else high_score
    if samples:
        average = total/float(samples)
    data = {
        u'Average Score': average,
        u'High Score': high_score,
        u'Total Inspections': samples
    }
    return data


def generate_results(test=False):
    kwargs = {
        'Inspection_Start': '2/1/2013',
        'Inspection_End': '2/1/2015',
        'Zip_Code': '98109'
    }
    if test:
        source, encoding = load_inspection_page()
    else:
        source, encoding = get_inspection_page(**kwargs)
    doc = parse_source(source, encoding)
    listings = extract_data_listings(doc)
    for listing in listings:
        metadata = extract_restaurant_metadata(listing)
        score_data = extract_score_data(listing)
        metadata.update(score_data)
        yield metadata


def get_geojson(result):
    # Get geocoding data from google using the address of the restaurant
    try:
        address = ' '.join(result['Address'])
    except KeyError:
        return None
    parameters = {'address': address, 'sensor': 'false'}
    response = requests.get(GEOCODE_API_URL, params=parameters)
    return json.loads(response.text)
    # Return the geojson representation of that data


if __name__ == '__main__':
    test = len(sys.argv) > 1 and sys.argv[1] == 'test'
    [pprint(get_geojson(r)) for r in generate_results(test)]
