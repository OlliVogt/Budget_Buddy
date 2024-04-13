import pandas as pd
from datetime import datetime
import os
import json
import argparse

import bankAccount.account as account

output_filename = 'kategorisiert'
decimal_seperator = ','
delimiter = ";"

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--csv', dest='csv', help='Path to the .csv file', required=True)
args = parser.parse_args()
input_filename = args.csv

def searchReplace(filename, search_text, replace_text):
    with open(filename, 'r') as file:
        data = file.read()  
        data = data.replace(search_text, replace_text) 
    
    with open(filename, 'w') as file:
        file.write(data) 
    print(f"Replacement of {search_text} with {replace_text} done")
  
  
cur_dir = os.getcwd()
file_path = cur_dir + '/' + input_filename
searchReplace(file_path, search_text='"', replace_text="")
df = pd.read_csv(file_path, delimiter=delimiter, on_bad_lines='skip', decimal=decimal_seperator)

with open('./categorie_mapper.json', 'r') as f:
  categorie_mapper = json.load(f)

def volksbank(df):
    columns = account.columns('Buchungstag', 'Name Zahlungsbeteiligter', 'Verwendungszweck', 'Betrag', 'Investment', 'Kategorie', 'Summe')

    bankAccount = account.account(df, categorie_mapper, columns)
    bankAccount.set_time_range(datetime(year=2023, month=1, day=1), datetime(year=2024, month=1, day=1))
    bankAccount.save_original_categorized_file(output_filename)
    bankAccount.save_short_categorized_file(output_filename)
    bankAccount.ignore_investment()
    bankAccount.print_savings()
    bankAccount.print_monthly_savings()

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
    accout = account.dkb(df, categorie_mapper, 'Buchungsdatum')
    account.set_time_range(datetime(year=2023, month=1, day=1), datetime(year=2024, month=1, day=1))
    df = account.df
    # startDate = datetime(year=2023, month=1, day=1)
    # endDate = datetime(year=2024, month=1, day=1)
    # df = df.loc[(df['Buchungsdatum'] < endDate) & (df['Buchungsdatum'] >= startDate)]

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