import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plot


with open("../JSONDATA/Nanopool/miner_workers_nanopool_final0.json") as r:
    miner_workers_nanopool = json.load(r)
with open("../JSONDATA/Ethermine/miner_workers_ethermine_final0.json") as r:
    miner_workers_ethermine = json.load(r)
with open("../JSONDATA/Nanopool/miner_workers_matches_final.json") as r:
    matches_nanopool = json.load(r)
with open("../JSONDATA/Ethermine/miner_workers_matches_final.json") as r:
    matches_ethermine = json.load(r)
with open('../JSONDATA/GPUdata/GPUDATA.json') as r:
    gpudata = json.load(r)



asicHardwareNames = ["E3", "ANTMINER", "ETHMASTER", "A10", "BITMAIN", "INNOSILICON"]
specificHardwareNames  = ["7870", "7990", "770", "R9", "750", "TITAN", "295X2", "970", "960", "390", "370", "380", "FURY",
                           "480", "460", "470", "570", "580", "550", "VEGA", "VII", "V100", "590",  "P100", "560",  "P104",
                          "P106", "680", "660", "650"]

HardwareVariations = ["780TI", "980TI", "1050TI", "1080TI", "1070TI", "2080TI", "380X", "5700XT", "1660TI", "290X", "2070TI", "2060TI", "1650TI"]
generalHardwareNames = ["780", "980", "290", "1080", "1050", "1060", "1070", "2070", "2060", "1650", "2080", "1660","5700"]
hardwareRigs = ["SHARK", "MAXIMUS", "ULTRON", "IMPERIUM", "THORIUM", "ZODIAC", "G2", "G1"]

combinedEfficienciesByID = dict({
'290X':11.3450074505,
'R9':10.2178544841,
'TITAN':6.8166899024,
'390':8.401352612,
'VEGA':7.2499232188 ,
'2070':4.911674347,
'2060':4.920212766,
'2080':5.521375075,
'A10':1.6865905503,
'ETHMASTER':1.6865905503,
'INNOSILICON':1.6865905503,
'SHARK':5.0953612925,
'THORIUM':4.788935705,
'7870':17.15686275 ,
'680':13 ,
'660':12.76595745 ,
'650': 10.64859632,
'7990': 10.41666667,
'780': 12.5,
'770': 15.33333333,
'760': 11.33333333,
'780TI':11.36363636 ,
'750': 6.666666667,
'295X2': 10.86956522,
'980': 8.25,
'970': 9.119496855,
'960': 11.00917431,
'370': 9.166666667,
'380': 11.17647059,
'FURY': 11.70212766,
'980TI': 10.63829787,
'380X': 11.11111111,
'1080': 6.666666667,
'480': 6,
'1070': 5,
'460': 5.769230769,
'470': 6.25,
'1060': 5,
'1050TI': 5,
'1050' : 5,
'1080TI': 6.756756757,
'570': 5.227272727,
'580': 6.166666667,
'550': 4.545454545,
'1070TI': 4.6875,
'1650': 5,
'VII': 3.296703297,
'V100':2.631578947 ,
'2080TI': 4.807692308,
'590': 7.03125,
'5700': 5.160550459,
'5700XT':5.365296804 ,
'P100': 5.165289256,
'1660': 6.818181818,
'1660TI': 4.597701149,
'560': 9.210526316,
'E3': 4.444444444,
'ANTMINER': 4.444444444,
'BITMAIN':4.444444444 ,
'P104': 3.375,
'P106': 3.269230769,
'MAXIMUS': 5.945945946,
'ULTRON': 5.3125,
'IMPERIUM':5.652173913 ,
'BITMAIN': 5.454545455,
'G2': 5.454545455,
'ZODIAC':6.209637357,
})

def getSubstringMatches(workernames, keywords):
    out = list()
    notmatched = list()
    amountMatched = 0
    matched = False
    for worker in workernames:
        matches = list()
        matched = False
        for word in keywords:
            if word in worker.upper():
                matched = True
                matches.append(word)
        if matched:
            amountMatched +=1
        else:
            notmatched.append(worker)
        result = (worker, matches)
        if matched:
            out.append(result)
    print("Coverage ratio = %i%%", (amountMatched/len(workernames)*100))
    with open('../JSONDATA/substringmatches.json', 'w') as w:
            json.dump(out, w, indent = 4)
    with open('../JSONDATA/notsubstringmatches.json', 'w') as w:
            json.dump(notmatched, w, indent = 4)

def matchBySubstrings(worker, keywords):
    matches = list()
    for word in keywords:
        if word in worker.upper():
            matches.append(word)
    return matches

