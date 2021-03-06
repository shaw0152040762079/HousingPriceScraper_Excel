import requests
from bs4 import BeautifulSoup

from rich.console import Console
from rich.table import Table
from tkinter import *
import statistics
from rich.prompt import Prompt
from progress.bar import Bar
import sqlite3
from datetime import date

console = Console()

house = Prompt.ask(
    "What kind of house are you look for ? enter the corresponding code",
    choices=["House", 'CondoApartment', 'RowTownhouse']
)

province = Prompt.ask(
    "What province are you looking in? enter the corresponding code",
    choices=["ON", "QC", 'AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'PE', 'SK', 'YT']
)

city = Prompt.ask(
    "Please Enter the city",
)

prices = []
url = 'https://www.point2homes.com/CA/Real-Estate-Listings/' + province + '/' + city + '.html?location=' + city + '%2C+' + province + '&PropertyType=' + house + '&search_mode=location&SelectedView=listings&page='
url_ = 'https://www.point2homes.com/CA/Condos-For-Sale/' + province + '/' + city + '.html?page='
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    , 'Cache-Control': 'no-cache'}

num_page = int(input("Enter the number of pages you want to scrape "))

print(num_page)
for i in range(num_page):
    page = requests.get(url + str(i), headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    print(url + str(i))

    with Bar('Downloading new page', fill='@', suffix='%(percent).1f%% - %(eta)ds') as bar:
        for spanclass in soup.findAll(class_="green"):
            bar.next(3.5)
            for span in spanclass.findAll('span'):
                priceOfHouse = re.findall(r'\d+(?:,\d+)+(?:,\d+)?', str(span))
                prices.append(int(priceOfHouse[0].replace(',', '')))

print('/n')

total = sum(prices)

print(prices.sort())
average_price = total / len(prices)

property_table = Table()
property_table.add_column('[bold green]city[/bold green]', style="bold cyan")
property_table.add_column("House Type")
property_table.add_column("Average Price")
property_table.add_column("Median Price")
property_table.add_column("Sample Size")

property_table.add_row('[bold cyan]' + city + '[/bold cyan]', house, "[bold red]" + str(average_price),
                       str(statistics.median(prices)), str(len(prices)))

console.print(property_table)

print(prices)

save = Prompt.ask(
    "Do you want to save this to the SQLlite database?",
    choices=["Y", 'N']
)

conn = sqlite3.connect('example.db')
c = conn.cursor()

if save == "Y":
    today = date.today()

    c.execute('''CREATE TABLE IF NOT EXISTS House_Prices (
    City text,
    House_Type  text,
    Average Integer,
    Median Integer,
    Sample_Size Integer,
    Current_Date Date
    );''')

    # Insert a row of data
    c.execute("INSERT INTO House_Prices VALUES(?,?,?,?,?,?)", (city, house, str(average_price),
                                                               str(statistics.median(prices)), str(len(prices)),
                                                               str(today)))
    # Save (commit) the changes
    conn.commit()

excel = Prompt.ask(
    "Would you like an Excel with all the historical data?",
    choices=["Y", 'N']
)

if excel == "Y":
    from xlsxwriter.workbook import Workbook

    workbook = Workbook('Output.xlsx')
    worksheet = workbook.add_worksheet()

    heads = ["City", "Type_Of_House", "Average", "Median", "Sample_Size", "Date"]
    for i in range(len(heads)):
        worksheet.write(0, i, heads[i])

    mysel = c.execute("select * from House_prices ")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i + 1, j, row[j])
    workbook.close()
    conn.close()
