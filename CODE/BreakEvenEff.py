import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import sys
import csv, json
import statistics

#BreakEvenEfficiency by date
with open('../JSONDATA/plotdata.json') as f:
    plotdata = reversed(json.load(f))
#Blockdata from etherscan API (crawler)
with open('../JSONDATA/EtherscanCrawler/CrawlerBlockDataAdjustedUncles.json', 'r') as r:
    crawlerblockdata = json.load(r)
#Blockdata from etherscan graphs
with open('../JSONDATA/Etherscan/DailyData.json') as r:
    blockdata = json.load(r)
#Gpudata from multiple sources
with open('../JSONDATA/GPUdata/GPUDATA.json') as r:
    gpudata = json.load(r)

def csvtojson(input, output):
    csvfile = open(input, 'r')
    jsonfile= open(output, 'w')
    reader = csv.reader(csvfile)
    rownames = next(reader)
    reader  = csv.DictReader(csvfile, rownames)
    out = json.dumps([row for row in reader],indent=4)
    jsonfile.write(out)

def getMatchingHardwareEfficiency(efficiency, datetuple):
    gpulist = getDateSet(datetuple) # Get a list of all hardware realeased in a given timeperiod 'datetuple'
    scores = list()
    if gpulist:
        for i in range (0, (len(gpulist))):
            if(float(gpulist[i]['Efficiency in J/Mh']) < efficiency):
                score = (i, efficiency-float(gpulist[i]['Efficiency in J/Mh']))
                scores.append(score)
            if scores:
                scores = sorted(scores, key=lambda x:x[1]) #Sort scores such that the closest match is the first element
                return float(gpulist[scores[0][0]]['Efficiency in J/Mh'])
            else:
                return -1
    else:
        return -1
    # # Testprint
    # for i in range (0, len(scores)-1):
    #     print(gpulist[scores[i][0]]['Product'] + "Efficiency = " +gpulist[scores[i][0]]['Efficiency in J/Mh'] + " J/Mh\n")

#Takes begindate and enddate as tuple of datetime obj and returns a list of hardware that has been released in that timeframe
def getDateSet(datetuple):
    begindate, enddate = datetuple
    gpulist = list()
    for gpu in gpudata:
        date = datetime.strptime(gpu['Release date'], "%m/%d/%Y")
        if date > begindate and date <= enddate:
            gpulist.append(gpu)
    return gpulist


def getBlockReward(blocknr):
    #Blockreward was originally 5 ETH (untill blocknr 4369999), this changed to 3 ETH with EIP-649 (blocknr 7,280,000) and to 2 ETH with EIP-1234
    if blocknr <= 4369999:
        reward = 5
    elif blocknr > 4369999 and blocknr < 7280000:
        reward = 3
    else:
        reward = 2
    return reward

def getblockReward(date):
    dateobj = datetime.strptime(date, "%m/%d/%Y")
    EIP649 = datetime.strptime("10/16/2017", "%m/%d/%Y")
    EIP1234 = datetime.strptime("3/1/2019", "%m/%d/%Y")
    if dateobj <= EIP649:
        reward = 5
    elif dateobj > EIP649 and dateobj < EIP1234:
        reward = 3
    else:
        reward = 2
    return reward


def getUncleReward(blocknr):
    return (getBlockReward(blocknr) * (7/8))

def calcBreakEvenEffCrawler(hashrate, blocktime, ETHPrice, timespan, nrOfBlocks, blockReward, uncleReward, unclerate, PriceperKWh):
    #Profitable efficiency
    ETHProfitGenerated = (nrOfBlocks*blockReward+(unclerate*nrOfBlocks*uncleReward))*ETHPrice
    BreakEvenEfficiency = ((ETHProfitGenerated/PriceperKWh)*3600000)/(timespan*hashrate)
    return BreakEvenEfficiency

