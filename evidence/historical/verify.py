#!/usr/bin/env python3
"""Reproduce historical public paytable comparisons using the Python standard library.

Run: python3 verify.py --output ../historical-recheck
Source evidence is never modified. This is payout-model analysis, not an RNG audit.
"""
import argparse
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_HALF_UP
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
D = Decimal
EDGE_FACTOR = Fraction(99, 100)
TILES = tuple(map(D, ('1.2','1.3','1.4','1.5','1.75','2','2.5','3','4.2')))

def load(path):
    return json.loads(path.read_text(encoding='utf-8'), parse_float=D)

def dec(value):
    if isinstance(value, Fraction):
        return D(value.numerator) / D(value.denominator)
    return D(str(value))

def ds(value):
    return format(dec(value), 'f')

def frac(value):
    return str(value.numerator) + '/' + str(value.denominator)

def close(a,b):
    return abs(dec(a)-dec(b)) <= max(D(1), abs(dec(b))) * D('0.000000000001')

def floor4(value):
    return dec(value).quantize(D('0.0001'), rounding=ROUND_FLOOR)

def cents(value):
    return dec(value).quantize(D('0.01'), rounding=ROUND_HALF_UP)

def verify_hashes(index):
    for source in index['sources']:
        data=(BASE/source['file']).read_bytes()
        assert len(data)==source['bytes'], 'Length mismatch: '+source['file']
        assert hashlib.sha256(data).hexdigest()==source['sha256'], 'Hash mismatch: '+source['file']

def name(row):
    return 'Hidden' if row['isHidden'] or not row['username'] else row['username']

def common(row, game, board, source_files, source_urls):
    assert not row.get('isMe'), 'Only third-party public records are allowed'
    return {'game':game,'leaderboard':board,'rank':row['rank'],
            'label':game+' / '+board+' / '+str(row['rank']),
            'source_files':source_files,'source_urls':source_urls,
            'round_id':row['roundId'],'recorded_at':row['settledAt'],
            'stake_usd':ds(row['betAmountUsd']),
            'actual_gross_usd':ds(row['payoutUsd']),
            'observed_multiplier':ds(row['multiplier'])}

def hilo_analysis(index):
    sources=index['sources']; rows=[]; prefix_count=0; post_first=0; repeat_matches=0; once_post_matches=0
    for board in ('top-wins','lucky-wins'):
        leader=next(x for x in sources if x['game']=='HiLo' and x['kind']=='leaderboard' and x['leaderboard']==board)
        for row in load(BASE/leader['file'])['rows']:
            src=next(x for x in sources if x['game']=='HiLo' and x['kind']=='bet-receipt' and x['leaderboard']==board and x['rank']==row['rank'])
            receipt=load(BASE/src['file']); response=receipt['presentation']['response']
            assert receipt['roundId']==row['roundId'] and receipt['betId']==row['betIdentifier']
            assert dec(receipt['payoutUsd'])==dec(row['payoutUsd'])
            r=common(row,'HiLo',board,[leader['file'],src['file']],[leader['url'],src['url']])
            repeated=Fraction(1); fair=Fraction(1); calls=0; skips=0; current=None; prefixes=[]
            for event in response['cardHistory']:
                card=int(event['card']); rank=card%13+1; action=event['action']
                assert 0 <= card < 52
                if action in ('deal','skip'):
                    if action=='skip':skips+=1
                    current=rank;continue
                assert current is not None and event['guessCorrect'] is True
                if action=='guess_same':
                    favourable=1; assert rank==current
                elif action=='guess_higher':
                    favourable=12 if current==1 else 14-current
                    assert rank>current if current==1 else rank>=current
                elif action=='guess_lower':
                    favourable=12 if current==13 else current
                    assert rank<current if current==13 else rank<=current
                else:raise AssertionError('Unexpected action '+action)
                calls+=1;prefix_count+=1
                fair*=Fraction(13,favourable);repeated*=EDGE_FACTOR*Fraction(13,favourable);once=EDGE_FACTOR*fair
                seen=event['multiplierAfter'];rep_ok=close(seen,repeated);once_ok=close(seen,once)
                repeat_matches+=rep_ok
                if calls>1:post_first+=1;once_post_matches+=once_ok
                assert rep_ok, 'Repeated model mismatch '+row['roundId']
                prefixes.append({'call':calls,'action':action,'from_rank':current,'to_rank':rank,
                                 'favourable_ranks':favourable,'observed_multiplier':ds(seen),
                                 'repeated_multiplier_exact':frac(repeated),'repeated_multiplier':ds(repeated),
                                 'once_multiplier_exact':frac(once),'once_multiplier':ds(once),
                                 'matches_repeated':rep_ok,'matches_once':once_ok})
                current=rank
            assert calls>=2 and close(response['currentMultiplier'],repeated)
            once=EDGE_FACTOR*fair; gross=dec(row['betAmountUsd'])*dec(once);actual=dec(row['payoutUsd'])
            r.update({'calls':calls,'skips':skips,'game_version':receipt['presentation'].get('gameVersion'),
                      'repeated_model_multiplier_exact':frac(repeated),'repeated_model_multiplier':ds(repeated),
                      'once_model_multiplier_exact':frac(once),'once_model_multiplier':ds(once),
                      'model_original_stake_return':ds(EDGE_FACTOR**calls),
                      'once_benchmark_usd':ds(gross),'benchmark_gap_usd':ds(gross-actual),
                      'benchmark_gap_rounded_usd':ds(cents(gross-actual)),
                      'history_final_multiplier':ds(response['currentMultiplier']),
                      'observed_payout_equals_history_times_display_stake':close(actual,dec(row['betAmountUsd'])*dec(response['currentMultiplier'])),
                      'prefixes':prefixes})
            rows.append(r)
    actual=sum((dec(r['actual_gross_usd']) for r in rows),D(0));benchmark=sum((dec(r['once_benchmark_usd']) for r in rows),D(0))
    assert len(rows)==20 and prefix_count==163 and post_first==143 and repeat_matches==163 and once_post_matches==0
    summary={'records':len(rows),'successful_prefixes':prefix_count,'post_first_prefixes':post_first,
             'repeat_prefix_matches':repeat_matches,'once_post_first_matches':once_post_matches,
             'final_repeat_matches':len(rows),'max_calls':max(r['calls'] for r in rows),
             'total_skips':sum(r['skips'] for r in rows),
             'actual_gross_usd':ds(actual),'once_benchmark_usd':ds(benchmark),
             'benchmark_gap_usd':ds(benchmark-actual),'benchmark_gap_rounded_usd':ds(cents(benchmark-actual)),
             'earliest_recorded_at':min(r['recorded_at'] for r in rows),'latest_recorded_at':max(r['recorded_at'] for r in rows)}
    return rows,summary

