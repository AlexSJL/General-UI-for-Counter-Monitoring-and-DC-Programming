import numpy as np
import csv

class Amp_DC_converter():
    def __init__(self, filename, fitting_order=0):
        self.data = self.read_file(filename)
        self.fitting_order = fitting_order

    def read_file(self, filename):
        x_data = []
        y_data = []
        with open(filename, 'r') as file:
            csvFile = csv.reader(file)
            for line in csvFile:
                try:
                    x_data.append(float(line[0]))
                    y_data.append(float(line[1]))
                except:
                    continue
        return [x_data, y_data]

    def converter(self, val):
        coef = self.fitting(self.data[1], self.data[0])
        return self.compute(val, coef), self.eval(self.data[0], self.data[1], coef)
    
    def fitting(self, y_data, x_data):
        coef = np.polyfit(y_data, x_data, self.fitting_order)
        return coef
        
    def eval(self, x_data, y_data, coef):
        x_temp = []
        for y in y_data:
            temp = 0
            for i in range(len(coef)):
                temp += coef[i] * y ** (len(coef) - 1 - i)
            x_temp.append(temp)
        error = np.max(([x_temp[i]-x_data[i] for i in range(len(x_temp))]))**2.
        return error

    def compute(self, x, coef):
        eval = 0
        for i in range(len(coef)):
            eval += coef[i] * x ** (len(coef) - 1 - i)
        return eval