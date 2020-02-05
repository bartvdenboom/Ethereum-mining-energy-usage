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

def plotBreakEvenEffAgainstSelectedEfficiency(efficiencyData, DailyData ):
    BreakEvenEfficiencySetDataFrame = pd.DataFrame(efficiencyData)
    data = pd.DataFrame(DailyData)
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('BreakEvenEfficiency (J/MH)', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    line1 = ax1.plot(BreakEvenEfficiencySetDataFrame['Date'], BreakEvenEfficiencySetDataFrame['BreakEvenEfficiency'], color=color, label='Break even Efficciency (J/Mh)')
    color = 'tab:green'
    line2 = ax1.plot(BreakEvenEfficiencySetDataFrame['Date'], BreakEvenEfficiencySetDataFrame['selectedHardwareEfficiencyJMh'], color=color, label='Used hardware Efficciency (J/Mh)')
    #ax1.legend(handles = [line1, line2])
    plt.xticks(rotation=90)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('', color=color)  # we already handled the x-label with ax1
    #ax2.plot(data['date'], (data['correctedhashrate']/1e9), color=color)
    #line3 = ax2.plot(data['date'], (data['averagedifficulty']/1e6), color=color, label='Average Difficulty')
    ax2.tick_params(axis='y', labelcolor=color)
    color = 'tab:pink'
    line4 = ax2.plot(data['date'], (data['computedhashrate']), color=color, label='Hashrate')

    ax1.xaxis.set_major_locator(plt.MaxNLocator(20))

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #
    # data.plot(kind='line', x='date', y='averagehashrate', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(kind='line', x='date', y='BreakEvenEfficiency', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(x='date', y='BreakEvenEfficiency', figsize=(16,9))
    # #plt.figure(BreakEvenEfficiencySetDataFrame, (200,100))
    #ax2.legend(handles = [line3,line4])
    first_legend = ax1.legend(handles = [line1[0],line2[0]] , loc = 'upper left')
    second_legend = ax2.legend(handles = line4, loc = 'upper right')
    ax1.add_artist(first_legend)
    ax2.add_artist(second_legend)
    plt.show()


#plotBreakEvenEffAgainstSelectedEfficiency()
#plotBreakEvenEff(phaseData)
#scatterPlotGpuEfficiencies()
#plotHashRategradient()
#plothashrates()
