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
        dps.append(dp)
    return dps

def addToHardwareMix(phaseHardwareEfficiency, hashrateIncrease, releaseDate):
    hashratedata.append((phaseHardwareEfficiency, hashrateIncrease, releaseDate))

def getHardwareMixEfficiency(upperBound):
    if not hashratedata:
        return -1
    if upperBound:
        hardwaremix = np.array(hashratedata)[:,:2].astype(float)
        cumulativeHardwareEfficiency = np.sum(np.prod(hardwaremix, axis=1),axis=0)
        cumulativeWeight = np.sum(hardwaremix,axis=0)[1]
        return float(cumulativeHardwareEfficiency/cumulativeWeight)
    else:
        hardwaremix = np.array(hashratedata)[:,:1].astype(float)
        return np.min(hardwaremix)

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

def getBestGuessHardwareEfficiency(meanBreakEvenEff, datetuple, asicshare=0.05):
    gpulist = getDateSetBestGuess(datetuple)        #Get a list of hardware that meets the best guess requirements:
    scores = list()                                     # Hardware must be released before the beginning of the phase 'datetuple'
    asics = list()                                      # Hardware must not be older than 1 year before beginning of phase 'datetyple'
    avg = 0
    if gpulist:
        for i in range (0, (len(gpulist))):
            if gpulist[i]['Type'] == "ASIC":
                asics.append(float(gpulist[i]['Efficiency in J/Mh']))
            elif(float(gpulist[i]['Efficiency in J/Mh']) < meanBreakEvenEff):
                score = (i, meanBreakEvenEff-float(gpulist[i]['Efficiency in J/Mh']))
                avg += float(gpulist[i]['Efficiency in J/Mh'])
                scores.append(score)
        if scores:
            scores = sorted(scores, key=lambda x:x[1], reverse = True) #Sort scores such that the closest match is the first element
            avg = avg/len(gpulist)
            medianindex = scores[int(len(scores)/2)][0]
            median = float(gpulist[medianindex]['Efficiency in J/Mh'])
            min = float(gpulist[scores[0][0]]['Efficiency in J/Mh'])
            hardwareEfficiency = median
            if asics:
                asicavg = sum(asics)/len(asics)
                hardwareEfficiency = ((1-asicshare)*median)+(asicshare*asicavg)
            return (hardwareEfficiency,gpulist[medianindex]['Release date'] )
        else:
            return -1
            print("Error, no hardware")
    else:
        return -1
        print("Error, no hardware")

