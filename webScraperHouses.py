import requests
from bs4 import BeautifulSoup

from rich.console import Console
from rich.table import Table
from tkinter import *
import statistics
from rich.prompt import Prompt
from progress.bar import Bar

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
url = 'https://www.point2homes.com/CA/Real-Estate-Listings/' + province + '/' + city + '.html?location=' + city +'%2C+' +  province +' &PropertyType=' + house +'&search_mode=location&SelectedView=listings&page='
url_ = 'https://www.point2homes.com/CA/Real-Estate-Listings/NB/Fredericton.html?location=Fredericton%2C+NB&PropertyType=CondoApartment&search_mode=location&page=1&SelectedView=listings&location_changed=&ajax=1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    ,'Cache-Control': 'no-cache'}

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
Average_Price = total / len(prices)

property_table = Table()
property_table.add_column('[bold green]city[/bold green]', style="bold cyan")
property_table.add_column("Average Price")
property_table.add_column("Median Price")
property_table.add_column("Sample Size")

property_table.add_row('[bold cyan]' + city + '[/bold cyan]', "[bold red]" + str(Average_Price),
                       str(statistics.median(prices)), str(len(prices)))

console.print(property_table)
