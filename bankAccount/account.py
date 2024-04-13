import os
import pandas as pd
from dataclasses import dataclass
from datetime import datetime

@dataclass
class columns:
    def __init__(self, booking_date, sender_name, purpose_of_use, amount, investment, category, sum) -> None:
        self.booking_date = booking_date
        self.sender_name = sender_name
        self.purpose_of_use = purpose_of_use
        self.amount = amount
        self.investment = investment
        self.category = category
        self.sum = sum

class account:
    def __init__(self, df, category_mapper, columns: columns):
        self.df = df
        self.category_mapper = category_mapper
        self.columns = columns

        # add category column for initial data frame
        for i in range(len(self.df)):
            # change format of Buchungstag
            self.df.loc[i, self.columns.booking_date] = datetime.strptime(self.df[self.columns.booking_date][i], '%d.%m.%Y')
            for cat in self.category_mapper:
                if type(self.df[self.columns.purpose_of_use][i]) is float or type(self.df[self.columns.sender_name][i]) is float:
                    continue
                if cat.lower() in self.df[self.columns.purpose_of_use][i].lower() or cat.lower() in self.df[self.columns.sender_name][i].lower() :
                    self.df.loc[i, self.columns.category] = self.category_mapper[cat]
    
    def set_time_range(self, start_date, end_date):
        self.df = self.df.loc[(self.df[self.columns.booking_date] < end_date) & (self.df[self.columns.booking_date] >= start_date)]
    
    def save_original_categorized_file(self, output_filename):
        self.df.to_csv(os.getcwd() + '/' + output_filename + '.csv', index = False)
    
    def save_short_categorized_file(self, output_filename):
        df_short = self.df.loc[:,(self.columns.booking_date, self.columns.purpose_of_use, self.columns.sender_name, self.columns.amount, self.columns.category)]
        df_short.to_csv(os.getcwd() + '/' + output_filename + '_short.csv', index = False)
    
    def print_savings(self):
        # print sum of all expenses, also known as total savings
        if not hasattr(self, 'df_categorie'):
            self._summerize_categories()
        total_savings = round(float(self.df_categorie[self.columns.sum].sum()), 2)
        print(f'total savings = {total_savings}€')
    
    def ignore_investment(self):
        # remove investments because this money is not spent although has negative sign
        print(f"Ignore {-1 * self.df.loc[self.df[self.columns.category] == self.columns.investment, self.columns.amount].sum()}€ of investments")
        self.df = self.df.loc[self.df[self.columns.category] != self.columns.investment]
    
    def print_monthly_savings(self):
        df_savings = self.df.loc[:, (self.columns.booking_date, self.columns.amount)]
        df_savings.set_index(self.columns.booking_date, drop=True, inplace=True)
        
        df_savings_monthly = df_savings.groupby([lambda x: x.year, lambda x: x.month]).sum()
        print(df_savings_monthly)
        average_savings = df_savings_monthly[self.columns.amount].sum() / len(df_savings_monthly)
        print(f'Average saving is {round(average_savings, 2)} €')

    def _summerize_categories(self):
        # create data frame with category and sum column only
        self.df_categorie = df_categorie = pd.DataFrame(data={self.columns.category: [], self.columns.sum : []})
        for cat in self.df[self.columns.category].unique():    
            df_categorie.loc[len(df_categorie)] = {self.columns.category: cat, self.columns.sum: round(self.df.loc[self.df[self.columns.category]== cat, self.columns.amount].sum(), 2)}
        print(df_categorie.sort_values(by=[self.columns.sum]))


class volksbank(account):
    def __init__(self, df, category_mapper, booking_date):
        super().__init__(df, category_mapper, booking_date)

class dkb(account):
    def __init__(self, df, category_mapper, booking_date):
        super().__init__(df, category_mapper, booking_date)