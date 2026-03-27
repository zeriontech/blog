---
title: The Easiest Way to Fetch Multichain DeFi Positions for Any Wallet (with Zerion API)
slug: how-to-fetch-multichain-defi-positions-for-wallet-with-zerion-api
date: 2025-09-10
published_at: 2025-09-10T20:20:30.000Z
feature_image: https://zerion.io/blog/content/images/2025/09/Defi_API.png
authors:
  - name: Vladimir Shamanov
    slug: vladimir
    avatar: https://zerion.io/blog/content/images/2026/01/c08b6248-334a-4749-8808-a28f8ddf58ce-1.png
tags:
  - Zerion API
excerpt: "Fetching a wallet’s DeFi positions isn’t easy. Between LPs, staked tokens, lending collateral, and rewards, blockchain data is fragmented and hard to interpret.  With Zerion API, you can skip the…"
---

<p>Fetching a wallet’s DeFi positions isn’t easy. Between LPs, staked tokens, lending collateral, and rewards, blockchain data is fragmented and hard to interpret.</p><p>With <a href="https://zerion.io/api" rel="noreferrer">Zerion API</a>, you can skip the complexity. A single endpoint returns all DeFi positions for a given wallet address across multiple chains. All positions are normalized, valued in USD (or another currency of your choice), and enriched with protocol data.</p><p>In this post, we’ll show you how to fetch DeFi positions in just a few lines of code, explain filtering options, and share best practices for using this data in your app.</p>
<!--kg-card-begin: html-->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "Why is it so hard to get DeFi positions for a wallet address?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Because DeFi positions aren’t simple token balances. They live inside smart contracts with unique logic: staking vaults, LP pools, lending protocols, reward contracts. Raw onchain calls return low-level data without financial meaning. To interpret them, you’d normally need to parse each protocol’s contracts or maintain subgraphs. Zerion API solves this by returning normalized, human-readable positions in one call."
    }
  },{
    "@type": "Question",
    "name": "How to get DeFi positions from multiple chains?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "With Zerion API, you don’t need separate integrations. The GET https://api.zerion.io/v1/wallets/{address}/positions/ endpoint returns protocol positions across all supported EVM chains. You can filter by blockchain if you want a narrower view, or query once for a unified multichain portfolio."
    }
  },{
    "@type": "Question",
    "name": "How to fetch staked token positions?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Staked tokens are included in Zerion API’s protocol positions.

You can use fetch('https://api.zerion.io/v1/wallets/address/positions/?filter[positions]=only_complex&currency=usd&filter[dapp_ids]=EXAMPLE_PROTOCOL) Instead of EXAMPLE_PROTOCOL you specify the staking protocol, e.g. Aave or Morpho. This will return staking positions along with protocol metadata, token amount, and USD value."
    }
  },{
    "@type": "Question",
    "name": "How to fetch liquidity pool positions for a wallet address?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Liquidity pool shares are also interpreted as protocol positions in Zerion API. The same positions endpoint with the “compex_only” filter will return LP positions, including underlying token breakdowns. You can use this to show both the pool share and its token composition in your app."
    }
  },{
    "@type": "Question",
    "name": "How to get staking rewards accrued to a wallet address?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Unclaimed rewards (like yield or farming incentives) are part of Zerion’s protocol positions endpoint. The response includes accrued rewards alongside staked balances, so you can show users what’s claimable without them calling reward contracts directly. You also get position value in USD, ETH, BTC or any major fiat currency of your choice."
    }
  },{
    "@type": "Question",
    "name": "How to get Uniswap LP positions on multiple chains?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "In Zerion API, all Uniswap positions (and other DEX LPs) are included automatically in the position endpoint. The positions endpoint normalizes LP shares across supported chains (Ethereum, Arbitrum, Optimism, Base, etc.). One call gives you a wallet’s Uniswap LPs across all chains."
    }
  }]
}
</script>
<!--kg-card-end: html-->
<h2 id="tldr">TL;DR</h2><p>You can fetch a wallet’s complete DeFi positions (staking, LPs, collateral, debt, and rewards) across 8,000+ protocols and 26+ EVM chains with one call to Zerion API:</p><pre><code class="language-shell">curl --request GET \
     --url 'https://api.zerion.io/v1/wallets/address/positions/?filter[positions]=only_complex' 
