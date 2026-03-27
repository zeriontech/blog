---
title: "Solana Webhooks with Zerion API: A Guide for Real-Time Transaction Alerts"
slug: solana-webhooks-zerion-api-real-time-transaction-alerts
date: 2025-10-17
published_at: 2025-10-17T16:24:42.000Z
feature_image: https://zerion.io/blog/content/images/2025/10/Solana-webhooks.png
authors:
  - name: Vladimir Shamanov
    slug: vladimir
    avatar: https://zerion.io/blog/content/images/2026/01/c08b6248-334a-4749-8808-a28f8ddf58ce-1.png
tags:
  - Zerion API
  - Solana
excerpt: "Real-time matters on Solana. Wallets, portfolio trackers, SocialFi apps, and onchain agents all need to know and listen to new transactions and react instantly. Zerion API now supports transaction…"
---

<p>Real-time matters on Solana. Wallets, portfolio trackers, SocialFi apps, and onchain agents all need to know and listen to new transactions and react instantly. Zerion API now supports <strong>transaction webhooks for Solana</strong>, giving you push-style updates without polling. It follows the same schema as for EVM, letting you use the same tool for both Ethereum and Solana ecosystems.&nbsp;</p><p>Below you’ll find a production-ready walkthrough: how webhooks work, how to create subscriptions to Solana addresses, and how to manage subscriptions over time.</p><div class="kg-card kg-cta-card kg-cta-bg-grey kg-cta-immersive    " data-layout="immersive">
            
                <div class="kg-cta-sponsor-label-wrapper">
                    <div class="kg-cta-sponsor-label">
                        <span style="white-space: pre-wrap;">TL;DR</span>
                    </div>
                </div>
            
            <div class="kg-cta-content">
                
                
                    <div class="kg-cta-content-inner">
                    
                        <div class="kg-cta-text">
                            <p><span style="white-space: pre-wrap;">Create real-time transaction webhooks for Solana wallets via Zerion API. Delivery is push (no polling), using a unified schema across EVM + Solana. Use </span><b><code spellcheck="false" style="white-space: pre-wrap;"><strong>https://api.zerion.io/v1/tx-subscriptions/</strong></code></b><span style="white-space: pre-wrap;"> with </span><b><code spellcheck="false" style="white-space: pre-wrap;"><strong>addresses</strong></code></b><span style="white-space: pre-wrap;">, </span><b><code spellcheck="false" style="white-space: pre-wrap;"><strong>callback_url</strong></code></b><span style="white-space: pre-wrap;">, and </span><b><code spellcheck="false" style="white-space: pre-wrap;"><strong>chain_ids: ["solana"]</strong></code></b><span style="white-space: pre-wrap;">. You can start with a dev key and webhook.site.&nbsp;</span></p>
                        </div>
                    
                    
                        <a href="https://zerion-io.typeform.com/zerionforsolana?utm_source=blog&amp;utm_medium=article&amp;utm_campaign=Solana-webhooks" class="kg-cta-button " style="background-color: #000000; color: #ffffff;">
                            Get free dev keys
                        </a>
                        
                    </div>
                
            </div>
        </div><h2 id="why-solana-webhooks">Why Solana webhooks?</h2><p>Polling Solana for new activity across many addresses can be wasteful and brittle.&nbsp;</p><p>Zerion’s webhook system listens to onchain activity, normalizes it into a merged EVM/Solana schema, and pushes a signed notification to your endpoint as soon as the transaction is seen and classified. That’s the same infrastructure that powers Zerion’s own app notifications. It’s now available for your app via Zerion's <a href="https://zerion.io/solana-api" rel="noreferrer">Solana API</a>.</p><h2 id="how-it-works">How it works</h2><p>Here's a quick overview of how Zerion's Solana webhooks work. </p><ol><li><strong>Zerion indexers. </strong>Observes Solana blocks/transactions, applies spam filtering and normalization to a unified transaction model for Solana and EVM. </li><li><strong>Webhook dispatch. </strong>When a subscribed address transacts, Zerion sends a signed POST to your <code>callback_url</code>. Delivery order is not guaranteed, and after 3 failed attempts, dispatch stops for that event.</li><li><strong>Your server. </strong>Verifies signature headers, processes the JSON payload, and triggers app logic (notify user, refresh positions, update feed, run an agent, etc.).</li><li><strong>Enrichment. </strong>If you need price/value immediately, fetch the transaction by hash with Zerion API’s transactions endpoint.&nbsp;</li></ol><h2 id="create-a-solana-subscription">Create a Solana subscription</h2><p>You can mirror the example from our earlier <a href="https://zerion.io/blog/how-to-create-real-time-ethereum-transaction-notifications-with-zerion-api/" rel="noreferrer">guide to Ethereum transaction notifications</a>. Just pass Solana addresses and <code>chain_ids: ["solana"]</code>. Here’s a minimal curl: </p><pre><code class="language-bash">