def matchWorkersByName(minerworkerdata):
    out = list()
    for miner in minerworkerdata:
        for worker in miner['Workers']:
            matches = matchBySubstrings(worker.get('id'), hardwareRigs)
            if len(matches)==0:
                matches = matchBySubstrings(worker.get('id'), HardwareVariations)
            if len(matches)==0:
                matches = matchBySubstrings(worker.get('id'), generalHardwareNames)
            if len(matches)==0:
                matches = matchBySubstrings(worker.get('id'), specificHardwareNames)
            if len(matches)==0:
                matches = matchBySubstrings(worker.get('id'), asicHardwareNames)
            worker['Matches'] = matches
        out.append(miner)
    return out

def pruneEmptyWorkerset(minerworkerdata):
    out = list()
    for miner in minerworkerdata:
        if miner['Workers']:
            out.append(miner)
    return out

def resolveMultipleMatches(minerworkerdata):
    out = list()
    for i in range(0,len(minerworkerdata)):
        for worker in minerworkerdata[i]['Workers']:
            matches = worker.get('Matches')
            newmatches = list()
            if len(matches)>1:
                print("\n")
                print("Index %i of %i" % (i, len(minerworkerdata)))
                print("id= " + worker.get('id'))
                print("hashrate= " + str(worker.get('hashrate')))
                print("--------------------------")
                count = 0
                for word in matches:
                    print(str(count) + ": " + str(word))
                    count+=1
                choice = int(input("Choose "))
                if(choice==-1):
                    newmatches = []
                elif(choice==-2):
                    newmatches = matches
                else:
                    newmatches = matches[choice]
                worker['Matches'] = newmatches
        out.append(minerworkerdata[i])
    return out

def getMatchRatioAndWorkerCount(minerworkerdata):
    workercount = 0
    matchcount = 0
    for miner in minerworkerdata:
        for worker in miner['Workers']:
            workercount += 1
            if len(worker['Matches'])>0:
                matchcount += 1
    return ((matchcount/workercount), workercount)

def showMatches(keyword, minerworkerdata):
    count = 0
    for miner in minerworkerdata:
        for worker in miner['Workers']:
            for match in worker['Matches']:
                if match == keyword:
                    print(worker['id'] + " hashrate: " + str(worker['hashrate']))

                    count += 1
    ratio, workercount = getMatchRatioAndWorkerCount(minerworkerdata)
    print(keyword + " has %i matches found out of %i workers (Matching coverage=%f)." % (count, workercount, ratio))

def resolveASICMiners(minerworkerdata):
    E3_hashrate_min = 180
    E3_hashrate_max = 220
    A10_hashate_min = 365
    A10_hashrate_max = 500
    G2_hashrate = 220
    margin = 10
    m = list()
    for miner in minerworkerdata:
        for worker in miner['Workers']:
            for match in worker['Matches']:
                if match == "E3" and (float(worker.get('hashrate')) + margin < E3_hashrate_min or float(worker.get('hashrate')) - margin > E3_hashrate_max or float(worker.get('hashrate'))<=0.0) :
                    worker['Matches'].remove(match)
                    print("Removed E3")
                elif match == "A10" and (float(worker.get('hashrate')) + margin < A10_hashate_min or float(worker.get('hashrate')) - margin > A10_hashrate_max or float(worker.get('hashrate'))<=0.0):
                    worker['Matches'].remove(match)
                    print("Removed A10")
                elif match == "G2" and (float(worker.get('hashrate')) + margin < G2_hashrate or float(worker.get('hashrate')) - margin > G2_hashrate or float(worker.get('hashrate'))<=0.0):
                    worker['Matches'].remove(match)
                    print("Removed G2")
        m.append(miner)
    return m

def groupResults(minerworkerdata, group):

    # E3_ANTMINER = 0         #Tags "E3" or "ANTMINER"
    # ETHMASTERA10 = 0        #Tags "ETHMASTER", "A10", "INNOSILICON"
    # BITMAIN = 0             #Tags "BITMAIN"
    allHardwareNames = [*hardwareRigs, *generalHardwareNames, *HardwareVariations, *specificHardwareNames, *asicHardwareNames]

    out = list()
    mixed = 0
    total = 0
    for name in allHardwareNames:
        result = {}
        result['id'] = name
        c = 0
        h = 0
        for miner in minerworkerdata:
            for worker in miner['Workers']:
                for matches in worker['Matches']:
                    if name in matches:
                        c+=1
                        total+=float(worker['hashrate'])
                        if(len(worker['Matches'])==1):
                            h+=float(worker['hashrate'])
                        else:
                            mixed+=float(worker['hashrate'])

        result['count'] = c
        result['hashrate'] = h
        out.append(result)
    result = {}
    result['id'] = "Combined Machines"
    result['hashrate'] = mixed
    out.append(result)
    out = list(filter(lambda x:x['hashrate']>0, out))
    out = sorted(out, key = lambda x:x['hashrate'])
    if group:
        groupedhashrate = sum(hardware['hashrate'] for hardware in out)/20
        c=0
        sum_lowest_5percent = 0
        grouped_names = ""
        while (sum_lowest_5percent < groupedhashrate):
            if out[c]['id'] not in [*asicHardwareNames, *hardwareRigs]:
                grouped_names += out[c]['id'] + ", "
                sum_lowest_5percent+= float(out[c]['hashrate'])
                out[c]['hashrate'] = -1

            c+=1
            if c%5==0:
                grouped_names+="\n"

        grouped_names=grouped_names[:-3]
        out = list(filter(lambda x:x['hashrate']>0, out))
        result = {}
        result['id'] = grouped_names
        result['hashrate'] = sum_lowest_5percent
        out.append(result)
        out = sorted(out, key = lambda x:x['hashrate'])
    return out