def calcBreakEvenEff(dailyETHreward, ethprice, PriceperKWh, timespan, hashrate):
    ETHProfitGenerated = dailyETHreward * ethprice
    BreakEvenEfficiency = ((ETHProfitGenerated/PriceperKWh)*3600000)/(timespan*hashrate)
    return BreakEvenEfficiency

#Outputs BreakEvenEfficiency from blockdata averages JSON to JSON
def calcBreakEvenEffSet(PriceperKWh, blockdata):
    dps = list()
    for i in range (0, len(blockdata)):
        dp = {}
        dp['date'] = blockdata[i]['date']
        dp['BreakEvenEfficiency'] = calcBreakEvenEff(float(blockdata[i]['dailyETHreward']),
                                                     float(blockdata[i]['ethprice']),
                                                     PriceperKWh,
                                                     float(blockdata[i]['timespan']),
                                                     float(blockdata[i]['calculatedhashrate']/1000000)
                                                     )
        dp['BreakEvenEfficiencyUncles'] = calcBreakEvenEff(float(blockdata[i]['dailyETHreward']),
                                                     float(blockdata[i]['ethprice']),
                                                     PriceperKWh,
                                                     float(blockdata[i]['timespan']),
                                                     float(blockdata[i]['correctedhashrate']/1000000)
                                                     )
        dp['BreakEvenEfficiencyActual'] = calcBreakEvenEff(float(blockdata[i]['dailyETHreward']),
                                                     float(blockdata[i]['ethprice']),
                                                     PriceperKWh,
                                                     float(blockdata[i]['timespan']),
                                                     float(blockdata[i]['averagehashrate']/1000000)
                                                     )
        dps.append(dp)
    return dps

def calcBreakEvenEffSetCrawler(PriceperKWh, blockdata):
    dps = list()
    for i in range (0, len(blockdata)):
        dp = {}
        dp['date'] = blockdata[i]['date']
        dp['BreakEvenEfficiency'] = calcBreakEvenEffCrawler(float(blockdata[i]['averagehashrate'])/1000000,
                                                     float(blockdata[i]['averageblocktime']),
                                                     float(blockdata[i]['ethprice']),
                                                     float(blockdata[i]['timespan']),
                                                     float(blockdata[i]['amountOfBlocks']),
                                                     getBlockReward(blockdata[i]['blocknr']),
                                                     getUncleReward(blockdata[i]['blocknr']),
                                                     float(blockdata[i]['unclerate']),
                                                     PriceperKWh)
        dp['BreakEvenEfficiencyUncles'] = calcBreakEvenEffCrawler(float(blockdata[i]['correctedhashrate'])/1000000,
                                                     float(blockdata[i]['averageblocktime']),
                                                     float(blockdata[i]['ethprice']),
                                                     float(blockdata[i]['timespan']),
                                                     float(blockdata[i]['amountOfBlocks']),
                                                     getBlockReward(blockdata[i]['blocknr']),
                                                     getUncleReward(blockdata[i]['blocknr']),
                                                     float(blockdata[i]['unclerate']),
                                                     PriceperKWh)
        dps.append(dp)
    return reversed(dps)

