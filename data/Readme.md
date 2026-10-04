# data/

Generated catalog files — do not edit by hand.

Each `<category>_catalog.json` is produced by `retrivals/preprocessing.py`
from the raw dataset (currently `flipkart.csv`, sampled to 150 rows per
category for a fast prototype demo). Re-run preprocessing any time the
source data changes:

    python retrivals/preprocessing.py /path/to/flipkart.csv

`<category>_faiss.index` and `<category>_ids.json` (not present yet) are
produced by `retrivals/embeddings.py` once you've run it for a category —
they require internet access to download the sentence-transformers model
the first time.
