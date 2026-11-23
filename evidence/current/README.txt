Our test receipts after the change
==================================

We kept 50 completed bets from our test account on 23 November 2026: 20 HiLo
and 30 Risky Click. Each bet ID is included so the bet can be traced. The
account name and fairness seeds are left out.

Contents
--------
receipt-transcripts.json  The text of each receipt, its collection date, bet ID
                          and label.
references.json           Each label mapped to its game, bet ID and game page.
                          These are game pages, not links to single receipts.
*-receipt-svg-1.svg       The card history or tile board from each receipt,
                          extracted as-is from the page. They are not
                          screenshots, so styling can differ from the site.
verify.py                 Rechecks the arithmetic. Standard-library Python.
analysis.json             Results for every call and every bet.

Run it
------
    python3 verify.py --output /tmp/yeet-current

It reads only these files and writes only to the folder you name, which must
be outside the evidence folder. No network, account or wagering.

Results
-------
HiLo: 20 bets, 6 wins, 14 losses. The 6 wins have 33 winning calls. All 33
match 1% taken once. All 27 calls after the first rule out 1% on every call.
The first call of a round cannot tell the two apart.

Risky Click: 30 bets, 11 wins, 19 losses. The second session that day is
complete: 17 rounds, 5 wins. From the first session we kept 13 of its 40
rounds, 6 of them wins.

All 17 winning final multipliers, across both games, match 1% taken once.
None matches 1% on every step.

Example: tiles 1.2, 1.3 and 1.5 multiply to 2.34x. With 1% taken once that is
2.34 / 0.99^2 = 2.3875x. The receipt shows 2.39x (RNEW01).

Limits
------
- Bet times are shown as the site displayed them, to the minute.
- These receipts check the displayed arithmetic. They do not replay the random
  draws or prove exact token settlement.
- 17 wins cannot measure RTP. They show how wins are priced now.
- RNEW01, RNEW02 and RNEW03 are three bets with the same three tiles and the
  same result, so their receipts look identical. Their bet IDs differ.
- The published bet IDs let YEET identify these bets and the account that
  placed them.
- 14 readable receipt crops are in ../../images. Every bet here has its text
  and its board.
