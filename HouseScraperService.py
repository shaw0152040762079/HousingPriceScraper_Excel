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


class Housing:
    console = Console()
    house = ''
    province = ''
    city = ''
    num_page=0
    url = 'https://www.point2homes.com/CA/Real-Estate-Listings/' + province + '/' + city + '.html?location=' + city + '%2C+' + province + '&PropertyType=' + house + '&search_mode=location&SelectedView=listings&page='

    total = 0
    average_price = 0


    prices = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        , 'Cache-Control': 'no-cache'}

    def get_info(self):
        Housing.house = Prompt.ask("What kind of house are you look for ? enter the corresponding code",
                                   choices=["House", 'CondoApartment', 'RowTownhouse']
                                   )
        Housing.province = Prompt.ask(
            "What province are you looking in? enter the corresponding code",
            choices=["ON", "QC", 'AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'PE', 'SK', 'YT']
        )
        Housing.city = Prompt.ask(
            "Please Enter the city",
        )
        Housing.url = 'https://www.point2homes.com/CA/Real-Estate-Listings/' + Housing.province + '/' + Housing.city + '.html?location=' + Housing.city + '%2C+' + Housing.province + '&PropertyType=' + Housing.house + '&search_mode=location&SelectedView=listings&page='

    def get_page_num(self):
        Housing.num_page = int(input("Enter the number of pages you want to scrape "))


    print(num_page)
    def scrape(self):
        for i in range(Housing.num_page):
            page = requests.get(Housing.url + str(i+1), headers=Housing.headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            print(Housing.url + str(i+1))

            with Bar('Downloading new page', fill='@', suffix='%(percent).1f%% - %(eta)ds') as bar:
                for spanclass in soup.findAll(class_="green"):
                    bar.next(3.5)
                    for span in spanclass.findAll('span'):
                        priceOfHouse = re.findall(r'\d+(?:,\d+)+(?:,\d+)?', str(span))
                        Housing.prices.append(int(priceOfHouse[0].replace(',', '')))

        print('/n')

        Housing.total = sum(Housing.prices)

        print(Housing.prices.sort())
        Housing.average_price = Housing.total / len(Housing.prices)

        property_table = Table()
        property_table.add_column('[bold green]city[/bold green]', style="bold cyan")
        property_table.add_column("House Type")
        property_table.add_column("Average Price")
        property_table.add_column("Median Price")
        property_table.add_column("Sample Size")

        property_table.add_row('[bold cyan]' + Housing.city + '[/bold cyan]', Housing.house, "[bold red]" + str(Housing.average_price),
                           str(statistics.median(Housing.prices)), str(len(Housing.prices)))

        Housing.console.print(property_table)
        print(Housing.prices)

    def db_option(self):
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
            c.execute("INSERT INTO House_Prices VALUES(?,?,?,?,?,?)",
                      (Housing.city, Housing.house, str(Housing.average_price),
                       str(statistics.median(Housing.prices)), str(len(Housing.prices)),
                       str(today)))
            # Save (commit) the changes
            conn.commit()

    def excel_option(self):

        excel = Prompt.ask(
            "Would you like an Excel with all the historical data?",
            choices=["Y", 'N']
        )

        if excel == "Y":
            from xlsxwriter.workbook import Workbook

            workbook = Workbook('Output.xlsx')
            worksheet = workbook.add_worksheet()

            conn = sqlite3.connect('example.db')
            c = conn.cursor()

            heads = ["City", "Type_Of_House", "Average", "Median", "Sample_Size", "Date"]
            for i in range(len(heads)):
                worksheet.write(0, i, heads[i])

            mysel = c.execute("select * from House_prices ")
            for i, row in enumerate(mysel):
                for j, value in enumerate(row):
                    worksheet.write(i + 1, j, row[j])
            workbook.close()
            conn.close()
