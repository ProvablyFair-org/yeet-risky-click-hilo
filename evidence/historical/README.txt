Public wins before the change
=============================

40 public winning records from YEET's own Top Wins and Lucky Wins boards: ten
of each for HiLo and Risky Click. They belong to other players. HiLo receipts
show every card, every call and the multiplier after each call. Risky Click
board rows show the stake, the payout and the final multiplier, but not which
tiles were picked.

Bet dates: HiLo 1 June to 10 November 2026, Risky Click September 2025 to
August 2026. All records were collected on 23 November 2026.

Contents
--------
SOURCE-INDEX.json         Public URLs, collection dates and SHA-256 hashes.
sources/                  The 20 HiLo receipts and the 4 leaderboards (HiLo and
                          Risky Click), saved as the JSON text the browser
                          showed. The two Risky Click leaderboards also link to
                          third-party Wayback copies.
verify.py                 Standard-library Python that rechecks every number.
analysis.json             Full results: all 163 HiLo calls and every possible
                          Risky Click tile set.
verification-summary.txt  The totals.

The individual receipts for the 20 Risky Click wins are in ../risky-receipts.

Run it
------
    python3 verify.py --output /tmp/yeet-historical

It checks all 24 source hashes first, then writes analysis.json and
verification-summary.txt to the folder you name, outside the evidence folder.
They match the bundled files byte for byte. No network, account or wagering.

How HiLo is checked
-------------------
13 equally likely ranks, drawn with replacement. Higher and lower include an
equal card, except higher from an Ace and lower from a King (12 of 13). Same is
1 of 13. A skip changes the card and pays nothing. For a call that wins with
probability p:

  1% on every call:  each winning call multiplies by 0.99/p
  1% once a round:   0.99 once, then each winning call multiplies by 1/p

All 163 winning calls match 1% on every call. The first call of a round cannot
tell the two apart. None of the 143 calls after the first matches 1% once.
All 20 final multipliers match 1% on every call. The 39 skips are not counted
as calls. Longest win: 25 calls.

How Risky Click is checked
--------------------------
Nine tiles: 1.2, 1.3, 1.4, 1.5, 1.75, 2, 2.5, 3 and 4.2 (YEET's paytable and
settings). Each tile wins with probability 0.99 / multiplier. The script tries
all 511 possible tile sets. All 20 recorded multipliers equal the plain product
of a tile set (within 0.0001), which is 1% on every tile. None matches 1% once,
at that tolerance or at two decimals. One record shows 40.1309 where the exact
product is 40.131; the difference is kept.

Nine records fit more than one tile set. For those we use the set with the
smallest 99% payout, so the difference is never overstated. analysis.json keeps
every candidate.

Money
-----
Paid: the USD payout on YEET's public board, stake included.
At 99% for the round: the same win with the 1% taken once.

HiLo uses exact fractions at 70-digit precision. Risky Click floors the 99%
multiplier and payout to four decimals. Only the final totals are rounded to
cents.

                     Paid            At 99% for the round   Difference
  HiLo (20)          $301,556.15     $316,393.43            $14,837.28
  Risky Click (20)   $718,706.78     $743,659.05            $24,952.27
  All 40           $1,020,262.93   $1,060,052.48            $39,789.55

Limits
------
These are YEET's top and lucky wins. They show how wins were priced. They are
not all play, so the totals are not a casino-wide figure. Board stakes are
shown in USD, so currency conversion can move cents. Hashes show the files are
unchanged since collection; they are not independent timestamps. HTTP status
and headers were not recorded. This checks payout pricing; it does not replay
the random draws.