curl --request POST \
     --url https://api.zerion.io/v1/tx-subscriptions/ \
     --header 'accept: application/json' \
     --header 'authorization: Basic emtfZGV2X2Q2YmEzYzM3NTNiYjQ2NWM4YjNjZTEzMTU2OTVlYjMwOg==' \
     --header 'content-type: application/json' \
     --data '
{
  "addresses": [
    "8BH9pjtgyZDC4iAQH5ZiYDZ1MDWC98xki2V8NzqqKW3K"
  ],
  "callback_url": "https://webhook.site/a1197f43-1522-4689-bbbb-5e7dcc3b346e"
}
'
</code></pre>
<p>Use <a href="https://webhook.site/" rel="noreferrer">webhook.site</a> for quick testing. Custom callback hosts must be approved. With a dev key, you get 1 subscription, 5 wallets max, 1-week validity. For production, request host whitelisting and long-lived subs—just <a href="https://zerion-io.typeform.com/zerionforsolana?utm_source=blog&amp;utm_medium=article&amp;utm_campaign=Solana-webhooks" rel="noreferrer">get your free dev keys</a> first and ask by email.&nbsp;</p><p>The same endpoint can be used for watching Solana and EVM addresses. Solana simply uses <strong><code>chain_ids: ["solana"]</code></strong>. But you don’t need to specify it because for a Solana address, you would only get Solana transactions.&nbsp;</p><p>Here is an example of a POST response in webhook.site:</p>
<!--kg-card-begin: html-->
<pre style="max-height:500px; overflow-y:auto; background:#1e1e1e; color:#dcdcdc; padding:1em; border-radius:8px; white-space:pre;">
<code style="white-space:pre;">
{
  "data": {
    "attributes": {
      "address": "8BH9pjtgyZDC4iAQH5ZiYDZ1MDWC98xki2V8NzqqKW3K",
      "callback_url": "https://webhook.site/a1197f43-1522-4689-bbbb-5e7dcc3b346e",
      "timestamp": "2025-10-16T10:56:50.047643374Z"
    },
    "id": "bf300927-3f57-4d00-a01a-f7b75bd9b8de",
    "relationships": {
      "subscription": {
        "id": "61f13641-443e-4068-932b-c28edeaefd85",
        "type": "tx-subscriptions"
      }
    },
    "type": "callback"
  },
  "included": [
    {
      "attributes": {
        "acts": [
          {
            "application_metadata": {
              "contract_address": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
              "icon": {
                "url": "https://protocol-icons.s3.amazonaws.com/icons/jupiter.jpg"
              },
              "name": "Jupiter"
            },
            "id": "0",
            "type": "trade"
          }
        ],
        "application_metadata": {
          "contract_address": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
          "icon": {
            "url": "https://protocol-icons.s3.amazonaws.com/icons/jupiter.jpg"
          },
          "name": "Jupiter"
        },
        "approvals": [],
        "fee": {
          "fungible_info": {
            "flags": {
              "verified": true
            },
            "icon": {
              "url": "https://cdn.zerion.io/11111111111111111111111111111111.png"
            },
            "implementations": [
              {
                "address": "11111111111111111111111111111111",
                "chain_id": "solana",
                "decimals": 9
              }
            ],
            "name": "Solana",
            "symbol": "SOL"
          },
          "price": 196.45239612519998,
          "quantity": {
            "decimals": 9,
            "float": 0.000005,
            "int": "5000",
            "numeric": "0.000005000"
          },
          "value": 0.000982261980626
        },
        "flags": {
          "is_trash": false
        },
        "hash": "i5hptq3Dx8mbuAY5SuF5mUz7mTrAQYmwrJSrdUC4L1MJEkxsXDgSVt9to6HU8EcNygoLnhD7ut11r3mAQafP6Gx",
        "mined_at": "2025-10-16T10:56:48Z",
        "mined_at_block": 0,
        "nonce": 0,
        "operation_type": "trade",
        "sent_from": "8BH9pjtgyZDC4iAQH5ZiYDZ1MDWC98xki2V8NzqqKW3K",
        "sent_to": "",
        "status": "confirmed",
        "transfers": [
          {
            "act_id": "0",
            "direction": "in",
            "fungible_info": {
              "flags": {
                "verified": true
              },
              "icon": {
                "url": "https://cdn.zerion.io/0xdac17f958d2ee523a2206206994597c13d831ec7.png"
              },
              "implementations": [
                {
                  "address": "0xbb06dca3ae6887fabf931640f67cab3e3a16f4dc",
                  "chain_id": "metis-andromeda",
                  "decimals": 6
                },
                {
                  "address": "0xf55bec9cafdbe8730f096aa55dad6d22d44099df",
                  "chain_id": "scroll",
                  "decimals": 6
                },
                {
                  "address": "0x6386da73545ae4e2b2e0393688fa8b65bb9a7169",
                  "chain_id": "zero",
                  "decimals": 6
                },
                {
                  "address": "0x55d398326f99059ff775485246999027b3197955",
                  "chain_id": "binance-smart-chain",
                  "decimals": 18
                },
                {
                  "address": "0x816e810f9f787d669fb71932deabf6c83781cd48",
                  "chain_id": "gravity-alpha",
                  "decimals": 6
                },
                {
                  "address": "0xfde4c96c8593536e31f229ea8f37b2ada2699bb2",
                  "chain_id": "base",
                  "decimals": 6
                },
                {
                  "address": "0x588ce4f028d8e7b53b687865d6a67b3a54c75518",
                  "chain_id": "unichain",
                  "decimals": 6
                },
                {
                  "address": "0x1e4a5963abfd975d8c9021ce480b42188849d41d",
                  "chain_id": "polygon-zkevm",
                  "decimals": 6
                },
                {
                  "address": "0xf0f161fda2712db8b566946122a5af183995e2ed",
                  "chain_id": "mode",
                  "decimals": 6
                },
                {
                  "address": "0x6047828dc181963ba44974801ff68e538da5eaf9",
                  "chain_id": "sonic",
                  "decimals": 6
                },
                {
                  "address": "0x1e4a5963abfd975d8c9021ce480b42188849d41d",
                  "chain_id": "okbchain",
                  "decimals": 6
                },
                {
                  "address": "0x48065fbbe25f71c9282ddf5e1cd6d6a887483d5e",
                  "chain_id": "celo",
                  "decimals": 6
                },
                {
                  "address": "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58",
                  "chain_id": "optimism",
                  "decimals": 6
                },
                {
                  "address": "0x493257fd37edb34451f62edf8d2a0c418852ba4c",
                  "chain_id": "zksync-era",
                  "decimals": 6
                },
                {
                  "address": "0x4ecaba5870353805a9f068101a40e0f32ed605c6",
                  "chain_id": "xdai",
                  "decimals": 6
                },
                {
                  "address": "0x4988a896b1227218e4a686fde5eabdcabd91571f",
                  "chain_id": "aurora",
                  "decimals": 6
                },
                {
                  "address": "0x0709f39376deee2a2dfc94a58edeb2eb9df012bd",
                  "chain_id": "abstract",
                  "decimals": 6
                },
                {
                  "address": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
                  "chain_id": "solana",
                  "decimals": 6
                },
                {
                  "address": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
                  "chain_id": "avalanche",
                  "decimals": 6
                },
                {
                  "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
                  "chain_id": "ethereum",
                  "decimals": 6
                },
                {
                  "address": "0xf417f5a458ec102b90352f697d6e2ac3a3d2851f",
                  "chain_id": "manta-pacific",
                  "decimals": 6
                }
              ],
              "name": "Tether USD",
              "symbol": "USDT"
            },
            "price": 1.0005395552,
            "quantity": {
              "decimals": 6,
              "float": 0.980106,
              "int": "980106",
              "numeric": "0.980106"
            },
            "recipient": "8BH9pjtgyZDC4iAQH5ZiYDZ1MDWC98xki2V8NzqqKW3K",
            "sender": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
            "value": 0.9806348212888513
          },
          {
            "act_id": "0",
            "direction": "out",
            "fungible_info": {
              "flags": {
                "verified": true
              },
              "icon": {
                "url": "https://cdn.zerion.io/11111111111111111111111111111111.png"
              },
              "implementations": [
                {
                  "address": "11111111111111111111111111111111",
                  "chain_id": "solana",
                  "decimals": 9
                }
              ],
              "name": "Solana",
              "symbol": "SOL"
            },
            "price": 196.45239612519998,
            "quantity": {
              "decimals": 9,
              "float": 0.005,
              "int": "5000000",
              "numeric": "0.005000000"
            },
            "recipient": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
            "sender": "8BH9pjtgyZDC4iAQH5ZiYDZ1MDWC98xki2V8NzqqKW3K",
            "value": 0.9822619806259999
          }
        ]
      },
      "id": "13de850a-bfa4-54c7-a7bb-fd6371d98894",
      "relationships": {
        "chain": {
          "id": "solana",
          "type": "chains"
        },
        "dapp": {
          "id": "jupiter",
          "type": "dapps"
        }
      },
      "type": "transactions"
    }
  ]
}
  </code></pre>