def plotHardwareCount(minerworkerdata):
    a = pd.DataFrame(minerworkerdata)
    labels = a['id'].values
    sizes = a['hashrate'].values
    percent = 100.*sizes/sizes.sum()
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(labels, percent)]
    fig,ax=plt.subplots()
    ax.pie(sizes)
    ax.axis('equal')

    plt.legend(labels, loc="upper right", bbox_to_anchor=(0.2,1.0), fontsize='x-small')
    plt.show()

def calcWeighedPoolAverage(match_data):
    allHardwareNames = [*hardwareRigs, *generalHardwareNames, *HardwareVariations, *specificHardwareNames, *asicHardwareNames]
    cumulativeHashrate = 0
    weightedProduct = 0
    for match in match_data:
        efficiency = 0
        if match['id'] in combinedEfficienciesByID:
            efficiency = combinedEfficienciesByID[match['id']]
            weightedProduct+=(efficiency*float(match['hashrate']))
            cumulativeHashrate+=float(match['hashrate'])
    Hardwaremix = weightedProduct/cumulativeHashrate
    print(Hardwaremix)


def plotHardwareDistribution(minerdata):
    hashratePerWorker = np.array([float(l['hashrate']) for l in [w for l in [l['Workers'] for l in minerdata] for w in l]])
    workersPerMiners = [l['Workers'] for l in minerdata]
    hashratePerMiner = []
    for i in range(len(workersPerMiners)):
        hashratePerMiner.append(sum([float(worker['hashrate']) for worker in workersPerMiners[i]]))
    hashratePerMiner = np.array(hashratePerMiner)
    data=hashratePerMiner
    bins=[0,5,10,20,30,50,100,200,500,1000,5000,10000,20000,100000]
    plt.hist(data,range(int(data.min()), int(data.max()), 10), density=False)
    plt.xscale('log')
    plt.show()


def main():
    # Nanopool
    # pruned_nano = pruneEmptyWorkerset(miner_workers_nanopool)
    # matches_nano = matchWorkersByName(pruned_nano)
    # matches_nano = resolveASICMiners(matches_nano)
    # resolvedMatches_nano = resolveMultipleMatches(matches_nano)
    # with open('../JSONDATA/Nanopool/miner_workers_matches_final.json', 'w') as w:
    #     json.dump(resolvedMatches_nano, w, indent = 4)

    # Weighted average of mining efficiency of identified mining hardware
    # calcWeighedPoolAverage(groupResults(matches_nanopool, False))
    # Evaluates to 5.8693368304852855

    # Plot histogram of distribution of hashrate per miner
    # plotHardwareDistribution(matches_nanopool)

    # Plot pie chart of mining hardware distribution according to reported hashrate
    # plotHardwareCount(groupResults(matches_nanopool, True))

    # #----------------------------------------------------------------------------

    # Ethermine
    # pruned_ether = pruneEmptyWorkerset(miner_workers_ethermine)
    # matches_ether = matchWorkersByName(pruned_ether)
    # matches_ether = resolveASICMiners(matches_ether)
    # resolvedMatches_ether = resolveMultipleMatches(matches_ether)
    # with open('../JSONDATA/Ethermine/miner_workers_matches_final.json', 'w') as w:
    #     json.dump(resolvedMatches_ether, w, indent = 4)

    # Weighted average of mining efficiency of identified mining hardware
    # calcWeighedPoolAverage(groupResults(matches_ethermine, False))
    # Evaluates to 5.851414739775516

    # Plot histogram of distribution of hashrate per miner
    # plotHardwareDistribution(matches_ethermine)

    # Plot pie chart of mining hardware distribution according to reported hashrate
    # plotHardwareCount(groupResults(matches_ethermine, True))
    out = groupResults(matches_ethermine, True)
    threshold = 4.714682
    totalhashrate = 0
    underprofit = 0
    for i in out:
        totalhashrate+=i['hashrate']
        if i['id'] in combinedEfficienciesByID:
            if (combinedEfficienciesByID[i['id']] > threshold):
                underprofit+=i['hashrate']
    print(underprofit)
    print(totalhashrate)
    print(underprofit/totalhashrate*100)

if __name__ == "__main__":
    main()
