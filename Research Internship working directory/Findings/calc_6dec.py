#Bart van den Boom
#Ethereum power usage calculations
#importing the requests library
import requests

maxhashvalue = pow(2,256)

#source: Innosilicon A10 432MH version in J/MH
InnosiliconA10_432 = 740/432    #1.713
Canaan = 0.68                   #0.68
TitanV = 237/77                 #3.078
Krause2018 = 4.7                #4.7
#Choose what Mining effiency to use:

MiningEfficiency = Krause2018

#nanopool api
#Network - Blocks
BLOCKSTATS_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/block_stats/0/1"
LASTBLOCK_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/blocks/0/1"
BLOCKTIME_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/network/avgblocktime"
WORKERS_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/pool/activeworkers"
HASHRATE_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/pool/hashrate"

#Ethermine APi
#Network stats
BLOCKS_URL_ETHERMINE = "https://api.ethermine.org/networkStats"
POOLSTATS_URL_ETHERMINE = "https://api.ethermine.org/poolStats"

# sending get request and saving the response as response object
blocks_req_nano = requests.get(url = BLOCKSTATS_URL_NANOPOOL)
lastblock_req_nano = requests.get(url = LASTBLOCK_URL_NANOPOOL)
avgblocktime_req_nano = requests.get(url = BLOCKTIME_URL_NANOPOOL)
workers_req_nano = requests.get(url = WORKERS_URL_NANOPOOL)
hashrate_req_nano = requests.get(url = HASHRATE_URL_NANOPOOL)

blocks_req_ethermine = requests.get(url = BLOCKS_URL_ETHERMINE)
poolstats_req_ethermine = requests.get(url = POOLSTATS_URL_ETHERMINE)

# extracting data in json format
#NANO Api
blocks_data_nano = blocks_req_nano.json()
lastblock_data_nano = lastblock_req_nano.json()
avgblocktime_data_nano = avgblocktime_req_nano.json()
workers_data_nano = workers_req_nano.json()
hashrate_data_nano = hashrate_req_nano.json()

#Ethermine Api
blocks_data_ethermine = blocks_req_ethermine.json()
poolstats_data_ethermine = poolstats_req_ethermine.json()

#Parsing BLOCKS_URL Response from Nanopool Api
data_nano = blocks_data_nano['data'][0]
difficulty_nano = data_nano['difficulty']
blocktime_nano = data_nano['block_time']
lastblock_number_nano = lastblock_data_nano['data'][0]['number']


#From yellowpaper spec (49)
targetvalue_nano = maxhashvalue/difficulty_nano

#probability of getting a hash under proposed targetvalue is
p_nano = targetvalue_nano/maxhashvalue
numberoftries_nano = 1/p_nano
ethereum_hashrate_nano = numberoftries_nano/blocktime_nano

nanopool_workers = workers_data_nano['data']
hashrate_pool_nanopool = hashrate_data_nano['data']
avghashrate_pool_nanopool = hashrate_pool_nanopool/nanopool_workers


hashrateGhs_nanopool = ethereum_hashrate_nano/1000000000
powerusageMW_nanopool = hashrateGhs_nanopool*MiningEfficiency/1000
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

#Parsing BLOCKS_URL Response from Ethermine Api
data_blocks_ethermine = blocks_data_ethermine['data']
blocktime_ethermine = data_blocks_ethermine['blockTime']
difficulty_ethermine = data_blocks_ethermine['difficulty']
hashrate_ethermine = data_blocks_ethermine['hashrate']
print()

#Calculations
targetvalue_ethermine = maxhashvalue/difficulty_ethermine

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
lastblock_number_ethermine =ethermine_pool_data['minedBlocks'][0]['number']
avghashrate_pool_ethermine = ethermine_pool_hashrate/ethermine_workers

hashrateGhs_ethermine = ethereum_hashrate_ethermine/1000000000
powerusageMW_ethermine = hashrateGhs_ethermine*MiningEfficiency/1000
powerusageMWH_yearly_ethermine = powerusageMW_ethermine*8760.25

powerusageMW_ethermine_actual = actual_hashrate_ethermine*MiningEfficiency/1000
powerusageMWH_yearly_ethermine_actual = powerusageMW_ethermine*8760.25

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



# print("COMPARISON OF DATA\n")
# print("NANOPOOL:")
# print("Difficulty = %i" % difficulty_nano)
# print("Block Time = %f" % blocktime_nano)
# print("Blocknumber = %i " % lastblock_number_nano)
# print("\n")
# print("ETHERMINE:")
# print("Difficulty = %i" % difficulty_ethermine)
# print("Block Time = %f" % blocktime_ethermine)
# print("Blocknumber = %i " % lastblock_number_ethermine) #Last block in the pool??
# print("-------------------------")
# print("\n")
print("TOTAL ENERGY USAGE OF POW CONSENSUS ALGORITHM")
print("")
print("Using Nanopool statistics: ")
print("The power usage of Ethereum PoW is currently: %f MW" % powerusageMW_nanopool)
print("Yearly this amounts to %f MWh\n" % powerusageMWH_yearly_nanopool)

print("Using Ethermine statistics: \n")
print("Using data from last mined block:")
print("The power usage of Ethereum PoW is currently: %f MW" % powerusageMW_ethermine)
print("Yearly this amounts to %f MWh\n" % powerusageMWH_yearly_ethermine)
print("Using average hashrate listed by website:")
print("The power usage of Ethereum PoW is currently: %f MW" % powerusageMW_ethermine_actual)
print("Yearly this amounts to %f MWh\n" % powerusageMWH_yearly_ethermine_actual)
print("Calculated using an efficiency of %f J/MH" % MiningEfficiency)
