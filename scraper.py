#!/usr/bin/python3.5
"""Parsing data from usaspending."""
import os
import logging
import itertools
from io import BytesIO
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def get_file(url, directory):
    """A function to download and unzip files."""
    print('Uploading', url, 'file to', '"' + directory + '"')
    try:
        datafile = requests.get(url).content
    except requests.exceptions.ConnectionError:
        logging.critical('Check internet/server connection!')
        exit(1)
    ZipFile(BytesIO(datafile)).extractall(directory)


def parse_links():
    """A function to create files links."""
    # Preparing the environment
    app = 'https://apps.usaspending.gov/DownloadCenter/AgencyArchive'
    payload = {'SpendingTypeSelected': '',
               'AgencySelected': 'All',
               'FiscalYearSelected': '',
               'OutputTypeSelected': '4'}
    spendings = ['C', 'G', 'L', 'O']
    # Parsing actual years list
    try:
        years = [i.string for i in BeautifulSoup(requests.get(app).text,
                                                 'html.parser').
                 find('select', {'name': 'FiscalYearSelected'}).
                 find_all('option')]
    except requests.exceptions.ConnectionError:
        logging.critical('Check internet/server connection!')
        exit(1)
    # Cartesian product for links generation
    links_payload = [i for i in itertools.product(years, spendings)]
    spendings_dict = {
        'C': 'Contracts',
        'G': 'Grants',
        'L': 'Loans',
        'O': 'Other Financial Assistance'}
    # Main parsing loop
    for i in links_payload:
        payload['SpendingTypeSelected'] = i[1]
        payload['FiscalYearSelected'] = i[0]
        directory = 'Output' + '/' +\
                    i[0] + '/' +\
                    spendings_dict[i[1]] + '/'
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError:
                logging.critical('Check folder permissions for dir:', directory)
                return
        try:
            for link in
             BeautifulSoup(requests.post(app, data=payload).text,
                           'html.parser').
             find('table', {'id': 'ResultsTable'}).
             find_all('a'):
             if not
             os.path.isfile(directory + '/' +
                            'datafeeds\\' +
                            os.path.splitext(link.
                                             string)[0]):
             get_file(link['href'], directory)
        except requests.exceptions.ConnectionError:
            logging.critical('Check internet/server connection!')
            exit(1)
        except AttributeError:
            continue


# Script body
if __name__ == '__main__':
    parse_links()
