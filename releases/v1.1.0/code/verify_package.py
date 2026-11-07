# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jonghan Ko
"""Offline file, schema and relational integrity checks; no performance metrics."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import sys

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def require(x,message):
    if not x:raise AssertionError(message)

def check(root,hashes_only=False):
    manifest=json.loads((root/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
    checks=0
    for entry in manifest['files']:
        rel=PurePosixPath(entry['path'])
        require(not rel.is_absolute() and '..' not in rel.parts,'unsafe manifest path')
        p=root.joinpath(*rel.parts)
        require(p.is_file() and p.stat().st_size==entry['bytes'] and digest(p)==entry['sha256'],'file integrity failure: '+entry['path'])
        checks+=1
    status=json.loads((root/'PACKAGE_STATUS.json').read_text(encoding='utf-8'))
    require(status['status']=='BUILD_SNAPSHOT_PREPARED_FOR_FINAL_USER_REVIEW','build snapshot state')
    require(not status['published'] and not status['actual_submission'],'build-time publication/submission state')
    require('workflow_snapshot_semantics' in status,'build-time semantics missing')
    snapshot_result={'build_snapshot_published':status['published'],
                     'current_publication_status':'NOT_TESTED_OFFLINE',
                     'P066_at_build_time':status['P066']}
    if hashes_only:return {'status':'PASS_FILE_HASHES_ONLY','files_checked':checks,
                            'validation_scope':'BYTE_HASHES_AND_BUILD_METADATA_ONLY',**snapshot_result}
    import numpy as np
    import pandas as pd
    import pyarrow.parquet as pq
    definition=json.loads((root/'metadata/DATA_DICTIONARY.json').read_text(encoding='utf-8'))
    frames={}
    forbidden=re.compile(r'(?:[A-Za-z]:[\\/]|/(?:data|home|Users|mnt)/[A-Za-z0-9])')
    secret=re.compile(r'(?:sk-proj-|sk-ant-api\d{2}-)[A-Za-z0-9_-]{12,}')
    for item in definition['tables']:
        p=root/item['path']
        t=pq.read_table(p)
        require(t.num_rows==item['rows'] and t.column_names==item['columns'],'schema or row count changed: '+item['path'])
        require([(f.name,str(f.type),f.nullable) for f in t.schema]==[(f['name'],f['arrow_type'],f['nullable']) for f in item['fields']],'Arrow field types/nullability changed')
        meta=json.dumps({str(k):str(v) for k,v in (t.schema.metadata or {}).items()})
        require(not forbidden.search(meta) and not secret.search(meta),'private footer metadata')
        d=t.to_pandas()
        for name in d.columns:
            if pd.api.types.is_object_dtype(d[name].dtype) or pd.api.types.is_string_dtype(d[name].dtype):
                require(not d[name].dropna().astype(str).map(lambda x:bool(forbidden.search(re.sub(r'https?://[^\s\"<>]+','',x)) or secret.search(x))).any(),'private string content: '+name)
        frames[Path(item['path']).name]=d
    primary=frames['primary_Ridge_LOSO_CS.parquet'].set_index('physical_key',drop=False)
    require(len(primary)==4357 and not primary.index.duplicated().any(),'primary key universe')
    require(np.isfinite(primary[['target_value','prediction_S','prediction_C']].to_numpy()).all(),'nonfinite primary values')
    keys=set(primary.index)
    for name in ['planned_Ridge_LOSO_P.parquet','secondary_Ridge_LOYO.parquet','secondary_RF_LOSO.parquet','secondary_RF_LOYO.parquet']:
        d=frames[name]
        require(not d.physical_key.duplicated().any() and set(d.physical_key)==keys,'paired key universe')
        require(np.isfinite(d.filter(regex='^prediction_').to_numpy()).all(),'nonfinite stored prediction')
    case=frames['case_and_site_season_catalog.parquet'].set_index('physical_key',drop=False)
    require(not case.index.duplicated().any() and set(case.index)==keys,'case keys')
    native=frames['reference_row_mapping.parquet'].set_index('physical_key',drop=False)
    require(not native.index.duplicated().any() and set(native.index)==keys,'native mapping keys')
    require(native.reference_id.reindex(primary.index).equals(primary.reference_id),'native/reference foreign key')
    tests=frames['frozen_test_membership.parquet']
    require(not tests.duplicated(['physical_key','axis']).any(),'test membership key')
    require(set(tests.axis)=={'cluster_loso','year_loyo'},'test axes')
    for _,d in tests.groupby('axis'):require(set(d.physical_key)==keys,'complete axis key coverage')
    require(tests[tests.axis.eq('cluster_loso')].set_index('physical_key').fold_id.reindex(primary.index).equals(primary.fold_id),'primary fold preservation')
    for name,axis in [('planned_Ridge_LOSO_P.parquet','cluster_loso'),('secondary_Ridge_LOYO.parquet','year_loyo'),('secondary_RF_LOSO.parquet','cluster_loso'),('secondary_RF_LOYO.parquet','year_loyo')]:
        got=frames[name].set_index('physical_key').fold_id.reindex(primary.index)
        want=tests[tests.axis.eq(axis)].set_index('physical_key').fold_id.reindex(primary.index)
        require(got.equals(want),'stored prediction/test-fold foreign key')
    sets=json.loads((root/'metadata/COMPANION_SET_CATALOG.json').read_text())['sets']
    matrix=frames['h2_membership_matrix.parquet'].set_index('physical_key',drop=False)
    universe=frames['companion_key_universe.parquet']
    links=frames['matched_reference_links.parquet']
    require(set(matrix.index)==keys and not matrix.index.duplicated().any(),'matrix keys')
    require(not universe.duplicated(['companion_set_id','physical_key']).any(),'set key uniqueness')
    require(not links.duplicated(['companion_set_id','physical_key']).any(),'reference-link uniqueness')
    require(set(universe.companion_set_id)=={s['companion_set_id'] for s in sets},'catalog/set foreign keys')
    for s in sets:
        sid=s['companion_set_id'];u=universe[universe.companion_set_id.eq(sid)]
        applicable=case.crop.eq(s['crop_comparison_domain']).reindex(matrix.index)
        require(matrix.loc[~applicable,sid].isna().all(),'out-of-domain must remain null')
        require(matrix.loc[applicable,sid].notna().all(),'applicable membership not checked')
        observed=set(matrix.index[applicable & matrix[sid].fillna(False)])
        require(observed==set(u.physical_key)&set(case.index[case.crop.eq(s['crop_comparison_domain'])]),'membership relation')
        ll=links[links.companion_set_id.eq(sid)]
        require(set(ll.physical_key)<=observed,'reference only for shared keys')
        if s['reference_field'] and not s['component_set_ids']:
            require(set(ll.physical_key)==observed,'complete shared-reference link set')
        if s['analysis_role'] in {'hindcast_train','hindcast_test'}:
            require(isinstance(s['role_artifact_sha256'],str) and len(s['role_artifact_sha256'])==64,'required frozen role hash')
            require(u.role_artifact_sha256.eq(s['role_artifact_sha256']).all(),'role hash continuity')
        if s['component_set_ids'] or not observed:require(ll.empty,'inapplicable reference links')
    hv=primary.target_value.reindex(links.physical_key).to_numpy('float64')
    cv=links.companion_target_value.to_numpy('float64')
    require(np.isfinite(hv).all() and np.isfinite(cv).all(),'finite references')
    exact=np.abs(hv-cv)==0
    require(np.array_equal(exact,links.reference_comparison_status.eq('numeric_exact_equal').to_numpy()),'reference comparison flags')
    require(links.h2_reference_id.reset_index(drop=True).equals(primary.reference_id.reindex(links.physical_key).reset_index(drop=True)),'reference identifier join')
    # This validates structure and stored flags, not new overlap totals or performance.
    return {'status':'PASS_STRUCTURAL_INTEGRITY_ONLY','files_checked':checks,'H2_unique_days':4357,'tables_checked':len(frames),
            'new_performance_metrics':0,'fits_predictions_replays_API_calls':0,**snapshot_result}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--hashes-only',action='store_true')
    args=parser.parse_args()
    try:print(json.dumps(check(args.root,args.hashes_only),sort_keys=True))
    except Exception as e:
        print(json.dumps({'status':'FAIL','error_type':type(e).__name__,'message':str(e)}));sys.exit(2)
