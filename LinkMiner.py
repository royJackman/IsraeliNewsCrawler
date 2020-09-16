from optparse import OptionParser
from urllib.error import URLError
import numpy as np
import pandas as pd

parser = OptionParser()
parser.add_option('-b', '--book', dest='book', type='string', default=None, help='Name of the Excel book to write to')
parser.add_option('-s', '--sheet_name', action='append', dest='sheet_names', default=[], help='Names of sheets to mine for')
parser.add_option('-u', '--url', action='append', dest='urls', help='Urls to parse')

(options, args) = parser.parse_args()

books = pd.read_excel(options.book, sheet_name=None)
amos = books['עמוס הראל']
yaniv = books['יניב קובוביץ']
yaniv['קישור'] = np.nan
yaniv = yaniv.rename(columns={'Unnamed: 8': 'קטלוג במחקר'})


haaretz = pd.concat([amos, yaniv], join='inner', ignore_index=True)

try: 
    from googlesearch import search
except ImportError:
    print('No module names "google" found')

for i, row in haaretz.iterrows():
    if row['קישור'] in [np.nan, '']:
        print('PARSING:', row['שם'])
        strings = [row['שם']]
        phrases = row['שם'].split(',')
        if len(phrases) > 1:
            for p in phrases:
                strings.append(p)
        while len(strings) > 0:
            s = strings.pop()
            try:
                for j in search(s, num=10):
                    if 'haaretz.co.il' in j:
                        print('FOUND:', j)
                        haaretz.loc[i, 'קישור'] = j
                        strings = []
                        break
            except URLError:
                print('NOT FOUND:', i)

haaretz.to_excel('haaretz.xlsx', index=False)