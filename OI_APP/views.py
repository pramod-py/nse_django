from django.shortcuts import render

import requests
import pandas as pd
# import time
# import matplotlib.pyplot as plt
# import seaborn as sns
# import time
from datetime import datetime

# Create your views here.



def fetch_option_chain_data():
    base_url = "https://www.nseindia.com/"
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'accept-language': 'en,gu;q=0.9,hi;q=0.8',
        'accept-encoding': 'gzip, deflate, br'
    }

    session = requests.Session()
    request = session.get(base_url, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    response = session.get(url, headers=headers, timeout=5, cookies=cookies)

    if response.status_code == 200:
        raw_data = response.json()
        raw_option_data = pd.DataFrame(raw_data['records']['data']).fillna(0)
        return raw_option_data
    else:
        print("Failed to fetch data from NSE.")
        return None

def load_data():
  baseurl = "https://www.nseindia.com/"
  url = f"https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
  headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         'like Gecko) '
                         'Chrome/80.0.3987.149 Safari/537.36',
           'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
  session = requests.Session()
  try:
    request = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    response = session.get(url, headers=headers, timeout=5, cookies=cookies)
    response.raise_for_status()  # Raise an exception for HTTP errors (optional)
    # Process the response here
  except requests.exceptions.ReadTimeout:
      # Handle the ReadTimeout exception here
      print("Request timed out. Please check your internet connection or try again later.")
      error = "Request timed out. Please check your internet connection or try again later."
      context = {'error':error, 'option_data':None}
      return render(request, 'index.html', context)
  except requests.exceptions.RequestException as e:
      # Handle other request-related exceptions here
      print(f"An error occurred: {e}")
      error = f"An error occurred: {e}."
      context = {'error':error, 'option_data':None}
      return render(request, 'index.html', context)
  
  rawdata = pd.DataFrame(response.json())
  rawop=pd.DataFrame(rawdata['filtered']['data']).fillna(0)
  time_stamp = rawdata['records']['timestamp']

  #Current Strik Price
  CTP=rawop['CE'][0]['underlyingValue']
  # logic for strick price conversion of multiple of 50
  f3digit = CTP // 100
  num =CTP // 10
  last = num % 10
  if last >= 5:
      f3digit = (f3digit + 1) * 100
  else:
      f3digit = (f3digit) * 100
      if url.split('=')[1] =='NIFTY':
        f3digit += 50
  return rawop, f3digit, time_stamp

def dataframe(rawop):
    data = []
    #import pdb; pdb.set_trace()
    for i in range(0, len(rawop)):
        calloi = callcoi = cltp = putoi = putcoi = pltp = calliv = putiv = 0
        stp = rawop['strikePrice'][i]
        if (rawop['CE'][i] == 0):
            calloi = callcoi = calliv = 0
        else:
            calloi = rawop['CE'][i]['openInterest']
            callcoi = rawop['CE'][i]['changeinOpenInterest']
            cltp = rawop['CE'][i]['lastPrice']
            calliv = rawop['CE'][i]['impliedVolatility']

        if (rawop['PE'][i] == 0):
            putoi = putcoi = putiv = 0
        else:
            putoi = rawop['PE'][i]['openInterest']
            putcoi = rawop['PE'][i]['changeinOpenInterest']
            pltp = rawop['PE'][i]['lastPrice']
            putiv = rawop['PE'][i]['impliedVolatility']

        # add this info into dict
        opdata = {
             'Strike Price': stp,'Call IV' : calliv,
             'Call LTP': cltp, 'Call OI': calloi, 'CHNG Call OI': callcoi,
             'Put LTP': pltp, 'Put OI': putoi, 'CHNG Put OI': putcoi, 'Put IV' : putiv,
        }
        data.append(opdata)
    optionchain_df = pd.DataFrame(data)
    return optionchain_df

def print_data():
  rawop, f3digit, time_stamp = load_data()

  option_chain_data = dataframe(rawop)

  df_diff = option_chain_data.copy()
  #row_of_list = diff_pcr_chart(df_diff)

  # it gives index of matched column value in int form
  i = option_chain_data.loc[option_chain_data['Strike Price'] == f3digit].index.values.astype(int)[0]
  start = i - 8
# df2 for nearby 17 rows only from current strike price -df2 used for dashboard
  df2 = option_chain_data.iloc[start:start + 17, ]
  df2 = df2.reset_index(drop=True)
  df3 = df2.copy()  # df3 for show data into table with sum at last

  # appending total sum at last
  df3.loc[len(df3.index)] = [datetime.now().strftime("%H:%M:%S"),
                             df2.iloc[9:17].sum(axis=0)['Call IV'],
                             '',
                             df2['Call OI'].sum(axis=0),
                             df2['CHNG Call OI'].sum(axis=0),
                             '',
                             df2['CHNG Put OI'].sum(axis=0),
                             df2['Put OI'].sum(axis=0),
                             df2.iloc[0:9].sum(axis=0)['Put IV']]
  df3['Strike Price_'] = df3['Strike Price']

  # shift column 'Strike Price_' to 6th position
  strike_price_column = df3.pop('Strike Price_')

  # insert column using insert(position,column_name,pop_column_name) function
  df3.insert(5, 'Strike Price_', strike_price_column)

  #save_data_google_sheet(df3, row_of_list)
#  print(df3)
  # df3.to_csv('Option_Live_Data.csv', index=False, mode='w+')
  # df3.to_html('index.html')
  return df3,df2, time_stamp

def option_chain_view(request):
    # option_data = fetch_option_chain_data()
    df3,df2, time_stamp = (print_data())
    # df2.to_csv('EOD.csv', index=False)
    # Remove two columns name is 'Call IV',	'Call LTP',	'Put LTP',	'Put IV'
    df2.drop(['Call IV',	'Call LTP',	'Put LTP',	'Put IV'], axis=1, inplace=True)
    PCR = df2['Put OI'].sum(axis=0)/df2['Call OI'].sum(axis=0)
    # print("PCR".center('-',10))
    # print("Sum CHNG CEOI: {}".format(df2['Call OI'].sum(axis=0)))
    # print("Sum CHNG PEOI: {}".format(df2['Put OI'].sum(axis=0)))
    # print("PCR: {}".format(PCR))
    groups = df2.groupby('Strike Price').mean()
    # groups.style\
    #   .format('{:.0f}')\
    #   .highlight_max(color = 'lightgreen')\
    #   .highlight_min(color = 'coral')\
    #   .highlight_null(color='yellow')\
    #   .background_gradient(cmap='Purples')
    # print(df2)

    df2.rename(columns={
                        'Strike Price': 'Strike_Price',
                        'Call OI': 'Call_OI',
                        'CHNG Call OI': 'CHNG_Call_OI',
                        'Put OI': 'Put_OI',
                        'CHNG Put OI': 'CHNG_Put_OI'
                        }, inplace=True)
    df3.rename(columns={
                        'Strike Price': 'Strike_Price',
                        'Call IV':'Call_IV', 'Call LTP':'Call_LTP',
                        'Call OI': 'Call_OI',
                        'CHNG Call OI': 'CHNG_Call_OI',
                        'Strike Price_':'Strike_Price_',
                        'Put OI': 'Put_OI',
                        'Put LTP':'Put_LTP',
                        'CHNG Put OI': 'CHNG_Put_OI',
                        'Put IV':'Put_IV' 
                        }, inplace=True)
    if not df2.empty:  # Check if the DataFrame is not empty
        sum_data = df3.tail(1).to_dict(orient='records')[0]
        
        context = {
            'option_data': df2.to_dict(orient='records'),  # Convert DataFrame to a list of dictionaries
            'sum_data':sum_data, 'time_stamp':time_stamp,
        }
        # print(df3.columns)
        return render(request, 'index.html', context)
    else:
        return render(request, 'error.html')
 
