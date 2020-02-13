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
    #patches, texts = pie = plt.pie(sizes)

    # bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    # arrowprops=dict(arrowstyle="-",connectionstyle="angle,angleA=0,angleB=90")
    # kw = dict(xycoords='data',textcoords='data',arrowprops=arrowprops,
    #           bbox=bbox_props, zorder=0, va="center")
    #
    # for i, p in enumerate(patches):
    #     ang = (p.theta2 - p.theta1)/2.+p.theta1
    #     y = np.sin(ang/180.*np.pi)
    #     x = 1.35*np.sign(np.cos(ang/180.*np.pi))
    #     plt.gca().annotate(str(1+i), xy=(0, 0), xytext=( x, y), **kw )
    #
    #fig.set_size_inches(8, 8)
    plt.legend(labels, loc="upper right", bbox_to_anchor=(0.2,1.0), fontsize='x-small')
    plt.show()

    # plt.tight_layout()
    # plt.show()


    # with open('../JSONDATA/matchResults.json', 'w') as w:
    #     json.dump(resolvedMatches_ether, w, indent = 4)

def calcWeighedPoolAverage(match_data):
    allHardwareNames = [*hardwareRigs, *generalHardwareNames, *HardwareVariations, *specificHardwareNames, *asicHardwareNames]
    combinedEfficienciesByID = dict({'290X':11.3450074505, 'R9':10.2178544841, 'TITAN':6.8166899024,'390':8.401352612,'VEGA':7.2499232188 ,'A10':1.6865905503, 'SHARK':5.0953612925, 'THORIUM':4.788935705})
    cumulativeHashrate = 0
    product = 0
    for match in match_data:
        print(match['id'])
        efficiency = 0
        if match['id'] in combinedEfficienciesByID:
            efficiency = combinedEfficienciesByID[match['id']]
        elif match['id'] == "Combined Machines":
            effieciency = 0
        else:
            efficiency = float(list(filter(lambda gpu: match['id'] in gpu['Short'] , gpudata))[0]['Efficiency in J/Mh'])
        print(efficiency)
        print("from: " + str(list(filter(lambda gpu: match['id'] in gpu['Short'] , gpudata))))
        product+=(efficiency*float(match['hashrate']))
        cumulativeHashrate+=float(match['hashrate'])
    Hardwaremix = product/cumulativeHashrate
    print(Hardwaremix)

    # for id in allHardwareNames:
    #     if id in
    #         print(id)




def main():
    # #Nanopool
    # pruned_nano = pruneEmptyWorkerset(miner_workers_nanopool)
    # matches_nano = matchWorkersByName(pruned_nano)
    # matches_nano = resolveASICMiners(matches_nano)
    # resolvedMatches_nano = resolveMultipleMatches(matches_nano)
    # with open('../JSONDATA/Nanopool/miner_workers_matches_final.json', 'w') as w:
    #     json.dump(resolvedMatches_nano, w, indent = 4)
    # #----------------------------------------------------------------------------
    # #Ethermine
    # pruned_ether = pruneEmptyWorkerset(miner_workers_ethermine)
    # matches_ether = matchWorkersByName(pruned_ether)
    # matches_ether = resolveASICMiners(matches_ether)
    # resolvedMatches_ether = resolveMultipleMatches(matches_ether)
    # with open('../JSONDATA/Ethermine/miner_workers_matches_final.json', 'w') as w:
    #     json.dump(resolvedMatches_ether, w, indent = 4)

    #Group results
    out = groupResults(matches_nanopool,False)
    #with open('../JSONDATA/Nanopool/miner_worker_count.json', 'w') as w:
    #    json.dump(out, w, indent = 4)
    # out = groupResults(matches_ethermine)
    # with open('../JSONDATA/Ethermine/miner_worker_count.json', 'w') as w:
    #     json.dump(out, w, indent = 4)

    # with open('../JSONDATA/Ethermine/miner_worker_count.json') as r :
    #     data = json.load(r)
    #plotHardwareCount(out)
    calcWeighedPoolAverage(out)

main()
