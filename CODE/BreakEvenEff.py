import json
from datetime import datetime
import matplotlib.pyplot as mpl
import pandas as pd
import sys

#BreakEvenEfficiency by date
with open('../JSONDATA/plotdata.json') as f:
    BreakEvenEfficiencySet = reversed(json.load(f))

#Blockdata from etherscan API
with open('../JSONDATA/BlockData.json', 'r') as r:
    blockdata = json.load(r)

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

#plot of BreakEvenEfficiency over time
def plot():
    BreakEvenEfficiencySetDataFrame = pd.DataFrame(BreakEvenEfficiencySet)
    BreakEvenEfficiencySetDataFrame.plot(x='date', y='BreakEvenEfficiency')
    mpl.show()

calcBreakEvenEffSet(0.10, blockdata)
plot()
