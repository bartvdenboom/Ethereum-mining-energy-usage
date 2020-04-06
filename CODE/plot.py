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
with open('../JSONDATA/UpperBoundEstimate10.json') as f:
    upperBoundData10 = json.load(f)
with open('../JSONDATA/LowerBoundEstimate.json') as f:
    lowerBoundData = json.load(f)
with open('../JSONDATA/LowerBoundEstimate10.json') as f:
    lowerBoundData10 = json.load(f)
with open('../JSONDATA/BestGuessEstimate.json') as f:
    bestGuessData = json.load(f)
with open('../JSONDATA/BestGuessEstimate10.json') as f:
    bestGuessData10 = json.load(f)


def csvtojson(input, output):
    csvfile = open(input, 'r')
    jsonfile= open(output, 'w')
    reader = csv.reader(csvfile)
    rownames = next(reader)
    reader  = csv.DictReader(csvfile, rownames)
    out = json.dumps([row for row in reader],indent=4)
    jsonfile.write(out)

# csvtojson('../JSONDATA/Digiconomist/data.csv','../JSONDATA/Digiconomist/data.json' )

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

def plotLowerBoundResult():
    lowerbound_MW_x = pd.to_datetime(pd.DataFrame(lowerBoundData)['Date'])
    lowerbound_MW_y = [date['MegaWatts'] for date in lowerBoundData]
    lowerboundLine_MW = pd.Series(data=lowerbound_MW_y, index=lowerbound_MW_x)

    lowerbound_EFF_x = pd.to_datetime(pd.DataFrame(lowerBoundData)['Date'])
    lowerbound_EFF_y = [date['HardwareEfficiency'] for date in lowerBoundData]
    lowerboundLine_EFF = pd.Series(data=lowerbound_EFF_y, index=lowerbound_EFF_x)

    fig, ax1 = plt.subplots()
    color='green'
    ax1.set_ylabel('Power consumption (MW)', color=color)
    ax1.set_xlabel('Date')
    ax1.tick_params(axis='y',colors=color)
    line1 = ax1.plot(lowerboundLine_MW, color=color, label='Lower bound power consumption ')

    ax2 = ax1.twinx()
    color='red'
    ax2.set_ylabel('Hardware Efficiency (J/MH)',color=color)
    ax2.tick_params(colors=color)
    line2 = ax2.plot(lowerboundLine_EFF, color=color, label='Lower bound hardware Efficiency')
    plt.title('Power consumption and hardware efficiency (lower bound)')
    fig.tight_layout()
    first_legend = ax1.legend(handles = [line1[0], line2[0]] )
    # second_legend = ax2.legend(handles = line2, loc = 'center right')
    ax1.add_artist(first_legend)
    # ax2.add_artist(second_legend)
    plt.show()

def plotUpperBoundResult():
    upperbound_MW_x = pd.to_datetime(pd.DataFrame(upperBoundData)['Date'])
    upperbound_MW_y = [date['MegaWatts'] for date in upperBoundData]
    upperboundLine_MW = pd.Series(data=upperbound_MW_y, index=upperbound_MW_x)

    upperbound_EFF_x = pd.to_datetime(pd.DataFrame(upperBoundData)['Date'])
    upperbound_EFF_y = [date['HardwareEfficiency'] for date in upperBoundData]
    upperboundLine_EFF = pd.Series(data=upperbound_EFF_y, index=upperbound_EFF_x)

    upperbound_THR_EFF_x = pd.to_datetime(pd.DataFrame(upperBoundData)['Date'])
    upperbound_THR_EFF_y = [date['BreakEvenEfficiency'] for date in upperBoundData]
    upperboundLine_THR_EFF = pd.Series(data=upperbound_THR_EFF_y, index=upperbound_THR_EFF_x)

    fig, ax1 = plt.subplots()
    color='green'
    ax1.set_ylabel('Power consumption (MW)', color=color)
    ax1.set_xlabel('Date')
    ax1.tick_params(axis='y',colors=color)
    line1 = ax1.plot(upperboundLine_MW, color=color, label='Upper bound power consumption ')

    ax2 = ax1.twinx()
    color='red'
    ax2.set_ylabel('Hardware Efficciency (J/MH)',color=color)
    ax2.tick_params(colors=color)
    ax2.set_ylim(top=225)
    line2 = ax2.plot(upperboundLine_EFF, color=color, label='Upper bound hardware Efficiency')
    line3 = ax2.plot(upperboundLine_THR_EFF, color=color, linestyle=':', label='Profitability Threshold')
    plt.title('Power consumption and hardware efficiency (upper bound)')
    fig.tight_layout()
    first_legend = ax1.legend(handles = [line1[0], line2[0], line3[0]], loc='upper right' )
    # second_legend = ax2.legend(handles = line2, loc = 'center right')
    ax1.add_artist(first_legend)
    # ax2.add_artist(second_legend)
    plt.show()

