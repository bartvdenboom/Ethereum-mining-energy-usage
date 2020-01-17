#  For each day we need:

#   date
#   ETH-USD price
#   Average difficulty
#   Average blocktime
#   Average hashrate (as a check)
#   Unclerate
#   Blockreward (by date)

import csv, json

def csvtojson(input, output):
    csvfile = open(input, 'r')
    jsonfile= open(output, 'w')
    reader = csv.reader(csvfile)
    rownames = next(reader)
    reader  = csv.DictReader(csvfile, rownames)
    out = json.dumps([row for row in reader],indent=4)
    jsonfile.write(out)

def getETHPriceByDate(date):
    with open('../JSONDATA/etherprice.json', 'r') as r:
        data = json.load(r)
    for i in range(0, len(data)):
        if data[i]['Date(UTC)'] == date:
            ethprice = data[i]['Value']
            return ethprice

def buildBlockData():
    with open('../JSONDATA/Etherscan/BlockDifficulty.json') as r:
        difficultydata = json.load(r)
    with open('../JSONDATA/Etherscan/BlockReward.json') as r:
        rewarddata = json.load(r)
    with open('../JSONDATA/Etherscan/BlockTime.json') as r:
        timedata = json.load(r)
    with open('../JSONDATA/Etherscan/EtherPrice.json') as r:
        pricedata = json.load(r)
    with open('../JSONDATA/Etherscan/NetworkHash.json') as r:
        hashdata = json.load(r)
    with open('../JSONDATA/Etherscan/BlockCountRewards.json') as r:
        blockcountdata = json.load(r)
    with open('../JSONDATA/Etherscan/Uncles.json') as r:
        unclecountdata = json.load(r)


    dailydata = list()

    for i in range (0,len(difficultydata)):
        day = {}
        averagedifficulty = float(difficultydata[i]['Value'])
        averagedifficulty = averagedifficulty*1000000000000
        averageblocktime = float(timedata[i]['Value'])
        calculatedhashrate = averagedifficulty/averageblocktime
        averagehashrate = float(hashdata[i]['Value'])*1000000000
        blockcount = int(blockcountdata[i]['Value'])
        unclecount = int(unclecountdata[i]['Value'])
        unclerate = unclecount/blockcount
        day['date'] = pricedata[i]['Date(UTC)']
        day['ethprice'] = float(pricedata[i]['Value'])
        day['timespan'] = blockcount*averageblocktime
        day['averagedifficulty'] = averagedifficulty
        day['averageblocktime'] = averageblocktime
        day['averagehashrate'] = averagehashrate
        day['calculatedhashrate'] = calculatedhashrate
        day['correctedhashrate'] = (averagedifficulty*(1+unclerate))/averageblocktime
        day['dailyETHreward'] = float(rewarddata[i]['Value'])
        day['unclerate'] = unclerate
        dailydata.append(day)
        print("%i of %i" % (i, len(difficultydata)))

    with open('../JSONDATA/Etherscan/DailyData.json', 'w') as w:
        json.dump(dailydata, w, indent = 4)


buildBlockData()
