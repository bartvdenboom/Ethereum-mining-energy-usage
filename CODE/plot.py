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
with open('../JSONDATA/BestGuessEstimate.json') as f:
    bestGuessData = json.load(f)

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
    df = pd.DataFrame(gpudata,columns=['Release date', 'Efficiency in J/Mh', 'Hash rate in Mh/s', 'Product', 'Type'])
    data_x = pd.to_datetime(df["Release date"])
    data_y = [float(d) for d in df["Efficiency in J/Mh"]]
    data_yh = [float(d) for d in df["Hash rate in Mh/s"]]
    types = df['Type']
    fig, ax = plt.subplots()
    colors = {"GPU": 'red',"RIG": 'blue',"ASIC": 'green'}
    for x,y,type in zip(data_x,data_yh,types):
        if not type == "RIG" or type == "ASIC":
            ax.scatter(x,y,label=type, c=colors[type])
    #ax.xaxis.set_major_locator(plt.MaxNLocator(20))



    legend_elements = [plt.scatter(data_x[0], data_y[0], label = 'General purpose graphics cards', c=colors[types[0]]),
                        # plt.scatter(data_x[69], data_y[69], label = 'Mining Rigs', c=colors[types[69]]),
                        plt.scatter(data_x[62], data_y[62], label = 'Ethereum specific ASIC', c=colors[types[62]])]


    plt.legend(handles=legend_elements)
    ax.set_xlabel('Date')
    # ax.set_ylabel('Efficiency in J/Mh')
    ax.set_ylabel('Hash rate in Mh/s')
    #plt.title('Mining hardware efficiencies over time')
    plt.title('Mining hardware hashrate over time')
    plt.show()

def Gigahashformatter(x, pos):
    'The two args are the value and tick position'
    return '%1ik' % (x*1e-12)


def plothashrates():
    formatter = FuncFormatter(Gigahashformatter)
    fig, ax = plt.subplots()

    data_x = pd.to_datetime(pd.DataFrame(blockdata)['date'])
    etherscan_y = [date['reportedhashrate'] for date in blockdata]
    etherscanReportedHashrate = pd.Series(data=etherscan_y, index=data_x)



    data_y = [date['computedhashrate'] for date in blockdata]
    computedHashrate = pd.Series(data=data_y, index=data_x)
    ax.plot(etherscanReportedHashrate, linestyle = '-.', label = 'Etherscan.io hashrate', color='red')
    ax.plot(computedHashrate, label = 'This study', color='blue')

    ax.axvline(x=pd.to_datetime("7/1/2018"),color='red')
    ax.axvline(x=pd.to_datetime("9/1/2018"),color='red')
    ax.yaxis.set_major_formatter(formatter)
    ax.set_xlabel('Date')
    ax.set_ylabel('Hashrate in GH/s')
    plt.title('Ethereum hashrate Etherscan.io vs this study.')
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()