</code></pre>
<ul><li><strong>Normalized and enriched:</strong> Returns positions with protocol names, logos, token breakdowns, USD values, and accrued rewards.</li><li><strong>Multichain:</strong> Works across all supported blockchains in a single call; filter by chain if needed.</li><li><strong>Easy integration:</strong> No need to parse smart contracts or maintain subgraphs, integrate in minutes, not weeks.</li><li><strong>Use cases:</strong> Wallets, portfolio apps, tax software, analytics dashboards, and AI agents.</li></ul><p>Zerion API makes it simple to add multichain DeFi tracking to your product with minimal engineering.</p><h2 id="what-%E2%80%9Cdefi-positions%E2%80%9D-actually-are-and-why-most-apis-get-messy">What “DeFi Positions” Actually Are (and Why Most APIs Get Messy)</h2><p>When people talk about a wallet’s DeFi positions, they usually mean more than just token balances. A position can be:</p><ul><li><strong>Liquidity pool (LP) shares</strong> — e.g., ETH/USDC in Uniswap</li><li><strong>Staked tokens</strong> — assets locked in staking contracts</li><li><strong>Lending collateral and debt</strong> — supplied and borrowed tokens in protocols like Aave or Morpho</li><li><strong>Unclaimed rewards</strong> — yield, incentives, or farming tokens accrued but not yet claimed</li></ul><p>The challenge is that these positions live inside different smart contracts, often with unique logic and token structures. Onchain, they appear as various contract calls, not clear “this wallet is staking 2 ETH in Lido.”</p><p>Most APIs that expose raw blockchain data (or even generic token balance endpoints) struggle here:</p><ul><li>They return contract storage values with no financial meaning.</li><li>They often cover only a few protocols and on just one chain.</li><li>Developers end up writing their own parsers or relying on subgraphs that need constant updates.</li></ul><p>But if you’re building your own product, you need an API that gives you that same interpreted view, with broad chain coverage and no maintenance overhead. That’s exactly where Zerion API comes in.</p><h2 id="zerion-api-in-one-minute">Zerion API in One Minute</h2><p>Zerion API gives developers the same data that is available to users in <a href="https://zerion.io/crypto-wallet-tracker" rel="noreferrer">Zerion portfolio tracker</a> and <a href="https://zerion.io/download" rel="noreferrer">Zerion Wallet</a>. It includes tokens, NFTs, transactions, and DeFi protocols across 26+ chains.&nbsp;</p><p>Leading wallets and apps like Uniswap, Base, Farcaster, Kraken, and many others use Zerion API to add rich onchain data to their user experiences.&nbsp;</p><p>For app developers, the biggest advantage of Zerion API is that with a single call it can deliver ready-to-use positions for 8,000+ DeFi protocols across dozens of EVM blockchains.&nbsp;</p><p>Zerion API requires no protocol-specific engineering or knowledge. Instead of spending weeks setting up indexers and parsing contracts or maintaining subgraphs, you get normalized, human-readable data in one call. Most builders integrate it in a day or two. </p><h2 id="quickstart-fetch-defi-protocols-in-10-lines">Quickstart: Fetch DeFi Protocols in ~10 Lines</h2><p>Fetching DeFi positons with Zerion API takes just a few steps: grab an API key, add it to your request header, and call the <a href="https://developers.zerion.io/reference/listwalletpositions"><u>positions endpoint</u></a> for a wallet address.</p><p>Here’s a minimal example in JavaScript that fetches only DeFi protocol positions for a wallet:</p><pre><code class="language-js">const options = {method: 'GET', headers: {accept: 'application/json'}};
fetch('https://api.zerion.io/v1/wallets/0x42b9df65b219b3dd36ff330a4dd8f327a6ada990/positions/?filter[positions]=only_complex&amp;currency=usd&amp;filter[trash]=only_non_trash&amp;sort=value', options)
  .then(res =&gt; res.json())
  .then(res =&gt; console.log(res))
  .catch(err =&gt; console.error(err));
