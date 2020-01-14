import requests
import json
import time

#NANOPOOL
MINERSTATS_NANOPOOL_URL_PREFIX = "https://api.nanopool.org/v1/eth/user/"
miner_addr = ""

with open('outgoing_addr.json') as f:
    content = json.load(f)

requesttimestamp = 0
miners = list()
#First 0 to 12000
#Then 12000 to 24000
#Then 24000 to 29493
for i in range(24000, len(content)):
    print("Processing address %i of %i" % (i, len(content)))
    workers = list()
    miner = {}
    miner_addr = content[i]
    if (time.time()-requesttimestamp < 2):
        time.sleep(2-(time.time()-requesttimestamp))
        #Making sure not to make more than 30 API calls per minute
    print("Delta t = %f" % (time.time()-requesttimestamp))
    requesttimestamp = time.time()
    req = requests.get(url=MINERSTATS_NANOPOOL_URL_PREFIX+miner_addr)
    req_data = req.json()
    if req_data['status'] == True:
        print("Miner found.")
        miner['Mineraddr'] = miner_addr
        print(miner)
        miners.append(miner)

        for i in range(0, len(req_data['data']['workers'])):
            worker ={}
            worker['id'] = req_data['data']['workers'][i]['id']
            worker['hashrate'] = req_data['data']['workers'][i]['hashrate']
            workers.append(worker)
        miner['Workers'] = workers
    else:
        print("Miner not found.")

with open('miner_workers_nanopool_24000-last.json', 'w') as fid:
    json.dump(miners, fid)

print("Done.")
