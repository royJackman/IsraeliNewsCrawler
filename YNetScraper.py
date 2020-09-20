from bs4 import BeautifulSoup as bs
import multitasking
import pandas as pd
import re
import signal
import time
import urllib.request

signal.signal(signal.SIGINT, multitasking.killall)
multitasking.set_max_threads(10)

BASE_URL = 'https://www.ynet.co.il'


def url_sorter(name, writer, url, start_year, end_year):
    if '/home/0,7340,L' in url:
        match = re.search(r'4269-[0-9]{3}[0-9]?-[0-9]+', url)
        lcode = match.group(0)
        parse_range(start_year, end_year + 1, lcode, writer, name)


def parse_article(url, month, year):
    articleUrl = BASE_URL + url
    articlehandle = urllib.request.urlopen(articleUrl)
    while articlehandle.getcode() != 200:
        articlehandle = urllib.request.urlopen(articleUrl)
    soup = bs(articlehandle.read(), 'html.parser')
    falist = soup.find_all('span', class_='art_header_footer_author')
    try:
        title = soup.find('h1', class_='art_header_title').contents[0]
    except:
        title = None

    try:
        author = falist[0].contents[0].contents[0]
    except:
        author = None

    try:
        subtitle = soup.find('h2', class_='art_header_sub_title').contents[0]
    except:
        subtitle = None
    retval = [
        title,
        author,
        month,
        2000 + year,
        subtitle,
        articleUrl
    ]
    return retval


def parse_month(year, month, page, lcode):
    url = f'https://www.ynet.co.il/home/0,7340,L-{lcode}-{year}{str(month).zfill(2)}-{page},00.html'
    filehandle = urllib.request.urlopen(url)
    error = False
    while error or filehandle.getcode() != 200:
        error = False
        try:
            filehandle = urllib.request.urlopen(url)
        except:
            error = True
    soup = bs(filehandle.read(), 'html.parser')
    table = soup.find('td', class_='ghciArticleIndex1')
    table = table.contents[2]
    articles = len(table.contents)
    retval = []
    if articles > 1:
        for i in range(int(articles/3)):
            link = table.contents[3 * i].find('a')
            metadata = table.contents[3 * i + 1].string.split(' ')
            dates = metadata[-1].replace('(', '').replace(')', '').split('/')
            retval.append([
                link.string,
                ' '.join(metadata[:-1]),
                dates[0],
                dates[1],
                dates[2],
                BASE_URL + link.get('href')
            ])
    if soup.find('a', string='לעמוד הבא') != None:
        retval += parse_month(year, month, page + 1, lcode)
    return retval


def parse_range(start_year, end_year, lcode, writer, name):
    columns = [
        'כותרת הידיעה',
        'שם הכותב',
        'תאריך',
        'חודש',
        'שנה',
        'קישור לידיעה'
    ]
    df = []
    for i in range(start_year, end_year):
        for j in range(1, 13):
            month = parse_month(i, j, 1, lcode)
            if len(month) > 0:
                df += month
            print(name, 'Month ', j, '/', i)
    DFrame = pd.DataFrame(df, columns=columns)
    print(DFrame)
    DFrame.to_excel(writer, sheet_name=name, index=False, verbose=True)
