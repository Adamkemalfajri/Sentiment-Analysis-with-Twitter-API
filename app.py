#Humam    humamahb@gmail.com

import tweepy
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import sqlite3

consumer_key = 'A9flvCFoZMY1oJgnSOGiWtUqx'
consumer_secret = 'Y8WBUoNcYT1dYZyadmhmjHdeA3QNPd7ECmgeFRwRXgagaSN1On'
access_token = '1011919448775593984-uVnMhUrVZVJjvbgapOnjbvGBSn60tQ'
access_token_secret = 'fN9yfleqEYRkx8ddyUet8VhsyqpMiEjiRa4qSzYwGjRDW'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def Check(search_words):
    date = datetime.today() - timedelta(days=2)
    date_since = date.strftime('%Y-%m-%d')
    new_search = search_words + " -filter:retweets"

    tweets = tweepy.Cursor(api.search,
            q=new_search,
            lang="id",
            since=date_since).items(1000)
            
    items = []
    for tweet in tweets:
        item = []
        item.append (tweet.user.screen_name)
        date = tweet.created_at
        newdate = date.strftime('%Y-%m-%d')
        item.append(newdate)
        item.append (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet.text).split()))
        items.append(item)
    hasil = pd.DataFrame(data=items, columns=['user','date','tweet'])
    return(hasil)

def connect():
    return sqlite3.connect("tugasakhir.db")

def create_table(table_query):
    conn = connect()
    with conn:
      cursor = conn.cursor()
      cursor.execute(table_query)
      conn.commit()
      cursor.close()
 
def data_entry(crud_query, input_list):
    conn = connect()
    with conn:
      cursor = conn.cursor()
      cursor.executemany(crud_query, input_list)
      conn.commit()
      cursor.close()

def fungsi1():
    df = Check("vaksin covid")
    input_list = (df.values.tolist())
    table_query = '''CREATE TABLE IF NOT EXISTS tugasakhir(User TEXT NOT NULL, 
                                                      Date TEXT NOT NULL, 
                                                      Tweet TEXT NOT NULL);'''
                                                      

    crud_query = '''INSERT INTO tugasakhir (User, Date, Tweet) 
                              VALUES(?, ?, ?);'''
    create_table(table_query)
    data_entry(crud_query, input_list)

def Sentimen():
    conn = connect()

    df = pd.read_sql_query("SELECT * FROM tugasakhir", conn)
    sentiment = df[['Tweet']]
    date = df[['Date']]
    user = df[['User']]

    pos_list= open("kata_positif.txt","r")
    pos_kata = pos_list.readlines()
    neg_list= open("kata_negatif.txt","r")
    neg_kata = neg_list.readlines()
    
    items = sentiment.values.tolist()
    
    S=[]
    for item in items:
        count_p = 0
        count_n = 0
        for kata_pos in pos_kata:
            if kata_pos.strip() in item[0]:
                count_p +=1
        for kata_neg in neg_kata:
            if kata_neg.strip() in item[0]:
                count_n +=1
        S.append(count_p - count_n)
    

    hasil = pd.DataFrame(data=S, columns=['Sentimen'])
    result = pd.concat([date,user,sentiment,hasil], axis=1, sort=False)
    return(result)

def fungsi2():
    df = Sentimen()
    input_list = df.values.tolist()
    table_query = '''CREATE TABLE IF NOT EXISTS sentimen(Date TEXT NOT NULL,
                                                        User TEXT NOT NULL,
                                                        Tweet TEXT NOT NULL,
                                                        Sentimen INTEGER NOT NULL);'''
                                                      
    crud_query = '''INSERT INTO sentimen (Date, User, Tweet, Sentimen) 
                              VALUES(?,?,?,?);'''
    create_table(table_query)
    data_entry(crud_query, input_list)

def fungsi3():
    conn = connect()
    cursor = conn.cursor()
    column = 'Date, User, Tweet'
    goal = 'Date'
    print('Input Range Tanggal dalam format YYYY-mm-dd (contoh: 2020-08-14)')

    date = input('Dimulai pada tanggal= ')
    date2 = input('Hingga tanggal= ')

    cursor.execute("SELECT "+column+" FROM sentimen where "+goal+" BETWEEN ? AND ?", (date, date2))
    rows = cursor.fetchall()
    S = []
    for row in rows:
        S.append(row)
    df = pd.DataFrame(data=S, columns=['date','user','tweet'])

    print(df)

def fungsi4():
    conn = connect()
    cursor = conn.cursor()
    column = 'Sentimen'
    goal = 'Date'

    date = input('Dimulai pada tanggal= ')
    date2 = input('Hingga tanggal= ')

    cursor.execute("SELECT "+column+" FROM sentimen where "+goal+" BETWEEN ? AND ?", (date, date2))
    rows = cursor.fetchall()
    S = []
    for row in rows:
        S.append(row)
        
    hasil = pd.DataFrame(data=S, columns=['value'])
    print ("Nilai rata-rata: "+str(np.mean(hasil["value"])))
    print ("Median: "+str(np.median(hasil["value"])))

    labels, counts = np.unique(hasil["value"], return_counts=True)
    plt.bar(labels, counts, align='center')
    plt.gca().set_xticks(labels)
    plt.show()
    return

x = 0

while x != '5':
    print('Apa yang ingin anda lakukan? \n 1. Update Data \n 2. Update Nilai Sentiment \n 3. Lihat Data \n 4. Visualisasi \n 5. Keluar \n Input Anda:')
    x = input()

    if x == '1':
        print('SEDANG MENJALANKAN FUNGSI 1...')
        fungsi1()
        print('FUNGSI 1 SELESAI DIJALANKAN')
    elif x == '2':
        print('SEDANG MENJALANKAN FUNGSI 2...')
        fungsi2()
        print('FUNGSI 2 SELESAI DIJALANKAN')
    elif x == '3':
        fungsi3()
        print('FUNGSI 3 SELESAI DIJALANKAN')
    elif x == '4':
        fungsi4()
        print('FUNGSI 4 SELESAI DIJALANKAN')

print('Selesai')