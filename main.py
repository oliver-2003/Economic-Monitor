from bs4 import BeautifulSoup
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import pandas as pd
import pymysql
import randHeaderProxy
import re
import requests
import schedule
import time
import win32com.client as win32


class EconomicMonitor:
    # The class attributes describe a database and the target email address for receiving reports
    host = "localhost"
    port = 3306
    user = ""
    passwd = ""
    db = ""
    email_address = ""
    watch_list = []
    table_list = ["commodity_prices", "exchange_rates", "market_indices", "bond_yields", "stock_prices"]

    def __init__(self, host, port, user, passwd, email_address, db="economic_monitor"):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.email_address = email_address
        self.db = db

    # Use pymysql to generate a mySQL database connection
    def get_database_connection(self):
        db = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)

        return db

    # Insert into the database certain data
    def data_to_sql(self, table, data):
        database = self.get_database_connection()
        sql = f"INSERT INTO  {table} VALUES(DEFAULT, {data}, CURDATE(), CURTIME())"
        database.query(sql)
        database.commit()

    # Get the exchange rates of major currencies
    def get_exchange_rate(self):
        table = 'exchange_rates'

        url = 'https://www.x-rates.com/table/?from=USD&amount=1'
        headers = randHeaderProxy.get_random_agent()
        proxy = randHeaderProxy.get_random_proxy()
        res = requests.get(url, headers=headers, proxies=proxy)

        currency_name = re.findall("""<tr>
						<td>(.*?)</td>
						<td class='rtRates'>""", res.text, re.S)
        # Use regular expression to get the exchange rates, keeping 4 decimal places
        exchange_rate = re.findall(r"to=USD'>\d\.\d\d\d\d", res.text, re.S)

        # Discard currencies with exchange rates that are very small, and then insert the remaining data into the data table
        for i in range(len(currency_name)):
            valid_exchange_rate = float(exchange_rate[i].split('>')[1])
            if valid_exchange_rate >= 0.00001:
                data = f'"{currency_name[i]}", "{valid_exchange_rate}"'
                self.data_to_sql(table, data)

    def get_stock_price(self):
        table = 'stock_prices'

        # Get stock information from both New York Stock Exchange and NASDAQ Stock Exchange
        stock_exchange_list = [
            f'https://www.centralcharts.com/en/price-list-ranking/ALL/asc/ts_29-us-nyse-stocks--qc_1-alphabetical-order?p=',
            f'https://www.centralcharts.com/en/price-list-ranking/ALL/asc/ts_19-us-nasdaq-stocks--qc_1-alphabetical-order?p=']
        # Construct the URL list with page numbers
        url_list = [stock_exchange + str(page_num) for stock_exchange in stock_exchange_list for page_num in range(1, 160)]

        headers = randHeaderProxy.get_random_agent()
        proxies = randHeaderProxy.get_random_proxy()
        for url in url_list:
            res = requests.get(url, headers=headers, proxies=proxies)
            soup = BeautifulSoup(res.text, 'html.parser')
            try:
                # Find the name of the stock exchange by scraping the h1 tag
                stock_exchange = soup.find("h1").text.split(" p")[0].strip()
            except IndexError:
                continue

            stock_info = soup.find_all('tr')[1:]
            for stock in stock_info:
                try:
                    # Get rid of extra spacing and commas in each data value
                    stock_name = stock.find('a').text
                    stock_price = float(stock.find_all('span')[0].text.strip().replace(',', ''))
                    open_price = float(stock.find_all('span')[2].text.strip().replace(',', ''))
                    high_price = float(stock.find_all('span')[3].text.strip().replace(',', ''))
                    low_price = float(stock.find_all('span')[4].text.strip().replace(',', ''))
                    data = f'"{stock_name}", "{stock_exchange}", "{stock_price}", "{open_price}", "{low_price}", "{high_price}"'
                    self.data_to_sql(table, data)
                except ValueError:
                    continue

    def get_bond_yield(self):
        table = 'bond_yields'

        url = 'https://tradingeconomics.com/bonds'
        headers = randHeaderProxy.get_random_agent()
        proxy = randHeaderProxy.get_random_proxy()

        res = requests.get(url, headers=headers, proxies=proxy)
        soup = BeautifulSoup(res.text, 'html.parser')
        bond_info = soup.find_all('tr')
        # Start from the 20th row to skip the table of bond yields of major countries
        for bond in bond_info[19:]:
            try:
                country_name = bond.find_all('td')[1].text.replace('\n', '').replace('\r', '').strip()
                bond_yield = float(bond.find_all('td')[2].text.replace('\n', '').replace('\r', '').strip().strip().replace(',', ''))
                data = f'"{country_name}", "{bond_yield}"'
                self.data_to_sql(table, data)
            except IndexError:
                continue

    def get_indices(self):
        table = 'market_indices'

        url = 'https://markets.businessinsider.com/indices'
        headers = randHeaderProxy.get_random_agent()
        proxy = randHeaderProxy.get_random_proxy()

        res = requests.get(url, headers=headers, proxies=proxy)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Start from the second row to skip the header of the table
        indices = soup.find_all('tr')[1:]
        for index in indices:
            try:
                index_name = index.find_all('td')[0].text.split('\n')[1]
                region_name = index.find_all('td')[0].text.split('\n')[2].strip()
                index_value = float(index.find_all('td')[1].text.split('\n')[1].strip().replace(',', ''))
                close_value = float(index.find_all('td')[1].text.split('\n')[2].strip().replace(',', ''))
                data = f'"{region_name}", "{index_name}", "{index_value}", "{close_value}"'
                self.data_to_sql(table, data)
            except IndexError:
                continue

    def get_commodity_price(self):
        table_name = 'commodity_prices'

        url = 'https://tradingeconomics.com/commodities'
        headers = randHeaderProxy.get_random_agent()
        proxy = randHeaderProxy.get_random_agent()

        res = requests.get(url, headers=headers, proxies=proxy)
        soup = BeautifulSoup(res.text, 'html.parser')
        tables = soup.find_all('table')
        for data_table in tables:
            # The category of the commodity is located at the first row and first column
            category = data_table.find_all('tr')[0].find_all('th')[0].text.strip()
            # Start from the second row to skip the header of the table
            bond_info = data_table.find_all('tr')[1:]
            for bond in bond_info:
                try:
                    commodity_name = bond.find('a').text.strip()

                    if "Electricity" in category:
                        commodity_name += " Electricity"

                    commodity_price = float(bond.find_all('td')[1].text.replace('\n', '').replace('\r', '').strip().replace(',', ''))
                    data = f'"{commodity_name}", "{commodity_price}", "{category}" '
                    self.data_to_sql(table_name, data)
                except IndexError:
                    continue

    def read_sql_change_query(self, table, interval=1):
        db = self.get_database_connection()
        query = f"""
        SELECT 
        DISTINCT(t1.name),
        t1.value AS current_value, 
        t2.value AS previous_value, 
        t1.value - t2.value AS growth, 
        t1.record_date 
        FROM {table} t1 
        JOIN {table} t2 USING (name) 
        WHERE (t1.record_date = CURDATE()) AND (t2.record_date = DATE_SUB(CURDATE(), INTERVAL {interval} DAY))  
        ORDER BY t1.record_date, t1.name"""
        # The above SQL code selects all unique items in a single table and compares the value of each with the value of "interval" days ago (By default it compares with yesterday)

        df = pd.read_sql(query, db)
        # Extract the data from the table as a Pandas Data Frame

        return df

    def send_email(self, subject, content, path):
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = self.email_address
        mail.Subject = subject
        mail.HTMLBody = content
        file_names = os.listdir(path)
        # Get the path of the data graphs
        current_path = os.getcwd()
        for file_name in file_names:
            mail.Attachments.Add(fr"{current_path}\{path}\{file_name}")

            # Attach all graphs in the target directory to the email
        mail.Send()

    @staticmethod
    def delete_files(dir_path):
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
    # Delete all graphs in the target directory

    def watch_list_generator(self):
        limit = 4
        to_stop = False
        self.watch_list.append(input("Pleaser enter the name of the table: "))
        self.watch_list.append(input("Pleaser enter the name of the item: "))
        while not (to_stop and limit == 0):
            to_stop = input("To add more items, please enter 'y', or enter anything else to break: ").lower()
            if to_stop == "y":
                self.watch_list.append(input("Pleaser enter the name of the item: "))
                limit -= 1
            else:
                break
        watch_list = tuple(self.watch_list)

        return watch_list
        # The function above returns a manually set watchlist of different items with a limit number of 5

    def daily_list_generator(self, interval=1):
        name_list = []
        for table in self.table_list[0:4]:
            # The table stock_prices is excluded here because the datatable is too large and matplotlib cannot handle too many graphs at once.
            df = self.read_sql_change_query(table, interval)
            # Compare the current value of the items with that of the last day
            for row in df.index:
                change_rate = (df.loc[row]["current_value"] - df.loc[row]["previous_value"]) / df.loc[row]["previous_value"]
                # Set a new column for percentage change in values of the items
                if abs(change_rate) > 0.03:
                    name_list.append([table, df.loc[row]["name"], df.loc[row]["previous_value"], df.loc[row]["current_value"], change_rate])
                    # If the percentage change is greater than 1%, append the item into the namelist
            if len(name_list) < 1:
                for row in df.index:
                    change_rate = (df.loc[row]["current_value"] - df.loc[row]["previous_value"]) / df.loc[row]["previous_value"]
                    name_list.append([table, df.loc[row]["name"], df.loc[row]["previous_value"], df.loc[row]["current_value"], change_rate])
            # If no item shows significant change, record all changed items in the namelist

        return name_list

    def weekly_watchlist_generator(self):
        name_list = self.daily_list_generator(interval=7)
        # By setting the interval to be 7, the function compares value of items with that of a week ago

        return name_list

    @staticmethod
    def get_directory():
        daily_graphs = "dailyGraphs"
        weekly_graphs = "weeklyGraphs"
        os.makedirs(daily_graphs, exist_ok=True)
        os.makedirs(weekly_graphs, exist_ok=True)
    # Create two directories to contain graphs of daily and weekly reports separately

    def graph_generator(self, watchlist=None, table=None, path=None):
        self.get_directory()
        # Generate the directories to contain daily and weekly graphs
        start_point = 0
        path = path

        if watchlist is None:
            watchlist = self.watch_list_generator()
            table = watchlist[0]
        # If no watchlist is passed in, a watchlist can be manually generated
        elif isinstance(watchlist[0], list):
            for i in watchlist:
                table = i[0]
                self.graph_generator(tuple(i), table=table, path=path)
            # If a watchlist generated by daily or weekly watchlist generator is passed in, the recursion above will graph each item in the list
            return watchlist
            # After the recursion of all items in the watchlist, the function should stop

        if path == "dailyGraph":
            duration = 7
            interval = 1
        # If a daily watchlist is passed in, the function should graph the changes of each day (interval=1) in 7 days (duration=7)
        else:
            duration = 30
            interval = 7
        # If a weekly watchlist is passed in, the function should graph the changes in value once a week (interval=7) in 30 days (duration=30)

        db = self.get_database_connection()
        query = f"""
        SELECT 
        DISTINCT record_date, 
        name, 
        value 
        from {table} 
        WHERE name in {watchlist} AND record_date BETWEEN DATE_SUB(CURDATE(),  INTERVAL {duration} DAY ) AND CURDATE()
        ORDER BY name"""
        df = pd.read_sql(query, db)

        count_unique_date = df["record_date"].value_counts()
        count_unique_name = df["name"].value_counts()
        group_number = count_unique_date[0]
        num_items = count_unique_name[0]
        dates = df.loc[0:num_items - 1, ["record_date"]]
        # Get unique record_dates as the x-axis
        fig = plt.figure()
        sub = fig.add_subplot(1, 1, 1)
        # Using subplot allows graphing multiple items in one graph
        for i in range(group_number):
            sub.plot(dates, df.loc[start_point:start_point + num_items - 1, ["value"]], "--o", label=df.iloc[start_point, 1])
            # Graph the values of each item under all dates
            start_point += num_items
            # Move to next item

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
        # Set the format of the x-axis to be date and alter the scale of the x-axis based on daily or weekly graphs
        fig.autofmt_xdate()
        plt.title(table.replace("_", " ").upper())
        plt.legend(loc="best")
        plt.savefig(f'{path}/{table}_{df.loc[0]["name"]}.png')
        # Save graphs to the target directory

    def message_generator(self, message_type=0):
        if message_type == 0:
            name_list = self.daily_list_generator()
            path = "dailyGraphs"
            subject = "Daily Report"
        else:
            name_list = self.weekly_watchlist_generator()
            path = "weeklyGraphs"
            subject = "Weekly Report"
        watch_list = self.graph_generator(watchlist=name_list, path=path)
        content = f"""
                   <table table border="1" cellspacing="0" cellpadding="0" width="100%" >
                      <tr>
                          <th style="color: white;" bgcolor="191970">Category</th>
                          <th style="color: white;" bgcolor="191970">Name</th>
                          <th style="color: white;" bgcolor="191970">Previous Value</th>
                          <th style="color: white;" bgcolor="191970">Current Value</th>
                          <th style="color: white;" bgcolor="191970">Percentage Change</th>
                      </tr>
                 """
        # Use HTML to generate a table

        for item in watch_list:
            data = f""" <tr>
                   <td style="text-align:center" >{item[0]}</td>
                   <td style="text-align:center" >{item[1]}</td>
                   <td style="text-align:center" >{item[2]}</td>
                   <td style="text-align:center" >{item[3]}</td>
                   <td style="text-align:center" >{str(format(item[4] * 100, '.3f')) + "%"}</td>
               </tr>"""
            content += data
        content += "</table>"
        # Append all table rows
        self.send_email(subject, content, path)
        self.delete_files(path)

    def data_collection(self):
        self.get_exchange_rate()
        # self.get_stock_price()
        self.get_indices()
        self.get_bond_yield()
        self.get_commodity_price()


monitor = EconomicMonitor("localhost", 3306, "root", "123456", "economicmonitor@gmail.com")
# Generate an EconomicMonitor object with the database host being "localhost", port being 3306, user being "root", passwd being "123456", and the email address receiving reports being "economicmonitor@gmail.com"


def daily_message_generator():
    monitor.message_generator(message_type=0)


def weekly_message_generator():
    monitor.message_generator(message_type=1)


schedule.every().day.do(monitor.data_collection)
schedule.every().day.do(daily_message_generator)
# Collect data and generate daily report everyday
schedule.every().week.do(weekly_message_generator)
# Generate weekly report every week

while True:
    schedule.run_pending()
    time.sleep(1)
