# ASRogue
Artifacts for the USENIX Security '26 paper: "ASRogue: Manipulating ASRank-Inferred AS Relationships"

## Overview

1. `asrank.py`: Provides a Python-based implementation of the ASRank inference algorithm.
2. `GeneratePath.py`: Generates forged AS paths used in ASRogue's attack evaluation.
3. `run_multi.py`: Executes multiple experiments by randomly selecting a pair of target ASes and a pair of P2C ASes as attackers, constructing forged attack paths, and injecting them into ASRank's inference pipeline. After inference completes, the attacked results are compared against the original baseline output.
4. Files in `data`: `inference-20241001_ori.txt` is the baseline ASRank inference output. `all rel TD.txt` lists, for each relationship in `inference-20241001_ori.txt`, the two ASes' transit degree values, their difference, and the inference step. `AS_size.txt` gives the number of ASes in each size category and the ASNs included in each category. `p2c rel tg.txt` contains, for each provider-to-customer (P2C) relation in `inference-20241001_ori.txt`, the two ASes' transit degree values, their difference, and the inference step.
5. Files in `plot and table data`: contain the plotting data, plotting scripts, table data, table-generation scripts, and generated figures.

## Dataset

1. **ASRank all-path dataset** :  
Available from CAIDA (e.g. https://publicdata.caida.org/datasets/as-relationships/serial-1/20241001.all-paths.bz2) or directly use the local copy of `20241001.all-paths.bz2`.
2. **Real-world RIB dataset** :  
Downloadable from RouteViews and RIPE RIS, e.g.  
https://data.ris.ripe.net/rrc00/2024.09/bview.20240930.0000.gz  
http://archive.routeviews.org/route-views2/bgpdata/2024.09/RIBS/rib.20240930.0000.bz2

	- Due to Zenodo's storage limitations, only a subset of the RIB snapshots from RouteViews and RIPE RIS is included directly.

## Requirements
- System and hardware requirements: No specific requirements
- Software requirements: Python 3.11
- Python dependencies: see `requirements.txt`
	- To run the BEAM poisoning experiment, you need an NVIDIA GPU with at least 8 GB of memory, as well as three additional dependencies: `torch`, `scipy`, and `python-dateutil`.

## Setup
1. Create and activate a Python 3.11 environment.
	```bash
	python -m venv .venv
	source .venv/bin/activate
	```
2. Install the required packages.
	```bash
	python -m pip install -r requirements.txt
	```

## Usage
1. Download the dataset `20241001.all-paths.bz2` from CAIDA, or obtain it by running
`python download.py https://publicdata.caida.org/datasets/as-relationships/serial-1/20241001.all-paths.bz2 -o data`. Alternatively, you can use the local copy of `20241001.all-paths.bz2`.
2. Run `python run.py` to generate the baseline ASRank inference result and `model_ori.pkl`. Then rename the generated `data/inference-20241001.txt` to `data/inference-20241001_ori.txt`, or directly use `data/inference-20241001_ori.txt` as the baseline output.
3. Run `python run_multi.py {step2, allp2c, allrel} {ASsize, allrand, p2p} {round}` to evaluate ASRogue's effectiveness. The tool randomly selects reverse provider/customer and attacker ASes, generates forged attack paths, and injects them into the inference pipeline. Attack results and corresponding analyses will be written to `data/attack result.txt`.