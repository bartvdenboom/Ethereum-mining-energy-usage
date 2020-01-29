import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import csv, json
import statistics
import plot

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
        gpuReleaseDate = datetime.strptime(gpu['Release date'], "%m/%d/%Y")
        if gpuReleaseDate <= enddate:
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
    with open('../JSONDATA/Etherscan/BreakEvenPlotData.json', 'w') as w:
        json.dump(dps, w, indent=4)

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

hashratedata = list()

def calcAvgEfficiency(phaseHardwareEfficiency, hashrateIncrease):
    global cumulativeHardwareEfficiency, totalHashRateIncrease, hashratedata
    if(hashrateIncrease>0):
        hashratedata.append((phaseHardwareEfficiency, hashrateIncrease))
    else:
        maxEfficiency = np.max(np.array(hashratedata), axis=0)[0]
        print("Removing %f Mh/s of hashing power with efficiency of %f J/Mh" % (-hashrateIncrease, maxEfficiency))
        hashratedata.append((maxEfficiency, hashrateIncrease))

def getAvgWeighedHardwareEfficiency():
    if not hashratedata:
        return 0
    cumulativeHardwareEfficiency = np.sum(np.prod(np.array(hashratedata), axis=1),axis=0)
    cumulativeWeight = np.sum(np.array(hashratedata),axis=0)[1]
    return cumulativeHardwareEfficiency/cumulativeWeight

def calcTotalEnergyUsage(PriceperKWh, phases):
    datePhases = []
    efficiencyData = []
    lol= 10
    for i in range(0,(len(phases))):
        datePhases.append(
                            (
                            datetime.strptime(blockdata[phases[i][0]]['date'],"%m/%d/%Y"),
                            datetime.strptime(blockdata[phases[i][1]]['date'],"%m/%d/%Y")
                            )
                        )
    breakEvenSet = calcBreakEvenEffSet(PriceperKWh, blockdata)
    energyUsageSum = 0
    for i in range(0, len(phases)):
        breakEvenSlice = breakEvenSet[phases[i][0]:phases[i][1]+1]
        hashRateSlice = blockdata[phases[i][0]:phases[i][1]+1]
        df_eff = pd.DataFrame(breakEvenSlice)
        df_hr = pd.DataFrame(hashRateSlice)
        meanBreakEvenEff = df_eff.mean(axis=0)["BreakEvenEfficiencyUncles"]
        phaseHashRateMhs = df_hr.mean(axis=0)['correctedhashrate']/1e6
        phaseBeginHashRateMhs = hashRateSlice[0]['correctedhashrate']/1e6
        phaseEndHashRateMhs   = hashRateSlice[len(hashRateSlice)-1]['correctedhashrate']/1e6
        phaseHashRateMhsIncrease = (phaseEndHashRateMhs - phaseBeginHashRateMhs)
        phaseTimespan = df_hr.sum(axis=0)['timespan']

        if(phaseHashRateMhsIncrease>0):
            phaseHardwareEfficiencyJMh = getMatchingHardwareEfficiency(meanBreakEvenEff,datePhases[i])
            j=0
            while(getMatchingHardwareEfficiency(meanBreakEvenEff,datePhases[i-j]) == -1):
                j+=1
                phaseHardwareEfficiencyJMh = getMatchingHardwareEfficiency(meanBreakEvenEff,datePhases[i-j])
            selectedHardwareEfficiency = phaseHardwareEfficiencyJMh
            phaseAddedWattage = (phaseHashRateMhsIncrease*selectedHardwareEfficiency)

            #phaseAddedEnergyUsage = phaseTimespan*(phaseHashRateMhsIncrease*selectedHardwareEfficiency)
        else:
            selectedHardwareEfficiency = getAvgWeighedHardwareEfficiency()
            phaseAddedWattage = 0

        avgWeighedHardwareEfficiency = getAvgWeighedHardwareEfficiency()
        if(avgWeighedHardwareEfficiency==0):
            phaseBeginWattage = phaseBeginHashRateMhs*selectedHardwareEfficiency
            #Accounting for the first period, where there is no weighed average of efficiency, so just use the known hardware efficiency
        else:
            phaseBeginWattage = phaseBeginHashRateMhs*avgWeighedHardwareEfficiency

        calcAvgEfficiency(selectedHardwareEfficiency, phaseHashRateMhsIncrease)

        #print("avgWeighedHardwareEfficiency = %f" % avgWeighedHardwareEfficiency)
        for k in range(len(breakEvenSlice)):
            phaseData = {}
            phaseData['Period'] = datetime.strftime(datePhases[i][0], "%m/%d/%Y") + "  -  " + datetime.strftime(datePhases[i][1], "%m/%d/%Y")
            phaseData['Date'] = breakEvenSlice[k]['date']
            phaseData['EfficiencyPeriod'] = datetime.strftime(datePhases[i-j][0], "%m/%d/%Y") + "  -  " + datetime.strftime(datePhases[i-j][1], "%m/%d/%Y")
            phaseData['BreakEvenEfficiency'] = breakEvenSlice[k]['BreakEvenEfficiencyUncles']
            phaseData['phaseHashRateMhsIncrease'] = float(phaseHashRateMhsIncrease)
            phaseData['selectedHardwareEfficiencyJMh'] = float(selectedHardwareEfficiency)
            phaseData['phaseBeginEnergyWattage'] = float(phaseBeginWattage)
            phaseData['phaseAddedEnergyWattage'] = float(phaseAddedWattage)
            efficiencyData.append(phaseData)


        energyUsageSum+=(phaseBeginWattage+phaseAddedWattage)*phaseTimespan
        EnergyUsageTWh = energyUsageSum/3.6e15
    with open('../JSONDATA/Etherscan/phaseData.json', 'w') as w:
        json.dump(efficiencyData, w, indent=4)
    print("The total energy usage of Ethereum is %i Joule or %i TWh"% (energyUsageSum, EnergyUsageTWh))


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
#getMatchingHardwareEfficiency(11, (datetime.strptime("4/7/2014", "%m/%d/%Y"), datetime.strptime("4/15/2015", "%m/%d/%Y")))
#plotBreakEvenEff(plotdata)
#calcBreakEvenEffSetCrawler(0.10, crawlerblockdata, '../JSONDATA/plotdata.json')
def ceiling_division(n, d):
    return -(n // -d)

def generatePhases(blockdata, interval):
    phases = list()
    for i in range(ceiling_division(len(blockdata),interval)):
        if i==0:
            begin = 0
            end = interval-1
            if(end>=len(blockdata)):
                end = len(blockdata)-1
        else:
            begin = i*interval
            end = (i*interval)+interval-1
            if(end>=len(blockdata)):
                end = len(blockdata)-1
        phases.append(
                        (
                        begin,
                        end
                        )
        )
        i+=interval
    return phases

def main():
    phasesManual = [(0, 200),(201, 454), (455, 598), (599,778), (779, 970), (971, 1106), (1107, 1141), (1142, 1237), (1238, 1275), (1276, 1479), (1480, 1538), (1539, 1621)]
    phases = generatePhases(blockdata, 14)
    calcTotalEnergyUsage(0.05,phasesManual)
    plot.plotBreakEvenEffAgainstSelectedEfficiency()
main()
