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
