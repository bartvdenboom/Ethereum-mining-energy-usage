#Bart van den Boom
#Ethereum power usage calculations
#importing the requests library
import requests
import time
import json
import csv
from datetime import datetime
import matplotlib.pyplot as mpl
import pandas as pd
import sys

#Constants
InnosiliconA10_432 = 740/432    #1.713 Innosilicon A10 432MH version in J/MH
Canaan = 0.68                   #0.68
TitanV = 237/77                 #3.078
Krause2018 = 4.7                #4.7

bestcasePUE = 1.01 #Best case scenario from CBECI
PriceperKWh = 0.05 #Regularly used
unclerate = 0.05   #Average
unclereward = 2/32
maxhashvalue = pow(2,256)

#PARAMETERS
MiningEfficiency = Krause2018
PUE = bestcasePUE

#nanopool api
#Network - Blocks
BLOCKSTATS_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/block_stats/0/1"
LASTBLOCK_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/blocks/0/1"
BLOCKTIME_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/network/avgblocktime"
WORKERS_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/pool/activeworkers"
HASHRATE_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/pool/hashrate"
PRICES_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/prices"

#Ethermine APi
#Network stats
BLOCKS_URL_ETHERMINE = "https://api.ethermine.org/networkStats"
POOLSTATS_URL_ETHERMINE = "https://api.ethermine.org/poolStats"

#Etherscan Api
LATEST_BLOCK_URL = "https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey=EAPRQ93KHAK7DVWKKQB2QTTYB6Z4BPTT5B"
BLOCKINFOBYNUMBER_URL_PREFIX = "https://api.etherscan.io/api?module=proxy&action=eth_getBlockByNumber&tag="
BLOCKINFOBYNUMBER_URL_SUFFIX = "&boolean=true&apikey=EAPRQ93KHAK7DVWKKQB2QTTYB6Z4BPTT5B"


def getBlockInfo(blocknr):
    req = requests.get(url=BLOCKINFOBYNUMBER_URL_PREFIX+str(blocknr)+BLOCKINFOBYNUMBER_URL_SUFFIX)
    data = req.json()
    return int(data['result']['difficulty'], 16), int(data['result']['timestamp'], 16), len(data['result']['uncles']), int(data['result']['gasUsed'], 16)

def getLatestBlockNr():
    time.sleep(0.2)
    req = requests.get(url=LATEST_BLOCK_URL)
    data = req.json()
    return data['result']


def processBlockInfo(amountOfBlocks, blocknr, file):
    with open(file) as r:
        results = json.load(r)
    result = {}
    startingblocknr = blocknr-amountOfBlocks
    cumulative_difficulty = 0
    cumulative_timestampdelta = 0
    cumulative_unclelen = 0
    prev_block_timestamp = 0
    prevtime = time.time()

    print("\nProcessing Block %i and %i previous blocks." % (blocknr, amountOfBlocks))

    for i in range (startingblocknr, blocknr):
        sys.stdout.write('\r')
        sys.stdout.write("%d%%" % ((i-startingblocknr)/(blocknr-startingblocknr)*100))
        difficulty, timestamp, unclelen, gasused = getBlockInfo(hex(i))
        #Timing to not overload the API
        if (time.time()-prevtime) < 0.2:
            sleep(0.2 - (time.time()-prevtime))
        prevtime = time.time()

        if(i == startingblocknr):
            prev_block_timestamp = timestamp
            startblock_timestamp = timestamp
        else:
            cumulative_timestampdelta += (timestamp - prev_block_timestamp)
            prev_block_timestamp = timestamp

        cumulative_difficulty += difficulty
        cumulative_unclelen += unclelen

    unclerate = cumulative_unclelen / amountOfBlocks
    averageblocktime = cumulative_timestampdelta/(amountOfBlocks-1)
    averagedifficulty = cumulative_difficulty/ amountOfBlocks
    averagehashrate = averagedifficulty/averageblocktime
    date = datetime.utcfromtimestamp(timestamp).strftime('%-m/%-d/%Y')

    result['blocknr'] = blocknr
    result['timestamp'] = timestamp
    result['date'] = date
    result['ethprice'] = getETHPriceByDate(date)
    result['timespan'] = timestamp-startblock_timestamp
    result['amountOfBlocks'] = amountOfBlocks
    result['averagedifficulty'] = averagedifficulty
    result['averageblocktime'] = averageblocktime
    result['averagehashrate'] = averagehashrate
    result['unclerate'] = unclerate
    result['gasused'] = gasused

    results.append(result)

    with open(file, 'w') as w:
        json.dump(results, w, indent=4)

