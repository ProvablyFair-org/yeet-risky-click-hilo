House edge by round length
==========================

If 1% is taken on every step, a round of n steps returns 0.99^n of the stake.
The house edge is 1 - 0.99^n.

  Steps   Returns   House edge
    1     99.00%     1.00%
    3     97.03%     2.97%
    9     91.35%     8.65%   Risky Click full board
   12     88.64%    11.36%
   25     77.78%    22.22%   longest public HiLo win
   49     61.11%    38.89%   HiLo at the 50-card limit

With the 1% taken once, every row returns 99%.
edge-table.csv has every value from 1 to 49 steps, exact.

Where 9 and 49 come from
------------------------
Risky Click has nine tiles, so nine is the most a round can take.

All 20 public HiLo receipts declare maxCardsAllowed 50. One starting card plus
49 calls uses 50 cards. The longest public win has 25 calls. We did not see a
49-call bet, and the game client does not show exactly how the server counts
the limit. If the limit allowed 50 calls the edge would be 39.50%, so 38.89%
is the lower reading.

What a winning player loses
---------------------------
Compared with 1% taken once, a winning n-step round pays 0.99^(n-1) as much:

  9 tiles     7.73% less
  25 calls   21.43% less
  49 calls   38.27% less

To see what a win should have paid: payout / 0.99^(steps - 1).

A 49-call example under the caps
--------------------------------
verify.py builds a 50-card HiLo round: start on a King, then Ace, King, Ace and
so on for 49 calls, calling lower from a King and higher from an Ace. Each call
wins 12 times in 13, and each win pays 0.99 / (12/13) = 1.0725x.

  1% on every call:  30.8651x   $3,086.51 on a $100 bet
  1% once:           50.0010x   $5,000.10 on a $100 bet

Every step stays under the current 10,000x and $200,000 caps, so the caps do
not stop a round like this. It is a worked example, not a real bet.

Why 0.99^n
----------
At each step, the chance of winning times the step payout is 0.99. Chain n
steps and the expected return is 0.99^n. With the 1% taken once, later steps
pay 1/p and the round stays at 0.99. Caps, rounding and forced cashouts can
change a real strategy's return; this table does not model them.

Run it
------
    python3 verify.py --output /tmp/yeet-edge

It checks 22 source hashes, rebuilds the table and the example, and checks all
49 steps against the caps. No network, account or wagering.
