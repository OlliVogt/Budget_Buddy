import pandas as pd
from datetime import datetime
import os
import json
import argparse

output_filename = 'kategorisiert'

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--csv', dest='csv', help='Path to the .csv file', required=True)
args = parser.parse_args()
input_filename = args.csv

def searchReplace(filename):
    # creating a variable and storing the text 
    # that we want to search 
    search_text = '"'
    
    # creating a variable and storing the text 
    # that we want to add 
    replace_text = ""
    
    # Opening our text file in read only 
    # mode using the open() function 
    with open(filename, 'r') as file: 
    
        # Reading the content of the file 
        # using the read() function and storing 
        # them in a new variable 
        data = file.read() 
    
        # Searching and replacing the text 
        # using the replace() function 
        data = data.replace(search_text, replace_text) 
    
    # Opening our text file in write only 
    # mode to write the replaced content 
    with open(filename, 'w') as file: 
    
        # Writing the replaced data in our 
        # text file 
        file.write(data) 
    
    # Printing Text replaced 
    print("Text replaced")
  
  
cur_dir = os.getcwd()
searchReplace(cur_dir + '/' + input_filename)
df = pd.read_csv(cur_dir + '/' + input_filename, delimiter=';', on_bad_lines='skip', decimal=',')

with open('./categorie_mapper.json', 'r') as f:
  categorie_mapper = json.load(f)

def volksbank(df):
    # add category column for initial data frame
    for i in range(len(df)):
        df.loc[i, 'Buchungstag'] = datetime.strptime(df['Buchungstag'][i], '%d.%m.%Y')
        for cat in categorie_mapper:
            if type(df['Verwendungszweck'][i]) is float or type(df['Name Zahlungsbeteiligter'][i]) is float:
                continue
            if cat.lower() in df['Verwendungszweck'][i].lower() or cat.lower() in df['Name Zahlungsbeteiligter'][i].lower() :
                df.loc[i, 'Kategorie'] = categorie_mapper[cat]

    # define range of data
    startDate = datetime(year=2023, month=1, day=1)
    endDate = datetime(year=2024, month=1, day=1)
    df = df.loc[(df['Buchungstag'] < endDate) & (df['Buchungstag'] >= startDate)]

    # save csv file with original data frame with category column
    df.to_csv(os.getcwd() + '/' + output_filename + '.csv')

    # create a short version of the data frame and save the file
    df_short = df.loc[:,('Valutadatum', 'Verwendungszweck', 'Name Zahlungsbeteiligter', 'Betrag', 'Saldo nach Buchung', 'Kategorie')]
    df_short.to_csv(os.getcwd() + '/' + output_filename + '_kurz.csv')

    # remove investments because this money is not spent although has negative sign
    df = df.loc[df['Kategorie'] != 'Investment']

    # create data frame with category and sum column only
    df_categorie = pd.DataFrame(data={'Kategorie': [], 'Summe' : []})
    for cat in df['Kategorie'].unique():    
        df_categorie.loc[len(df_categorie)] = {'Kategorie': cat, 'Summe': round(df.loc[df['Kategorie']== cat, 'Betrag'].sum(), 2)}
    print(df_categorie.sort_values(by=['Summe']))

    # print sum of all expenses, also known as total savings
    total_savings = round(float(df_categorie['Summe'].sum()), 2)
    print(f'total savings = {total_savings}€')

    # print savings across months
    df_savings = df.loc[:, ('Buchungstag', 'Betrag')]
    df_savings.set_index('Buchungstag', drop=True, inplace=True)
    
    df_savings_monthly = df_savings.groupby([lambda x: x.year, lambda x: x.month]).sum()
    print(df_savings_monthly)

    average_savings = df_savings_monthly['Betrag'].sum() / len(df_savings_monthly)
    print(f'Average saving is {round(average_savings, 2)} €')

def dkb(df):
    df['Betrag (€)'] = df['Betrag (€)'].str.replace(',','.').astype(float)
    
    # add category column for initial data frame
    for i in range(len(df)):
        df.loc[i, 'Buchungsdatum'] = datetime.strptime(df['Buchungsdatum'][i], '%d.%m.%y')
        for cat in categorie_mapper:
            if type(df['Verwendungszweck'][i]) is float or type(df['Zahlungsempfänger*in'][i]) is float:
                continue
            if cat.lower() in df['Verwendungszweck'][i].lower() or cat.lower() in df['Zahlungsempfänger*in'][i].lower() :
                df.loc[i, 'Kategorie'] = categorie_mapper[cat]
    
    m = df['Verwendungszweck'] == 'Monatliche Kosten'
    df.loc[m, 'Kategorie'] = df.loc[m, 'Kategorie'].replace("Lebensunterhalt", "Einzahlungen")
    m = df['Verwendungszweck'] == 'Monatliche Kosten Prisca'
    df.loc[m, 'Kategorie'] = df.loc[m, 'Kategorie'].replace("Lebensunterhalt", "Einzahlungen")
    df = df.fillna('Unknown')

    # define range of data
    startDate = datetime(year=2023, month=1, day=1)
    endDate = datetime(year=2024, month=1, day=1)
    df = df.loc[(df['Buchungsdatum'] < endDate) & (df['Buchungsdatum'] >= startDate)]

    # save csv file with original data frame with category column
    df.to_csv(os.getcwd() + '/' + output_filename + '.csv')

    # create a short version of the data frame and save the file
    df_short = df.loc[:,('Wertstellung', 'Verwendungszweck', 'Zahlungsempfänger*in', 'Betrag (€)', 'Kategorie')]
    df_short.to_csv(os.getcwd() + '/' + output_filename + '_kurz.csv')

    # remove investments because this money is not spent although has negative sign
    df = df.loc[df['Kategorie'] != 'Investment']

    # create data frame with category and sum column only
    df_categorie = pd.DataFrame(data={'Kategorie': [], 'Summe' : []})
    for cat in df['Kategorie'].unique():    
        df_categorie.loc[len(df_categorie)] = {'Kategorie': cat, 'Summe': round(df.loc[df['Kategorie']== cat, 'Betrag (€)'].sum(), 2)}
    print(df_categorie.sort_values(by=['Summe']))

    # print sum of all expenses, also known as total savings
    total_savings = round(float(df_categorie['Summe'].sum()), 2)
    print(f'total savings = {total_savings}€')

    # print savings across months
    df_savings = df.loc[:, ('Buchungsdatum', 'Betrag (€)', 'Kategorie')]
    df_savings.index = df_savings['Buchungsdatum']
    # df_savings_monthly = df_savings.groupby(by=[df_savings.index.month, df_savings.index.year])
    df_savings_monthly = df_savings.groupby([lambda x: x.year, lambda x: x.month]).sum()
    print(df_savings_monthly)

    average_savings = df_savings_monthly['Betrag (€)'].sum() / len(df_savings_monthly)
    print(f'Average saving is {round(average_savings, 2)} €')
    

if 'Buchungstag' in df.columns:
    volksbank(df)
if 'Buchungsdatum' in df.columns:
    dkb(df)