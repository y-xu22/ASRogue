# ASRogue
Artifacts for the USENIX Security '26 paper: "ASRogue: Manipulating ASRank-Inferred AS Relationships"

## Overview
- `asrank.py`: A Python implementation of ASRank.
- `GeneratePath.py`: Generate forged AS paths for ASRogue.
- `run multi.py`: Run multiple experiments, each randomly selecting a target and an attacker, generating attack paths and injecting them into the input of ASRank. After inference completes, compare the attacked results with the original one.

## Dataset
- ASRank all path data: get from CAIDA, e.g. https://publicdata.caida.org/datasets/as-relationships/serial-1/

- RIB data: get from RouteViews and RIPE RIS, e.g.
https://data.ris.ripe.net/rrc00/2024.09/bview.20240930.0000.gz
http://archive.routeviews.org/route-views2/bgpdata/2024.09/RIBS/rib.20240930.0000.bz2

## Usage
1. Download the dataset `20241001.all-paths.bz2` from CAIDA, or run
`download.py https://publicdata.caida.org/datasets/routing/20241001.all-paths.bz2 -o Data -d`
to obtain the dataset.
2. Run `model_run()` function in `run.py` to obtain the origin inference result, or simply use `data/inference-20241001_ori.txt` as the baseline result.
3. Run `run multi.py`  to evaluate the effectiveness of ASRogue. The attack outputs will be recorded in `data/attack result.txt`.