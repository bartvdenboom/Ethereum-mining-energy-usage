import json,csv


def csvtojson(input, output):
    csvfile = open(input, "r")
    jsonfile= open(output, "w")
    reader = csv.reader(csvfile)
    rownames = next(reader)
    reader  = csv.DictReader(csvfile, rownames)
    out = json.dumps([row for row in reader],indent=4)
    jsonfile.write(out)

csvtojson('../JSONDATA/Etherscan/export-BlockDifficulty.csv', '../JSONDATA/Etherscan/BlockDifficulty.json')
csvtojson('../JSONDATA/Etherscan/export-BlockReward.csv', '../JSONDATA/Etherscan/BlockReward.json')
csvtojson('../JSONDATA/Etherscan/export-BlockTime.csv', '../JSONDATA/Etherscan/BlockTime.json')
csvtojson('../JSONDATA/Etherscan/export-EtherPrice.csv', '../JSONDATA/Etherscan/EtherPrice.json')
csvtojson('../JSONDATA/Etherscan/export-NetworkHash.csv', '../JSONDATA/Etherscan/NetworkHash.json')
csvtojson('../JSONDATA/Etherscan/export-BlockCountRewards.csv', '../JSONDATA/Etherscan/BlockCountRewards.json')
csvtojson('../JSONDATA/Etherscan/export-Uncles.csv', '../JSONDATA/Etherscan/Uncles.json')


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
        averageblocktime = float(timedata[i]['Value'])
        blockcount = int(blockcountdata[i]['Value'])
        unclecount = int(unclecountdata[i]['Value'])
        unclerate = unclecount/blockcount
        ethprice = float(pricedata[i]['Value'])
        averagedifficulty = float(difficultydata[i]['Value'])*1000000000000
        day['date'] = pricedata[i]['Date(UTC)']
        day['ethprice'] = ethprice
        day['timespan'] = blockcount*averageblocktime
        day['averagedifficulty'] = averagedifficulty
        day['averageblocktime'] = averageblocktime
        day['reportedhashrate'] = float(hashdata[i]['Value'])*1000000000
        day['computedhashrate'] = (averagedifficulty*(1+unclerate))/averageblocktime
        day['dailyETHreward'] = float(rewarddata[i]['Value'])
        day['unclerate'] = unclerate
        if(ethprice>0):
            dailydata.append(day)
            print("%i of %i" % (i, len(difficultydata)))

    with open('../JSONDATA/Etherscan/DailyData.json', 'w') as w:
        json.dump(dailydata, w, indent = 4)

buildBlockData()
