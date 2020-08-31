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

def parse_article(url, month, year):
    articleUrl = BASE_URL + url
    articlehandle = urllib.request.urlopen(articleUrl)
    while articlehandle.getcode() != 200:
        articlehandle = urllib.request.urlopen(articleUrl)
    soup = bs(articlehandle.read(), 'html.parser')
    falist = soup.find_all('span',class_='art_header_footer_author')
    try:
        title = soup.find('h1',class_='art_header_title').contents[0]
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
    url = f'https://www.ynet.co.il/home/0,7340,L-{lcode}-20{year}{str(month).zfill(2)}-{page},00.html'
    filehandle = urllib.request.urlopen(url)
    error = False
    while error or filehandle.getcode() != 200:
        error = False
        try:
            filehandle = urllib.request.urlopen(url)
        except:
            error = True
    soup = bs(filehandle.read(), 'html.parser')
    table = soup.find('td', class_='ghciArticleIndex1').contents[2]
    articles = len(table.contents)
    retval = []
    if articles > 1:
        for i in range(int(articles/3)):
            link = table.contents[3 * i].find('a')
            metadata = table.contents[3 * i + 1].string.split(' ')
            dates = metadata[-1].replace('(', '').replace(')','').split('/')
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

# @multitasking.task
def parse_range(start_year, end_year, lcode, writer, name):
    columns=[
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
            print(name[::-1], 'Month ', j, '/', '20' + str(i), 'finished at', time.time() - start_time)
    DFrame = pd.DataFrame(df, columns=columns)
    print(DFrame)
    DFrame.to_excel(writer, sheet_name=name, index=False, verbose=True)
    # DFrame.to_csv(path_or_buf=writer, index=False)

start_time = time.time()
first_time = start_time

@multitasking.task
def politics():
    with pd.ExcelWriter('politics.xlsx') as writer:
        parse_range(15, 21, '4269-890-315', writer, 'מדיני')
        parse_range(15, 21, '4269-891-317', writer, 'המערכת הפוליטית')
        parse_range(15, 21, '4269-109-185', writer, 'פוליטי מדיני')

@multitasking.task
def army():
    with pd.ExcelWriter('army.xlsx') as writer:
        parse_range(15, 21, '4269-141-344', writer, 'צבא וביטחון')
        parse_range(15, 21, '4269-3259-4172', writer, 'פלסטינים')
        parse_range(15, 21, '4269-3602-4502', writer, 'רון בן ישי')

@multitasking.task
def economics():
    with pd.ExcelWriter('economics.xlsx') as writer:
        parse_range(15, 21, '4269-116-429', writer, 'כלכלה בארץ')
        parse_range(15, 21, '4269-117-430', writer, 'כלכלה בעולם')
        parse_range(15, 21, '4269-118-431', writer, 'הייטק')
        parse_range(15, 21, '4269-271-750', writer, 'מיוחד')
        parse_range(15, 21, '4269-583-1336', writer, 'בורסה')
        parse_range(15, 21, '4269-3757-5363', writer, 'צרכנות')
        parse_range(15, 21, '4269-3751-6567', writer, 'מטבח חוץ')
        parse_range(15, 21, '4269-3747-7615', writer, 'הכסף שלי')
        parse_range(15, 21, '4269-3749-8091', writer, 'קריירה')
        parse_range(15, 21, '4269-3755-8315', writer, 'נדלן')

politics()
army()
economics()