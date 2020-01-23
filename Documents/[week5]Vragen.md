#Research Internship
##Week 5 
###Verzamelen blockdata
Gezien met huidige API er een beperking is tov de compleetheid van data: er wordt slechts gekeken naar blocks gedurende 2 uur per week. Meer laat de API van ETHERSCAN niet toe. De literatuur heeft een aantal tools die kunnen helpen, echter:

#####Ethereum-etl (python package):
Data heeft alles behalve genoeg informatie over de uncles.
Wellicht deze data gebruiken en uncle-data van andere bron?

#####JSON-RPC:
Heel compleet, echter heb je een geth/parity full ethereum node nodig om alle data van oude blokken te kunnen opvragen. Dit vereist een computer met veel (300GB-2TB) en snelle opslag. Het sync-process schijnt ook weken te kunnen duren. 

#####Upper bound
#####CBECI

Assumption 2: during time periods where no mining equipment is profitable, the model uses the last known profitable equipment.

Assumption 3b (upper bound): all miners always use the least efficient hardware available at each time period as long as the equipment is still profitable in terms of electricity costs.

The model applies a 14-day moving average to the profitability threshold in order to smoothen the switch from one equipment type to another as a result of short-term hashrate variations and price volatility.

As soon as a given equipment type is not profitable anymore, it will be retired and replaced with the next least efficient hardware model that still remains profitable.

It is worth remembering that the profitability threshold for each mining hardware type is calculated strictly in electricity terms and does not take into account capital expenditures nor other operational expenditures.

Assumption 4b (upper bound): all mining facilities have a PUE of 1.20.



#####Bevand
We can calculate the upper bound for the global electricity consumption of Bitcoin miners by assuming they deploy the least efficient hardware of their time and never upgrade it.

The model presented in this post makes one assumption: it looks at the difference in hash rate between the beginning and end of a phase, and assumes it indicates how many machines were manufactured during that phase.

Hypothetically, if a machine is first put online, and if it is immediately decommissioned within the same phase (eg. mining is suddenly no longer profitable,) and if it is put online again in a subsequent phase (eg. mining is profitable again,) then the model would classify the extra hash rate as belonging to the wrong phase.

Firstly we assume that 100% of the mining power added during each phase came from the least efficient hardware available at that time that is still mining profitably



