# van der Meer lab → BIDS

Conversion tools for ingesting data from the van der Meer group at Dartmouth College and outputting it into BEP-32 compliant datasets for upload to the DANDI Archive.



## Usage

### CLI

```bash
vandermeerlab2bids convert nwb
  --datapath [source data directory] \
  --outpath [dandiset directory]
  --experiment [experiment name] \
  --subject-id [subject ID] \
  --session-id [session ID] \
```

For example:

```bash
vandermeerlab2bids convert nwb \
  --datapath E:/vandermeerlab/mvdm/OdorSequence/sourcedata \
  --outpath E:/vandermeerlab/mvdm/OdorSequence/nwb \
  --experiment OdorSequence \
  --subject-id M541 \
  --session-id M541-2024-08-31 \
```


## YODA-style DataLad Conversion Pipeline

[YODA](https://handbook.datalad.org/en/latest/basics/101-127-yoda.html) is a framework for enabling reproducible computations through version-controlled pipelines.

To run these tools through these pipelines, you only need an environment with `datalad`, `datalad-containers`, `singularity`, and likely `git-annex` installed.

Start by running:

```bash
datalad install -r -s smaug:/mnt/datasets/datalad/incoming/mvdm/OdorSequence
cd OdorSequence
datalad get *

# On Windows, you might need
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
  --session 2024-08-31"
```

> [!NOTE]
> This process will take some time.
> On average, about 25 MB/s (compression is the slowest part).
> To test it out quickly, you can add the `--testing` flag, which will reduce the amount of data written.

Once it is done creating the NWB file, organize it according to the BIDS standard by calling:

```
datalad containers-run
  --container-name nwb2bids \
  "nwb2bids convert ./sourcedata/nwb-raw \
  --bids-directory ./sourcedata/nwb-bids"
```

If you are tight on disk space and need to remove any files, you can do so with:

```bash
datalad drop ./sourcedata/raw/[subject ID]/[session ID]
datalad drop ./sourcedata/preprocesed/[subject ID]/[session ID]
datalad drop ./sourcedata/nwb-raw
```

If you were even tighter on disk space during this process, you could have dropped the `sourcedata/raw` after first creating the full NWB file.