def getETHPriceUSD():
    prices_req_nano = requests.get(url = PRICES_URL_NANOPOOL)
    prices_req_nano_data = prices_req_nano.json()
    return prices_req_nano_data['data']['price_usd']

def getETHPriceByDate(date):
    with open('../JSONDATA/etherprice.json', 'r') as r:
        data = json.load(r)
    for i in range(0, len(data)):
        if data[i]['Date(UTC)'] == date:
            ethprice = data[i]['Value']
            return ethprice

def runNanoPool():
    # Requests
    # NANOPOOL
    blocks_req_nano = requests.get(url = BLOCKSTATS_URL_NANOPOOL)           #BLOCKSTATS
    lastblock_req_nano = requests.get(url = LASTBLOCK_URL_NANOPOOL)         #LASTBLOCK
    avgblocktime_req_nano = requests.get(url = BLOCKTIME_URL_NANOPOOL)      #AVGBLOCKTIME
    workers_req_nano = requests.get(url = WORKERS_URL_NANOPOOL)             #WORKERS
    hashrate_req_nano = requests.get(url = HASHRATE_URL_NANOPOOL)           #POOL_HASHRATE
                   #PRICES



    # extracting data in json format
    #NANO Api
    blocks_data_nano = blocks_req_nano.json()
    lastblock_data_nano = lastblock_req_nano.json()
    avgblocktime_data_nano = avgblocktime_req_nano.json()
    workers_data_nano = workers_req_nano.json()
    hashrate_data_nano = hashrate_req_nano.json()



    ############################################################################
    #NANOPOOL
    #Parsing Responses from Nanopool Api
    data_nano = blocks_data_nano['data'][0]
    difficulty_nano = data_nano['difficulty']
    blocktime_nano = data_nano['block_time']
    lastblock_number_nano = lastblock_data_nano['data'][0]['number']
    eth_price_usd = prices_req_nano_data['data']['price_usd']
    nanopool_workers = workers_data_nano['data']
    hashrate_pool_nanopool = hashrate_data_nano['data']

    #Calculations
    #From yellowpaper spec (49)
    targetvalue_nano = maxhashvalue/difficulty_nano

    #probability of getting a hash under proposed targetvalue is
    p_nano = targetvalue_nano/maxhashvalue
    numberoftries_nano = 1/p_nano
    ethereum_hashrate_nano = numberoftries_nano/blocktime_nano

    avghashrate_pool_nanopool = hashrate_pool_nanopool/nanopool_workers
    hashrateGhs_nanopool = ethereum_hashrate_nano/1000000000
    powerusageMW_nanopool = PUE*hashrateGhs_nanopool*MiningEfficiency/1000
    powerusageMWH_yearly_nanopool = powerusageMW_nanopool*8760.25

    print("\n")
    print("ACCORDING TO NANOPOOL API")
    print("-------------------------")

    print("The probability of finding a hashvalue under the target is %e."% p_nano)
    print("It will take %i tries to find a correct nonce if geometrically distributed." % numberoftries_nano)
    print("The average time to mine a block is %i seconds." % blocktime_nano)
    print("The hashrate of Ethereum thus needs to be %i hashes per second or %i Gh/s." % (ethereum_hashrate_nano, hashrateGhs_nanopool))
    print("The average hashrate of a worker in the Nanopool mining pool is %i MH/s." % avghashrate_pool_nanopool)

    print("-------------------------")
    print("\n")

