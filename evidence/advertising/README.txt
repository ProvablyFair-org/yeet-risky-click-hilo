What YEET told players
======================

november-6/
Page text saved logged out on 6 November 2026. It is the page's accessibility
text, not raw HTML. No bets were placed and no account was signed in.

  hilo-description-excerpt.txt         HiLo: 99% Return to Player, 1% House Edge
  risky-click-description-excerpt.txt  Risky Click: 99% Return to Player,
                                       1% House Edge
  hilo-rules.txt                       HiLo rules: RTP 99.00%, cashing out,
                                       ties and skips
  risky-click-rules.txt                Risky Click rules: RTP 99.00%, tile
                                       multipliers multiply together, a full
                                       board pays 361.17x
  risky-click-paytable.txt             All nine tile multipliers and chances

The two description files are excerpts: the Login and Create Account buttons,
which show the page was logged out, and the game description block. The rest
of the page (site chat, game lists, footer) is left out. SOURCE-INDEX.json
records the exact line ranges and the hash of each full saved page. The three
rules and paytable files are complete.

Nothing on these pages says the house edge grows with each tile or call.

public-settings/
Public Risky Click files saved on 22 November 2026.

  risky-click-settings-2026-11-22.json   Nine tile multipliers, their exact
        chances, houseEdgeFactor 0.99 and fullBoardMultiplier 391.4181. Each
        chance times its multiplier is 0.99.
  risky-click-rules-en-2026-11-22.json   The current rules text. It has a new
        line (RULES_EDGE_ONCE): the edge is charged once, every tile after the
        first pays its multiplier divided by 0.99, and the game returns 99%
        however many tiles you take.
  risky-click-public-helper-excerpt.js   The client function that keeps the
        first tile multiplier and divides every later one by 0.99.
  risky-click-rule-rendering-excerpts.json  How the rule text is rendered.
  asset-response-header-excerpts.json    Server headers for the two game files.

asset-timing-and-rule-excerpts.txt
The Last-Modified headers: Risky Click file 10 Nov 2026 10:28:39 GMT, HiLo
file 10 Nov 2026 11:54:14 GMT.

What this shows
---------------
On 6 November both games told players 99% RTP and a 1% house edge. Each
Risky Click tile was priced at 99% on its own, so before the change a round of
k tiles returned 0.99^k: 91.35% for a full board. A full board paid 361.18x.
Since the change it pays 391.42x, which is 99% for the whole round. YEET's
current rules describe exactly that.

Limits
------
Hashes show these files have not changed since they were saved. They are not
independent timestamps. We do not claim the 6 November wording for every
earlier date. Last-Modified shows when YEET's server files last changed, not
the exact minute the payout engine changed.
