# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 11:15:00 2017

@author: Prashant Kumar, RCCIIT

@mail: kr.prashant94@gmail.com

@supervision: Dilip Kumar , NIT Jsr

"""

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import csv
import time
import datetime
import numpy as np
import matplotlib.animation as animation
import threading
import pandas
import os
import serial

class pyAnalysis:
    dataColumns = ['Time','Data','Average','SD']
    dataALog = pandas.DataFrame(columns = dataColumns)
    dataBLog = pandas.DataFrame(columns = dataColumns)
    
    fig = plt.figure()
    fig.subplots_adjust(hspace = 0.8, wspace = 0.4)
    plt.rc('font', size=8)          # controls default text sizes
    
    ax1 = fig.add_subplot(2,3,1)
    ax2 = fig.add_subplot(2,3,2)
    ax3 = fig.add_subplot(2,3,3)
    ax4 = fig.add_subplot(2,3,4)
    ax5 = fig.add_subplot(2,3,5)
    ax6 = fig.add_subplot(2,3,6)
    
    ax6.get_xaxis().set_visible(False)
    ax6.get_yaxis().set_visible(False)
    plt.axis('off')
    
    xdata, dataA, dataB, dataAmean, dataBmean, dataAsd, dataBsd = [0], [0], [0], [0], [0], [0], [0]
    labels = ['0:0']
    ln1, = ax1.plot([0], [0], 'red', linewidth = 1 )
    ln2, = ax1.plot([0], [0], 'green', linewidth = 1 )
    ln3, = ax2.plot([0], [0], 'red', linewidth = 1 )
    ln4, = ax2.plot([0], [0], 'blue', linestyle = '--', linewidth = 1)
    ln5, = ax3.plot([0], [0], 'green', linewidth = 1 )
    ln6, = ax3.plot([0], [0], 'blue', linestyle = '--', linewidth = 1)
    ln7, = ax4.plot([0], [0], 'red', linewidth = 1 )
    ln8, = ax4.plot([0], [0], 'black', linestyle = '--', linewidth = 1)
    ln9, = ax5.plot([0], [0], 'green', linewidth = 1 )
    ln10, = ax5.plot([0], [0], 'black', linestyle = '--', linewidth = 1)
    
    red_patch = patches.Patch(color='red', label='Pollutent (ppm)')
    green_patch = patches.Patch(color='green', label='CO (ppm)')
    avg_patch = patches.Patch(color='blue', label='Avgerage')
    sd_patch = patches.Patch(color='black', label='SD')
        
    initTime = time.time()
    threads = []
    
    yLimits = 100

    def __init__(self, port, path):
        #Initilize the dataBase.csv file to Start writing
        self.path = path
        self.ser = serial.Serial()
        self.ser.port = port
        self.fig.canvas.set_window_title('Pollution Data form ' + port)
        if(os.path.isfile(self.path+"/dataBaseA.csv")):
            self.fetchDatabase()
            self.dataA[0] = dataALog.iloc[-1]['Data']
            self.dataB[0] = dataBLog.iloc[-1]['Data']
            
            self.dataAmean[0] = dataALog.iloc[-1]['Average']
            self.dataBmean[0] = dataBLog.iloc[-1]['Average']
            
            self.dataAsd[0] = dataALog.iloc[-1]['SD']
            self.dataBsd[0] = dataBLog.iloc[-1]['SD']
        else:
            self.createCSV()

    #Data function
	
    def getNewData(self, number, error):
        try:
            self.ser.open()
            tmp = self.ser.readline().decode().strip()
            data = tmp.split(',')
            self.ser.close()
            return int(data[0].strip()) , int(data[1].strip())
        except:
            raise Exception('There is error in fatching data '+self.ser)
    
    def average(self, data, log, n):
        if(len(log) > n-1):
            dataList = list(log.iloc[-n:-1]['Data'])
            dataList.append(data)
            return round(np.mean(dataList, axis=0), 2)
        else:
            return 0
    
    def sd(self, data, log, n):
        if(len(log) > n-1):
            dataList = list(log.iloc[-n:-1]['Data'])
            dataList.append(data)
            return round(np.std(dataList, axis=0),2)
        else:
            return 0
    
    
    def Save(self, inputDataA, inputDataB):
        #os.system('cls')
        #print(pandas.concat([self.dataALog, self.dataBLog], axis=1))
        with open('dataBaseA.csv', 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar=' ', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(inputDataA)
        
        with open('dataBaseB.csv', 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar=' ', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(inputDataB)
    
    
    def createCSV(self):
        with open('dataBaseA.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar=' ', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.dataColumns)
            writer.writerow([''])
        with open('dataBaseB.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar=' ',lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.dataColumns)
            writer.writerow([''])
    def fetchDatabase(self):
        global dataALog, dataBLog
        dataALog = pandas.read_csv(self.path+"/dataBaseA.csv")
        dataBLog = pandas.read_csv(self.path+"/dataBaseB.csv")
    
        
    '''
        Graph Function
    '''
    def init(self):
        self.ax1.set_title('All Pollutent vs CO')
        self.ax2.set_title('All Pollutent vs Average')
        self.ax3.set_title('CO vs Average')
        self.ax4.set_title('All Pollutent vs SD')
        self.ax5.set_title('CO vs SD')
        
        self.setAxisLimits(self.ax1)
        self.setAxisLimits(self.ax2)
        self.setAxisLimits(self.ax3)
        self.setAxisLimits(self.ax4)
        self.setAxisLimits(self.ax5)
        
        self.ax1.legend(handles=[self.red_patch, self.green_patch])
        
        self.ax2.legend(handles=[self.red_patch, self.avg_patch])
        self.ax3.legend(handles=[self.green_patch, self.avg_patch])
        
        self.ax4.legend(handles=[self.red_patch, self.sd_patch])
        self.ax5.legend(handles=[self.green_patch, self.sd_patch])
        
        return
    
    def graph(self, frame):
        global yLimits, dataALog, dataBLog
        
        #Time Sync.
        dateTime = time.time()
        time.sleep(1 - (dateTime-self.initTime - int(dateTime-self.initTime)))
        
        #Inputs
        inputDataA, inputDataB = self.getNewData(self.dataA[-1], 5)
        
        dateTime = time.time() #Timestamp
        dateTimeNow = str(datetime.datetime.fromtimestamp(dateTime).strftime('%H:%M:%S ')) # Time in Calander format
        timeWhole = int(dateTime-self.initTime)
        
        #change Y-axis
        if(inputDataA >= self.yLimits or inputDataB >= self.yLimits):
            self.yLimits = inputDataA+5 if (inputDataA > inputDataB) else inputDataB+5
            self.ax1.set_ylim(0, self.yLimits)
            self.ax2.set_ylim(0, self.yLimits)
            self.ax3.set_ylim(0, self.yLimits)
            self.ax4.set_ylim(0, self.yLimits)
            self.ax5.set_ylim(0, self.yLimits)
            
        #Change X-axis
        if timeWhole > 11:
            self.labels.pop(0)
            self.xdata.pop(0)
            self.dataA.pop(0)
            self.dataB.pop(0)
            self.dataAmean.pop(0)
            self.dataBmean.pop(0)
            self.dataAsd.pop(0)
            self.dataBsd.pop(0)
            self.ax1.set_xlim(timeWhole-10, timeWhole)
            self.ax2.set_xlim(timeWhole-10, timeWhole)
            self.ax3.set_xlim(timeWhole-10, timeWhole)
            self.ax4.set_xlim(timeWhole-10, timeWhole)
            self.ax5.set_xlim(timeWhole-10, timeWhole)
            
        dataALog = dataALog.append({'Time':dateTimeNow,'Data':round(inputDataA,2),'Average':self.average(inputDataA, dataALog, 10),'SD':self.sd(inputDataA, dataALog, 10)}, ignore_index=True)
        dataBLog = dataBLog.append({'Time':dateTimeNow,'Data':inputDataB,'Average':self.average(inputDataB, dataBLog, 10),'SD':self.sd(inputDataB, dataBLog, 10)}, ignore_index=True)
        
        self.ax6.clear()
        self.ax6.text(0.1, 0, '$Status$ \nTime    : '+dateTimeNow+' \nAir Quality (ppm): '+str(inputDataA)+' \nCO (ppm) : '+str(inputDataB)+' \nAvg Air Quility  : '+str(dataALog.iloc[-1]['Average'])+' \nAvg CO  : '+str(dataBLog.iloc[-1]['Average'])+' \nSD Air Quility    : '+str(dataALog.iloc[-1]['SD'])+' \nSD CO    : '+str(dataBLog.iloc[-1]['SD'])+' ', fontsize=10)
        plt.axis('off')
    
        self.xdata.append(timeWhole)
        self.dataA.append(inputDataA)
        self.dataB.append(inputDataB)
        self.dataAmean.append(dataALog.iloc[-1]['Average'])
        self.dataBmean.append(dataBLog.iloc[-1]['Average'])
        self.dataAsd.append(dataALog.iloc[-1]['SD'])
        self.dataBsd.append(dataBLog.iloc[-1]['SD'])
        self.labels.append(dateTimeNow)

        plt.setp(self.ax1, xticks=self.xdata, xticklabels=self.labels)
        plt.setp(self.ax2, xticks=self.xdata, xticklabels=self.labels)
        plt.setp(self.ax3, xticks=self.xdata, xticklabels=self.labels)
        plt.setp(self.ax4, xticks=self.xdata, xticklabels=self.labels)
        plt.setp(self.ax5, xticks=self.xdata, xticklabels=self.labels)
        
        self.ln1.set_data(self.xdata, self.dataA)
        self.ln2.set_data(self.xdata, self.dataB)
        self.ln3.set_data(self.xdata, self.dataA)
        self.ln4.set_data(self.xdata, self.dataAmean)
        self.ln5.set_data(self.xdata, self.dataB)
        self.ln6.set_data(self.xdata, self.dataBmean)
        self.ln7.set_data(self.xdata, self.dataA)
        self.ln8.set_data(self.xdata, self.dataAsd)
        self.ln9.set_data(self.xdata, self.dataB)
        self.ln10.set_data(self.xdata, self.dataBsd)
        
        #Threaded Work
        t = threading.Thread(target=self.Save, args=(list(dataALog.iloc[-1]), list(dataBLog.iloc[-1]),))
        self.threads.append(t)
        t.start()
        
        return 
    
    def setAxisLimits(self, ax):
        ax.set_xlim(0, 11)
        ax.set_ylim(0, self.yLimits)
        self.rotateLabel(ax)
    
    def rotateLabel(self, ax):
        for label in ax.get_xmajorticklabels() + ax.get_xmajorticklabels():
            label.set_rotation(90)
            label.set_horizontalalignment("right")
    
    def genrateLineAnalysis(self):
        ani = animation.FuncAnimation(self.fig, self.graph, init_func=self.init,
                                      interval=500, blit=False)
        plt.show()