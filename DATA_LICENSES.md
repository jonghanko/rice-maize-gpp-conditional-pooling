# Data and output licenses

The H2 author-generated aggregate inputs, reported tables, figure inputs and generated figures in this aggregate package are licensed under Creative Commons Attribution 4.0 International by Jonghan Ko. Cite the version-specific H2 software and aggregate-data identifiers in `PUBLICATION_IDENTIFIERS.json`, retain the source attribution below and identify changes. The license text is available at https://creativecommons.org/licenses/by/4.0/legalcode.en.

The software and its associated software documentation are covered by the MIT license in `LICENSE`. Dependencies retain their own licenses. `THIRD_PARTY_NOTICES.md` identifies the software and source-product references.

## Included material

The release inputs contain group-level error summaries and source values for Tables 1–3, Supplementary Table S1 and Figures 1–2. The H2 panel comprised 4,357 site-days. Counts in aggregate files describe the original panel and repeated evaluation. These counts are metadata for the archived analysis.

Daily input observations, fold memberships, the 52,284 row-level OOF predictions, the 120 saved estimators and provider-native archives are outside this aggregate release. Their future distribution requires an artifact-specific source-terms check and author review. This package grants no new license over those provider products.

## Provider products

| Source | Recorded product | Attribution and access status |
|---|---|---|
| Korean rice flux references | KOF FLUXNET v1.3_r1 daily `GPP_NT_VUT_REF` for KR-CRK, KR-CmF and KR-HPK | Source identifiers and archive hashes are listed in `docs/data_sources.csv`. Archived companion evidence records an ICOS CC BY 4.0 display. Matching the exact three ZIP deliveries to their complete license and citation text remains a daily-data release check. |
| US maize flux references | AmeriFlux FLUXNET-1F v1.3_r1 for US-Ne1, US-Ne3, US-Ro1 and US-IAC | The acquired policy documents, version 20251226, identify CC BY 4.0 and require site-level citation and acknowledgments. The retained policy-file SHA-256 is `81a8933fc7ac3baac9b987bfebeb51a02f90ae9fc7d1a1559e9d8672ef21dbd8`. |
| Satellite inputs | Terra MODIS MOD09A1.061 Collection 6.1 | Retain the NASA LP DAAC product citation. The original raster files are obtained through the provider. |
| Weather inputs | AgERA5 v2.0 | Retain the Copernicus Climate Data Store product citation and the version used. The product DOI identifies its catalog entry. |

The H2 aggregate license applies to the author-generated material identified above. Source terms, citations and required acknowledgment text remain associated with the corresponding source products.

## Citation and download records

`docs/data_sources.csv` separates product identifiers, source archive hashes, product coverage and the recorded acquisition route/date. The US flux archives were acquired through the FLUXNET Shuttle on 26 October 2026. A source coverage period is distinct from an access date. The exact Korean archive acquisition route/date should be confirmed from the archived acquisition evidence before any daily-data redistribution.

The H2 source-data release scope differs from the companion rice and maize projects. Existing companion identifiers should be cited as related work when applicable. The H2 software repository is https://github.com/jonghanko/rice-maize-gpp-conditional-pooling. Version-specific code and data archive identifiers are recorded in `PUBLICATION_IDENTIFIERS.json`.

The software DOI is https://doi.org/10.5281/zenodo.24029095 and the aggregate-data DOI is https://doi.org/10.5281/zenodo.24029126. Both identifiers were reserved when this package was prepared; `PUBLICATION_IDENTIFIERS.json` records the pending publication status.
