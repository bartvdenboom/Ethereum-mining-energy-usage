import requests
import json
import datetime

RPC_ENDPOINT = "http://127.0.0.1:8545"
IPC_ENDPOINT = "/Users/bartboom/Library/Ethereum/geth.ipc"

with open('../JSONDATA/Etherscan/EtherPrice.json') as r:
    pricedata = json.load(r)


def eth_getBlockByNumber(blocknr):
    blockhex = str(hex(blocknr))
    payload = {
        "jsonrpc":"2.0",
        "method":"eth_getBlockByNumber",
        "params":[blockhex, True],
        "id":1
    }
    response = requests.post(RPC_ENDPOINT,json=payload).json()['result']
    difficulty = int(response['difficulty'], 16)
    timestamp = datetime.datetime.fromtimestamp(int(response['timestamp'], 16))
    unclelen = len(response['uncles'])
    return difficulty,timestamp,unclelen

def eth_getBlockByNumberIPC(blocknr):
    return 0

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


def runIPC(start_blocknr, stop_blocknr):
    difficulty_start,prevtimestamp,unclelen_start = eth_getBlockByNumber(start_blocknr)
    difficulty_avg = difficulty_start
    blocktime_avg = 0
    unclelen_avg = unclelen_start
    nr_of_blocks = 1
    day_since_genesis = 0
    for i in range(start_blocknr+1,stop_blocknr):
        difficulty, timestamp, unclelen = eth_getBlockByNumber(i)
        if prevtimestamp:
            blocktime = (timestamp - prevtimestamp).total_seconds()
        else:
            blocktime = 0

        if timestamp.day == prevtimestamp.day:
            difficulty_avg += difficulty
            blocktime_avg += blocktime
            unclelen_avg += unclelen
            nr_of_blocks += 1
        else:
            print("Parsing date %s" % datetime.datetime.strftime(prevtimestamp, "%m/%d/%Y"))
            difficulty_avg = difficulty_avg / nr_of_blocks
            blocktime_avg = blocktime_avg / nr_of_blocks
            unclelen_avg = unclelen_avg / nr_of_blocks
            if unclelen_avg > 0:
                unclerate = unclelen/nr_of_blocks
            else:
                unclerate = 0
            day = {}
            day['date'] = datetime.datetime.strftime(prevtimestamp, "%m/%d/%Y %H:%M:%S")
            day['ethprice'] = float(pricedata[day_since_genesis]['Value'])
            day['timespan'] = blocktime_avg * nr_of_blocks
            day['averagedifficulty'] = difficulty_avg
            day['averageblocktime'] = blocktime_avg
            day['computedhashrate'] = (difficulty_avg*(1+unclerate))/blocktime_avg
            day['dailyETHreward'] = (nr_of_blocks * getBlockReward(i)) + (nr_of_blocks * unclerate * getUncleReward(i))
            day['unclerate'] = unclerate

            with open('../JSONDATA/JSONRPC/BLOCKDATA.json', 'r+') as file:
                data = json.load(file)
                data.append(day)
                file.seek(0)
                json.dump(data, file, indent = 4)

            difficulty_avg = difficulty
            blocktime_avg = blocktime
            unclelen_avg = unclelen
            nr_of_blocks = 1
            day_since_genesis += 1

        prevtimestamp = timestamp

def main():
    runIPC(1,15000)

if __name__ == "__main__":
    main()
