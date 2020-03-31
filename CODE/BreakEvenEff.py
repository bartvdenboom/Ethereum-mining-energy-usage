import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import csv, json
import statistics
import plot
import time

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

hashratedata = list()
EFFICIENCYMARGIN = 0.05


def csvtojson(input, output):
    csvfile = open(input, 'r')
    jsonfile= open(output, 'w')
    reader = csv.reader(csvfile)
    rownames = next(reader)
    reader  = csv.DictReader(csvfile, rownames)
    out = json.dumps([row for row in reader],indent=4)
    jsonfile.write(out)


def ceiling_division(n, d):
    return -(n // -d)

def generatePhases(blockdata, interval, endDate):
    for i in range(len(blockdata)):
        if(blockdata[i]['date'] == endDate):
            index = i+1
            break

    phases = list()
    for i in range(ceiling_division(index,interval)):
        if i==0:
            begin = 0
            end = interval-1
            if(end>=index):
                end = index-1
        else:
            begin = i*interval
            end = (i*interval)+interval-1
            if(end>=index):
                end = index-1
        phases.append((begin, end))
        i+=interval
    return phases

#Takes begindate and enddate as tuple of datetime obj and returns a list of hardware that has been released in that timeframe
def getDateSet(datetuple):
    begindate, enddate = datetuple
    gpulist = list()
    for gpu in gpudata:
        gpuReleaseDate = datetime.strptime(gpu['Release date'], "%m/%d/%Y")
        if gpuReleaseDate <= begindate:
            gpulist.append(gpu)
    return gpulist

def getDateSetBestGuess(datetuple):
    begindate, enddate = datetuple
    gpulist = list()
    for gpu in gpudata:
        gpuReleaseDate = datetime.strptime(gpu['Release date'], "%m/%d/%Y")
        if gpuReleaseDate <= begindate and gpuReleaseDate > (begindate-timedelta(days=365)):
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
                                                     float(blockdata[i]['computedhashrate']/1000000)
                                                     )
        dp['BreakEvenEfficiencyActual'] = calcBreakEvenEff(float(blockdata[i]['dailyETHreward']),
                                                     float(blockdata[i]['ethprice']),
                                                     PriceperKWh,
                                                     float(blockdata[i]['timespan']),
                                                     float(blockdata[i]['reportedhashrate']/1000000)
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


def addToHardwareMix(phaseHardwareEfficiency, hashrateIncrease, releaseDate):
    hashratedata.append((phaseHardwareEfficiency, hashrateIncrease, releaseDate))

def getHardwareMixEfficiency():
    if not hashratedata:
        return -1
    hardwaremix = np.array(hashratedata)[:,:2].astype(float)
    cumulativeHardwareEfficiency = np.sum(np.prod(hardwaremix, axis=1),axis=0)
    cumulativeWeight = np.sum(hardwaremix,axis=0)[1]
    return cumulativeHardwareEfficiency/cumulativeWeight

def getMaxHardwareEfficiency():
    if not hashratedata:
        return -1
    l = list()
    for h in hashratedata:
        if(h[1]>0):
            l.append(h)
    return sorted(l, key = lambda x:x[0], reverse=True)[0]

def getMatchingHardwareEfficiency(efficiency, datetuple, upperbound):
    gpulist = getDateSet(datetuple) # Get a list of all hardware realeased before the the phase 'datetuple'
    scores = list()
    if gpulist:
        for i in range (0, (len(gpulist))):
            if upperbound:
                if(float(gpulist[i]['Efficiency in J/Mh']) < efficiency and gpulist[i]['Type'] != "ASIC" and gpulist[i]['Type'] !="RIG"):
                    score = (i, efficiency-float(gpulist[i]['Efficiency in J/Mh']))
                    scores.append(score)
            else:
                if(float(gpulist[i]['Efficiency in J/Mh']) < efficiency):
                    score = (i, efficiency-float(gpulist[i]['Efficiency in J/Mh']))
                    scores.append(score)
        if scores:
            if upperbound:
                scores = sorted(scores, key=lambda x:x[1]) #Sort scores such that the closest match is the first element
                return (float(gpulist[scores[0][0]]['Efficiency in J/Mh']), datetime.strptime(gpulist[scores[0][0]]['Release date'],"%m/%d/%Y"))
            else:
                scores = sorted(scores, key=lambda x:x[1], reverse = True) #Sort scores such that the closest match is the first element
                return (float(gpulist[scores[0][0]]['Efficiency in J/Mh']), datetime.strptime(gpulist[scores[0][0]]['Release date'],"%m/%d/%Y"))
        else:
            return -1
            print("Error, no hardware")
    else:
        return -1
        print("Error, no hardware")

#TODO First remove ASIC from mean than, correct for 1% of asic efficiency when available.
def getBestGuessHardwareEfficiency(meanBreakEvenEff, datetuple):
    gpulist = getDateSetBestGuess(datetuple) # Get a list of all hardware realeased in a given timeperiod 'datetuple'
    scores = list()
    avg = 0
    if gpulist:
        for i in range (0, (len(gpulist))):
            if(float(gpulist[i]['Efficiency in J/Mh']) < meanBreakEvenEff):
                score = (i, meanBreakEvenEff-float(gpulist[i]['Efficiency in J/Mh']))
                avg += float(gpulist[i]['Efficiency in J/Mh'])
                scores.append(score)
        avg = avg/len(gpulist)+1
        if scores:
            scores = sorted(scores, key=lambda x:x[1], reverse = True) #Sort scores such that the closest match is the first element
            # print("Hardware")
            # for i in range(len(gpulist)):
            #     print("%s @ %s" % (gpulist[scores[i][0]]['Product'],gpulist[scores[i][0]]['Efficiency in J/Mh']) )
            # print("Min: %f" % float(gpulist[scores[0][0]]['Efficiency in J/Mh']))
            # print("Max: %f" % float(gpulist[scores[len(scores)-1][0]]['Efficiency in J/Mh']))
            # print("Avg: %f" % avg)
            # print("Median: %f" % float(gpulist[scores[int(len(scores)/2)][0]]['Efficiency in J/Mh']))
            # print('Median hardware: %s' % gpulist[scores[int(len(scores)/2)][0]]['Product'])
            # print("==============================")
            #return float(gpulist[scores[0][0]]['Efficiency in J/Mh'])
            return (float(gpulist[scores[int(len(scores)/2)][0]]['Efficiency in J/Mh']),gpulist[scores[int(len(scores)/2)][0]]['Release date'])#Median
        else:
            return -1
            print("Error, no hardware")
    else:
        return -1
        print("Error, no hardware")

# Replaces most inefficient hardware in the hardware-mix with hardware with hardware with efficiency 'hardwareEfficiency'
# untill the hardware-mix is within EFFICIENCYMARGIN of the target efficiency 'meanBreakEvenEff'
def replaceHardware(hardwareEfficiency, meanBreakEvenEff):
    if hashratedata:
        while(getHardwareMixEfficiency() - meanBreakEvenEff > EFFICIENCYMARGIN):
            hardwaremix = np.array(hashratedata)[:,:2].astype(float)
            cumulativeHardwareEfficiency = np.sum(np.prod(hardwaremix, axis=1),axis=0)
            cumulativeWeight = np.sum(hardwaremix,axis=0)[1]

            hashratedata.sort(key=lambda x:x[0], reverse = True)
            for i in range(len(hashratedata)):
                if(hashratedata[i][1] > 0 and hashratedata[i][0] != hardwareEfficiency):
                    maxReplaceAmount = hashratedata[i][1]
                    maxReplaceEfficiency = hashratedata[i][0]
                    releaseDate = hashratedata[i][2]
                    diff = cumulativeHardwareEfficiency - (meanBreakEvenEff*cumulativeWeight)
                    amountToReplace = diff//(maxReplaceEfficiency-hardwareEfficiency)
                    if(amountToReplace > maxReplaceAmount):
                        amountToReplace = maxReplaceAmount
                    hashratedata[i] = (hashratedata[i][0],(hashratedata[i][1]-amountToReplace))
                    addToHardwareMix(hardwareEfficiency, amountToReplace,releaseDate)
                    break
    else:
        print("Error: No hardware to replace.")
        return -1

def getHashrate():
    if hashratedata:
        hardwaremix = np.array(hashratedata)[:,:2].astype(float)
        return np.sum(np.array(hardwaremix),axis=0)[1]
    else:
        return 0

def calcTotalEnergyUsage(PriceperKWh, phases, upperBound):
    datePhases = []
    efficiencyData = []
    for i in range(0,(len(phases))):
        datePhases.append(
                            (
                            datetime.strptime(blockdata[phases[i][0]]['date'],"%m/%d/%Y"),
                            datetime.strptime(blockdata[phases[i][1]]['date'],"%m/%d/%Y")
                            )
                        )
    breakEvenSet = calcBreakEvenEffSet(PriceperKWh, blockdata)
    minHardwareEfficiency,d = getMatchingHardwareEfficiency(15,datePhases[len(datePhases)-1], False)
    totalWattage = 0
    energyUsageJoule = 0
    totalHashRate = 0
    yearlyTWh = 0
    for i in range(0, len(phases)):
        breakEvenSlice = breakEvenSet[phases[i][0]:phases[i][1]+1]
        hashRateSlice = blockdata[phases[i][0]:phases[i][1]+1]
        meanBreakEvenEff = pd.DataFrame(breakEvenSlice).mean(axis=0)["BreakEvenEfficiency"]
        phaseTimespan = pd.DataFrame(hashRateSlice).sum(axis=0)['timespan']
        phaseBeginHashRateMhs = hashRateSlice[0]['computedhashrate']/1e6
        phaseEndHashRateMhs   = hashRateSlice[len(hashRateSlice)-1]['computedhashrate']/1e6
        phaseHashRateMhsIncrease = (phaseEndHashRateMhs - phaseBeginHashRateMhs)
        if(i==0):
            selectedHardwareEfficiency, releaseDate = getMatchingHardwareEfficiency(meanBreakEvenEff,datePhases[i], upperBound)
            addToHardwareMix(selectedHardwareEfficiency, phaseBeginHashRateMhs,releaseDate)
            totalWattage+=(phaseBeginHashRateMhs*selectedHardwareEfficiency)
        else:
            if(phaseHashRateMhsIncrease>0):
                selectedHardwareEfficiency,releaseDate = getMatchingHardwareEfficiency(meanBreakEvenEff,datePhases[i], upperBound)#minHardwareEfficiency
                addToHardwareMix(selectedHardwareEfficiency, phaseHashRateMhsIncrease,releaseDate)
            else:
                phaseHardwareEfficiencyJMh,releaseDate = getMatchingHardwareEfficiency(meanBreakEvenEff,datePhases[i],upperBound)
                if upperBound:
                    releaseDate=datetime.strftime(datetime.today, "%m/%d/%Y")
                    addToHardwareMix(getHardwareMixEfficiency(), phaseHashRateMhsIncrease,releaseDate) # first remove the hashrate equivalent amount of wattage of the average hardware mix
                else:
                    removeMostInefficientHardware(phaseHashRateMhsIncrease)
                replaceHardware(phaseHardwareEfficiencyJMh,meanBreakEvenEff)
                selectedHardwareEfficiency = getHardwareMixEfficiency()
        totalHashRate = phaseEndHashRateMhs
        totalWattage = totalHashRate * getHardwareMixEfficiency()
        energyUsageJoule += totalWattage * phaseTimespan
        EnergyUsageTWh = energyUsageJoule/3.6e15
        yearlyTWh = ((totalWattage*8765.81277)/1e12)

        for k in range(len(breakEvenSlice)):
            phaseData = {}
            phaseData['Period'] = datetime.strftime(datePhases[i][0], "%m/%d/%Y") + "  -  " + datetime.strftime(datePhases[i][1], "%m/%d/%Y")
            phaseData['Date'] = breakEvenSlice[k]['date']
            phaseData['BreakEvenEfficiency'] = breakEvenSlice[k]['BreakEvenEfficiency']
            phaseData['phaseHashRateMhsIncrease'] = float(phaseHashRateMhsIncrease)
            phaseData['cumulativeHardwareEfficiency'] = float(getHardwareMixEfficiency())
            phaseData['yearlyTWh'] = float(yearlyTWh)
            efficiencyData.append(phaseData)
    if upperBound:
        with open('../JSONDATA/UpperBoundEstimate.json', 'w') as w:
            json.dump(efficiencyData, w, indent=4)
    else:
        with open('../JSONDATA/LowerBoundEstimate.json', 'w') as w:
            json.dump(efficiencyData, w, indent=4)
    print("The total energy usage of Ethereum is %f Joule or %f TWh"% (energyUsageJoule, EnergyUsageTWh))
    print("On " + datetime.strftime(datePhases[len(datePhases)-1][1],"%m/%d/%Y") + " the power draw was " + str(totalWattage/1e6) + " MW." )
    print("This equals %f TWh per year." % yearlyTWh)
    return efficiencyData

# Used in the Best-guess estimate
# Removes the most inefficient hardware from the harware-mix with amount equivalent to the amount of hashrate decline 'phaseHashRateMhsIncrease'
def removeMostInefficientHardware(phaseHashRateMhsIncrease):
    remainder = -phaseHashRateMhsIncrease
    i=0
    if hashratedata and remainder < getHashrate():
        hashratedata.sort(key=lambda x:x[0], reverse = True)
        while remainder > 0 and i < len(hashratedata):
            if(hashratedata[i][1] > 0):
                maxReplaceAmount = hashratedata[i][1]
                if(remainder > maxReplaceAmount):
                    hashratedata.pop(i)
                    amountToReplace = maxReplaceAmount
                else:
                    amountToReplace = remainder
                    hashratedata[i] = (hashratedata[i][0],(hashratedata[i][1]-amountToReplace),hashratedata[i][2])
                remainder -= amountToReplace
            i+=1
    else:
        return 0

def removeOldHardware(meanBreakEvenEff,datetuple):
    begindate,enddate = datetuple
    done=False
    if hashratedata:
        i=0
        while not done:
            if datetime.strptime(hashratedata[i][2],"%m/%d/%Y" )<(begindate-timedelta(days=365)):
                oldHardwareHashrate = hashratedata[i][1]
                newHardwareEfficiency, newHardwareReleaseDate = getBestGuessHardwareEfficiency(meanBreakEvenEff, datetuple)
                print("%s replaced with (%s,%s,%s)"%(hashratedata[i],newHardwareEfficiency, oldHardwareHashrate, newHardwareReleaseDate))
                hashratedata.pop(i)
                addToHardwareMix(newHardwareEfficiency, oldHardwareHashrate, newHardwareReleaseDate)
            if (i < len(hashratedata)-1):
                i+=1
            else:
                done = True
    else:
        return -1

# def removeOldHardware(meanBreakEvenEff,datetuple):
#     begindate,enddate = datetuple
#     if hashratedata:
#         for i in range(len(hashratedata)):
#             if datetime.strptime(hashratedata[i][2],"%m/%d/%Y" )<(begindate-timedelta(days=365)):
#                 oldHardwareHashrate = hashratedata[i][1]
#                 newHardwareEfficiency, newHardwareReleaseDate = getBestGuessHardwareEfficiency(meanBreakEvenEff, datetuple)
#                 print("%s replaced with (%s,%s,%s)"%(hashratedata[1],newHardwareEfficiency, oldHardwareHashrate, newHardwareReleaseDate))
#                 hashratedata.pop(i)
#                 print(len(hashratedata))
#                 addToHardwareMix(newHardwareEfficiency, oldHardwareHashrate, newHardwareReleaseDate)
#                 # if (i < len(hashratedata)-1):
#                 #     i+=1
#                 # else:
#                 #     done = True
#     else:
#         return -1

def bestGuessEstimate(PriceperKWh, phases):
    datePhases = []
    efficiencyData = []
    for i in range(0,(len(phases))):
        datePhases.append(
                            (
                            datetime.strptime(blockdata[phases[i][0]]['date'],"%m/%d/%Y"),
                            datetime.strptime(blockdata[phases[i][1]]['date'],"%m/%d/%Y")
                            )
                        )
    breakEvenSet = calcBreakEvenEffSet(PriceperKWh, blockdata)
    totalWattage = 0
    energyUsageJoule = 0
    totalHashRate = 0
    yearlyTWh = 0
    for i in range(0, len(phases)):
        breakEvenSlice = breakEvenSet[phases[i][0]:phases[i][1]+1]
        hashRateSlice = blockdata[phases[i][0]:phases[i][1]+1]
        meanBreakEvenEff = pd.DataFrame(breakEvenSlice).mean(axis=0)["BreakEvenEfficiency"]
        phaseTimespan = pd.DataFrame(hashRateSlice).sum(axis=0)['timespan']
        phaseBeginHashRateMhs = hashRateSlice[0]['computedhashrate']/1e6
        phaseEndHashRateMhs   = hashRateSlice[len(hashRateSlice)-1]['computedhashrate']/1e6
        phaseHashRateMhsIncrease = (phaseEndHashRateMhs - phaseBeginHashRateMhs)
        if(i==0):
            selectedHardwareEfficiency,releaseDate = getBestGuessHardwareEfficiency(meanBreakEvenEff,datePhases[i])
            addToHardwareMix(selectedHardwareEfficiency, phaseBeginHashRateMhs,releaseDate)
            totalWattage+=(phaseBeginHashRateMhs*selectedHardwareEfficiency)
        else:
            if(phaseHashRateMhsIncrease>0):
                selectedHardwareEfficiency,releaseDate = getBestGuessHardwareEfficiency(meanBreakEvenEff,datePhases[i])
                addToHardwareMix(selectedHardwareEfficiency, phaseHashRateMhsIncrease,releaseDate)
            else:
                phaseHardwareEfficiencyJMh = getBestGuessHardwareEfficiency(meanBreakEvenEff,datePhases[i])
                removeMostInefficientHardware(phaseHashRateMhsIncrease)
                #removeOldHardware(meanBreakEvenEff,datePhases[i])
                replaceHardware(phaseHardwareEfficiencyJMh,meanBreakEvenEff)
                selectedHardwareEfficiency = getHardwareMixEfficiency()
        totalHashRate = phaseEndHashRateMhs
        totalWattage = totalHashRate * getHardwareMixEfficiency()
        energyUsageJoule += totalWattage * phaseTimespan
        EnergyUsageTWh = energyUsageJoule/3.6e15
        yearlyTWh = ((totalWattage*8765.81277)/1e12)
        for k in range(len(breakEvenSlice)):
            phaseData = {}
            phaseData['Period'] = datetime.strftime(datePhases[i][0], "%m/%d/%Y") + "  -  " + datetime.strftime(datePhases[i][1], "%m/%d/%Y")
            phaseData['Date'] = breakEvenSlice[k]['date']
            phaseData['BreakEvenEfficiency'] = breakEvenSlice[k]['BreakEvenEfficiency']
            phaseData['phaseHashRateMhsIncrease'] = float(phaseHashRateMhsIncrease)
            phaseData['cumulativeHardwareEfficiency'] = float(getHardwareMixEfficiency())
            phaseData['yearlyTWh'] = float(yearlyTWh)
            efficiencyData.append(phaseData)

    with open('../JSONDATA/BestGuessEstimate.json', 'w') as w:
        json.dump(efficiencyData, w, indent=4)

    print("The total energy usage of Ethereum is %f Joule or %f TWh"% (energyUsageJoule, EnergyUsageTWh))
    print("On " + datetime.strftime(datePhases[len(datePhases)-1][1],"%m/%d/%Y") + " the power draw was " + str(totalWattage/1e6) + " MW." )
    print("This equals %f TWh per year." % yearlyTWh)
    return efficiencyData


def main():
    # phasesManual = [(0, 200),(201, 454), (455, 598), (599,778),
    # (779, 970), (971, 1106), (1107, 1141), (1142, 1237), (1238, 1275),
    # (1276, 1479), (1480, 1538), (1539, 1679)]
    interval = 14
    upperBound = False
    endOfData = "3/3/2020"
    endDate = "12/31/2017"
    PriceperKWh = 0.05
    phases = generatePhases(blockdata,interval,endOfData)
    # efficiencyData = calcTotalEnergyUsage(PriceperKWh, phases, upperBound)



    efficiencyData = bestGuessEstimate(PriceperKWh, phases)


    # plot.plotBreakEvenEffAgainstSelectedEfficiency(efficiencyData, blockdata)
    # plot.scatterPlotGpuEfficiencies()

    #csvtojson('../JSONDATA/GPUdata/CSV/GPUDATA.csv', '../JSONDATA/GPUdata/GPUDATA.json')
    #plot.compareOtherResults()
    #plot.scatterPlotGpuEfficiencies()
    #plot.plothashrates()
main()
