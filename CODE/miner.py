import requests
import json
import time



#Ethermine
POOLSTATS_URL_ETHERMINE = "https://api.ethermine.org/miner/0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8/statistics"
req_poolstats = requests.get(url=POOLSTATS_URL_ETHERMINE)
addr_ethermine = "0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8"

#Nanopool
BLOCKSTATS_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/block_stats/0/100"
NETWORK_BLOCKS_URL_NANOPOOL = "https://api.nanopool.org/v1/eth/blocks/0/100"
AVG_HASHRATE_NANOPOOL = "https://api.nanopool.org/v1/eth/avghashrate/"
addr_nanopool = "0x52bc44d5378309ee2abf1539bf71de1b7d7be3b5"
LAST_BLOCKNR = "https://api.nanopool.org/v1/eth/network/lastblocknumber"
lastblocknrdata = requests.get(url=LAST_BLOCKNR).json()
lastblocknr = lastblocknrdata['data']


#Etherscan.io
OUTGOINPREFIX = "https://api.etherscan.io/api?module=account&action=txlist&address="
OUTGOING_STARTBLOCK = "&startblock="
OUTGOING_SUFFIX = "&endblock=99999999&page=1&offset=10000&sort=asc&apikey=EAPRQ93KHAK7DVWKKQB2QTTYB6Z4BPTT5B"
startblock = "8900000"

# req_blockstats = requests.get(url=BLOCKSTATS_URL_NANOPOOL)
# req_network_blocks = requests.get(url=NETWORK_BLOCKS_URL_NANOPOOL)
# req_miner_avghashrate = requests.get(url=AVG_HASHRATE_NANOPOOL+addr)

#Timer for requests (not used)
# localtime = time.time()
# requesttimeinterval = 2.1
# while(1):
#
#     if(time.time()>= localtime+requesttimeinterval):
#         print("Doing a requests at %f" % time.time())
#         localtime = time.time()

outgoing_addr = set()
blocknrmaxindex = startblock
while(1):
    req = requests.get(url=OUTGOINPREFIX+addr_ethermine+OUTGOING_STARTBLOCK+startblock+OUTGOING_SUFFIX)
    req_data = req.json()
    if req_data['status'] == '1':
        s = json.dumps(req_data)

        open("out.json","w").write(s)

        with open('out.json') as f:
            content = json.load(f)
            blocknr = set()
            for item in content['result']:
                blocknr.add(item['blockNumber'])
            if (blocknrmaxindex == max(blocknr)):
                break
            blocknrmaxindex = max(blocknr)
            startblock = blocknrmaxindex
            for addr in content['result']:
                outgoing_addr.add(addr['to'])
            print("Gathering 10000 outgoing transactions for addr %s starting at blocknr %s" % (addr_nanopool, startblock))

print("Writing outgoing addresses to outgoing_addr.json.")
with open('outgoing_addr_ethermine.json', 'w') as fid:
    json.dump(list(outgoing_addr), fid)