# Replaces most inefficient hardware in the hardware-mix with hardware with hardware with efficiency 'hardwareEfficiency'
# untill the hardware-mix is within EFFICIENCYMARGIN of the target efficiency 'meanBreakEvenEff'
def replaceHardware(hardwareEfficiency, meanBreakEvenEff, releaseDate, upperBound):
    if hashratedata:
        hardwaremix = np.array(hashratedata)[:,:2].astype(float)
        cumulativeHardwareEfficiency = np.sum(np.prod(hardwaremix, axis=1),axis=0)
        cumulativeWeight = np.sum(hardwaremix,axis=0)[1]
        while(getHardwareMixEfficiency(upperBound) - meanBreakEvenEff > EFFICIENCYMARGIN):
            hashratedata.sort(key=lambda x:x[0], reverse = True)
            for i in range(len(hashratedata)):
                oldHardwareHashrate = hashratedata[i][1]
                oldHardwareEfficiency = hashratedata[i][0]
                if(oldHardwareHashrate > 0 and oldHardwareEfficiency > hardwareEfficiency):
                    diff = cumulativeHardwareEfficiency - (meanBreakEvenEff*cumulativeWeight)
                    replaceAmount = diff//(oldHardwareEfficiency-hardwareEfficiency)
                    if(replaceAmount >= oldHardwareHashrate):
                        hashratedata.pop(i)
                        replaceAmount = oldHardwareHashrate
                    else:
                        hashratedata[i] = (hashratedata[i][0], hashratedata[i][1]-replaceAmount, hashratedata[i][2])
                    addToHardwareMix(hardwareEfficiency, replaceAmount,releaseDate)
        # worstHardwareEfficiency = np.max(np.array([float(gpu['Efficiency in J/Mh']) for gpu in gpudata]))
        # while(worstHardwareEfficiency-getHardwareMixEfficiency(upperBound) > EFFICIENCYMARGIN and meanBreakEvenEff >= worstHardwareEfficiency):
        #     hashratedata.sort(key=lambda x:x[0], reverse = False)
        #     for i in range(len(hashratedata)):
        #         oldHardwareHashrate = hashratedata[i][1]
        #         oldHardwareEfficiency = hashratedata[i][0]
        #         if(oldHardwareHashrate > 0 and oldHardwareEfficiency < worstHardwareEfficiency):
        #             diff =  (worstHardwareEfficiency*cumulativeWeight)-cumulativeHardwareEfficiency
        #             replaceAmount = diff//(worstHardwareEfficiency-oldHardwareEfficiency)
        #
        #             print(diff)
        #             if(replaceAmount >= oldHardwareHashrate):
        #                 hashratedata.pop(i)
        #                 replaceAmount = oldHardwareHashrate
        #             else:
        #                 hashratedata[i] = (hashratedata[i][0], hashratedata[i][1]-replaceAmount, hashratedata[i][2])
        #             addToHardwareMix(worstHardwareEfficiency, replaceAmount,releaseDate)
        #             # print("Higher")

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
        datePhases.append((datetime.strptime(blockdata[phases[i][0]]['date'],"%m/%d/%Y"),
                           datetime.strptime(blockdata[phases[i][1]]['date'],"%m/%d/%Y")))
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
            selectedHardwareEfficiency, releaseDate = getMatchingHardwareEfficiency(meanBreakEvenEff,datePhases[i], upperBound)
            addToHardwareMix(selectedHardwareEfficiency, phaseBeginHashRateMhs,releaseDate)
            totalWattage+=(phaseBeginHashRateMhs*selectedHardwareEfficiency)
        else:
            if(phaseHashRateMhsIncrease>0):
                selectedHardwareEfficiency,releaseDate = getMatchingHardwareEfficiency(meanBreakEvenEff,datePhases[i], upperBound)#minHardwareEfficiency
                addToHardwareMix(selectedHardwareEfficiency, phaseHashRateMhsIncrease,releaseDate)
            else:
                selectedHardwareEfficiency,releaseDate = getMatchingHardwareEfficiency(meanBreakEvenEff,datePhases[i],upperBound)
                releaseDate=datetime.today() #Hack to ensure that hashrate declines never get removed from the hardwaremix set
                addToHardwareMix(getHardwareMixEfficiency(upperBound), phaseHashRateMhsIncrease,releaseDate) # first remove the hashrate equivalent amount of wattage of the average hardware mix
            replaceHardware(selectedHardwareEfficiency,meanBreakEvenEff,releaseDate, upperBound)
        totalHashRate = phaseEndHashRateMhs
        totalWattage = totalHashRate * getHardwareMixEfficiency(upperBound)
        energyUsageJoule += totalWattage * phaseTimespan
        EnergyUsageTWh = energyUsageJoule/3.6e15
        yearlyTWh = ((totalWattage*8765.81277)/1e12)

        # for k in range(len(breakEvenSlice)):
        k=0
        phaseData = {}
        phaseData['Period'] = datetime.strftime(datePhases[i][0], "%m/%d/%Y") + "  -  " + datetime.strftime(datePhases[i][1], "%m/%d/%Y")
        phaseData['Date'] = breakEvenSlice[k]['date']
        phaseData['BreakEvenEfficiency'] = breakEvenSlice[k]['BreakEvenEfficiency']
        phaseData['HardwareEfficiency'] = getHardwareMixEfficiency(upperBound)
        phaseData['yearlyTWh'] = float(yearlyTWh)
        phaseData['MegaWatts'] = totalWattage/1e6
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

#Remove hardware older than a year iff newer hardware yields a better efficiency
def removeOldHardware(meanBreakEvenEff,datetuple):
    begindate,enddate = datetuple
    done=False
    if hashratedata:
        i=0
        while not done:
            if datetime.strptime(hashratedata[i][2],"%m/%d/%Y" )<(begindate-timedelta(days=365)):
                oldHardwareHashrate = hashratedata[i][1]
                oldHardwareEfficiency = hashratedata[i][0]
                newHardwareEfficiency, newHardwareReleaseDate = getBestGuessHardwareEfficiency(meanBreakEvenEff, datetuple)
                if(newHardwareEfficiency < oldHardwareEfficiency):
                    hashratedata.pop(i)
                    addToHardwareMix(newHardwareEfficiency, oldHardwareHashrate, newHardwareReleaseDate)
            if (i < len(hashratedata)-1):
                i+=1
            else:
                done = True
    else:
        return -1

