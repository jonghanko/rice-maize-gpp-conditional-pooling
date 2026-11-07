# Rice maize GPP conditional pooling

## Archive identifiers

- Software: https://doi.org/10.5281/zenodo.24029095
- Companion aggregate data: https://doi.org/10.5281/zenodo.24029126
- Source repository: https://github.com/jonghanko/rice-maize-gpp-conditional-pooling

The code and data DOIs were reserved for version 1.0.0. This package snapshot was prepared before publication confirmation (RESERVED_PENDING_PUBLICATION; published=false). The intended publication date is 2026-11-07; the actual publication date remains unconfirmed in this snapshot. Publication status and identifier scope are recorded in `PUBLICATION_IDENTIFIERS.json`.

Version 1.0.0 regenerates the reported H2 tables and final-layout figures from archived aggregate results. The source repository is https://github.com/jonghanko/rice-maize-gpp-conditional-pooling. Code and data archive identifiers and publication status are recorded in `PUBLICATION_IDENTIFIERS.json`.

Jonghan Ko, Department of Applied Plant Science, Chonnam National University. ORCID 0000-0001-7974-3808.

## Reproduce the tables and figures

Use Python 3.11 or newer. The verified rendering environment is Python 3.11.15, NumPy 2.4.6, Matplotlib 3.11.1 and Pillow 12.2.0 on Windows, with Arial. The original model execution used a separate environment recorded in `config/analysis_protocol.json`.

From the repository directory, install the code and rendering dependencies.

```sh
python -m pip install ".[render]"
h2-gpp verify --data-dir data/aggregate
h2-gpp reproduce --data-dir data/aggregate --output-dir ../h2-regenerated
```

The output directory must be new. A successful run creates 12 CSV/Markdown/HTML table files, two figures in SVG/PNG/TIFF, the final captions and an `AGGREGATE_REGENERATION_RECEIPT.json`. The input files and historical execution records are preserved. The `verify` command uses the Python standard library and checks aggregate input hashes and arithmetic relationships.

An optional `--receipt` path must be new and outside the regeneration output directory. The regeneration receipt is written after a successful run. If rendering fails, review the partial output and retry with a new directory.

The command also works outside the repository when given an explicit input directory.

```sh
python -m h2_gpp reproduce --data-dir /path/to/data/aggregate --output-dir /path/to/new-output
```

For the separately archived data record, pass its `data/aggregate` directory. Installation supplies the `h2_gpp` module, while the data remain at the chosen location. `tables` and `figures` commands regenerate only their named outputs.

## Included results

The historical panel contained 4,357 unique site-days from Korean rice and US maize in 2012–2020. The public aggregate files contain 456 metric rows, 24 regional macro scores, 444 paired group contrasts and 24 site-season summaries. Figures show 16 crop-level contrasts and 116 site-season cells. Daily observations, fold membership records, model objects and row-level predictions are outside this aggregate release.

The prespecified primary comparison was crop-conditioned versus crop-specific Ridge under spatial-cluster holdout. Its equal-crop mean relative RMSE change was +0.18150003401997683%. Unconditioned pooling increased regional macro RMSE for both crops under both model families and axes. Secondary and post hoc results retain their stated roles. Crop labels also identify countries and reference-processing histories. The panel was previously examined, some crop windows and footprint support remain uncertain, and the results are descriptive point estimates from the recorded model recipes and one random-forest seed.

Observation reuse with companion rice and maize analyses is documented in `docs/reproduction.md`. It is carried into the manuscript disclosure. ET and German model training remain on hold.

## Layout and numerical verification

`verify` checks input checksums, regional macro aggregation, crop and equal-crop contrasts, 444 paired contrasts and error decompositions, adverse-season counts, cross-axis recurrence, and the source values for both figures. It verifies stored aggregate relationships. The historical model checks are described as historical records in the protocol metadata.

Rendering uses the approved 180 mm submission layouts, Arial at 12.2 pt, 600 dpi RGB TIFF and final captions. Cell values, signed zeros, colors, source coordinates, minimum text size and bounding-box overlap are checked during rendering. The verified runtime reproduced the two submitted TIFF files byte for byte. Different fonts or dependency versions can change raster bytes and layout. Arial is not distributed with this repository.

## Files and licenses

- `src/h2_gpp` contains explicitly invoked aggregate verification and regeneration functions.
- `data/aggregate` contains the public aggregate inputs and their input manifest.
- `config` contains the model recipe, cohort and split summaries and original hashes.
- `environment` records the tested rendering versions.
- `docs` contains source attribution, a data dictionary, reproduction guidance and manuscript crosswalk.

Author-created software is licensed under MIT. Author-created aggregate data and figures are licensed under CC BY 4.0. See `DATA_LICENSES.md` for the file and provider scope and `THIRD_PARTY_NOTICES.md` for attribution.

Supported by Chonnam National University Grant No. 2026-1417-01 and the Basic Science Research Program through the National Research Foundation of Korea, Grant No. NRF-2021R1A2C2004459. Neither funder was involved in study design, data collection, analysis or interpretation, manuscript preparation, or the decision to submit. The author declares no competing interests.
