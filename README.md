# ASRogue
Artifacts for the USENIX Security '26 paper: "ASRogue: Manipulating ASRank-Inferred AS Relationships"

## Overview
- `asrank.py`: Provides a Python-based implementation of the ASRank inference algorithm.
- `GeneratePath.py`: Generates forged AS paths used in ASRogue's attack evaluation.
- `run multi.py`: Executes multiple experiments by randomly selecting a pair of target ASes and a pair of P2C ASes as attackers, constructing forged attack paths, and injecting them into ASRank's inference pipeline. After inference completes, the attacked results are compared against the original baseline output.

## Dataset
- **ASRank all-path dataset** : Obtainable from CAIDA, e.g. https://publicdata.caida.org/datasets/as-relationships/serial-1/

- **Real-world RIB dataset** : Downloadable from RouteViews and RIPE RIS, e.g.
https://data.ris.ripe.net/rrc00/2024.09/bview.20240930.0000.gz
http://archive.routeviews.org/route-views2/bgpdata/2024.09/RIBS/rib.20240930.0000.bz2

## Usage
1. Download the dataset `20241001.all-paths.bz2` from CAIDA, or obtain it by running
`download.py https://publicdata.caida.org/datasets/routing/20241001.all-paths.bz2 -o Data -d`.
2. Run the `model_run()` function in `run.py` to generate the original ASRank inference result, or directly use `data/inference-20241001_ori.txt` as the baseline output.
3. Run `run multi.py`  to evaluate the effectiveness of ASRogue. The attack outputs and corresponding analyses will be written to `data/attack result.txt`.