def risky_analysis(index):
    candidates=[]
    for count in range(1,10):
        for subset in combinations(TILES,count):
            repeated=Fraction(1)
            for tile in subset: repeated*=Fraction(tile)
            once=repeated/(EDGE_FACTOR**(count-1))
            candidates.append({'tiles':[ds(v) for v in subset],'calls':count,'repeat':repeated,'once':once})
    rows=[]
    for board in ('top-wins','lucky-wins'):
        src=next(x for x in index['sources'] if x['game']=='Risky Click' and x['leaderboard']==board)
        for row in load(BASE/src['file'])['rows']:
            observed=dec(row['multiplier'])
            # One historical value is 40.1309 versus the exact tile product 40.131.
            # Preserve that one-last-place discrepancy; do not silently round it away.
            matches=[c for c in candidates if abs(dec(c['repeat'])-observed)<=D('0.0001')]
            once_matches=[c for c in candidates if abs(dec(c['once'])-observed)<=D('0.0001')]
            once_cents_nearest=[c for c in candidates if cents(c['once'])==cents(observed)]
            once_cents_floor=[c for c in candidates if dec(c['once']).quantize(D('.01'),rounding=ROUND_FLOOR)==observed.quantize(D('.01'),rounding=ROUND_FLOOR)]
            assert matches and not once_matches and not once_cents_nearest and not once_cents_floor
            chosen=min(matches,key=lambda c:c['once']);once=chosen['once'];repeated=chosen['repeat']
            floor_multiplier=floor4(once);benchmark=floor4(dec(row['betAmountUsd'])*floor_multiplier);actual=dec(row['payoutUsd'])
            r=common(row,'Risky Click',board,[src['file']],[src['url']])
            r.update({'calls':chosen['calls'],'calls_candidates':sorted(set(c['calls'] for c in matches)),
                      'calls_basis':'Fewest compatible tiles; the hidden route is not disclosed by this leaderboard.',
                      'compatible_subsets':[{'tiles':c['tiles'],'calls':c['calls'],
                                             'repeated_multiplier_exact':frac(c['repeat']),
                                             'once_multiplier_exact':frac(c['once']),
                                             'once_multiplier':ds(c['once'])} for c in matches],
                      'repeated_model_multiplier_exact':frac(repeated),'repeated_model_multiplier':ds(repeated),
                      'old_model_exact_difference':ds(observed-dec(repeated)),
                      'once_model_multiplier_exact':frac(once),'once_model_multiplier':ds(once),
                      'once_model_matches_within_0001':len(once_matches),
                      'once_model_matches_nearest_cent':len(once_cents_nearest),
                      'once_model_matches_floor_cent':len(once_cents_floor),
                      'once_benchmark_multiplier_floor4':ds(floor_multiplier),
                      'once_benchmark_usd':ds(benchmark),'benchmark_gap_usd':ds(benchmark-actual),
                      'benchmark_gap_rounded_usd':ds(cents(benchmark-actual))})
            rows.append(r)
    actual=sum((dec(r['actual_gross_usd']) for r in rows),D(0));benchmark=sum((dec(r['once_benchmark_usd']) for r in rows),D(0))
    assert len(rows)==20
    summary={'records':len(rows),'enumerated_tile_subsets':len(candidates),'old_model_matches':len(rows),
             'once_model_matches':0,'ambiguous_subset_records':sum(len(r['compatible_subsets'])>1 for r in rows),
             'actual_gross_usd':ds(actual),'conservative_once_benchmark_usd':ds(benchmark),
             'benchmark_gap_usd':ds(benchmark-actual),'benchmark_gap_rounded_usd':ds(cents(benchmark-actual)),
             'earliest_recorded_at':min(r['recorded_at'] for r in rows),'latest_recorded_at':max(r['recorded_at'] for r in rows)}
    return rows,summary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path,help='Separate directory outside this evidence folder')
    args=parser.parse_args();out=args.output.resolve()
    if out==BASE or BASE in out.parents:parser.error('Output must be outside the evidence folder; preserved files are not modified.')
    with localcontext() as ctx:
        ctx.prec=70
        index=load(BASE/'SOURCE-INDEX.json');verify_hashes(index)
        hilo,hs=hilo_analysis(index);risky,rs=risky_analysis(index)
        actual=dec(hs['actual_gross_usd'])+dec(rs['actual_gross_usd']);gap=dec(hs['benchmark_gap_usd'])+dec(rs['benchmark_gap_usd'])
        result={'schema_version':1,
          'scope':'40 selected public historical winning records: 20 HiLo and 20 Risky Click. Payout-model reconstruction only; not an RNG audit or a representative RTP sample.',
          'methods':{
            'hilo':'13 equally likely ranks with replacement, inclusive higher/lower except strict opposite-direction calls at A/K; same is 1/13. Every successful paid call multiplies the reconstructed old value by 0.99/p. Skips change the current rank but apply no payout factor. Compare with 0.99/product(p) for a once-only factor.',
            'hilo_precision':'Exact rational model; Decimal calculations at 70-digit precision. Recorded float values compared at 1e-12 relative tolerance. No per-row cent rounding in aggregate benchmark.',
            'risky':'Enumerate all 511 non-empty subsets of the nine documented historical tile multipliers. Match the stored leaderboard multiplier within 0.0001. Each candidate once-only multiplier divides the old product by 0.99^(tiles-1). Choose the smallest once-only candidate for each row.',
            'risky_precision':'Floor chosen once-only multiplier to four decimals; multiply the displayed USD stake, then floor gross USD to four decimals. A stored 40.1309 value is 0.0001 below exact product 40.131; this discrepancy is preserved.',
            'combined_precision':'Sum unrounded HiLo route benchmarks and four-decimal floored Risky Click lower benchmarks, then subtract stored gross payouts. Round the final aggregate to cents with ROUND_HALF_UP.',
            'interpretation':'YEET advertised a 1% house edge and 99% RTP. The benchmark charges that 1% once on the whole round, so the round returns 99% of the stake however many steps are taken. Charging it again at every step returns 0.99 to the power of the steps taken.',
            'limits':'Public winning leaderboards are selected examples. Risky Click leaderboards do not disclose paths, so subset matches are compatible reconstructions, not revealed choices. Displayed USD stakes are the available unit for cross-record benchmarks; raw payouts may round differently from path multipliers. Source acquisition dates are locally recorded provenance, not independent timestamp attestations. No RNG generation is replayed.'},
          'summary':{'source_files_verified':len(index['sources']),'hilo':hs,'risky':rs,'combined':{'records':40,'actual_gross_usd':ds(actual),'once_benchmark_usd':ds(actual+gap),'benchmark_gap_usd':ds(gap),'benchmark_gap_rounded_usd':ds(cents(gap))}},
          'rows':hilo+risky}
        assert cents(gap)==D('39789.55')
        out.mkdir(parents=True,exist_ok=True)
        (out/'analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        (out/'verification-summary.txt').write_text(json.dumps(result['summary'],indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result['summary'],indent=2))

if __name__=='__main__':main()
