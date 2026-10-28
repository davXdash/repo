# Agent selection and link tools

Dave’s catalog keeps all source offers and their EUR reference prices available, independently of the preferred agent. On the first successful unlock a chooser asks which agent to use. The choice is stored locally and can be changed from the toolbar. Existing filters, wishlists, exclusions and separate agent hauls remain available.

The preferred agent controls the primary opening links on cards and in product details. A genuine existing source offer for that agent keeps its original link and price. Otherwise, the site converts the underlying Weidian, Taobao or 1688 product ID and leaves the target-agent price unknown. Converted links can be added to that agent’s haul with an unknown price; the source agent’s price is never assigned to the converted offer. Generated links do not insert affiliate codes. Original source offers and attribution are retained.

Supported targets: USFans, Litbuy, Pikobuy, Kakobuy, CNFans, Mulebuy, Hipobuy, Joyagoo, Oopbuy, Gtbuy and Ossbuy. Unsupported or unrecognized product URLs fall back to their original source rather than inventing an ID.

Tools includes a local link converter, lookup of the cheapest known source offers for the exact product ID, and explicitly external ASMRHauler QC, parcel tracking and shipping tools. Tracking codes are not automatically sent anywhere by Dave’s page.

## Observed source behavior, 28 October 2026

- https://agentlinks.de/de/usfans switches to a corresponding `/de/litbuy/...` route while retaining the product’s internal ID.
- https://agentlinks.de/en/tools/converter generated agent links for actual Taobao product 844978413180 and 1688 product 950518363279. USFans uses numeric route 2 for Taobao and 1 for 1688; existing USFans source links use 3 for Weidian. Other targets expose literal platforms or an embedded seller URL.
- https://asmrhauler.com/ exposes QC, converter, parcel tracking and shipping tools. Its public `/api/products` returns offset-based pagination and a total of 5824 products during this inspection. Its product prices are displayed in USD.
- https://docs.google.com/spreadsheets/d/1Tz9bH3g0ZWcNhA646jNddF_qrQbE_iJ9tY7IuJ2SjbY/edit is titled Theswagagenda Spreadsheet. It is a separate source from ASMRHauler. The import found 2438 distinct named product records, with no missing source prices or source images and no failed tabs. The 27 unassigned links are registrations or blank duplicate rows; the two product IDs appearing there are also retained from named product rows.

Link conversion is not a live target-agent quote or a guarantee of availability or anonymous access. Provider login requirements remain provider-controlled. Automated shipping comparison is unchanged and remains explicitly incomplete.
