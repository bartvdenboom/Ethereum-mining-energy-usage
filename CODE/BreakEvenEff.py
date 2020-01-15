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

def getMatchingHardware(efficiency):
    scores = list()
    for i in range (0, len(gpudata)):
        scores[i] = (i, abs(efficiency-float(gpudata[i]['Efficiency in J/Mh'])))
    sorted(scores, key=lambda x: x[1])
    for i in range (0,4):
        print(scores[i])

def getBlockReward(blocknr):
    #Blockreward was originally 5 ETH (untill blocknr 4369999), this changed to 3 ETH with EIP-649 (blocknr 7,280,000) and to 2 ETH with EIP-1234
    if blocknr <= 4369999:
        reward = 5
    elif blocknr > 4369999 and blocknr < 7280000:
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

getMatchingHardware(10)
#calcBreakEvenEffSet(0.10, blockdata)
#csvtojson("transactions.csv", "transactions.json")
# plot()
