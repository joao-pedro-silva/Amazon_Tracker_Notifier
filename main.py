import requests
from bs4 import BeautifulSoup
import smtplib
from variables import email, password, user_agent, email_from, email_to, stipulated_price, url
import time
import pandas as pd
from datetime import datetime


class AmazonTracker:

    def __init__(self, url, headers):
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser',)
        # Gets the product's Name by it's id
        product_title = str(soup.find(id="productTitle").getText().strip())
        print('Product:', product_title)
        # Gets the product's Price by it's id
        self.product_price = str(soup.find(id="priceblock_ourprice").getText())
        print('Price:', self.product_price)

    def check_price(self, stipulated_price):
        # List of Prices
        price_list = []
        # List of times when prices were save
        time_list = []

        # Clean product_price variable
        product_price = self.product_price.replace('£', '')
        converted_price = float(product_price)

        # While loop checks if product price is bellow the price stipulated
        while converted_price > stipulated_price:
            # Gets time when price was saved and adds it to the time_list
            now = datetime.now()
            date_time = now.strftime("%d/%m/%Y %H:%M:%S")
            time_list.append(date_time)
            print('Time: ', time_list)

            # Gets price and adds it to the price_list
            price_list.append(converted_price)
            print('Price', price_list)

            # Generate dataframe from list and write to xlsx.
            df = pd.DataFrame({'Time': time_list, 'Price': price_list})
            writer = pd.ExcelWriter('amazon_price_list.xlsx', engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1')
            writer.save()

            # Frequence of price check
            time.sleep(5)

        # If price drops bellow stipulated price calls method send_email()
        self.send_email()


    def send_email(self):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo() #command sent by email to identify itself when connecting to another email
        server.starttls() #incript  connection
        server.ehlo()
        server.login(email, password)

        # Email composition
        subject = 'Price Alert!'
        body = ('Price Feel Down! \n\nClick link to check: ' + url)
        msg = f"Subject: {subject}\n\n{body}"

        # Send Email
        server.sendmail(email_from, #from
                        email_to, #to
                        msg) #email
        print('Email sent!')
        # Shuts server
        server.quit()


headers = {"User-Agent": user_agent}
amazon_tracker = AmazonTracker(url, headers)
amazon_tracker.check_price(stipulated_price)
