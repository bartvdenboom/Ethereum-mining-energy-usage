import json
import matplotlib.pyplot as mpl
import pandas as pd


with open("../JSONDATA/Nanopool/miner_workers_nanopool_final0.json") as r:
    miner_workers_nanopool = json.load(r)
with open("../JSONDATA/Ethermine/miner_workers_ethermine_final0.json") as r:
    miner_workers_ethermine = json.load(r)


specificHardwareNames  = ["7870", "7990", "770", "R9", "750", "TITAN", "295X2", "970", "960", "390", "370", "380", "FURY",
                           "480", "460", "470", "570", "580", "550", "VEGA", "VII", "V100",
                          "590",  "P100", "560", "E3", "ANTMINER", "ETHMASTER", "A10", "P104",
                          "P106", "680", "660", "650"]

HardwareVariations = ["780TI", "980TI", "1050TI", "1080TI", "1070TI", "2080TI", "380X", "5700XT", "1660TI", "290X", "2070TI", "2060TI", "1650TI"]
generalHardwareNames = ["780", "980", "290","1080", "1050", "1060", "1070", "2070", "2060", "1650", "2080", "1660","5700"]
hardwareRigs = ["SHARK", "MAMIMUS", "ULTRON", "IMPERIUM", "THORIUM", "ZODIAC"]

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
            worker['Matches'] = matches
        out.append(miner)
    return out
    # with open('../JSONDATA/Nanopool/miner_workers_matches.json', 'w') as w:
    #     json.dump(out, w, indent = 4)

def pruneEmptyWorkerset(minerworkerdata):
    out = list()
    for miner in minerworkerdata:
        if miner['Workers']:
            out.append(miner)
    return out
    # with open('../JSONDATA/Nanopool/miner_workers_matches_pruned.json', 'w') as w:
        # json.dump(out, w, indent = 4)

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
                    #print(worker['id'] + " hashrate: " + worker['hashrate'])

                    count += 1
    ratio, workercount = getMatchRatioAndWorkerCount(minerworkerdata)
    print(keyword + " has %i matches found out of %i workers (Matching coverage=%f)." % (count, workercount, ratio))


def matchResults():
    for name in specificHardwareNames:
        showMatches(name, workerdata_nanopool)
    for name in HardwareVariations:
        showMatches(name, workerdata_nanopool)
    for name in generalHardwareNames:
        showMatches(name, workerdata_nanopool)


def main():
    # pruned = pruneEmptyWorkerset(miner_workers_ethermine)
    # matches = matchWorkersByName(pruned)
    # with open('../JSONDATA/Ethermine/miner_workers_matches.json', 'w') as w:
    #     json.dump(matches, w, indent = 4)
    # resolvedMatches = resolveMultipleMatches(matches)
    # with open('../JSONDATA/Ethermine/miner_workers_matches_resolved.json', 'w') as w:
    #     json.dump(resolvedMatches, w, indent = 4)







main()

#matchWorkersByName(miner_workers_nanopool)
#pruneEmptyWorkerset(miner_workers_nanopool_matched)
#resolveMultipleMatches(workernames_nanopool_matched_pruned)
