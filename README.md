# van der Meer lab → BIDS

Conversion tools for ingesting data from the van der Meer group at Dartmouth College and outputting it into BEP-32 compliant datasets for upload to the DANDI Archive.



## Usage

### CLI

```bash
vandermeer2bids odorseq \
  --data-directory <source data directory> \
  --subject-id <subject ID> \
  --session-id <session ID> \
  --dandiset-directory <dandiset directory>
```

For example:

```bash
vandermeer2bids odorseq \
  --data-directory E:/bids_32_examples/mvdm/OdorSequence/sourcedata \
  --subject-id M541 \
  --session-id M541-2024-08-31 \
  --dandiset-directory
```


## YODA-style DataLad Conversion Pipeline

[YODA](https://handbook.datalad.org/en/latest/basics/101-127-yoda.html) is a framework for enabling reproducible computations through version-controlled pipelines.

To run these tools through these pipelines, you only need an environment with `datalad`, `datalad-containers`, `singularity`, and likely `git-annex` installed.

```bash
datalad install -r -s smaug:/mnt/datasets/datalad/crawl/labs/mvdm/OdorSequence
cd OdorSequence
datalad get *
# On Windows might need
# git config --global core.whitespace cr-at-eol
# datalad get sourcedata/preprocessed
# datalad get sourcedata/raw

datalad containers-add vandermeerlab-to-bids --url docker://ghcr.io/con/vandermeerlab-to-bids:dev
datalad containers-add nwb2bids --url docker://ghcr.io/con/nwb2bids:latest

datalad containers-run \
  --container-name vandermeerlab-to-bids \
  "vandermeerlab2bids convert nwb \
  --datapath ./sourcedata \
  --outpath ./sourcedata/nwb-raw/ \
  --experiment OdorSequence \
  --subject M541 \
  --session 2024-08-31 \
  --testing"
```

You can drop the `--testing` flag when doing this for real. Then

```
datalad save --message "save NWB conversion"
cd ../bids-raw
datalad install --reckless=ephemeral -s ../nwb-raw sourcedata/nwb-raw
datalad container-run nwb2bids ./nwb_raw --bids-directory
datalad save --message "save BIDS conversion"
```