def runEthermine():
    ############################################################################
    #Ethermine
    # ETHERMINE
    blocks_req_ethermine = requests.get(url = BLOCKS_URL_ETHERMINE)         #BLOCKINFO
    poolstats_req_ethermine = requests.get(url = POOLSTATS_URL_ETHERMINE)   #POOLINFO

    #Ethermine Api
    blocks_data_ethermine = blocks_req_ethermine.json()
    poolstats_data_ethermine = poolstats_req_ethermine.json()

    #Parsing BLOCKS_URL Response from Ethermine Api
    data_blocks_ethermine = blocks_data_ethermine['data']
    blocktime_ethermine = data_blocks_ethermine['blockTime']
    difficulty_ethermine = data_blocks_ethermine['difficulty']
    hashrate_ethermine = data_blocks_ethermine['hashrate']

    #Calculations
    #From yellowpaper spec (49)
    targetvalue_ethermine = maxhashvalue/difficulty_ethermine

    p_ethermine = targetvalue_ethermine/maxhashvalue
    numberoftries_ethermine = 1/p_ethermine
    ethereum_hashrate_ethermine = numberoftries_ethermine/blocktime_ethermine
    actual_hashrate_ethermine = hashrate_ethermine/1000000000

    #Pool data
    ethermine_pool_data = poolstats_data_ethermine['data']
    ethermine_pool_stats = ethermine_pool_data['poolStats']
    ethermine_pool_hashrate = ethermine_pool_stats['hashRate']
    ethermine_workers = ethermine_pool_stats['workers']
    lastblock_number_ethermine = ethermine_pool_data['minedBlocks'][0]['number']
    avghashrate_pool_ethermine = ethermine_pool_hashrate/ethermine_workers

    hashrateGhs_ethermine = ethereum_hashrate_ethermine/1000000000
    powerusageMW_ethermine = PUE*hashrateGhs_ethermine*MiningEfficiency/1000
    powerusageMWH_yearly_ethermine = powerusageMW_ethermine*8760.25

    powerusageMW_ethermine_actual = PUE*actual_hashrate_ethermine*MiningEfficiency/1000
    powerusageMWH_yearly_ethermine_actual = powerusageMW_ethermine_actual*8760.25

    print("ACCORDING TO ETHERMINE")
    print("-------------------------")

    print("The probability of finding a hashvalue under the target is %e."% p_ethermine)
    print("It will take %i tries to find a correct nonce if geometrically distributed." % numberoftries_ethermine)
    print("The average time to mine a block is %i seconds." % blocktime_ethermine)
    print("The hashrate of Ethereum thus needs to be %i hashes per second or %i Gh/s." % (ethereum_hashrate_ethermine, hashrateGhs_ethermine))
    print("The actual hashrate of Ethereum according to Ethermine is %i Gh/s" % actual_hashrate_ethermine)

    print("The average hashrate of a worker in the Ethermine mining pool is %i MH/s." % (avghashrate_pool_ethermine/1000000))

    print("-------------------------")
    print("\n")

def runPoWComparison():
    print("TOTAL ENERGY USAGE OF POW CONSENSUS ALGORITHM")
    print("")
    print("Using Nanopool statistics: ")
    print("Using a PUE of %f, the power usage of Ethereum PoW is currently: %f MW" % (PUE,powerusageMW_nanopool))
    print("Yearly this amounts to %f MWh\n" % powerusageMWH_yearly_nanopool)

    print("Using Ethermine statistics: \n")
    print("Using data from last mined block:")
    print("Using a PUE of %f, The power usage of Ethereum PoW is currently: %f MW" % (PUE, powerusageMW_ethermine))
    print("Yearly this amounts to %f MWh\n" % powerusageMWH_yearly_ethermine)
    print("Using average hashrate listed by website:")
    print("Using a PUE of %f, the power usage of Ethereum PoW is currently: %f MW" % (PUE, powerusageMW_ethermine_actual))
    print("Yearly this amounts to %f MWh\n" % powerusageMWH_yearly_ethermine_actual)
    print("Calculated using an efficiency of %f J/MH" % MiningEfficiency)
    print("\n")

def runProfitabilityThreshold(hashrateMhs,blocktime):
    #Blocks per day
    BlockPerDay = 86400/blocktime

    #Profitable efficiency (daily)
    ETHGeneratedPerDay = (BlockPerDay*2+(unclerate*BlockPerDay*unclereward))
    ETHPrice = getETHPriceUSD()
    BreakEvenEfficiency = (ETHGeneratedPerDay*ETHPrice)/(PUE*(hashrateMhs)*(24/1000)*PriceperKWh)

    print("-------------------------")
    print("PROFITABILITY THRESHOLD")
    print("The total hashrate of Ethereum is %f MH/s" % hashrateMhs)
    print("The average time to mine a block is currently %f" % blocktime)
    print("1 ETH @ %f USD and 1 KWh @ %f USD" % (ETHPrice, PriceperKWh))
    print("Daily ETH reward(Excluding transaction fees): %f USD" % (ETHGeneratedPerDay*ETHPrice))
    print("The Break-even efficiency of hardware is %f J/MH" % BreakEvenEfficiency)
    return BreakEvenEfficiency

