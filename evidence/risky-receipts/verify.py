#!/usr/bin/env python3
"""Reconcile 20 individual public Risky Click receipts with their 20 leaderboard rows.
No network access or account is required. Writes only to a separate output folder.
"""
import argparse
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
EXPECTED_TOP={'betId','roundId','placedAt','result','provider','game','player','currencyCode','isFreeBet','wagerUsd','payoutUsd','multiplier','type','legacy','fairness','presentation'}
EXPECTED_CHILD={'provider':{'id','name'},'game':{'id','name','identifier','urlId'},'player':{'isPrivate','username','tierImage'},'presentation':{'type','url'},'fairness':{'status','serverSeedHash','nonce','serverSeed'}}

def load(p):return json.loads(p.read_text(),parse_float=Decimal)
def utc(value):return datetime.fromisoformat(value.replace('Z','+00:00'))
def sha(data):return hashlib.sha256(data).hexdigest()
def schema_paths(obj,prefix='$'):
    paths=[]
    if isinstance(obj,dict):
        for k,v in sorted(obj.items()):
            path=prefix+'.'+k;paths.append(path);paths.extend(schema_paths(v,path))
    elif isinstance(obj,list):
        paths.append(prefix+'[]')
        for v in obj:paths.extend(schema_paths(v,prefix+'[]'))
    return paths

def calculate():
    index=load(BASE/'SOURCE-INDEX.json');sources=index['sources'];objects={}
    for s in sources:
        data=(BASE/s['file']).read_bytes();assert len(data)==s['bytes'] and sha(data)==s['sha256'],s['file'];objects[s['file']]=json.loads(data,parse_float=Decimal)
    boards={s['leaderboard']:objects[s['file']] for s in sources if s['kind']=='comparison_leaderboard'}
    rows=[];images=set();allpaths=set();fairness_count=0;revealed_count=0;legacy_count=0
    receipts=[s for s in sources if s['kind']=='additional_receipt'];assert len(receipts)==20
    assert len({s['round_id'] for s in receipts})==20
    for src in receipts:
        receipt=objects[src['file']];feed=next(r for r in boards[src['leaderboard']]['rows'] if r['roundId']==src['round_id'])
        assert set(receipt)==EXPECTED_TOP,'Unexpected top-level payload fields require manual review'
        for key,allowed in EXPECTED_CHILD.items():
            if receipt[key] is not None:assert set(receipt[key])==allowed,'Unexpected '+key+' fields require manual review'
        assert receipt['game']['identifier']=='risky-click' and receipt['result']=='won'
        assert receipt['type']=='original' and receipt['isFreeBet'] is False
        assert receipt['legacy'] in (None,True) and receipt['presentation']['type']=='image'
        images.add(receipt['presentation']['url']);allpaths.update(schema_paths(receipt))
        checks={'bet_id':receipt['betId']==feed['betIdentifier'],'round_id':receipt['roundId']==feed['roundId'],
          'recorded_date_same_instant':utc(receipt['placedAt'])==utc(feed['settledAt']),
          'stake_usd':Decimal(receipt['wagerUsd'])==Decimal(feed['betAmountUsd']),
          'gross_payout_usd':Decimal(receipt['payoutUsd'])==Decimal(feed['payoutUsd']),
          'multiplier':Decimal(receipt['multiplier'])==Decimal(feed['multiplier']),
          'currency':receipt['currencyCode']==feed['currency']}
        assert all(checks.values()),'Receipt/feed mismatch for '+src['file']
        fairness=receipt['fairness'];fairness_count+=fairness is not None;revealed_count+=bool(fairness and fairness.get('serverSeed'));legacy_count+=receipt['legacy'] is True
        rows.append({'leaderboard':src['leaderboard'],'original_rank':src['rank'],'round_id':receipt['roundId'],'bet_id':receipt['betId'],
          'receipt_source_url':src['url'],'receipt_recorded_at':receipt['placedAt'],'feed_recorded_at':feed['settledAt'],
          'date_text_identical':receipt['placedAt']==feed['settledAt'],'checks':checks,
          'stake_usd':receipt['wagerUsd'],'gross_payout_usd':receipt['payoutUsd'],'multiplier':receipt['multiplier'],
          'presentation_type':receipt['presentation']['type'],'has_fairness_metadata':fairness is not None,
          'has_revealed_server_seed':bool(fairness and fairness.get('serverSeed')),'legacy_flag':receipt['legacy'],
          'explicit_tile_choices_or_actions_present':False})
    assert len(images)==1 and fairness_count==5 and revealed_count==1 and legacy_count==5
    return {'schema_version':1,'capture_date':'2026-11-23',
      'summary':{'additional_public_receipts':20,'comparison_leaderboards':2,'all20_ids_dates_currency_stake_payout_multiplier_match':True,
        'presentation_image_only_count':20,'distinct_shared_presentation_image_urls':len(images),'receipts_with_explicit_choices_or_actions':0,
        'fairness_metadata_present':fairness_count,'revealed_public_server_seeds':revealed_count,'legacy_true_count':legacy_count,
        'original_ambiguous_subset_records':9,'ambiguous_subset_records_resolved_by_these_receipts':0,
        'original40_record_pricing_analysis_changed':False,'original_combined_benchmark_gap_usd_rounded':'39789.55'},
      'payload_inspection':{'all_top_level_and_nested_fields_checked':True,'field_paths':sorted(allpaths),'shared_image_url':next(iter(images)),
        'conclusion':'Each presentation contains only an image type and the same image URL. No payload contains selected tiles, action order, per-step multipliers, or an outcome history. Legacy/fairness metadata does not record those choices. No RNG replay is claimed.'},
      'scope':'Individual public receipts corroborate the same 20 Risky Click leaderboard records. Their placedAt values are bet times, not collection dates. The two leaderboard files are reference copies of ../historical/sources.',
      'route_limit':'The leaderboard-based subset ambiguity remains unchanged: nine records have multiple compatible tile sets. Do not select a route merely because this supplementary receipt exists.',
      'rows':rows}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
    if out==BASE or BASE in out.parents:p.error('Choose an output directory outside the preserved supplement folder')
    result=calculate();out.mkdir(parents=True,exist_ok=True);(out/'analysis.json').write_text(json.dumps(result,indent=2,default=str)+'\n');(out/'verification-summary.txt').write_text(json.dumps(result['summary'],indent=2)+'\n');print(json.dumps(result['summary'],indent=2))
if __name__=='__main__':main()
