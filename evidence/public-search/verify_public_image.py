#!/usr/bin/env python3
"""Recalculate transcribed public-image figures; no files or network are changed."""
from fractions import Fraction as F
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, localcontext
import json

ranks=[4,7,12,4,9,7,9,9,9,6]
actions=['higher','higher','lower','higher','lower','higher','lower','lower','lower']
shown=['1.28','2.36','2.53','3.26','4.67','8.58','12.27','17.55','25.11']
edge=F(99,100);product=F(1);repeated=F(1);prefixes=[]
with localcontext() as ctx:
    ctx.prec=60
    def dec(x):return Decimal(x.numerator)/Decimal(x.denominator)
    for i,action in enumerate(actions):
        r=ranks[i]
        p=F(14-r if action=='higher' else r,13)
        product*=p;repeated*=edge/p
        truncated=format(dec(repeated).quantize(Decimal('.01'),rounding=ROUND_DOWN),'f')
        assert truncated==shown[i]
        prefixes.append({'call':i+1,'from_rank':r,'to_rank':ranks[i+1],
            'action':action,'success_probability_model':str(p),
            'repeated_multiplier':str(dec(repeated)),
            'shown_multiplier':shown[i],'matches_truncation':True})
    stake=F('40.96');once=edge/product
    assert format(dec(stake*repeated).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'f')=='1028.54'
    result={'source':'https://x.com/JerzyNFT/status/2062294277598609851/photo/1',
        'image':'../../images/jerzy-original-posted-image.jpg',
        'evidence_kind':'Analyst transcription of public promotional image; inspect image independently.',
        'stake_usd':'40.96','shown_cashout_usd':'1028.54','prefixes':prefixes,
        'once_only_multiplier':str(dec(once)),
        'once_only_gross_usd_rounded':format(dec(stake*once).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'f'),
        'limits':'Uses stated independent uniform-rank model; media is not an authenticated ledger or a visible RTP claim.'}
print(json.dumps(result,indent=2))
