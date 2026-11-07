# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jonghan Ko
"""Optional calculations from stored predictions only; never fits or predicts.

Not executed during local package preparation. This is separate from the
integrity checker. Use an explicit output path to opt in to derived calculations.
No statistical significance, causal or new generalization claims are produced.
"""
from pathlib import Path
import argparse
import json

def calculate(root):
    import numpy as np
    import pandas as pd
    base=pd.read_parquet(root/'data/primary_Ridge_LOSO_CS.parquet').set_index('physical_key')
    cases=pd.read_parquet(root/'data/case_and_site_season_catalog.parquet').set_index('physical_key').reindex(base.index)
    cells={
      ('Ridge','cluster_loso'):base[['prediction_S','prediction_C']].join(pd.read_parquet(root/'data/planned_Ridge_LOSO_P.parquet').set_index('physical_key')[['prediction_P']]),
      ('Ridge','year_loyo'):pd.read_parquet(root/'data/secondary_Ridge_LOYO.parquet').set_index('physical_key'),
      ('RF','cluster_loso'):pd.read_parquet(root/'data/secondary_RF_LOSO.parquet').set_index('physical_key'),
      ('RF','year_loyo'):pd.read_parquet(root/'data/secondary_RF_LOYO.parquet').set_index('physical_key')}
    rows=[]
    for (family,axis),pred in cells.items():
        assert set(pred.index)==set(base.index) and not pred.index.duplicated().any()
        pred=pred.reindex(base.index)
        for crop in ['rice','maize']:
            chosen=cases.crop.eq(crop);regions=sorted(cases.loc[chosen,'spatial_split_group'].unique());assert len(regions)==3
            macros={}
            for arm in ['S','P','C']:
                scores=[]
                for region in regions:
                    mask=chosen & cases.spatial_split_group.eq(region)
                    err=pred.loc[mask,'prediction_'+arm].to_numpy()-base.loc[mask,'target_value'].to_numpy()
                    assert len(err)>0 and np.isfinite(err).all()
                    scores.append(float(np.sqrt(np.mean(err**2))))
                macros[arm]=float(np.mean(scores))
            for a,b in [('C','S'),('P','S'),('C','P')]:
                assert macros[b]!=0
                rows.append({'family':family,'axis':axis,'crop':crop,'contrast':a+'-'+b,
                  'scope':'primary' if (family,axis,a,b)==('Ridge','cluster_loso','C','S') else ('planned_support' if (family,axis)==('Ridge','cluster_loso') else 'secondary'),
                  'macro_rmse_arm':macros[a],'macro_rmse_comparator':macros[b],
                  'relative_percent':100*(macros[a]/macros[b]-1),
                  'definition':'Mean of three unrounded regional RMSEs; combine OOF years inside region first; positive relative value=worse'})
    return {'calculation_scope':'stored prediction macro comparisons only; not model training, all posthoc artwork or independent truth validation',
            'fits_predictions_model_replays_API_calls':0,'comparisons':rows}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True,help='Explicit new JSON destination; never overwrites')
    args=parser.parse_args()
    result=calculate(args.root)
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print('Wrote stored-prediction comparisons; no model was fitted or replayed.')