def bestGuessEstimate(PriceperKWh, phases):
    datePhases = []
    efficiencyData = []
    for i in range(0,(len(phases))):
        datePhases.append((datetime.strptime(blockdata[phases[i][0]]['date'],"%m/%d/%Y"),
                           datetime.strptime(blockdata[phases[i][1]]['date'],"%m/%d/%Y")))
    breakEvenSet = calcBreakEvenEffSet(PriceperKWh, blockdata)
    totalWattage = 0
    energyUsageJoule = 0
    totalHashRate = 0
    yearlyTWh = 0
    for i in range(len(phases)):
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
                phaseHardwareEfficiencyJMh,releaseDate = getBestGuessHardwareEfficiency(meanBreakEvenEff,datePhases[i])
                removeMostInefficientHardware(phaseHashRateMhsIncrease)
                removeOldHardware(meanBreakEvenEff,datePhases[i])
                replaceHardware(phaseHardwareEfficiencyJMh,meanBreakEvenEff,releaseDate, False)
        totalHashRate = phaseEndHashRateMhs
        totalWattage = totalHashRate * getHardwareMixEfficiency(True)
        energyUsageJoule += totalWattage * phaseTimespan
        EnergyUsageTWh = energyUsageJoule/3.6e15
        yearlyTWh = ((totalWattage*8765.81277)/1e12)
        # for k in range(len(breakEvenSlice)):
        k=0
        phaseData = {}
        phaseData['Period'] = datetime.strftime(datePhases[i][0], "%m/%d/%Y") + "  -  " + datetime.strftime(datePhases[i][1], "%m/%d/%Y")
        phaseData['Date'] = breakEvenSlice[k]['date']
        phaseData['BreakEvenEfficiency'] = breakEvenSlice[k]['BreakEvenEfficiency']
        phaseData['HardwareEfficiency'] = getHardwareMixEfficiency(True)
        phaseData['yearlyTWh'] = float(yearlyTWh)
        phaseData['MegaWatts'] = totalWattage/1e6
        efficiencyData.append(phaseData)

    with open('../JSONDATA/BestGuessEstimate.json', 'w') as w:
        json.dump(efficiencyData, w, indent=4)

    print("The total energy usage of Ethereum is %f Joule or %f TWh"% (energyUsageJoule, EnergyUsageTWh))
    print("On " + datetime.strftime(datePhases[len(datePhases)-1][1],"%m/%d/%Y") + " the power draw was " + str(totalWattage/1e6) + " MW." )
    print("This equals %f TWh per year." % yearlyTWh)
    return efficiencyData

def run(mode, showplot, interval, priceperKWh, endDate):
    phases = generatePhases(blockdata,interval,endDate)
    if mode == "U":
        efficiencyData = calcTotalEnergyUsage(priceperKWh, phases, True)
    elif mode == "L":
        efficiencyData = calcTotalEnergyUsage(priceperKWh, phases, False)
    elif mode == "B":
        efficiencyData = bestGuessEstimate(priceperKWh, phases)
    else:
        print("Error: Wrong mode.")
    if showplot:
        return
        # plot.plotResults(efficiencyData)
        # plot.plotWattageandEfficiency(efficiencyData)

def main():
    interval = 14
    mode = "B"
    endOfData = "3/3/2020"
    endDate = "12/31/2017"
    priceperKWh = 0.05
    showplot = False
    # run(mode,showplot,interval,priceperKWh, endOfData)
    plot.plotProfThres()
    # plot.plotLowerBoundResult()
    # plot.plotUpperBoundResult()
    # plot.plotBestGuessResult()
    # plot.plotResultsVariableEnergyPrice()

    # plot.plotBreakEvenEffAndHashrate(efficiencyData, blockdata)


    # plot.compareOtherResults()
    # plot.scatterPlotGpuEfficiencies()
    # plot.plothashrates()

if __name__ == "__main__":
    main()
