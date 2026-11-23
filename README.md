# YEET Risky Click and HiLo investigation

ProvablyFair.org · 23 November 2026

Evidence and reproducible calculations for the investigation of YEET's Risky Click and HiLo payout pricing.

## Download the evidence

[Download the complete evidence package](yeet-risky-click-hilo-evidence-2026-11-23.zip?raw=true).

The ZIP contains the report, original public records, captured receipt material, Discord and X records, source indexes and Python verification scripts. It has **164 files: 163 hashed files plus its SHA256SUMS manifest**.

Unzip with the folders intact, then open `yeet-risky-click-hilo-investigation.html` in a browser. The report works locally without scripts, trackers or a login.

## Findings

YEET advertised both games at 99% RTP, a 1% house edge. Historical pricing took the 1% again on every tile or paid call. The resulting house edge is `1 - 0.99^steps`.

- Risky Click: up to **8.65%**, at nine tiles.
- HiLo: up to **38.89%**, at 49 calls under the documented 50-card limit. No 49-call round was observed. The longest public win had 25 calls, corresponding to **22.22%**.
- All **40 selected historical public wins** match the old pricing, including all **163 HiLo calls**. The specified payout difference across those wins is **$39,789.55**, not total player losses or an established compensation total.
- All **17 captured wins** among **50 kept current receipts** match 1% taken once.
- The 10 November change date rests on the last old-price public win, file dates and current rules. We cannot see YEET's server.
- By 23 November we had found no announcement on X or in YEET's Discord, and no refund notice. The package describes the searches and their limits.

## Reproduce the checks

Python 3.9 or later, standard library only. No network, casino account or wagering is required.

From the extracted package folder:

```sh
python3 verify_package.py
python3 evidence/historical/verify.py --output /tmp/yeet-historical
python3 evidence/risky-receipts/verify.py --output /tmp/yeet-risky-receipts
python3 evidence/current/verify.py --output /tmp/yeet-current
python3 evidence/edge-model/verify.py --output /tmp/yeet-edge
python3 evidence/public-search/verify_public_image.py
```

The four analysis scripts write only to the separate output folders named above. Their outputs reproduce the bundled analysis files byte for byte.

Expected package check:

```text
PASS: 163 files match SHA256SUMS; no unlisted files.
```

This repository's `SHA256SUMS` checks the downloadable ZIP. The separate manifest inside the ZIP checks each package file. Hashes verify integrity; they do not independently authenticate capture dates or source truth.

## Scope and disclosure

The historical sample consists of selected public Top Wins and Lucky Wins, not a representative sample of all play. Nine Risky Click records fit more than one tile set; their calculations use the smallest compatible difference. This investigation checks payout arithmetic, not a replay of random draws.

Current test bet IDs are published, so YEET can identify those bets. Account names and fairness inputs for the test receipts are omitted. Public historical records retain their documented public fields.

We have previously contacted YEET about our audit services, as we do with many of the larger casinos. They did not reply.

## Licensing and corrections

The package includes a `LICENSE`: MIT for the Python scripts and CC BY 4.0 for our text and analysis. Third-party evidence remains with its owners.

Send corrections or new evidence to audit@provablyfair.org. Material corrections will be dated and published.
