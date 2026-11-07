# Third party notices and source attribution

## Software dependencies

This package uses Python, NumPy, Matplotlib and Pillow for aggregate processing and rendering. These packages are installed in the runtime and are not vendored in this repository. Their own license notices continue to apply. The environment files and regeneration receipt record the tested versions.

- Python is distributed under the Python Software Foundation License and associated historical notices. https://docs.python.org/3/license.html
- NumPy uses its BSD license. https://numpy.org/doc/stable/license.html
- Matplotlib uses its Matplotlib license and retains its historical notices. https://matplotlib.org/stable/project/license.html
- Pillow uses its HPND license. https://pillow.readthedocs.io/en/stable/about.html#license

The archived fitted-model recipes used scikit-learn. The aggregate regeneration runtime does not load or replay those estimators. The historical model environment is documented separately from the environment tested for aggregate regeneration.

The H2 scripts were adapted from author-generated analysis and artwork code. The new explicit aggregate commands and their generated outputs must be cited using the H2 package's version once published.

## Flux source acknowledgment

The acquired US FLUXNET policy documents prescribe the following global acknowledgment text for use of their products.

> FLUXNET data products were produced and harmonized by eddy covariance regional networks and data processing centers, including AmeriFlux, ChinaFlux, European Fluxes Database, ICOS, JapanFlux, KoFlux, OzFlux, SAEON, and TERN. These products also include a modified version of ERA5 hourly data provided by the Copernicus Climate Change Service.

For the AmeriFlux products, they also prescribe the following text.

> Funding for the AmeriFlux data service was provided by the U.S. Department of Energy Office of Science.

The latter acknowledges the data service. Research funding for H2 is listed in `docs/metadata_notes.md`.

Site-level product citations and identifiers are listed in `docs/data_sources.csv`. Preserve the product's original creator string in a citation-tracked location when redistributing provider files. The complete supplied policy remains the authority for the archived delivery.

The following US source citations reproduce the creator strings retained in the acquired product-citation records. Apparent name duplication or formatting anomalies are retained as supplied.

- Andy Suyker (2026). *AmeriFlux FLUXNET-1F US-Ne1 Mead - irrigated continuous maize site, Ver. v1.3_r1 (2001-2024)*. AmeriFlux AMP. https://doi.org/10.17190/AMF/1871140
- Andy Suyker (2026). *AmeriFlux FLUXNET-1F US-Ne3 Mead - rainfed maize-soybean rotation site, Ver. v1.3_r1 (2001-2024)*. AmeriFlux AMP. https://doi.org/10.17190/AMF/3028954
- John Baker, Tim Griffis, and Timothy Griffis (2026). *AmeriFlux FLUXNET-1F US-Ro1 Rosemount- G21, Ver. v1.3_r1 (2004-2016)*. AmeriFlux AMP. https://doi.org/10.17190/AMF/1881588
- Guler Aslan Sungur (Rojda), and Vanloocke Andy (2026). *AmeriFlux FLUXNET-1F US-IAC Iowa State University SE tower, Ver. v1.3_r1 (2019-2024)*. AmeriFlux AMP. https://doi.org/10.17190/AMF/3027373

## Product and method references

- Vermote, E. (2021). *MODIS/Terra Surface Reflectance 8-Day L3 Global 500m SIN Grid V061*. NASA Land Processes Distributed Active Archive Center. https://doi.org/10.5067/MODIS/MOD09A1.061
- Boogaard, H., Schubert, J., De Wit, A., Lazebnik, J., Hutjes, R., and Van der Grijn, G. (2020). *Agrometeorological indicators from 1979 to present derived from reanalysis*. Version 2.0 used for H2. Copernicus Climate Change Service Climate Data Store. https://doi.org/10.24381/cds.6c68c9bb
- Pastorello, G., et al. (2020). The FLUXNET2015 dataset and the ONEFlux processing pipeline for eddy covariance data. *Scientific Data*, 7, 225. https://doi.org/10.1038/s41597-020-0534-3
- Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography*, 40, 913–929. https://doi.org/10.1111/ecog.02881
- Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html
- Harris, C. R., et al. (2020). Array programming with NumPy. *Nature*, 585, 357–362. https://doi.org/10.1038/s41586-020-2649-2
- Hunter, J. D. (2007). Matplotlib: A 2D Graphics Environment. *Computing in Science & Engineering*, 9, 90–95. https://doi.org/10.1109/MCSE.2007.55

The source records describe a retrospective registered-point, calendar-screened comparison. Crop, country, climate, management and reference-processing histories are confounded across the two domains. The primary comparison, secondary comparisons and post hoc summaries retain their original labels in the released outputs.
