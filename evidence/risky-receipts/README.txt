Individual Risky Click receipts
===============================

The 20 Risky Click wins in ../historical come from YEET's leaderboards. This
folder adds the individual public receipt for each of those 20 wins, collected
on 23 November 2026.

Every receipt matches its leaderboard row: bet ID, round ID, bet time,
currency, stake, payout and multiplier.

The receipts do not show which tiles were picked. Each one carries the same
game image and no tile list, click order or step multipliers. So the nine wins
that fit more than one tile set stay ambiguous, and the calculation still uses
the set with the smallest difference.

Five receipts are marked legacy and carry fairness fields; one shows a
revealed server seed. None records tile choices. No RNG replay is done here.

Contents
--------
sources/                  The 20 receipts, plus byte-identical copies of the
                          two Risky Click leaderboard files in
                          ../historical/sources.
SOURCE-INDEX.json         URLs, collection date, sizes and SHA-256 hashes.
verify.py                 Checks the hashes, matches each receipt to its
                          leaderboard row and checks every field for tile data.
analysis.json             Saved results.
verification-summary.txt  The totals.

Run it
------
    python3 verify.py --output /tmp/yeet-risky-receipts

No network, account or wagering. It writes only to the folder you name.