def calculateAverageAmount():
    f = [5000]
    for i in f:
        difficulty, blocktime, hashrate = getAverageDifficultyBlocktimeHashrate(i)
        runProfitabilityThreshold((hashrate/1000000), blocktime)

def mininghardwaretojson():
    csvfile = open('GPUDATA.csv', 'r')
    jsonfile= open('GPUDATA.json', 'w')
    rownames = ["Number","Type","Release date/date of original information retrieval","Source","Accessed on","Manufacturer","Product","Hash rate in Mh/s","Power in W","Efficiency in Mh/J","Efficiency in J/MH"]
    reader  = csv.DictReader(csvfile, rownames)
    out = json.dumps([row for row in reader])
    jsonfile.write(out)

def ethpricetojson():
    csvfile = open('../etherprice.csv', 'r')
    jsonfile = open('../etherprice.json', 'w')
    rownames = ["Date(UTC)","UnixTimeStamp","Value"]
    reader  = csv.DictReader(csvfile, rownames)
    out = json.dumps([row for row in reader])
    jsonfile.write(out)

def comparedates():
    with open('GPUDATA.json') as f:
        content = json.load(f)
    a = datetime.strptime(content[1]['Release date/date of original information retrieval'], '%m/%d/%Y')
    b = datetime.strptime(content[2]['Release date/date of original information retrieval'], '%m/%d/%Y')
    print(a)

def dateToBlockNr():
    difficulty, timestamp = getBlockInfo(getLatestBlockNr())
    timestampobj = time.gmtime(timestamp)
    print(datetime.utcfromtimestamp(timestamp).strftime('%m-%d-%Y'))

def printaverages():
    with open('../difficultyblocktimehashrate_results.json') as f:
        content = json.load(f)
    df = pd.DataFrame(content)
    print(df)
    df.plot(x='amountOfBlocks', y='averagehashrate')
    mpl.show()

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

def calcBreakEvenEff(hashrate,blocktime,ETHPrice,timespan, nrOfBlocks, blockReward, uncleReward):
    #Profitable efficiency
    ETHProfitGenerated = (nrOfBlocks*blockReward+(unclerate*nrOfBlocks*uncleReward))*ETHPrice
    BreakEvenEfficiency = ((ETHProfitGenerated/PriceperKWh)*3600000)/(timespan*hashrate)
    return BreakEvenEfficiency

#Outputs BreakEvenEfficiency from blockdata averages JSON to JSON
def calcBreakEvenEffSet():
    with open('../JSONDATA/BlockData.json', 'r') as r:
        rdata = json.load(r)
    dps = list()
    for i in range (0, len(rdata)):
        dp = {}
        dp['date'] = rdata[i]['date']
        dp['BreakEvenEfficiency'] = calcBreakEvenEff(float(rdata[i]['averagehashrate'])/1000000,
                                                     float(rdata[i]['averageblocktime']),
                                                     float(rdata[i]['ethprice']),
                                                     float(rdata[i]['timespan']),
                                                     float(rdata[i]['amountOfBlocks']),
                                                     getBlockReward(rdata[i]['blocknr']),
                                                     getUncleReward(rdata[i]['blocknr']))
        dps.append(dp)
    with open('../JSONDATA/plotdata.json', 'w') as w:
        json.dump(dps, w, indent = 4)
#plot of BreakEvenEfficiency over time
def plotBreakEvenEff():
    with open('../JSONDATA/plotdata.json') as f:
        BreakEvenEfficiencySet = json.load(f)
    BreakEvenEfficiencySet = reversed(BreakEvenEfficiencySet)
    BreakEvenEfficiencySetDataFrame = pd.DataFrame(BreakEvenEfficiencySet)



    BreakEvenEfficiencySetDataFrame.plot(x='date', y='BreakEvenEfficiency')

    mpl.show()

def main():
    BLOCKNR = 163600
    INTERVAL = 40000
    file = '../JSONDATA/BlockData.json'
    while(1):
        processBlockInfo(500, BLOCKNR,file)
        BLOCKNR-=INTERVAL

#main()
calcBreakEvenEffSet()
plotBreakEvenEff()
