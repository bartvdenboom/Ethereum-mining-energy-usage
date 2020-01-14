import requests
import json
import time

#NANOPOOL
MINERDASHBOARD_ETHERMINE_URL_PREFIX = "https://api.ethermine.org/miner/"
miner_addr = "0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8"
MINERDASHBOARD_ETHERMINE_URL_SUFFIX = "/dashboard"

def old():
    with open('../JSONDATA/Ethermine/outgoing_addr_ethermine.json') as f:
        content = json.load(f)
    requesttimestamp = 0
    miners = list()
    #65287 addresses
    #ETHERMINE API allows for 100 API calls per 15 minutes = approx 9 seconds bewteen each call
    for i in range(26000, 26500):
        print("Processing address %i of %i" % (i, len(content)))
        workers = list()
        miner = {}
        miner_addr = content[i]
        if (time.time()-requesttimestamp < 9):
            time.sleep(9-(time.time()-requesttimestamp))
            #Making sure not to make more than 30 API calls per minute
        print("Delta t = %f" % (time.time()-requesttimestamp))
        requesttimestamp = time.time()
        req = requests.get(url=MINERDASHBOARD_ETHERMINE_URL_PREFIX+miner_addr+MINERDASHBOARD_ETHERMINE_URL_SUFFIX)
        req_data = req.json()
        #print(req_data)
        if req_data['status'] == "OK":
            print("Miner found.")
            miner['Mineraddr'] = miner_addr
            print(miner)
            miners.append(miner)
            for i in range(0, len(req_data['data']['workers'])):
                worker ={}
                worker['id'] = req_data['data']['workers'][i]['worker']
                worker['hashrate'] = (req_data['data']['workers'][i]['currentHashrate']/1000000)
                worker['reportedhashrate'] = (req_data['data']['workers'][i]['reportedHashrate']/1000000)
                workers.append(worker)
            miner['Workers'] = workers
        else:
            print("Miner not found.")

    with open('miner_workers_ethermine_26000-26500.json', 'w') as fid:
        json.dump(miners, fid)
    print("Done.")




def workers_miners():
    with open('../JSONDATA/Ethermine/outgoing_addr_ethermine.json') as f:
        content = json.load(f)

    with open('../miner_workers_ethermine_final.json') as r:
        results = json.load(r)

    requesttimestamp = 0
    # 65287 addresses
    # ETHERMINE API allows for 100 API calls per 15 minutes = approx 9 seconds bewteen each call
    for i in range(len(results), len(content)):
        print("Processing address %i of %i" % (i, len(content)))
        workers = list()
        miner = {}
        miner_addr = content[i]
        if (time.time()-requesttimestamp < 9):
            time.sleep(9-(time.time()-requesttimestamp))
            #Making sure not to make more than 30 API calls per minute
        print("Delta t = %f" % (time.time()-requesttimestamp))
        requesttimestamp = time.time()
        req = requests.get(url=MINERDASHBOARD_ETHERMINE_URL_PREFIX+miner_addr+MINERDASHBOARD_ETHERMINE_URL_SUFFIX)
        req_data = req.json()
        if req_data['status'] == "OK":
            print("Miner found.")
            miner['Mineraddr'] = miner_addr
            for i in range(0, len(req_data['data']['workers'])):
                worker ={}
                worker['id'] = req_data['data']['workers'][i]['worker']
                worker['hashrate'] = (req_data['data']['workers'][i]['currentHashrate']/1000000)
                worker['reportedhashrate'] = (req_data['data']['workers'][i]['reportedHashrate']/1000000)
                workers.append(worker)
            miner['Workers'] = workers
            results.append(miner)
            with open('../miner_workers_ethermine_final.json', 'w') as fid:
                json.dump(results, fid, indent = 4)
        else:
            print("Miner not found.")
    print("Done.")

workers_miners()