<!--kg-card-end: html-->
<h2 id="manage-subscriptions-over-time">Manage subscriptions over time</h2><p>As your product evolves, you can modify subscriptions without recreating them:</p><ul><li><a href="https://developers.zerion.io/reference/findwallettransactionssubscription#/" rel="noreferrer"><strong>List all subscriptions</strong></a> or <a href="https://developers.zerion.io/reference/getwallettransactionssubscription#/" rel="noreferrer">fetch by ID</a> to introspect settings,</li><li><a href="https://developers.zerion.io/reference/enablesubscription#/" rel="noreferrer"><strong>Enable</strong></a><strong> or </strong><a href="https://developers.zerion.io/reference/disablesubscription#/" rel="noreferrer"><strong>disable</strong></a> a subscription (pause without deleting),</li><li><a href="https://developers.zerion.io/reference/updatecallbackurlinsubscription#/" rel="noreferrer"><strong>Update the callback URL</strong></a> safely,</li><li><strong>Replace or </strong><a href="https://developers.zerion.io/reference/patchsubscribedwalletsinsubscription#/" rel="noreferrer"><strong>patch wallets</strong></a> within a subscription to track new addresses (e.g., users who opt into notifications),</li><li><a href="https://developers.zerion.io/reference/updatechainidsinsubscription#/" rel="noreferrer"><strong>Change chains</strong></a> via <strong><code>chain_ids</code></strong>—you can expand to specific chains in addition to Solana. Zerion API covers mainnet Ethereum, Base, BSC, and all the main EVM chains.&nbsp;</li></ul><h2 id="production-notes-and-best-practices">Production notes and best practices</h2><p>Here are a few things to keep in mind for your implementation of Solana webhooks:&nbsp;</p><ul><li><strong>Ordering:</strong> Don’t assume webhook order equals onchain order.</li><li><strong>Retries:</strong> Zerion retries up to 3 times per event; after that, it stops. Monitor logs and build a reconciliation job that backfills missed events by time window if needed.</li><li><strong>Spam &amp; UX:</strong> Use webhook events to instantly refresh balances/positions in your UI and surface only meaningful transfers (the unified schema + Zerion’s spam filtering helps).</li><li><strong>Scope:</strong> Keep <code><strong>chain_ids</strong></code> to <code>["solana"]</code> for fastest Solana-first launches. Extend to EVM later with the same payload model.</li></ul><h2 id="common-solana-use-cases">Common Solana use cases</h2><p>Solana webhooks are useful in many cases.&nbsp;</p><ul><li><strong>Wallet &amp; super-app notifications:</strong> Create pushes for confirmed and failed transactions, fees, or DEX trades.</li><li><strong>Social/copy trading feeds:</strong> Follow specific wallets and publish activity streams in near-real time.</li><li><strong>Agentic workflows:</strong> Trigger actions when your agent’s Solana address receives funds or completes an instruction.</li><li><strong>Compliance/monitoring:</strong> Pipe transactions into your alerting stack instantly.</li></ul><h2 id="get-started">Get started</h2><p>You’ve now learned how Solana webhooks work in <a href="https://zerion.io/api" rel="noreferrer">Zerion API</a>. It’s time to put into action.&nbsp;</p><p><a href="https://zerion-io.typeform.com/zerionforsolana?utm_source=blog&amp;utm_medium=article&amp;utm_campaign=Solana-webhooks" rel="noreferrer"><strong>Request your free dev keys</strong></a>—and get $2,500 in free credits while Zerion’s Solana API is in early access.&nbsp;</p><p>If you need help or want us to review your setup, reply in the #devs-lounge on <a href="http://zerion.io/discord" rel="noreferrer">Discord</a> or ping the API team via the docs.</p>