def plotResults(efficiencyData):
    BreakEvenEfficiencySetDataFrame = pd.DataFrame(efficiencyData)
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('BreakEvenEfficiency (J/MH)', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    line1 = ax1.plot(BreakEvenEfficiencySetDataFrame['Date'], BreakEvenEfficiencySetDataFrame['BreakEvenEfficiency'], color=color, label='Break even Efficciency (J/Mh)')
    color = 'tab:green'
    line2 = ax1.plot(BreakEvenEfficiencySetDataFrame['Date'], BreakEvenEfficiencySetDataFrame['HardwareEfficiency'], color=color, label='Used hardware Efficciency (J/Mh)')
    ax1.legend()
    plt.xticks(rotation=90)

    ax1.xaxis.set_major_locator(plt.MaxNLocator(20))

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #
    # data.plot(kind='line', x='date', y='averagehashrate', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(kind='line', x='date', y='BreakEvenEfficiency', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(x='date', y='BreakEvenEfficiency', figsize=(16,9))
    # #plt.figure(BreakEvenEfficiencySetDataFrame, (200,100))
    #ax2.legend(handles = [line3,line4])
    # first_legend = ax1.legend(handles = [line1[0],line2[0]] , loc = 'upper left')
    # ax1.add_artist(first_legend)
    plt.show()

def plotBreakEvenEffAndHashrate(efficiencyData, DailyData ):
    fig, ax1 = plt.subplots()

    ax1.set_xlabel('Date')
    ax1.set_ylabel('BreakEvenEfficiency (J/MH)')

    breakeven_x = pd.to_datetime(pd.DataFrame(efficiencyData)['Date'])
    breakeven_y = [date['BreakEvenEfficiency'] for date in efficiencyData]
    breakevenLine = pd.Series(data=breakeven_y, index=breakeven_x)

    hardware_x = breakeven_x
    hardware_y = [date['HardwareEfficiency'] for date in efficiencyData]
    hardwareLine = pd.Series(data=hardware_y, index=hardware_x)

    line1 = ax1.plot(breakevenLine, color='red', label='Break even Efficciency (J/MH)')
    line2 = ax1.plot(hardwareLine, color='green', label='Used hardware Efficciency (J/MhH)')
    ax1.axvline(x=pd.to_datetime("7/1/2018"),color='red')
    ax1.axvline(x=pd.to_datetime("9/1/2018"),color='red')
    plt.xticks(rotation=90)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Hashrate in GH/s')
    formatter = FuncFormatter(Gigahashformatter)
    ax2.yaxis.set_major_formatter(formatter)

    hashrate_x = pd.to_datetime(pd.DataFrame(DailyData)['date'])
    hashrate_y = [date['computedhashrate'] for date in DailyData]
    hashrateLine = pd.Series(data=hashrate_y,index=hashrate_x)
    line3 = ax2.plot(hashrateLine, color='blue', label='Hashrate (GH/s)')
    ax1.xaxis.set_major_locator(plt.MaxNLocator(20))
    fig.tight_layout()
    #
    # data.plot(kind='line', x='date', y='averagehashrate', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(kind='line', x='date', y='BreakEvenEfficiency', figsize = (16,9), ax=ax)
    # BreakEvenEfficiencySetDataFrame.plot(x='date', y='BreakEvenEfficiency', figsize=(16,9))
    # #plt.figure(BreakEvenEfficiencySetDataFrame, (200,100))
    #ax2.legend(handles = [line3,line4])
    first_legend = ax1.legend(handles = [line1[0],line2[0]] , loc = 'upper left')
    second_legend = ax2.legend(handles = line3, loc = 'upper right')
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

    bestguess_x = pd.to_datetime(pd.DataFrame(bestGuessData)['Date'])
    bestguess_y = [date['yearlyTWh'] for date in bestGuessData]
    bestGuessLine = pd.Series(data=bestguess_y, index=bestguess_x)

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

    ax.plot(digiconomistLine,   label='Digiconomist Estimate', color='red')
    ax.plot(upperboundLine,     label='Upper bound (this study)', color='green')
    ax.plot(lowerboundLine,     label='Lower bound (this study)', color='blue')
    ax.plot(bestGuessLine,      label='Best guess (this study)', color='magenta')
    ax.plot(zade2015Line,       label = 'Zade (2018)',linestyle='-.', color='black')
    ax.plot(zade2016Line,       linestyle='-.', color='black')
    ax.plot(zade2017Line,       linestyle='-.', color='black')
    ax.plot(zade2018Line,       linestyle='-.', color='black')
    ax.plot(krause2016Line,     label = 'Krause & Tolalymat (2018)', linestyle=':', color='red')
    ax.plot(krause2017Line,     linestyle=':', color='red')
    ax.plot(krause2018Line,     linestyle=':', color='red')
    ax.scatter(cleancoins_x,cleancoins_y, c='black', label='Cleancoin', marker="s")


    ax.set_xlabel('Date')
    ax.set_ylabel('Estimated TWh per year')
    plt.title('Comparison of Ethereum energy usage estimates in other studies.')
    plt.legend()

    #plt.xticks(rotation=45)
    plt.show()
