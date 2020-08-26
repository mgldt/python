import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re
import statsmodels.api as sm
#import numpy as np
url = 'https://www.olx.com.pe'
url_add = '/santiago-de-surco_g5301117/departamentos-casas-venta_c367?filter=bathrooms_min_2%2Cbedrooms_min_2%2Csurface_between_200_to_500%2Ctipo_eq_41243&sorting=desc-relevance'

r = requests.get(url + url_add)

str_remove = {'Dor.', 'Bñ.', 'm2'}


mydata = pd.DataFrame({'link':str(),
                       'title':str(),
                       'price':int(),
                       'location':str(),
                       'br':int(),
                       'bd':int(),
                       'm2':float(),
                       'curr':str()}, index=[1])

# make sure that the page exist
if r.status_code == 200:
  html = r.text
  soup = BeautifulSoup(html, 'lxml')

  for listing in soup.find_all('li', {'data-aut-id': 'itemBox'}, {'class': 'EIR5N'}):
    
    title = listing.find('span', {'data-aut-id': 'itemTitle'})
    
    prices = listing.find('span', {'data-aut-id': 'itemPrice'})
    if prices.get_text().startswith('$'):
      currency = 'dollar'
    else:
      currency = 'sol'
    prices = int(re.sub('[^0-9]', '', prices.get_text()))
    
    location = listing.find('span', {'data-aut-id': 'item-location'})
  
    details = listing.find('span', {'data-aut-id': 'itemDetails'})
    
    str_detail = details.get_text()
    for strg in str_remove:
      str_detail = str_detail.replace(strg, '').replace(' ', '')
    str_detail = str_detail.split('-')
    
    df2 = pd.DataFrame({'link':[url + listing.a['href']],
                        'title': title.get_text(),
                        'price': prices,
                        'location': location.get_text(),
                        'br': int(str_detail[0]),
                        'bd': int(str_detail[1]),
                        'm2': float(str_detail[2]),
                        'curr':currency})
    mydata = mydata.append(df2)    

# ols
mydata = mydata[(mydata.br > 0) & (mydata.br < 10)]
X = mydata[['br', 'bd', 'm2']]#[mydata.location == '']
Y = mydata.price#[mydata.location == '']

model = sm.OLS(Y, X)
results_ols = model.fit()
print(results_ols.summary())

fig, ax = plt.subplots(1, 3, figsize=(25,6))
groups = mydata.groupby("location")
for name, group in groups:
    ax[0].plot(group["m2"], group["price"], marker="o", linestyle="", label=name)
    ax[0].set_title('m2')
    ax[1].plot(group["br"], group["price"], marker="o", linestyle="", label=name)
    ax[1].set_title('cuartos')
    ax[2].plot(group["bd"], group["price"], marker="o", linestyle="", label=name)
    ax[2].set_title('banos')
ax[0].legend();
