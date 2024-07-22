import csv
import os
import numpy
import pandas as pd

from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']

class DataAnalysis():
    def __init__(self, datapath = None, Year = None, Month = None, Day = None, Hour = None):
        self.datapath = datapath
        self.Year = Year
        self.Month = Month
        self.Day = Day
        self.Hour = Hour
        self.histogram_filename = self.datapath + '/' + str(Year) + str(Month) + str(Day) + '/' + 'Histogram' + '/' + str(Year) + str(Month) + str(Day) + str(Hour) + "_Counter_Histogram_Data.csv"
        self.line_filename = self.datapath + '/' + str(Year) + str(Month) + str(Day) + '/' + 'Line Chart' + '/' + str(Year) + str(Month) + str(Day) + str(Hour) + "_Counter_mean_Data.csv"

    def hist_sort(self, bin): # Binning Counts in different Bins into a single file
        bin_path = self.datapath + '/'  + str(self.Year) + str(self.Month) + str(self.Day) + '/' + 'Binned_Data'
        _filename = bin_path + '/' + str(self.Year) + str(self.Month) + str(self.Day) + str(self.Hour) + "_Bin_" + str(bin) + "_Data.csv"
        if os.path.exists(bin_path) is False:
                os.makedirs(bin_path)
        
        col_names = ['Date and Time', 'Bin_ID', 'Counts']
        df = pd.read_csv(self.histogram_filename, names = col_names, header=None)
        df = df.loc[df['Bin_ID'] == bin]
        
        df = df[['Date and Time', 'Counts']]
        df.to_csv(_filename, index=False)

    def line_check(self, win = 100):
        self.win = win
        col_names = ['Date and Time', 'Time Mark', 'Mean', 'Counts', 'Note']
        df = pd.read_csv(self.line_filename, names = col_names, header=None, encoding = 'gbk')
        #line_path = self.datapath + '/'  + str(self.Year) + str(self.Month) + str(self.Day) + '/' + 'Line_Analysis'
        #_filename = line_path + '/' + str(self.Year) + str(self.Month) + str(self.Day) + str(self.Hour) + "_Line_Analysis.csv"
        f = df.dropna(how ='any', axis = 0)
        df = df[['Date and Time', 'Mean', 'Counts', 'Note']]

        ind = list(f.index.values.tolist())
        self.dic = []
        self.flag = None
        
        if ind == []:
            self.flag = False
            try:
                self.dic = df.iloc[0:self.win,:]
            except:
                self.dic = df.iloc[0:, :]
                self.win = len(self.dic)
        else:
            self.flag = True
            for i in ind:
                if i + win< len(df):
                    self.dic.append(df.iloc[i:i + win, :])
                else:
                    self.dic.append(df.iloc[i:, :])
    
    def hist_check(self, num_bin = 32):
        self.hist = []
        for bin in range(num_bin):
            bin_path = self.datapath + '/'  + str(self.Year) + str(self.Month) + str(self.Day) + '/' + 'Binned_Data'
            _filename = bin_path + '/' + str(self.Year) + str(self.Month) + str(self.Day) + str(self.Hour) + "_Bin_" + str(bin + 1) + "_Data.csv"
            #print(_filename)

            col_names = ['Date and Time', 'Counts']
            try:
                df = pd.read_csv(_filename, names = col_names, header=None, encoding = 'gbk', skiprows=1)
            except:
                raise ValueError('The file or directory does not exist')

            self.hist.append(df)

        
        #fig, ax = plt.subplots(num_bin, 1, figsize=(14, 7 * num_bin))

        #fig, ax = plt.subplots(1, 1, figsize=(14, 7))
        #tick_spacing0 = 100
        #tick_spacing1 = 200
        #ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing0))
        #ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing1))
        #ax.plot(self.hist[0].iloc[1:,0], self.hist[0].iloc[1:,1])
        '''
        for i in range(num_bin):
            #import ipdb; ipdb.set_trace()
        #    print(len(self.hist[i].iloc[1:,0]))
            ax[i].set_title("Evolution of bin {}".format(str(i + 1)))
            ax[i].set_xlabel("Date and Time")
            ax[i].set_ylabel("Counts")
            ax[i].plot(list(range(1, len(self.hist[i].iloc[1:,0]) + 1)), self.hist[i].iloc[1:,1])
        '''


