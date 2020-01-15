import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import sys
import csv, json

with open('../JSONDATA/CrawlerBlockDataAdjustedUncles.json') as r:
    crawlerdata = reversed(json.load(r))
with open('../JSONDATA/Etherscan/DailyData.json') as r:
    etherscandata = json.load(r)

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

def plot():

    crawlerdataframe = pd.DataFrame(crawlerdata,columns=['date', 'averagehashrate', 'correctedhashrate'])

    etherscandataframe = pd.DataFrame(etherscandata,columns=['date', 'averagehashrate', 'calculatedhashrate', 'correctedhashrate'])
    crawlerdataframe.plot(kind='line', x='date', y=['averagehashrate', 'correctedhashrate'])
    etherscandataframe.plot(kind='line', x='date', y=['averagehashrate', 'calculatedhashrate', 'correctedhashrate'])
    plt.show()
plot()