</code></pre>
<p><strong>What this does:</strong></p><ul><li>Calls positions for <code>0x42b9df65b219b3dd36ff330a4dd8f327a6ada990</code></li><li>Applies <code>filter[positions]=only_protocol</code> to exclude simple token balances and return only protocol-level positions (staking, LPs, lending, etc.).</li><li>Returns a structured JSON response with protocol names, position types, underlying tokens, and USD values.</li></ul><p>From here, you can group positions by protocol, display them in a portfolio view, or use the data for analytics and risk checks in your dapp.</p><h2 id="filtering-shaping-the-response">Filtering &amp; Shaping the Response</h2><p>By default, Zerion API wallet positions endpoint will return:&nbsp;</p><ul><li><strong>Both token and DeFi protocol positions</strong>. If you want to get only DeFi positions, you can use the <code>only_complex</code> filter.&nbsp;</li><li><strong>Positions from all supported chains.</strong> If you’re only interested in specific blockchains, you can filter by chain IDs.&nbsp;</li><li><strong>USD values. </strong>You can change this to any major fiat currency, BTC, or ETH.&nbsp;&nbsp;</li></ul><p>Additionally, you can use <code>dapp_ids</code> to isolate positions for specific dapps/protocols. You can check the <a href="https://developers.zerion.io/reference/listdapps#/" rel="noreferrer">dapps endpoint</a> to see all supported dapps and protocols.</p><h2 id="interpreting-defi-protocols-for-your-product">Interpreting DeFi Protocols for Your Product</h2><p>Fetching DeFi positions is just the first step. The real value comes from how you use that data in your product. Zerion API is designed to make this easy by returning normalized positions enriched with protocol metadata, USD values, and underlying token breakdowns.</p><p>For example, here is how a Uniswap LP position looks in a response from Zerion API:&nbsp;</p><pre><code class="language-js">"type": "positions",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"id": "0x4200000000000000000000000000000000000006-base-uniswap v3 weth/usdc pool (#60321)-deposit",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"attributes": {
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"parent": null,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"protocol": "Uniswap V3",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"protocol_module": "liquidity_pool",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"pool_address": "0xd0b53d9277642d899df5c87a3966a349a798f224",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"group_id": "2e81724832654bbb9a66cae3f0d6405765b6b61f22351e368e7cfc2e565498b0",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"name": "Uniswap V3 WETH/USDC Pool (#60321)",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"position_type": "deposit",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"quantity": {
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"int": "47808488758558",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"decimals": 18,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"float": 0.0000478084887586,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"numeric": "0.000047808488758558"
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"value": 0.20808546747230408,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"price": 4352.479504700001,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"changes": {
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"absolute_1d": 0.0015173896221812588,
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"percent_1d": 0.7345712067293508
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"fungible_info": {
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"name": "Wrapped Ether",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"symbol": "WETH",
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"icon": {
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"url": "https://cdn.zerion.io/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2.png"
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"flags": {
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"verified": true
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},
</code></pre>
<p>As you can see, it’s ready to use in a product and doesn’t require additional work.&nbsp;</p><p>Here are a few common ways developers put this to work:</p><ul><li><strong>Portfolio apps and wallets. </strong>Show users exactly where their assets are deployed without them digging through multiple protocols. Because Zerion API already groups positions by protocol, you can present a clear overview with totals per dapp or chain.</li><li><strong>Risk and health monitoring. </strong>Lending positions include both supplied collateral and outstanding debt. You can use this data to calculate loan-to-value ratios or trigger health warnings inside your app.</li><li><strong>Analytics and dashboards. </strong>Position data can be aggregated across wallets to analyze protocol adoption, liquidity distribution, or market share. This is useful for research products or institutional tools.</li><li><strong>Tax and compliance software. </strong>By combining positions with transaction history, you can reconstruct cost basis, track staking income, or calculate unrealized gains for regulatory reporting.</li><li><strong>AI agents and alerts. </strong>Wallet positions can serve as “state,” while new transactions become “events.” This makes it easy to build bots or agents that notify users when their collateral ratio is risky or when rewards are ready to claim. Some projects like <a href="https://zerion.io/blog/askgina-ai-wallet-companion-built-with-zerion-api/" rel="noreferrer">Gina</a> and <a href="https://zerion.io/blog/how-loomlay-added-zerion-api-to-ai-agent-platform/" rel="noreferrer">LoomLay</a> give Zerion API endpoints to agents and let them pick the most relevant ones. </li></ul><p>In all these cases, Zerion API saves you from building protocol integrations yourself, letting you focus on product logic and user experience.</p><h2 id="use-case-examples">Use Case Examples</h2><p>Some of the best-known companies in crypto use Zerion API to fetch and show DeFi positions in their products or internal dashboards.&nbsp;</p><h3 id="wallet-defi-summary-view">Wallet DeFi Summary View</h3><p><a href="https://safe.global/" rel="noreferrer"><strong>Safe</strong></a><strong>, </strong>the biggest multisig wallet, uses Zerion API’s complex positions endpoint to show DeFi protocol positions across multiple chains.&nbsp;</p><figure class="kg-card kg-embed-card"><blockquote class="twitter-tweet"><p lang="en" dir="ltr">All Your DeFi. One Clear View. 👀<br><br>Safe{Wallet} just launched the cleanest DeFi portfolio view.<br>One dashboard. All your positions. No guesswork.<br><br> 🔥 What's new with Positions:<br>- Full DeFi visibility across protocols - <a href="https://twitter.com/aave?ref_src=twsrc%5Etfw">@aave</a> <a href="https://twitter.com/Kiln_finance?ref_src=twsrc%5Etfw">@Kiln_finance</a> <a href="https://twitter.com/MorphoLabs?ref_src=twsrc%5Etfw">@MorphoLabs</a> <a href="https://twitter.com/LidoFinance?ref_src=twsrc%5Etfw">@LidoFinance</a> and so much… <a href="https://t.co/MkWoIAASiE">pic.twitter.com/MkWoIAASiE</a></p>— Safe.eth (@safe) <a href="https://twitter.com/safe/status/1963603772103692404?ref_src=twsrc%5Etfw">September 4, 2025</a></blockquote>
<script async="" src="https://platform.twitter.com/widgets.js" charset="utf-8"></script></figure><h3 id="tax-software">Tax Software&nbsp;</h3><p><a href="https://www.waltio.com/" rel="noreferrer"><strong>Waltio</strong></a>, a leading crypto tax software, uses Zerion API’s wallet positions endpoints to fetch DeFi positions from multiple blockchains in a single call. Zerion’s robust data infrastructure allowed Waltio to offer detailed, reliable tax reporting and portfolio insights without additional blockchain infrastructure.</p><h3 id="analytics-and-dashboards">Analytics and dashboards</h3><p><a href="https://cmt.digital/" rel="noreferrer"><strong>CMT Digital</strong></a>, a leading global VC firm, uses Zerion’s complex positions endpoint to fetch a detailed DeFi portfolio for informed investment decisions.</p><hr><p>Whether you’re building a new product or want to add DeFi positions as a feature, Zerion API makes it very easy.</p><h2 id="get-started">Get Started</h2><p>Zerion API makes fetching DeFi positions across multiple blockchains simple — just use one call to fetch positions from 8,000+ protocols on 26, + EVM networks.&nbsp;</p><p>It’s also very easy to get started with Zerion API — just <a href="https://dashboard.zerion.io/?utm_source=blog&amp;utm_medium=article&amp;utm_campaign=defi_positions" rel="noreferrer">get your free API key</a>. The  dev key includes up to 2k requests per day, which should be enough to build a proof of concept.&nbsp;</p><p>Once you’re ready to deploy in production, you can upgrade to one of the monthly plans. If you need more scale, we’re always happy to hop on a call and discuss what you need.&nbsp;</p><hr><h2 id="faq">FAQ</h2><h3 id="why-is-it-so-hard-to-get-defi-positions-for-a-wallet-address">Why is it so hard to get DeFi positions for a wallet address?&nbsp;</h3><p>Because DeFi positions aren’t simple token balances. They live inside smart contracts with unique logic: staking vaults, LP pools, lending protocols, reward contracts. Raw onchain calls return low-level data without financial meaning. To interpret them, you’d normally need to parse each protocol’s contracts or maintain subgraphs. Zerion API solves this by returning normalized, human-readable positions in one call.</p><h3 id="how-to-get-defi-positions-from-multiple-chains">How to get DeFi positions from multiple chains?&nbsp;</h3><p>With Zerion API, you don’t need separate integrations. The GET https://api.zerion.io/v1/wallets/{address}/positions/ endpoint returns protocol positions across all supported EVM chains. You can filter by blockchain if you want a narrower view, or query once for a unified multichain portfolio.</p><h3 id="how-to-fetch-staked-token-positions">How to fetch staked token positions?&nbsp;</h3><p>Staked tokens are included in Zerion API’s protocol positions.</p><p>You can use <code>fetch('https://api.zerion.io/v1/wallets/address/positions/?filter[positions]=only_complex&amp;currency=usd&amp;filter[dapp_ids]=EXAMPLE_PROTOCOL)</code> Instead of <code>EXAMPLE_PROTOCOL</code> you specify the staking protocol, e.g. Aave or Morpho. This will return staking positions along with protocol metadata, token amount, and USD value.</p><h3 id="how-to-fetch-liquidity-pool-positions-for-a-wallet-address">How to fetch liquidity pool positions for a wallet address?&nbsp;</h3><p>Liquidity pool shares are also interpreted as protocol positions in Zerion API. The same positions endpoint with the “compex_only” filter will return LP positions, including underlying token breakdowns. You can use this to show both the pool share and its token composition in your app.</p><h3 id="how-to-get-staking-rewards-accrued-to-a-wallet-address">How to get staking rewards accrued to a wallet address?&nbsp;</h3><p>Unclaimed rewards (like yield or farming incentives) are part of Zerion’s protocol positions endpoint. The response includes accrued rewards alongside staked balances, so you can show users what’s claimable without them calling reward contracts directly. You also get position value in USD, ETH, BTC or any major fiat currency of your choice.&nbsp;&nbsp;</p><h3 id="how-to-get-uniswap-lp-positions-on-multiple-chains">How to get Uniswap LP positions on multiple chains?&nbsp;</h3><p>In Zerion API, all Uniswap positions (and other DEX LPs) are included automatically in the position endpoint. The positions endpoint normalizes LP shares across supported chains (Ethereum, Arbitrum, Optimism, Base, etc.). One call gives you a wallet’s Uniswap LPs across all chains.&nbsp;</p>
