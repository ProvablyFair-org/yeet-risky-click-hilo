# YEET Risky Click and HiLo: evidence package

ProvablyFair.org, 23 November 2026. The evidence behind our investigation of YEET's Risky Click and HiLo, and the code to check the payout calculations.

## The finding

YEET advertised both games at **99% RTP**, a **1% house edge**. Historical pricing took the 1% again on every tile or paid call. After `n` steps, the house edge was `1 - 0.99^n`.

- **Risky Click: up to 8.65%**, on a full nine-tile board.
- **HiLo: up to 38.89%**, at 49 calls under the documented 50-card limit. We did not observe a 49-call round. The longest public win had 25 calls, corresponding to **22.22%**.
- All **40 selected historical public wins** match that pricing, including all **163 HiLo calls**. They paid **$39,789.55 less** than the specified calculation with the 1% taken once. This is the difference across those selected wins, not total player losses or an established compensation total.
- All **17 captured wins** among **50 kept current receipts** match the 1% taken once.
- The **10 November** change date rests on the last old-price public win, file dates and current rules. We cannot see YEET's server.
- By **23 November**, we had found no announcement on X or in YEET's Discord, and no refund notice. The search records describe what was checked and their limits.

## Check it yourself

Python 3.9 or later, standard library only. No account, network access or wagering is needed for the checks. Download or clone this repository, then run:

```sh
git clone https://github.com/ProvablyFair-org/yeet-risky-click-hilo.git
cd yeet-risky-click-hilo
make check
```

`make check` verifies all **163 file hashes**, runs all six verification commands and checks the regenerated analysis files against the stored results byte for byte. Generated files go to a temporary folder outside the repository. The complete repository contains **164 files**, including `SHA256SUMS` itself.

You can also run each check directly:

```sh
python3 verify_package.py
python3 evidence/historical/verify.py --output /tmp/yeet-historical
python3 evidence/risky-receipts/verify.py --output /tmp/yeet-risky-receipts
python3 evidence/current/verify.py --output /tmp/yeet-current
python3 evidence/edge-model/verify.py --output /tmp/yeet-edge
python3 evidence/public-search/verify_public_image.py
```

The four analysis scripts write only to the output directories you specify. The manifest check reports:

```text
PASS: 163 files match SHA256SUMS; no unlisted files.
```

Hashes verify integrity. They do not independently authenticate capture dates or source truth.

## What is in here

| Folder or file | What it holds |
| --- | --- |
| [evidence/advertising/](evidence/advertising/) | Logged-out page text saved on 6 November, and public settings, rules and code saved on 22 November. |
| [evidence/historical/](evidence/historical/) | Forty public wins collected on 23 November, source indexes, analysis and the payout reconstruction script. |
| [evidence/risky-receipts/](evidence/risky-receipts/) | The twenty individual public Risky Click receipts, reconciled with their leaderboard rows. |
| [evidence/current/](evidence/current/) | Fifty kept test receipts from 23 November, transcripts, extracted SVGs and payout checks. |
| [evidence/edge-model/](evidence/edge-model/) | Exact house-edge calculations for one through 49 steps and the public 50-card setting. |
| [evidence/public-search/](evidence/public-search/) | X search records, official posts and the public player screenshot calculation. |
| [evidence/discord/](evidence/discord/) | Announcements, patch notes, searches and the June 2025 team RTP statement. |
| [images/](images/) | Fourteen selected test-receipt crops, the public player screenshot and their source index. |
| [verify_package.py](verify_package.py) | Offline hash and file-completeness verification. |
| [Makefile](Makefile) | Runs all checks and compares the regenerated results. |
| [SHA256SUMS](SHA256SUMS) | Hashes for all 163 other repository files. |

## Expected results

Before the change:

- HiLo: **20 wins, 163 winning calls**. Every call matches the old pricing. None of the 143 calls after the first matches 1% taken once. The longest win has 25 calls.
- Risky Click: **20 wins**. Every multiplier matches the historical tile products; none matches 1% taken once. All twenty individual public receipts match their leaderboard rows.
- The forty wins paid **$1,020,262.93**. The specified calculation with 1% taken once pays **$39,789.55 more**.

After the change:

- **50 kept receipts: 20 HiLo and 30 Risky Click**, including **17 wins**: six HiLo and eleven Risky Click. All seventeen match 1% taken once.
- The thirty Risky Click receipts comprise one complete seventeen-round session and thirteen of forty rounds from an earlier session.
- All twenty-seven captured winning HiLo calls after the first rule out 1% taken on every call.

## Limits and privacy

- The public sample consists of selected Top Wins and Lucky Wins, not a representative sample of all play.
- Risky Click receipts do not reveal the selected tiles. Nine wins fit more than one tile set; the calculations use the smallest compatible difference.
- All twenty historical HiLo receipts declare a fifty-card limit. The 49-call calculation is not an observed bet or a confirmed server maximum. If the server allowed fifty paid calls, the calculated edge would be 39.50%.
- File dates and the latest old-price public win support the change date. They do not expose the backend deployment history.
- These checks reproduce payout arithmetic. They do not replay random draws or independently authenticate receipt origins.
- The notice search covers the retained X and Discord material. We cannot see emails, private messages or account credits.
- Current test bet IDs are published so YEET can identify the bets. Test-account names and fairness inputs are omitted. Historical records retain their documented public fields.

## Disclosure

We have previously contacted YEET about our audit services, as we do with many of the larger casinos. They did not reply.

## Licensing and corrections

[LICENSE](LICENSE) provides MIT terms for the Python scripts and CC BY 4.0 for our text and analysis. Third-party evidence remains with its owners.

Send corrections or new evidence to audit@provablyfair.org. Material corrections will be dated and published.
