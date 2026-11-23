#!/usr/bin/env python3
"""Reproduce display arithmetic using only the adjacent public transcripts/SVGs.

Python standard library only. No network, account access, seeds or hidden inputs.
Run: python3 verify.py --output /tmp/yeet-current-recheck
Writes analysis.json only in the explicit directory outside the evidence tree.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, localcontext
import json
import math
import re
import argparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
EDGE = Fraction(99, 100)
RANKS = {str(x): x for x in range(2, 11)} | {'A': 1, 'J': 11, 'Q': 12, 'K': 13}

def exact(x):
    with localcontext() as ctx:
        ctx.prec = 60
        return f'{Decimal(x.numerator)/Decimal(x.denominator):.12f}'

def display(x, nearest=False):
    hundredths = ((2*x.numerator*100+x.denominator)//(2*x.denominator)
                  if nearest else (x.numerator*100)//x.denominator)
    return f'{hundredths//100}.{hundredths%100:02}'

def read_svg(record):
    files = record['svgFiles']
    assert len(files) == 1, record['label']
    relative = Path(files[0])
    assert not relative.is_absolute() and '..' not in relative.parts
    tree = ET.fromstring((ROOT/relative).read_text())
    assert tree.tag == 'svg'
    assert not any(e.tag.lower() in {'script','foreignobject'} for e in tree.iter())
    return tree

def common(record):
    text = record['receiptTextWithoutAccountFields']
    amount = re.search(r'^([0-9.]+)x\n\$([0-9,.]+)\nfrom \$([0-9,.]+)', text, re.M)
    assert amount, record['label']
    placed = next(s.removeprefix('Placed ') for s in text.splitlines() if s.startswith('Placed '))
    return {'label':record['label'], 'betId':record['betId'], 'game':record['game'], 'status':record['status'],
            'displayedPlaced':placed, 'captureDate':record['captureDate'],
            'outerFinalMultiplier':amount[1], 'displayedGrossDollars':amount[2],
            'displayedStakeDollars':amount[3]}

def hilo(record):
    out = common(record)
    tree = read_svg(record)
    groups = tree.findall('g')
    ranks = [g.find('g/text').text for g in groups]
    badges = [g.find('text').text.removesuffix('x') for g in groups]
    titles = [[t.text for t in g.findall('.//title')] for g in groups]
    panel = re.search(r'MULTIPLIER\n([0-9.]+)x\nCORRECT CALLS\n(\d+)',record['receiptTextWithoutAccountFields'])
    assert panel, record['label']
    once = repeated = Fraction(1)
    calls = 0
    actions = []
    for i in range(len(ranks)-1):
        assert len(titles[i]) == 1, (record['label'], i)
        title = titles[i][0]
        # This set contains no skips. Fail rather than infer a skipped action.
        m = re.fullmatch(r'(Correct|Wrong) (higher|lower|same) call',title)
        assert m, (record['label'], title)
        verdict, direction = m.groups()
        before, after = RANKS[ranks[i]], RANKS[ranks[i+1]]
        if direction == 'same':
            n = 1; actual_success = before == after
        elif direction == 'higher':
            n = 12 if before == 1 else 14-before
            actual_success = after > before if before == 1 else after >= before
        else:
            n = 12 if before == 13 else before
            actual_success = after < before if before == 13 else after <= before
        correct = verdict == 'Correct'
        assert correct == actual_success, (record['label'],i)
        if correct:
            calls += 1
            once *= Fraction(13,n)*(EDGE if calls == 1 else 1)
            repeated *= EDGE*Fraction(13,n)
        else: once = repeated = Fraction(0)
        observed = badges[i+1]
        actions.append({'from':ranks[i], 'to':ranks[i+1], 'observedCallTitle':title,
                        'direction':direction, 'correct':correct, 'p':f'{n}/13',
                        'observedInnerPrefix':observed,
                        'onceOnly':exact(once), 'repeated':exact(repeated),
                        'matchesOnceOnlyTruncation':observed == display(once),
                        'matchesRepeatedTruncation':observed == display(repeated),
                        'matchesRepeatedNearest':observed == display(repeated,True)})
    assert calls == int(panel[2]) and badges[-1] == panel[1], record['label']
    out.update(rankSequence=ranks,correctCalls=calls,innerFinalMultiplier=panel[1],
               onceOnlyFinal=exact(once),repeatedFinal=exact(repeated),
               innerMatchesOnceOnlyTruncation=panel[1]==display(once),
               outerMatchesOnceOnlyNearest=out['outerFinalMultiplier']==display(once,True),
               outerMatchesRepeatedNearest=out['outerFinalMultiplier']==display(repeated,True),actions=actions)
    return out

def risky(record):
    out = common(record)
    tree = read_svg(record)
    m = re.fullmatch(r'Turned over (\d+) of 9 tiles for ([0-9.]+)x',tree.get('aria-label',''))
    assert m,record['label']
    safe, failed = [], []
    for g in tree.findall('g'):
        rect,text = g.find('rect'),g.find('text')
        if rect is None or text is None: continue
        base = text.text.removesuffix('x')
        cls = rect.get('class','')
        if 'rr:fill-win' in cls:safe.append(base)
        elif 'rr:fill-risky-rug' in cls:failed.append(base)
    assert len(safe)==int(m[1]),record['label']
    won = out['status']=='WON'
    assert len(failed)==(0 if won else 1),record['label']
    product = math.prod((Fraction(x) for x in safe),start=Fraction(1))
    once = product/EDGE**(len(safe)-1) if won else Fraction(0)
    repeated = product if won else Fraction(0)
    inner = m[2]
    out.update(safeTileBasesUnordered=safe,failedTileBases=failed,successfulClicks=len(safe),
               innerFinalMultiplier=inner,onceOnlyFinal=exact(once),repeatedFinal=exact(repeated),
               innerMatchesOnceOnlyTruncation=inner==display(once),
               innerMatchesOnceOnlyNearest=inner==display(once,True),
               outerMatchesOnceOnlyNearest=out['outerFinalMultiplier']==display(once,True),
               outerMatchesRepeatedNearest=out['outerFinalMultiplier']==display(repeated,True),
               clickOrderAvailable=False)
    return out

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,
                        help='Output directory outside the evidence tree; writes analysis.json there.')
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.is_relative_to(ROOT.parent):
        parser.error('Choose an output directory outside the evidence tree.')
    records = json.loads((ROOT/'receipt-transcripts.json').read_text())
    assert len(records)==50 and len({r['label'] for r in records})==50
    assert all(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',r['betId']) for r in records)
    assert len({r['betId'] for r in records})==50
    references=json.loads((ROOT/'references.json').read_text())['records']
    assert len(references)==50 and len({r['label'] for r in references})==50
    reference_by_label={r['label']:r for r in references}
    for record in records:
        ref=reference_by_label[record['label']]
        assert (ref['game'],ref['betId'],ref['sourceGameURL']) == (record['game'],record['betId'],record['sourceURL'])
    calculated=[hilo(r) if r['game']=='HiLo' else risky(r) for r in records]
    hs=[r for r in calculated if r['game']=='HiLo']
    rs=[r for r in calculated if r['game']=='Risky Click']
    hw=[r for r in hs if r['status']=='WON'];rw=[r for r in rs if r['status']=='WON']
    assert len(hs)==20 and len(rs)==30 and len(hw)==6 and len(rw)==11
    winning_prefixes=[a for r in hw for a in r['actions']]
    subsequent=[a for r in hw for a in r['actions'][1:]]
    assert len(winning_prefixes)==33 and len(subsequent)==27
    assert all(a['matchesOnceOnlyTruncation'] for a in winning_prefixes)
    assert all(not a['matchesRepeatedTruncation'] and not a['matchesRepeatedNearest'] for a in subsequent)
    assert all(r['outerMatchesOnceOnlyNearest'] and not r['outerMatchesRepeatedNearest'] for r in hw+rw)
    summary={'receiptRecords':50,'distinctPublishedBetIds':50,'hiLoRecords':20,'hiLoWins':6,'hiLoLosses':14,
             'riskyClickRecords':30,'riskyClickWins':11,'riskyClickLosses':19,
             'winningHiLoPrefixes':33,'subsequentWinningHiLoPrefixesExcludingRepeated':27,
             'winningFinalsMatchingOnceOnly':17,'winningFinalsMatchingRepeated':0,
             'freshRiskySessionRecords':17,'freshRiskySessionWins':5,
             'earlierSameDayRiskyRecords':13,'earlierSameDayRiskyWins':6}
    result={'scope':'Receipts from our test account, captured on 23 November 2026. Bet IDs kept; account name and fairness inputs omitted. Reproduces the displayed arithmetic; it is not an RNG replay.',
            'summary':summary,
            'dates':{'captureDate':sorted({r['captureDate'] for r in calculated}),
                     'placedTimes':'Bet times are kept as displayed on each receipt, to the minute.'},
            'method':{'hiLo':'Uniform independent ranks. Ordinary higher/lower include equality; higher from A and lower from K exclude equality. Probability qualifying ranks / 13. Once-only=0.99/product(p); repeated=product(0.99/p).',
                      'riskyClick':'Tile success model p=0.99/base. With k successful tiles: once-only=product(base)/0.99^(k-1); repeated=product(base). Captured selected set is sufficient for final multiplier; click order is not provided.',
                      'display':'Exact rational arithmetic. Compare inner fields with two-decimal truncation/rounding, outer fields with nearest-half-up two decimals. Agreement does not prove exact formatter or monetary settlement implementation.'},
            'limits':['Test account bet IDs are published. Account name and fairness inputs are omitted; this package does not independently replay the current RNG. Exact public receipt URLs and anonymous refetchability have not been established; sourceGameURL values point to the games, not individual receipts.',
                      'This script checks 50 distinct, well-formed published bet IDs, consistency with references.json, and the supplied receipt arithmetic. It does not independently fetch records from the casino or authenticate their server origin.',
                      'The 17-round final Risky session is completely captured. The earlier 40-round session has only 13 captured receipts; its all-win coverage is not claimed.',
                      'Screenshots are a selected readable subset. Every record has a redacted text transcript and full extracted receipt SVG. SVGs are DOM extracts, not independent screenshots.',
                      'No empirical or casino-wide 99% RTP, pre-bet commitment timing, exact token settlement, compensation or change-date claim follows from these current receipts.',
                      'The published bet IDs let the operator identify these bets and the account that placed them.'],
            'records':calculated}
    output.mkdir(parents=True,exist_ok=True)
    (output/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(summary,indent=2));print(json.dumps(result['dates'],indent=2))

if __name__=='__main__':main()
