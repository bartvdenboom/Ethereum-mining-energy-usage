#Research Internship literature findings

##Reading list

###Comparative evaluation of consensus mechanisms in cryptocurrencies, Shihab S. Hazari Qusay H. Mahmoud

Badly written
Ethereum still POW istead of POS

###Proof of Stake with Casper the Friendly Finality Gadget Protocol for Fair Validation Consensus in Ethereum, Jain et al.

Switch from POW to POS

Casper-the Friendly Finality Gadget protocol

####Proof of stake

Block creation is called minting
The stake in the currency represents the amount of blocks that can be minted
Stake is locked untill mintin occurs
forger or minter is rewarded with transaction fees, no new crypto is generated

Live examples: Peercoin, Nxt, Blackcoin, and shadowcoin

####Casper-the Friendly Finality Gadget protocol
Casper follows Byzantine Fault Tolerant based proof of stake algorithm with some modifications.
The additional features include:

● Accountability: Violation of a rule can easily be detected and the guilty validators are penalized by slashing of their deposit
● Dynamic Validators: Validators can easily join and withdraw from the validator set with some delay
● Defenses: Casper has the ability to defend against long range revision attacks and attacks where > 1⁄3 validators drop offline.
● Modular overlay: Casper’s design is an overlay on the existing Proof of Work chain, which makes it easier to implement


###Proof of Kernel Work: a democratic low-energy consensus for distributed access-control protocols, Lundbæk et al.



###Blockchain Consensus Protocols, Energy Consumption and Cryptocurrency Prices, Sapkota et al.


Crypocurrencies do not follow higher risk higher payoff from financial theory


###Is Bitcoin the Only Problem? A Scenario Model for the Power Demand of Blockchains, Zade et al.

Hayes (economical model) of calculating energy costs associated with bitcoin

De Vries (digiconomist) can provide upper bound

Research in current and possibly future power draw of ethereum

####Estimates vary:
Krause et al (no access to paper)
2017: 299 MW

Zade et al:
2017: 367 MW 

Stoll et at:

2017: 1,637 MW (more inclusive with cooling costs)

mrb's blog:
2017:
640 MW - 1248 MW

Current(year): 0.6 to 3 GW

Results based upon Hashrate, difficulty and test results of possibly used hardware.

----

<https://www.ofnumbers.com/2018/08/26/how-much-electricity-is-consumed-by-bitcoin-bitcoin-cash-ethereum-litecoin-and-monero/>

gpu candidates: vega64

would mean 900 MW 

####ETHEREUM  WILL CUT BACK  ITS ABSURD ENERGY  USE

Ethereum mining uses a quarter o a half of what bitcoin mining uses.


-------

###The carbon footprint of Bitcoin, Stoll et al.




#Methodologies of determining Cryptocurrency (Bitcoin) power usage

#####Hayes (2015)[OBSOLETE]
Production costs of bitcoin using outdated assumptions

#####Digiconimist (later)
By looking at the revenue, capital investment, percentage of revenue used as electricity to provice an upper bound.

#####mbr blog (Errors in digiconomist, Feb 2017)
Points out everything wrong, (selective) misinterpretation, wrong assumptions on hardware mix used and portion of revenue used for electricity (adoption of hardware)

#####mbr blog(Electricity consumption of Bitcoin: a market-based and technical analysis)

Both technical and economical approach (most complete)

Average hashing efficiency using weighted average of market share hardware

#####Cambridge Bitcoin Electricity Consumption Index
Based on bottom-up approach of Bevand.
Largely follows results from Digiconomist.


#####Vranken (2017)
Comparative analysis, best guess


#####Energy consumption of cryptocurrency mining(Li)
Experimental setup using decicated computers mining Monero.

#####Stoll(2019)
Lower limit by hash rate and most efficient hardware
Upper limit by break even point of revenues and electricity costs (Marc bevand)

Then a best guess is constructed using the PUE(Power usage effectiveness)

The effectiveness of the network is calculated using the market shares of hardware and and efficiency of hardware in operation.

The residual computing power is dedicated to hardware not generating profit (relatively STRONG ASSUMPTION)

Furthermore, mining operations are split into three groups, small, medium and large with correspoding PUE values. (Data derived from a large pulbic mining pool)


Can provide upper and lower bound by looking at worst-case and best-case hardware-mix.

####Quantification of energy and carbon costs for mining cryptocurrencies, Krause


#[DRAFT]Proposed Method for calculating Ethereums power usage 

##(Flawed?) Digiconomist method (Ethereum energy index)
* Total mining revenues are calculated and converted to USD
* Estimated what part of mining revenues are being spent on electricity costs
* The resulting numer is easily converted to kolowatt-hours by dividing by average electricity costs

###Problems with this approach
* Largely the same as with Marc Bevands critisism on his Bitcoin energy index:
	* Estimation of amount of energy spent may be far-off. Especially considering Ethereum is mined on GPU's, often not on a large scale (industrially)
* Average electricity cost need to be a weighed electricity costs because a share of the hashing power of the Ethereum network is industrial (lower electricity cost) and a share is people at home (higher).

	 
##Fundamental differences comparing to bitcoin
* PoW algirthm is memory-hard thus ASICS usage for mining is not conventional
* Hardware mix of Ethereum may be harder to determine
	* GPU mining is agreed upon the largest portion
	* Incentives may be different from purely economic because not every user performs an extensive cost-benefit analysis (Think of students not paying for their electricity and using their GPU when they are not using them for gaming). This makes 'unprofitable' GPU's still profitable.
* 


##Open questions
* What is portion of energy used for the execution of Smart Contracts (Largely the portion of energy used in the upcoming PoS system?) and what is used for the Proof of work? 
* Hardware mix
	* Innosilicon A10?
	* Other ASIC developments
	* GPU farms : home users
	* What is still profitable? Also looking at price developments
		* What was profitable in the peak?



##READ - TODO
Demystifying Crypto-Mining:
Analysis and Optimizations of memory-hard PoW Algorithms

Mathematical analysis of memory hard pow (ethash) (malone)
Daarna model opstellen met aannamen over laagste gemiddelde van hardware efficientie.
Large mining pools -> can we deduce the average efficiency of one card? -> extrapolate to model seems like a smart thing to do

eth.nanopool.org for hardware statistics?