# Asset Timeline for Counterparty & Dogeparty

Shows a timeline of milestones on Counterparty / Dogeparty.

Lookup an asset to show a timeline specific to that asset.

Live versions:
* https://jpjanssen.com/timeline/counterparty.html
* https://jpjanssen.com/timeline/dogeparty.html

## How It Works

All broadcasts, asset issuances and token destructions are extracted from the latest DB with `db/counterparty_db_to_js.py` or `db/dogeparty_db_to_js.py`. The generated JS arrays are written to `db/cp_history.js` or `db/dp_history.js`.

When `counterparty.html` or `dogeparty.html` loads, the relevant timeline is generated.

A query string with parameter `asset` can be specified, e.g. `counterparty.html?asset=JPJA` shows the timeline for JPJA.

Run a Counterparty / Dogeparty node to get the current DB.

## Milestones

Milestones are found by chronologically scanning events up until the defined conditions are met. Add more conditions, or review the existing ones, in function `list_of_firsts()`.

## Asset Timeline

The timeline shows all changes to asset properties, such as increase of supply, lock, change of description, transfer of issuance, and token destructions.

It also shows all broadcasts by the current issuer and any broadcast by third parties where the asset is mentioned.

In case of a broadcast by the issuer, but the issuer does not mention the asset specifically, the text is grey to indicate that it may not be relevant. The same is true for broadcasts by third parties, as the mention may be coincidental.

## Donate

* BTC: bc1qg8vldv8kk4mqafs87z2yv0xpq4wr4csucr3cj7
* DOGE: DChdsuLuEvAPZb9ZXpiEpimgidSJ5VqShq
* ETH: 0x4144CbaF54044510AB2F2f3c51061Dd5558cD604

## License

MIT