import requests
from bs4 import BeautifulSoup

from rich.console import Console
from rich.table import Table
from tkinter import *
import statistics
from rich.prompt import Prompt
import progressbar
import time, sys
from time import sleep
from progress.bar import Bar

console = Console()


house = Prompt.ask(
    "What Kind of House are you look for? enter the type",
    choices=["CondoApartment", "House", "RowTownhouse", ]
)

Province = Prompt.ask(
    "What province are you looking in? enter the corresponding code",
    choices=["ON", "QC", 'AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'PE', 'SK', 'YT']
)

City = Prompt.ask(
    "Please Enter the City",
)

prices = []
url = 'https://www.point2homes.com/CA/Real-Estate-Listings/' + Province + '/' + City + '.html?location=Ottawa,%20ON&PropertyType=' + house + '&search_mode=location&SelectedView=listings&LocationGeoId=783093&page='
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

# may need to change URL if throttled!!!
page = requests.get(url,headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')
number_of_houses = soup.find(id="search_history_form")
number = number_of_houses.find(id='search-history-results')

pages = int(int(number['value']) / 24)

for i in range(pages):
    page = requests.get(url + str(i),headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    pagenum = 1
    with Bar('Downloading new page', fill='@', suffix='%(percent).1f%% - %(eta)ds') as bar:
        for spanclass in soup.findAll(class_="green"):
            sleep(0.01)
            pagenum+=1
            bar.next(3)
            for span in spanclass.findAll('span'):
                priceOfHouse = re.findall(r'\d+(?:,\d+)+(?:,\d+)?', str(span))
                prices.append(int(priceOfHouse[0].replace(',', '')))


print('/n')
total = 0
for price in prices:
    total += price

print(prices.sort())
Average_Price = total / len(prices)

property_table = Table()
property_table.add_column('[bold green]City[/bold green]', style="bold cyan")
property_table.add_column("House Type")
property_table.add_column("Average Price")
property_table.add_column("Median Price")
property_table.add_column("Sample Size")

property_table.add_row(City, '[bold cyan]' + house + '[/bold cyan]', "[bold red]" + str(Average_Price),
                       str(statistics.median(prices)), str(len(prices)))

console.print(property_table)