def plotBestGuessResult():
    bestguess_MW_x = pd.to_datetime(pd.DataFrame(bestGuessData)['Date'])
    bestguess_MW_y = [date['MegaWatts'] for date in bestGuessData]
    bestguessLine_MW = pd.Series(data=bestguess_MW_y, index=bestguess_MW_x)

    bestguess_EFF_x = pd.to_datetime(pd.DataFrame(bestGuessData)['Date'])
    bestguess_EFF_y = [date['HardwareEfficiency'] for date in bestGuessData]
    bestguessLine_EFF = pd.Series(data=bestguess_EFF_y, index=bestguess_EFF_x)

    bestguess_THR_EFF_x = pd.to_datetime(pd.DataFrame(bestGuessData)['Date'])
    bestguess_THR_EFF_y = [date['BreakEvenEfficiency'] for date in bestGuessData]
    bestguessLine_THR_EFF = pd.Series(data=bestguess_THR_EFF_y, index=bestguess_THR_EFF_x)

    fig, ax1 = plt.subplots()
    color='green'
    ax1.set_ylabel('Power consumption (MW)', color=color)
    ax1.set_xlabel('Date')
    ax1.tick_params(axis='y',colors=color)
    line1 = ax1.plot(bestguessLine_MW, color=color, label='Best guess power consumption ')

    ax2 = ax1.twinx()
    color='red'
    ax2.set_ylabel('Hardware Efficciency (J/MH)',color=color)
    ax2.tick_params(colors=color)
    ax2.set_ylim(top=225)

    line2 = ax2.plot(bestguessLine_EFF, color=color, label='Best guess hardware Efficiency')
    line3 = ax2.plot(bestguessLine_THR_EFF, color=color, linestyle=':', label='Profitability Threshold')
    plt.title('Power consumption and hardware efficiency (Best guess)')
    fig.tight_layout()
    first_legend = ax1.legend(handles = [line1[0], line2[0], line3[0]], loc='upper right' )
    # second_legend = ax2.legend(handles = line2, loc = 'center right')
    ax1.add_artist(first_legend)
    # ax2.add_artist(second_legend)
    plt.show()

