---
title: "Solana Token Price Charts, Now in Zerion API"
slug: solana-token-price-charts-now-in-zerion-api
date: 2025-10-15
published_at: 2025-10-15T19:48:50.000Z
feature_image: https://zerion.io/blog/content/images/2025/10/Solana_price_charts.png
authors:
  - name: Vladimir Shamanov
    slug: vladimir
    avatar: https://zerion.io/blog/content/images/2026/01/c08b6248-334a-4749-8808-a28f8ddf58ce-1.png
tags:
  - Zerion API
  - Solana
excerpt: "When a Solana wallet connects, users expect price charts to load instantly. But adding charts often means managing several APIs. This becomes even more complex with several chains. But not if you use…"
---

<p>When a Solana wallet connects, users expect price charts to load instantly. But adding charts often means managing several APIs. This becomes even more complex with several chains. But not if you use Zerion API. The fungible charts endpoint uses the same schema for Solana, Ethereum, and 24+ EVM chains. In this post, you’ll learn everything about Zerion API’s Solana token price charts.&nbsp;</p><h3 id="tldr">TL;DR:&nbsp;</h3><p>Use Zerion API’s <strong><code>GET /v1/fungibles/{fungible_id}/charts/{chart_period}</code></strong> for Solana tokens to fetch normalized price series for drop-in sparklines and time-series charts.</p>
<h2 id="what-is-zerion-api">What is Zerion API?&nbsp;</h2><p><a href="https://zerion.io/api" rel="noreferrer">Zerion API</a> is a production-ready wallet data platform that gives you instant, normalized access to multi-chain portfolio state: tokens, <a href="https://zerion.io/blog/how-to-fetch-multichain-defi-positions-for-wallet-with-zerion-api/" rel="noreferrer">DeFi positions</a>, NFTs, transactions, <a href="https://zerion.io/blog/onchain-pnl-api-how-to-track-profit-and-loss-for-wallets-and-tokens/" rel="noreferrer">PnL</a>, and price charts. Zerion uses one auth and the same schema across Solana and EVM. It’s built for high-scale consumer apps to ship fast experiences, eliminate token-coverage gaps, and keep UIs snappy without running your own indexers.</p><p>The API offers the same data you see in Zerion’s <a href="https://zerion.io/solana-wallet" rel="noreferrer">Solana wallet</a> and <a href="https://app.zerion.io/" rel="noreferrer">web app</a>. It's also used by companies like Kraken, Infinex, OpenSea, and many others. </p><h2 id="fungibles-chart-endpoint-overview">Fungibles chart endpoint overview</h2><p>Zerion API offers a single <a href="https://developers.zerion.io/reference/getfungiblechart#/" rel="noreferrer">endpoint for token price charts</a> for both Ethereum / EVM chains and Solana.&nbsp;</p><pre><code class="language-bash">GET https://api.zerion.io/v1/fungibles/{fungible_id}/charts/{chart_period}?currency=usd

</code></pre>
<ul><li><strong><code>{fungible_id}</code></strong> – the fungible asset ID, the same one you can get in Zerion’s /positions and other endpoints&nbsp;</li><li><strong><code>{chart_period}</code></strong> – the prices can be returned for hour, day, week, month, year, or maximum (usually since the token launched)</li><li><strong><code>currency</code></strong> – normalize prices in ETH, BTC, USD, or major fiat currencies </li></ul><p>The response is given as a timeseries with unix_seconds and prices. Here is an example for a day chart with prices for every 5 minutes.&nbsp;</p><pre><code class="language-js">{
  "links": {
    "self": "https://api.zerion.io/v1/fungibles/11111111111111111111111111111111/charts/day?currency=usd"
  },
  "data": {
    "type": "fungible_charts",
    "id": "11111111111111111111111111111111-day",
    "attributes": {
      "begin_at": "2025-10-13T13:50:00Z",
      "end_at": "2025-10-14T13:50:00Z",
      "stats": {
        "first": 194.22407550479997,
        "min": 192.21674282849997,
        "avg": 201.49800676928095,
        "max": 210.7062787433,
        "last": 193.34017981059998
      },
      "points": [
        [
          1760363400,
          194.22407550479997
        ],
        [
          1760363700,
          195.1531912116
        ]
        // ... [unix_seconds, price]
      ]
    }
  }
}
</code></pre>
<p>Here is how the price chart looks in the <a href="https://app.zerion.io/tokens/SOL-11111111111111111111111111111111" rel="noreferrer">Zerion web app</a>. </p><figure class="kg-card kg-image-card kg-card-hascaption"><img src="https://zerion.io/blog/content/images/2025/10/Solana-price-chart.png" class="kg-image" alt="Solana price chart in Zerion" loading="lazy" width="914" height="587" srcset="https://zerion.io/blog/content/images/size/w600/2025/10/Solana-price-chart.png 600w, https://zerion.io/blog/content/images/2025/10/Solana-price-chart.png 914w" sizes="(min-width: 720px) 720px"><figcaption><span style="white-space: pre-wrap;">Solana price chart in Zerion</span></figcaption></figure><h2 id="where-to-use-fungible-price-charts">Where to use fungible price charts?&nbsp;</h2><p>The endpoint returns standard JSON data. So it's compatible with virtually any modern programming language or framework that can make HTTP requests and parse JSON responses.</p><h2 id="how-to-find-the-right-fungibleid">How to find the right fungible_id?&nbsp;</h2><p>You can use the Zerion <a href="https://developers.zerion.io/reference/listfungibles#/" rel="noreferrer">fungibles endpoints</a> to search for a token and take the returned <strong><code>fungible_id</code></strong> into the charts endpoint. Zerion API keeps the same ID across Solana and EVM paths to avoid schema forks.&nbsp;</p><h2 id="ship-with-zerion">Ship with Zerion&nbsp;</h2><p>Zerion API’s Solana support for fungible token price charts means you can deliver the same fast, reliable chart UX across Solana and EVM. With one endpoint and one schema, you can reduce the integration time even further.&nbsp;</p><p><a href="https://dashboard.zerion.io/?utm_source=blog&amp;utm_medium=article&amp;utm_campaign=Solana-price-charts" rel="noreferrer"><u>Get your free dev API key</u></a>.</p>
