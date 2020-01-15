import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import sys
import csv, json

#BreakEvenEfficiency by date
with open('../JSONDATA/plotdata.json') as f:
    BreakEvenEfficiencySet = reversed(json.load(f))

#Blockdata from etherscan API
with open('../JSONDATA/BlockData.json', 'r') as r:
    blockdata = json.load(r)

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

def getMatchingHardware(efficiency, begindate, enddate):
    gpulist = getDateSet(begindate, enddate)
    scores = list()
    for i in range (0, (len(gpulist)-1)):
        score = (i, abs(efficiency-float(gpulist[i]['Efficiency in J/Mh'])))
        scores.append(score)
    scores = sorted(scores, key=lambda x:x[1])
    for i in range (0, len(scores)-1):
        print(gpulist[scores[i][0]]['Product'] + "Efficiency = " +gpulist[scores[i][0]]['Efficiency in J/Mh'] + " J/Mh\n")

def getDateSet(begindate, enddate):
    begindateobj = datetime.strptime(begindate,"%m/%d/%Y")
    enddateobj = datetime.strptime(enddate, "%m/%d/%Y")
    gpulist = list()
    for gpu in gpudata:
        date = datetime.strptime(gpu['Release date'], "%m/%d/%Y")
        if date > begindateobj and date <= enddateobj:
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

def calcBreakEvenEff(hashrate,blocktime,ETHPrice,timespan, nrOfBlocks, blockReward, uncleReward, unclerate, PriceperKWh):
    #Profitable efficiency
    ETHProfitGenerated = (nrOfBlocks*blockReward+(unclerate*nrOfBlocks*uncleReward))*ETHPrice
    BreakEvenEfficiency = ((ETHProfitGenerated/PriceperKWh)*3600000)/(timespan*hashrate)
    return BreakEvenEfficiency

#Outputs BreakEvenEfficiency from blockdata averages JSON to JSON
def calcBreakEvenEffSet(PriceperKWh, blockdata):

    dps = list()
    for i in range (0, len(blockdata)):
        dp = {}
        dp['date'] = blockdata[i]['date']
        dp['BreakEvenEfficiency'] = calcBreakEvenEff(float(blockdata[i]['averagehashrate'])/1000000,
                                                     float(blockdata[i]['averageblocktime']),
                                                     float(blockdata[i]['ethprice']),
                                                     float(blockdata[i]['timespan']),
                                                     float(blockdata[i]['amountOfBlocks']),
                                                     getBlockReward(blockdata[i]['blocknr']),
                                                     getUncleReward(blockdata[i]['blocknr']),
                                                     float(blockdata[i]['unclerate']),
                                                     PriceperKWh)
        dps.append(dp)
    with open('../JSONDATA/plotdata.json', 'w') as w:
        json.dump(dps, w, indent = 4)

#getMatchingHardware(5, "7/8/2019", "12/1/2019")
#calcBreakEvenEffSet(0.10, blockdata)
#csvtojson("transactions.csv", "transactions.json")
# plot()
#csvtojson('../JSONDATA/GPUDATA/CSV/GPUDATA.csv', '../JSONDATA/GPUDATA/GPUDATA.json')
print(getblockReward("3/1/2019"))