def plotResultsVariableEnergyPrice():
    # 0.05 USD/KWh
    lowerbound_MW_x = pd.to_datetime(pd.DataFrame(lowerBoundData)['Date'])
    lowerbound_MW_y = [date['MegaWatts'] for date in lowerBoundData]
    lowerboundLine_MW = pd.Series(data=lowerbound_MW_y, index=lowerbound_MW_x)

    bestguess_MW_x = pd.to_datetime(pd.DataFrame(bestGuessData)['Date'])
    bestguess_MW_y = [date['MegaWatts'] for date in bestGuessData]
    bestguessLine_MW = pd.Series(data=bestguess_MW_y, index=bestguess_MW_x)

    upperbound_MW_x = pd.to_datetime(pd.DataFrame(upperBoundData)['Date'])
    upperbound_MW_y = [date['MegaWatts'] for date in upperBoundData]
    upperboundLine_MW = pd.Series(data=upperbound_MW_y, index=upperbound_MW_x)

    # 0.10 USD/KWh
    lowerbound_MW_x_10 = pd.to_datetime(pd.DataFrame(lowerBoundData10)['Date'])
    lowerbound_MW_y_10 = [date['MegaWatts'] for date in lowerBoundData10]
    lowerboundLine_MW_10 = pd.Series(data=lowerbound_MW_y_10, index=lowerbound_MW_x_10)

    bestguess_MW_x_10 = pd.to_datetime(pd.DataFrame(bestGuessData10)['Date'])
    bestguess_MW_y_10 = [date['MegaWatts'] for date in bestGuessData10]
    bestguessLine_MW_10 = pd.Series(data=bestguess_MW_y_10, index=bestguess_MW_x_10)

    upperbound_MW_x_10 = pd.to_datetime(pd.DataFrame(upperBoundData10)['Date'])
    upperbound_MW_y_10 = [date['MegaWatts'] for date in upperBoundData10]
    upperboundLine_MW_10 = pd.Series(data=upperbound_MW_y_10, index=upperbound_MW_x_10)

    fig, ax = plt.subplots()
    color='green'
    ax.set_ylabel('Power consumption (MW)')
    ax.set_xlabel('Date')
    color='blue'
    lower5 = ax.plot(lowerboundLine_MW, color=color, label='Lower bound (0.05 - 0.10 USD/KWh)')
    lower10 = ax.plot(lowerboundLine_MW_10, color=color)
    color='magenta'
    best5 = ax.plot(bestguessLine_MW, color=color, label='Best guess (0.05 - 0.10 USD/KWh)')
    best10 = ax.plot(bestguessLine_MW_10, color=color)
    color='green'
    upper5 = ax.plot(upperboundLine_MW, color=color, label='Upper bound (0.05 - 0.10 USD/KWh)')
    upper10 =ax.plot(upperboundLine_MW_10, color=color)

    ax.fill_between(lowerbound_MW_x, bestguess_MW_y,bestguess_MW_y_10, color='magenta', alpha=0.5)
    ax.fill_between(lowerbound_MW_x, upperbound_MW_y,upperbound_MW_y_10, color='green', alpha=0.5)


    plt.title('Effect of energy price on power consumption')
    fig.tight_layout()
    legend = ax.legend(handles = [lower5[0],  best5[0], upper5[0]], loc='upper left' )
    ax.add_artist(legend)
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
    line2 = ax1.plot(hardwareLine, color='green', label='Used hardware Efficciency (J/MH)')
    # ax1.axvline(x=pd.to_datetime("7/1/2018"),color='red')
    # ax1.axvline(x=pd.to_datetime("9/1/2018"),color='red')
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
    upperbound_y = [date['MegaWatts'] for date in upperBoundData]
    upperboundLine = pd.Series(data=upperbound_y, index=upperbound_x)

    lowerbound_x = pd.to_datetime(pd.DataFrame(lowerBoundData)['Date'])
    lowerbound_y = [date['MegaWatts'] for date in lowerBoundData]
    lowerboundLine = pd.Series(data=lowerbound_y, index=lowerbound_x)

    bestguess_x = pd.to_datetime(pd.DataFrame(bestGuessData)['Date'])
    bestguess_y = [date['MegaWatts'] for date in bestGuessData]
    bestGuessLine = pd.Series(data=bestguess_y, index=bestguess_x)

    #Digiconomist estimate
    digiconomist_x = pd.to_datetime(pd.DataFrame(DigiconomistData)['Date'])
    digiconomist_y = [((float(date['EECI'])*1e6)/8765.81277) for date in DigiconomistData]
    digiconomistLine = pd.Series(data=digiconomist_y, index=digiconomist_x)

    #Cleancoins initiative estimate
    cleancoins_x = pd.to_datetime(pd.DataFrame(["3/5/2020"])[0])
    cleancoins_y = ((float(5.65)*1e6)/8765.81277)
    cleancoinsLine = pd.Series(data=cleancoins_y, index=cleancoins_x)

    #Zade (2018)
    zade_x2015 = pd.to_datetime(pd.DataFrame(["1/1/2015","12/31/2015"])[0])
    zade_y2015 = [3.0,3.0]
    zade2015Line = pd.Series(data=zade_y2015, index=zade_x2015)
    zade_x2016 = pd.to_datetime(pd.DataFrame(["1/1/2016","12/31/2016"])[0])
    zade_y2016 = [19.0,19.0]
    zade2016Line = pd.Series(data=zade_y2016, index=zade_x2016)
    zade_x2017 = pd.to_datetime(pd.DataFrame(["1/1/2017","12/31/2017"])[0])
    zade_y2017 = [367.0,367.0]
    zade2017Line = pd.Series(data=zade_y2017, index=zade_x2017)
    zade_x2018 = pd.to_datetime(pd.DataFrame(["1/1/2018","10/31/2018"])[0])
    zade_y2018 = [991.0,991.0]
    zade2018Line = pd.Series(data=zade_y2018, index=zade_x2018)

    #Krause (2019)
    krause_x2016 = pd.to_datetime(pd.DataFrame(["1/1/2016","12/31/2016"])[0])
    krause_y2016 = [24.0,24.0]
    krause2016Line = pd.Series(data=krause_y2016, index=krause_x2016)
    krause_x2017 = pd.to_datetime(pd.DataFrame(["1/1/2017","12/31/2017"])[0])
    krause_y2017 = [299.9,299.0]
    krause2017Line = pd.Series(data=krause_y2017, index=krause_x2017)
    krause_x2018 = pd.to_datetime(pd.DataFrame(["1/1/2018","6/30/2018"])[0])
    krause_y2018 = [1165.0,1165.0]
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
    ax.set_ylabel('Estimated power usage (MW)')
    plt.title('Comparison of Ethereum energy usage estimates in other studies.')
    plt.legend()

    #plt.xticks(rotation=45)
    plt.show()

def plotProfThres():
    breakeven_x = pd.to_datetime(pd.DataFrame(upperBoundData)['Date'])
    breakeven_y = [date['BreakEvenEfficiency'] for date in upperBoundData]
    breakevenLine = pd.Series(data=breakeven_y, index=breakeven_x)

    hashrate_x = pd.to_datetime(pd.DataFrame(blockdata)['date'])
    hashrate_y = [date['computedhashrate'] for date in blockdata]
    hashrateLine = pd.Series(data=hashrate_y, index=hashrate_x)

    ethprice_x = pd.to_datetime(pd.DataFrame(blockdata)['date'])
    ethprice_y = [date['ethprice'] for date in blockdata]
    ethpriceLine =pd.Series(data=ethprice_y, index=ethprice_x)

    fig, ax1 = plt.subplots()
    color='green'
    ax1.set_ylabel('Profitability Threshold (J/MH)',color=color)
    ax1.set_xlabel('Date')
    ax1.tick_params(axis='y',colors=color)
    line1 = ax1.plot(breakevenLine, color=color)

    ax2 = ax1.twinx()
    color='red'
    ax2.set_ylabel('ETH/USD',color=color)
    ax2.tick_params(axis='y',colors=color)
    line2 = ax2.plot(ethpriceLine, color=color)

    plt.title('Profitablity Threshold (green) and ETH/USD (red) against time.')
    fig.tight_layout()
    plt.show()
