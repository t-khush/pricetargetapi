#https://www.youtube.com/watch?v=JBGC9Dp9cXI&t=556s&ab_channel=JacobKoehler
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
import re
import bs4
from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine
from datetime import datetime 


app = Flask(__name__)
api = Api(app)
CORS(app)

engine = create_engine('sqlite:///StockTickers.db')

def scrape(stock_name):
    connection = engine.connect(); 
    try: 
        url = "https://money.cnn.com/quote/forecast/forecast.html?symb={t}".format(t = stock_name)
        r = requests.get(url) 
        soup = BeautifulSoup(r.content, 'html.parser')
            
        x = soup.find('div', class_='wsod_twoCol clearfix')
        str = x.text
        str = str.replace(',', '')

        set = re.findall('\d*\.?\d+',str)
        analysts = set[0]
        median = float(set[2])
        high = float(set[3]) 
        low = float(set[4])
        buyOrSell = soup.find('span', class_ = 'wsod_rating')
        name  = soup.find('h1', class_ = 'wsod_fLeft')
        query = "DELETE FROM stocks WHERE ticker = '{st}'".format(st = stock_name)
        connection.execute(query) 
        query = "INSERT INTO stocks(ticker, company, low, median, high, analysts, date, buysell) VALUES('{sName}', '{name}', {lPrice}, {medPrice}, {highPrice}, {aCount}, '{d}', '{bS}')".format(sName = stock_name, name = name.text, lPrice = low, medPrice = median, highPrice = high, aCount= analysts, bS = buyOrSell.text, d = datetime.now())
        connection.execute(query)
    except: 
        return -1


class getData(Resource): 

    def get(self): 
        connection = engine.connect() 
        stock_name = request.args.get("stock")

        if(connection.execute("SELECT * FROM stocks WHERE ticker='"+stock_name+"' AND date('now','-3 day')").fetchone() is None): 
            if(scrape(stock_name)==-1): 
                return {"404": "Error"}
        query = "SELECT * FROM stocks WHERE ticker = '{s}'".format(s = stock_name) 
        query = connection.execute(query) 
        return{
            stock_name : [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
        }

api.add_resource(getData, "/getData")

if(__name__=="__main__"):
    app.run(debug=True)