from openpyxl import load_workbook
from optparse import OptionParser
import os
import pandas as pd
import YNetScraper as yns


def url_sorter(name, writer, url, start_year, end_year):
    if yns.BASE_URL in url:
        yns.url_sorter(name, writer, url, start_year, end_year)
    else:
        print('This URL is not recognized, quitting..')


parser = OptionParser()
parser.add_option('-b', '--book', dest='book', type='string', default=None, help='Name of the Excel book to write to')
parser.add_option('-s', '--start_year', dest='start_year', type='int', default=2015, help='Year to start parsing')
parser.add_option('-e', '--end_year', dest='end_year', type='int', default=2020, help='Year to end parsing (inclusive)')
parser.add_option('-n', '--sheet_name', action='append', dest='sheet_names', default=[], help='Names of sheets in order of url')
parser.add_option('-u', '--url', action='append', dest='urls', help='Urls to parse')

(options, args) = parser.parse_args()
if options.book != None and ('.xlsx' not in options.book[-5:]):
    options.book += '.xlsx'
if options.book == None:
    options.book = 'output.xlsx'
default = 0
book = None

try:
    book = load_workbook(filename=options.book)
except:
    print('Could not find existing book, creating one at', options.book)

with pd.ExcelWriter(options.book, engine='openpyxl', mode='a') as writer:
    if book is not None:
        writer.book = book
    for i in range(len(options.urls)):
        if i < len(options.sheet_names):
            name = options.sheet_names[i]
        else:
            name = f'default_name_{default}'
            default += 1

        url_sorter(
            name,
            writer,
            options.urls[i],
            options.start_year,
            options.end_year
        )
