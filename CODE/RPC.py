import requests
import json
import datetime

RPC_ENDPOINT = "http://127.0.0.1:8545"



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





def main():
    prevtimestamp = datetime.datetime.strptime("26/30/2015 17:07:14:382699", "%M/%d/%Y %H:%m:%S:%f")
    openingbracket = [
    f = open('../JSONDATA/JSONRPC/BLOCKDATA.json', 'a') as w:
    f.write('[', "a")
    for i in range(1,100):
        print("Parsing Block %i" % i)
        block = {}
        difficulty, timestamp, unclelen = eth_getBlockByNumber(i)
        blocktime = (prevtimestamp - timestamp).microseconds
        block['blocknr'] = i
        block['difficulty'] = difficulty
        block['unclelen'] = unclelen
        block['timestamp'] = datetime.datetime.strftime(timestamp, "%M/%d/%Y %H:%m:%S:%f")
        # block['blocktime'] = datetime.datetime.strftime(prevtimestamp, "%M/%d/%Y %H:%m:%S:%f")
        # prevtimestamp = timestamp


        with open('../JSONDATA/JSONRPC/BLOCKDATA.json', 'a') as w:
            json.dump(block, w, indent = 4)



if __name__ == "__main__":
    main()