def calcEnergyUsage(PriceperKWh):
    phases = [(0, 200),(201, 454), (455, 598), (599,778), (779, 970), (971, 1106), (1107, 1141), (1142, 1237), (1238, 1275), (1276, 1479), (1480, 1538), (1539, 1629)]
    datephases = []
    for i in range(0,(len(phases))):
        datephases.append(
                            (
                            datetime.strptime(blockdata[phases[i][0]]['date'],"%m/%d/%Y"),
                            datetime.strptime(blockdata[phases[i][1]]['date'],"%m/%d/%Y")
                            )
                        )
    breakevenset = calcBreakEvenEffSet(PriceperKWh, blockdata)
    EnergyUsageSum = 0
    for i in range(0, len(phases)):
        breakEvenSlice = breakevenset[phases[i][0]:phases[i][1]]
        hashRateSlice = blockdata[phases[i][0]:phases[i][1]]

        df_eff = pd.DataFrame(breakEvenSlice)
        meanBreakEvenEff = df_eff.mean(axis=0)["BreakEvenEfficiencyUncles"]
        phaseHardwareEfficiencyJMh = getMatchingHardwareEfficiency(meanBreakEvenEff,datephases[i])
        if(phaseHardwareEfficiencyJMh == -1):
            phaseHardwareEfficiencyJMh = getMatchingHardwareEfficiency(meanBreakEvenEff,datephases[i-1])
            #If no matching hardware was found in given timeperiod, look for the hardware in the previous timeperiod
            print("Period= " + datephases[i][0].strftime("%m/%d/%Y") + "  -  " + datephases[i][1].strftime("%m/%d/%Y"))
            print("NO HARDWARE FOUND IN THIS PERIOD")
            print("Mean eff in period: %i " % meanBreakEvenEff)
            print("Looking in period " + datephases[i-1][0].strftime("%m/%d/%Y") + "  -  " + datephases[i-1][1].strftime("%m/%d/%Y"))
            print("Corresponding efficiency: " + str(phaseHardwareEfficiencyJMh))
        else:
            print("Period= " + datephases[i][0].strftime("%m/%d/%Y") + "  -  " + datephases[i][1].strftime("%m/%d/%Y"))
            print("Mean eff in period: %i " % meanBreakEvenEff)
            print("Corresponding efficiency: " + str(phaseHardwareEfficiencyJMh))

        df_hr = pd.DataFrame(hashRateSlice)
        phaseHashRateMhs = df_hr.mean(axis=0)['correctedhashrate']/1e6
        phaseTimespan = df_hr.sum(axis=0)['timespan']
        phaseEnergyUsage = phaseTimespan*(phaseHashRateMhs*phaseHardwareEfficiencyJMh)
        EnergyUsageSum+=phaseEnergyUsage
        EnergyUsageTWh = EnergyUsageSum/3.6e15
    print("The total energy usage of Ethereum is %i Joule or %i TWh"% (EnergyUsageSum, EnergyUsageTWh))


def plotBreakEvenEff(BreakEvenEfficiencySet):
    df = pd.DataFrame(BreakEvenEfficiencySet)
    df.plot(kind='line', x='date', y=['BreakEvenEfficiency','BreakEvenEfficiencyUncles', 'BreakEvenEfficiencyActual'])
    plt.show()

def compareplots(d1, d2):
    df1 = pd.DataFrame(d1)
    df2 = pd.DataFrame(d2)
    df1.plot(kind='line', x='date', y=['BreakEvenEfficiency', 'BreakEvenEfficiencyUncles'])
    df2.plot(kind='line', x='date', y=['BreakEvenEfficiency', 'BreakEvenEfficiencyUncles', 'BreakEvenEfficiencyActual'])
    plt.locator_params(axis='x', nbins=20)
    plt.show()

def plottwoaxis(BreakEvenEfficiencySet):
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


#getMatchingHardware(5, "7/8/2019", "12/1/2019")
#csvtojson("transactions.csv", "transactions.json")
#csvtojson('../JSONDATA/GPUDATA/CSV/GPUDATA.csv', '../JSONDATA/GPUDATA/GPUDATA.json')
# breakevenset = calcBreakEvenEffSet(0.10, blockdata)
# breakevensetcrawler = calcBreakEvenEffSetCrawler(0.10, crawlerblockdata)
# compareplots(breakevensetcrawler,breakevenset)
#plottwoaxis(breakevenset)
calcEnergyUsage(0.10)

#getMatchingHardwareEfficiency(11, (datetime.strptime("4/7/2014", "%m/%d/%Y"), datetime.strptime("4/15/2015", "%m/%d/%Y")))
#plotBreakEvenEff(plotdata)
#calcBreakEvenEffSetCrawler(0.10, crawlerblockdata, '../JSONDATA/plotdata.json')
