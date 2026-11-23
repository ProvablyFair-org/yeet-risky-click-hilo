#!/usr/bin/env python3
"""Reproduce the repeated-factor table and a synthetic 49-call HiLo sequence.
Standard library only. No network, account access or bets.
"""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, localcontext, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

BASE=Path(__file__).resolve().parent
F=Fraction
D=Decimal
FACTOR=F(99,100)

def decimal(x):
    return D(x.numerator)/D(x.denominator) if isinstance(x,F) else D(str(x))
def txt(x):return format(decimal(x),'f')
def exact(x):return str(x.numerator)+'/'+str(x.denominator)
def money(x):return txt(decimal(x).quantize(D('.01'),rounding=ROUND_HALF_UP))
def read(p):return json.loads(p.read_text(),parse_float=D)

def calculate():
    sources=read(BASE/'SOURCE-INDEX.json')['sources'];receipt_count=0;observed_max_calls=0;stored_limits=set()
    for source in sources:
        data=(BASE/source['file']).read_bytes()
        assert len(data)==source['bytes'] and hashlib.sha256(data).hexdigest()==source['sha256'], source['file']
        if source['kind']=='public_historical_receipt':
            record=json.loads(data);state=record['presentation']['response'];receipt_count+=1
            history=state['cardHistory'];assert sum(e['action']=='deal' for e in history)==1
            calls=sum(e['action'].startswith('guess_') and e['guessCorrect'] for e in history)
            observed_max_calls=max(observed_max_calls,calls);stored_limits.add(state['maxCardsAllowed'])
    assert receipt_count==20 and stored_limits=={50} and observed_max_calls==25
    settings=read(BASE/'hilo-public-settings-2026-11-22.json')['data']
    assert settings['maxCards']==50 and settings['houseEdgeFactor']==D('.99')
    assert settings['maxMultiplier']==10000 and settings['currencies']['native']['maxWin']==200000
    table=[]
    for n in range(1,50):
        ret=FACTOR**n;edge=1-ret;shortfall=1-FACTOR**(n-1)
        table.append({'paid_decisions':n,'opening_stake_return_exact':exact(ret),'opening_stake_return_percent':txt(100*ret),
                      'cumulative_edge_percent':txt(100*edge),'once_only_return_percent':'99',
                      'extra_edge_vs_once_percentage_points':txt(100*(FACTOR-ret)),
                      'winning_payout_reduction_vs_fair_percent':txt(100*edge),
                      'winning_payout_reduction_vs_once_percent':txt(100*shortfall),
                      'within_observed_hilo_prefix_count_range':n<=observed_max_calls,
                      'within_risky_click_nine_tile_board':n<=9})
    # Construct one outcome history, starting K and alternating A/K. Every chosen
    # call succeeds with12/13 under the stated uniform-rank model. Exact next
    # cards have probability1/13 by rank; do NOT treat(12/13)^49 as the probability
    # of this specific alternating-rank history. This is an existence example.
    rank=13;repeated=F(1);fair=F(1);stake=F(100);steps=[]
    for n in range(1,50):
        action='guess_lower' if rank==13 else 'guess_higher';next_rank=1 if rank==13 else 13
        p=F(12,13);increment=FACTOR/p;repeated*=increment;fair/=p;once=FACTOR*fair
        assert repeated<settings['maxMultiplier'] and once<settings['maxMultiplier']
        assert stake*repeated<settings['currencies']['native']['maxWin']
        assert stake*once<settings['currencies']['native']['maxWin']
        steps.append({'paid_call':n,'current_rank':rank,'action':action,'next_rank':next_rank,
                      'call_success_probability_model':'12/13','repeated_increment_exact':exact(increment),
                      'repeated_cumulative_multiplier':txt(repeated),'once_only_cumulative_multiplier':txt(once),
                      'repeated_gross_usd':txt(stake*repeated),'once_only_gross_usd':txt(stake*once),
                      'below_current_multiplier_and_money_caps':True})
        rank=next_rank
    assert len(steps)+1==50
    return {'schema_version':1,'source_references_verified':len(sources),
      'historical_observations':{'public_hilo_receipts':receipt_count,'declared_maxCardsAllowed_values':sorted(stored_limits),
                                'largest_observed_paid_call_count':observed_max_calls,'observed49_call_bets':0},
      'headline_figures':{'risky_full_board':table[8],'hilo49_call_model':table[48]},
      'interpretation':{'measure':'House edge is measured against the original bet: with 1% taken on every step, a round of n paid steps returns 0.99^n of the bet on average, before caps and rounding. With 1% taken once it returns 0.99 at any length.',
         'once_only_comparator':'For a winning 49-call path, reduction relative to the once-only 99% model is 1-0.99^48, approximately 38.27%, not 38.89%. The 38.89% cumulative edge includes the original 1%.',
         '49_call_limit':'All 20 receipt payloads declare 50 allowed cards and show one starting deal. A synthetic history with one deal and 49 calls contains 50 cards. No captured backend enforcement proves 49 is the maximum number of paid calls or that this precise history was accepted in production.',
         'caps':'Synthetic path below both current caps demonstrates that those caps need not mathematically bind every 49-call outcome path. It does not establish actual RTP of a strategy subject to forced cashouts, caps, rounding or unavailable actions.',
         'probability':'At each paid decision, conditional win probability times repeated incremental payout equals 0.99. With a fixed number of paid calls and no cap/rounding interventions, repeated conditional expectation yields 0.99^n. No statistical RNG/distribution test is performed.',
         'historical_limits':'November 22 public settings are used only to check the displayed current caps. Their unchanged historical application is not proven. Historical receipt fields were collected on 23 November 2026, after the bets.'},
      'synthetic49_call_example':{'evidence_type':'Constructed mathematics, not a captured or live bet.',
         'starting_rank':13,'starting_rank_name':'K','rank_pattern':'K,A,K,A,...,A','starting_deal_count':1,'paid_calls':49,'skips':0,'total_cards':50,
         'illustrative_stake_usd':'100','repeated_final_multiplier_exact':exact(repeated),'repeated_final_multiplier':txt(repeated),
         'once_only_final_multiplier_exact':exact(once),'once_only_final_multiplier':txt(once),
         'zero_edge_final_multiplier':txt(fair),'repeated_gross_usd_rounded':money(stake*repeated),
         'once_only_gross_usd_rounded':money(stake*once),'payout_difference_vs_once_usd_rounded':money(stake*(once-repeated)),
         'current_cap_reference':{'settings_capture_date':'2026-11-22','multiplier':'10000','max_payout_usd':'200000'},
         'all49_prefixes_below_both_current_caps':True,'steps':steps},
      'table_1_to_49':table}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    if out==BASE or BASE in out.parents:parser.error('Choose an output directory outside the preserved edge-model evidence folder.')
    with localcontext() as ctx:
        ctx.prec=80;result=calculate()
        out.mkdir(parents=True,exist_ok=True)
        (out/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
        with (out/'edge-table.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(result['table_1_to_49'][0]));w.writeheader();w.writerows(result['table_1_to_49'])
        print(json.dumps({'historical_observations':result['historical_observations'],'risky9_edge_percent':result['headline_figures']['risky_full_board']['cumulative_edge_percent'],
                         'hilo49_edge_percent':result['headline_figures']['hilo49_call_model']['cumulative_edge_percent'],
                         'hilo49_winning_payout_reduction_vs_once_percent':result['headline_figures']['hilo49_call_model']['winning_payout_reduction_vs_once_percent'],
                         'synthetic_repeated_payout_usd':result['synthetic49_call_example']['repeated_gross_usd_rounded'],
                         'synthetic_once_only_payout_usd':result['synthetic49_call_example']['once_only_gross_usd_rounded']},indent=2))
if __name__=='__main__':main()
