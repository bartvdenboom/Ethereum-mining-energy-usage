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
#Ethereum Energy Consumption Index (beta) at https://digiconomist.net/
with open('../JSONDATA/Digiconomist/data.json') as f:
    DigiconomistData = json.load(f)
#This study: upperbound and lowerbound data
with open('../JSONDATA/UpperBoundEstimate.json') as f:
    upperBoundData = json.load(f)
with open('../JSONDATA/LowerBoundEstimate.json') as f:
    lowerBoundData = json.load(f)


def csvtojson(input, output):
    csvfile = open(input, 'r')
    jsonfile= open(output, 'w')
    reader = csv.reader(csvfile)
    rownames = next(reader)
    reader  = csv.DictReader(csvfile, rownames)
    out = json.dumps([row for row in reader],indent=4)
    jsonfile.write(out)

csvtojson('../JSONDATA/Digiconomist/data.csv','../JSONDATA/Digiconomist/data.json' )
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
    df = pd.DataFrame(gpudata,columns=['Release date', 'Efficiency in J/Mh', 'Product', 'Type'])
    data_x = pd.to_datetime(df["Release date"])
    data_y = [float(d) for d in df["Efficiency in J/Mh"]]
    types = df['Type']
    fig, ax = plt.subplots()
    colors = {"GPU": 'red',"RIG": 'blue',"ASIC": 'green'}
    for x,y,type in zip(data_x,data_y,types):
        ax.scatter(x,y,label=type, c=colors[type])
    #ax.xaxis.set_major_locator(plt.MaxNLocator(20))



    legend_elements = [plt.scatter(data_x[0], data_y[0], label = 'General purpose graphics cards', c=colors[types[0]]),
                        plt.scatter(data_x[69], data_y[69], label = 'Mining Rigs', c=colors[types[69]]),
                        plt.scatter(data_x[62], data_y[62], label = 'Ethereum specific ASIC', c=colors[types[62]])]

    # Create the figure
    #plt.xticks(rotation=45)
    plt.legend(handles=legend_elements)
    ax.set_xlabel('Date')
    ax.set_ylabel('Efficiency in J/Mh')
    plt.title('Mining hardware efficiencies over time')
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
    line2 = ax1.plot(BreakEvenEfficiencySetDataFrame['Date'], BreakEvenEfficiencySetDataFrame['cumulativeHardwareEfficiency'], color=color, label='Used hardware Efficciency (J/Mh)')
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

def compareOtherResults():

    #This study
    upperbound_x = pd.to_datetime(pd.DataFrame(upperBoundData)['Date'])
    upperbound_y = [date['yearlyTWh'] for date in upperBoundData]
    upperboundLine = pd.Series(data=upperbound_y, index=upperbound_x)

    lowerbound_x = pd.to_datetime(pd.DataFrame(lowerBoundData)['Date'])
    lowerbound_y = [date['yearlyTWh'] for date in lowerBoundData]
    lowerboundLine = pd.Series(data=lowerbound_y, index=lowerbound_x)

    #Digiconomist estimate
    digiconomist_x = pd.to_datetime(pd.DataFrame(DigiconomistData)['Date'])
    digiconomist_y = [float(date['EECI']) for date in DigiconomistData]
    digiconomistLine = pd.Series(data=digiconomist_y, index=digiconomist_x)

    #Cleancoins initiative estimate
    cleancoins_x = pd.to_datetime(pd.DataFrame(["3/5/2020"])[0])
    cleancoins_y = float(5.65)
    cleancoinsLine = pd.Series(data=cleancoins_y, index=cleancoins_x)

    #Zade (2018)
    zade_x2015 = pd.to_datetime(pd.DataFrame(["1/1/2015","12/31/2015"])[0])
    zade_y2015 = [((wattage*8765.81277)/1e6) for wattage in [3.0,3.0]]
    zade2015Line = pd.Series(data=zade_y2015, index=zade_x2015)
    zade_x2016 = pd.to_datetime(pd.DataFrame(["1/1/2016","12/31/2016"])[0])
    zade_y2016 = [((wattage*8765.81277)/1e6) for wattage in [19.0,19.0]]
    zade2016Line = pd.Series(data=zade_y2016, index=zade_x2016)
    zade_x2017 = pd.to_datetime(pd.DataFrame(["1/1/2017","12/31/2017"])[0])
    zade_y2017 = [((wattage*8765.81277)/1e6) for wattage in [367.0,367.0]]
    zade2017Line = pd.Series(data=zade_y2017, index=zade_x2017)
    zade_x2018 = pd.to_datetime(pd.DataFrame(["1/1/2018","10/31/2018"])[0])
    zade_y2018 = [((wattage*8765.81277)/1e6) for wattage in [991.0,991.0]]
    zade2018Line = pd.Series(data=zade_y2018, index=zade_x2018)

    #Krause (2019)
    krause_x2016 = pd.to_datetime(pd.DataFrame(["1/1/2016","12/31/2016"])[0])
    krause_y2016 = [((wattage*8765.81277)/1e6) for wattage in [24.0,24.0]]
    krause2016Line = pd.Series(data=krause_y2016, index=krause_x2016)
    krause_x2017 = pd.to_datetime(pd.DataFrame(["1/1/2017","12/31/2017"])[0])
    krause_y2017 = [((wattage*8765.81277)/1e6) for wattage in [299.9,299.0]]
    krause2017Line = pd.Series(data=krause_y2017, index=krause_x2017)
    krause_x2018 = pd.to_datetime(pd.DataFrame(["1/1/2018","6/30/2018"])[0])
    krause_y2018 = [((wattage*8765.81277)/1e6) for wattage in [1165.0,1165.0]]
    krause2018Line = pd.Series(data=krause_y2018, index=krause_x2018)


    fig, ax = plt.subplots()

    ax.plot(digiconomistLine, label='Digiconomist Estimate', color='red')
    ax.plot(upperboundLine, label='Upper bound (This study)', color='green')
    ax.plot(lowerboundLine, label='Lower bound (This study)', color='blue')
    ax.plot(zade2015Line, label = 'Zade (2018)',linestyle='-.', color='black')
    ax.plot(zade2016Line, linestyle='-.', color='black')
    ax.plot(zade2017Line, linestyle='-.', color='black')
    ax.plot(zade2018Line, linestyle='-.', color='black')
    ax.plot(krause2016Line, label = 'Krause & Tolalymat (2018)', linestyle=':', color='orange')
    ax.plot(krause2017Line, linestyle=':', color='orange')
    ax.plot(krause2018Line, linestyle=':', color='orange')
    ax.scatter(cleancoins_x,cleancoins_y, c='black', label='Cleancoin', marker="s")


    ax.set_xlabel('Date')
    ax.set_ylabel('Estimated TWh per year')
    plt.title('Comparison of Ethereum energy usage estimates in other studies.')
    plt.legend()

    #plt.xticks(rotation=45)
    plt.show()
