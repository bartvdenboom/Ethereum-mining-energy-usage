import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import sys
import csv
from matplotlib.ticker import FuncFormatter
import numpy as np
import matplotlib.dates as mdates

with open('../JSONDATA/EtherscanCrawler/CrawlerBlockDataAdjustedUncles.json') as r:
    crawlerdata = reversed(json.load(r))
with open('../JSONDATA/Etherscan/DailyData.json') as r:
    blockdata = json.load(r)
with open('../JSONDATA/GPUdata/GPUDATA.json') as r:
    gpudata = json.load(r)
#Data regarding energy consumption per phase
with open('../JSONDATA/Etherscan/phaseData.json') as f:
    phaseData = json.load(f)
#Data regarding BreakevenEfficiency per day
with open('../JSONDATA/Etherscan/BreakEvenPlotData.json') as f:
    breakEvenPlotData = json.load(f)


def plottwoaxis():
    BreakEvenEfficiencySetDataFrame = pd.DataFrame(BreakEvenEfficiencySet)
    data = pd.DataFrame(reversed(blockdata))
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('BreakEvenEfficiency (J/MH)', color=color)
    ax1.plot(BreakEvenEfficiencySetDataFrame['date'], BreakEvenEfficiencySetDataFrame['BreakEvenEfficiency'], color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    plt.xticks(rotation=90)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Average Hashrate (GH/s)', color=color)  # we already handled the x-label with ax1
    ax2.plot(data['date'], (data['averagehashrate']/1000000000), color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax1.xaxis.set_major_locator(plt.MaxNLocator(20))

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #
    # data.plot(kind='line', x='date', y='averagehashrate', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(kind='line', x='date', y='BreakEvenEfficiency', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(x='date', y='BreakEvenEfficiency', figsize=(16,9))
    # #plt.figure(BreakEvenEfficiencySetDataFrame, (200,100))
    plt.show()

def scatterPlotGpuEfficiencies():

    df = pd.DataFrame(gpudata,columns=['Release date', 'Efficiency in J/Mh', 'Product'])

    df["Release date"] = pd.to_datetime(df["Release date"])

    df = df.sort_values(by="Release date")

    for i in range(0, len(df)-1):
        plt.scatter(df['Release date'][i], float(df['Efficiency in J/Mh'][i]))
        plt.text(df['Release date'][i],float(df['Efficiency in J/Mh'][i]),df['Product'][i])
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(20))
    #plt.gca().yaxis.set_major_locator(plt.MaxNLocator(20))
    #plt.ylim(1, 20)
    plt.xticks(rotation=45)
    plt.show()

def Gigahashformatter(x, pos):
    'The two args are the value and tick position'
    return '%1ik' % (x*1e-12)


def plothashrates():
    formatter = FuncFormatter(Gigahashformatter)
    crawlerdataframe = pd.DataFrame(crawlerdata,columns=['date', 'averagehashrate', 'correctedhashrate'])

    etherscandataframe = pd.DataFrame(blockdata,columns=['date', 'averagehashrate', 'calculatedhashrate', 'correctedhashrate'])
    #ax1 = crawlerdataframe.plot(kind='line', x='date', y=['averagehashrate', 'correctedhashrate'])
    ax2 = etherscandataframe.plot(kind='line', x='date', y=['correctedhashrate'])
    # ax1.set_xlabel("Date")
    # ax1.set_ylabel("Hashrate GH/s")
    # ax1.yaxis.set_major_formatter(formatter)
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Hashrate GH/s")
    ax2.yaxis.set_major_formatter(formatter)
    ax2.axvline(x=200,color='red')
    ax2.axvline(x=454,color='red')
    ax2.axvline(x=598,color='red')
    ax2.axvline(x=778,color='red')
    ax2.axvline(x=970,color='red')
    ax2.axvline(x=1106,color='red')
    ax2.axvline(x=1141, color='red')
    ax2.axvline(x=1237,color='red')
    ax2.axvline(x=1275,color='red')
    ax2.axvline(x=1479,color='red')
    ax2.axvline(x=1538,color='red')


    plt.xticks(rotation=45)
    plt.show()


def plotHashRategradient():
    etherscandataframe = pd.DataFrame(blockdata,columns=['date', 'correctedhashrate'])
    etherscanhashrate = pd.DataFrame(etherscandataframe, columns=['correctedhashrate']).to_numpy().flatten()
    gradient = np.gradient(etherscanhashrate)
    plt.plot(gradient, label="Gradient of hashrate")
    plt.show()

def plotBreakEvenEff(BreakEvenEfficiencySet):
    df = pd.DataFrame(BreakEvenEfficiencySet)
    df.plot(kind='line', x='Period', y=['BreakEvenEfficiency','selectedHardwareEfficiencyJMh'])
    plt.xticks(rotation=45)
    plt.show()

def plotBreakEvenEffAgainstSelectedEfficiency():
    BreakEvenEfficiencySetDataFrame = pd.DataFrame(phaseData)
    data = pd.DataFrame(blockdata)
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('BreakEvenEfficiency (J/MH)', color=color)
    ax1.plot(BreakEvenEfficiencySetDataFrame['Date'], BreakEvenEfficiencySetDataFrame['BreakEvenEfficiency'], color=color)
    color = 'tab:green'
    ax1.plot(BreakEvenEfficiencySetDataFrame['Date'], BreakEvenEfficiencySetDataFrame['selectedHardwareEfficiencyJMh'], color=color)
    BreakEvenEfficiencySetDataFrame['selectedHardwareEfficiencyJMh']
    ax1.tick_params(axis='y', labelcolor=color)

    plt.xticks(rotation=90)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Hashrate Gh/s', color=color)  # we already handled the x-label with ax1
    ax2.plot(data['date'], (data['correctedhashrate']/1000000000), color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax1.xaxis.set_major_locator(plt.MaxNLocator(20))

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #
    # data.plot(kind='line', x='date', y='averagehashrate', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(kind='line', x='date', y='BreakEvenEfficiency', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(x='date', y='BreakEvenEfficiency', figsize=(16,9))
    # #plt.figure(BreakEvenEfficiencySetDataFrame, (200,100))
    plt.show()

plotBreakEvenEffAgainstSelectedEfficiency()
#plotBreakEvenEff(phaseData)
#scatterPlotGpuEfficiencies()
#plotHashRategradient()
#plothashrates()
