# Release metadata and author declarations

Version 1.0.0 contains software and aggregate-result metadata for the H2 study. The software repository is https://github.com/jonghanko/rice-maize-gpp-conditional-pooling. Archive identifiers and publication status are recorded in `PUBLICATION_IDENTIFIERS.json`.

## Creator and contributions

Jonghan Ko is the sole and corresponding author. His affiliation is the Department of Applied Plant Science, Chonnam National University, Gwangju, Republic of Korea. His ORCID is https://orcid.org/0000-0001-7974-3808 and his correspondence email is jonghan.ko@jnu.ac.kr.

His confirmed CRediT roles are Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Resources, Data curation, Writing – original draft, Writing – review & editing, Visualization, Supervision, Project administration and Funding acquisition.

## Research funding and conflict of interest

This work was supported by Chonnam National University (Grant No. 2026-1417-01) and the Basic Science Research Program through the National Research Foundation of Korea (Grant No. NRF-2021R1A2C2004459).

Neither funder was involved in study design, data collection, analysis or interpretation, manuscript preparation, or the decision to submit. The author declares no competing interests.

## Software and data records

The GitHub repository is `rice-maize-gpp-conditional-pooling`. Its software metadata are in `CITATION.cff` and `.zenodo.json`. The software is licensed under MIT. Author-generated aggregate inputs and outputs are licensed under CC BY 4.0 as defined in `DATA_LICENSES.md`.

The separate aggregate-data record is titled *Rice–Maize GPP Conditional Pooling Aggregate Results*. The code archive and aggregate-data record should identify the same release version and the matching aggregate-input manifest. The assigned software/data identifiers are recorded below. Add the actual Git commit/tag after release. The related maize manuscript's public archive identifiers remain identifiers for that earlier work.

Provider products retain their source-specific terms and attribution. The aggregate record contains group-level results. Daily observations, memberships, OOF predictions, fitted estimators and provider-native archives require separate source-terms and release-scope review.

## Interpretation and regeneration scope

The analysis compares three fitting recipes using an exposed retrospective panel of Korean rice and US maize. Crop identity is confounded with country, climate, management and reference-processing history. Calendar-proxy and footprint limitations remain in force. The primary Ridge spatial-holdout contrast and the secondary RF/year-holdout comparisons are identified separately. Site-season adverse-error summaries are post hoc descriptions.

The packaged commands regenerate tables and figures from aggregate JSON inputs. Provider-native acquisition, daily input construction and model fitting are documented by the frozen protocol and historical records. Their complete raw-to-model execution is outside this aggregate regeneration check. Any historical model-verification receipt refers to the archived execution; the public aggregate regeneration creates its own receipt.

## Archive identifier binding

- The public repository URL, Git commit/tag and code/data archive identifiers.
- Release publication date and the manuscript's eventual publication identifier.
- Source archive/license bindings for any future daily-data redistribution.
- The scope of any row-level or fitted-model archive added to a later release.

Software DOI: https://doi.org/10.5281/zenodo.24029095. Aggregate-data DOI: https://doi.org/10.5281/zenodo.24029126. The code and data DOIs were reserved for version 1.0.0. This package snapshot was prepared before publication confirmation (RESERVED_PENDING_PUBLICATION; published=false). The intended publication date is 2026-11-07; the actual publication date remains unconfirmed in this snapshot. The citation file carries the reserved software DOI and repository URL without an unconfirmed release date. Actual publication confirmation is recorded separately from this preparation snapshot.

For a future GitHub-linked release, Zenodo gives `.zenodo.json` precedence when both that file and `CITATION.cff` exist. Keep the shared creator, title, version and license fields synchronized. Funding awards are retained in the description and this document. A machine-readable grant identifier should be added only after its authoritative funder/grant identifier has been confirmed. [Zenodo JSON metadata guidance](https://help.zenodo.org/docs/github/describe-software/zenodo-json/)
