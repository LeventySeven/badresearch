# AI Engineer transcript lane — measured on 2026-10-10 (the chair's own run, not agent output)

`yt.sh titles aiDotEngineer` with no limit returned 1268 titles; a generous regex picked 35 talks on agentic search vs embeddings/RAG; 13 of them sit inside a 400-title recency window, 22 outside it.
First pass at `xargs -P 4`: 15 of 35 walled. Three serial retries with 45 s pauses recovered 1 (21 via YouTube in all). The 14 still walled reported `UNVERIFIED_ABSENCE` — "a PO token was not provided"; an explicit tv_embedded/web_safari client also failed.
The conference's own pages, `https://ai.engineer/talks/<id>`, recovered 12 of the 14 (two returned a 142-word shell).

| position in channel list (1 = newest) | id | transcript via | title |
|---|---|---|---|
| 10 | k2ClBT4aqAg | unavailable | We Mapped 115 Microservices for Our Coding Agents — Kamalakannan Nandagopal, Postman |
| 23 | X4w2Pkz5tDY | unavailable | Grep or Embeddings? Agentic Search Over Company Documents — George He, LlamaIndex |
| 46 | T3SS931wU0I | ai.engineer | Agentic Search vs Vector Search for Coding Agents: We Ran the Eval — Braintrust |
| 49 | Bdrs3uAX0_M | ai.engineer | AI Coding Agents Are Breaking Big Codebases — Dan Adler, Sourcegraph |
| 54 | qflLT3SoVbw | ai.engineer | Stop Fine-Tuning to Fix Retrieval Problems — Anant Srivastava |
| 67 | cKhpeEBnT1o | ai.engineer | Your Coding Agent Is 6 Months Out of Date — Jakub Hojsan, Exa |
| 108 | RQi7x-navxU | ai.engineer | Building the Document Context Layer for AI Agents — Jerry Liu, LlamaIndex |
| 122 | iJVxxxHM_Oc | ai.engineer | Where RL Will Take Search — Maximilian-David Rumpf, SID.ai |
| 123 | V-isu4eTHgw | ai.engineer | Connect AI to Billions of Legal Documents — Simon Eskildsen, turbopuffer & Jacob Lauritzen, Legora |
| 128 | fZH97QHHYjY | youtube | The unreasonable effectiveness of BM25 for agentic search — Jo Kristian Bergum, Hornet.dev |
| 253 | WP3hjUXd918 | ai.engineer | Context Engineering in 2026 — Louis-François Bouchard, Omar Solano & Samridhi Vaid, Towards AI |
| 273 | aeTb5BdmTTc | ai.engineer | Agents, codebases, and teams — Aditya Khandelwal, Amazon AGI Lab |
| 281 | 7vn4WpqNpck | youtube | Benchmarking Coding Agents on New vs Legacy Codebases — Denys Linkov, Wisedocs |
| 423 | 8oyalrfwgjw | ai.engineer | RLM: Recursive Language Models for Large Codebases - Shashi, Superagentic AI |
| 454 | 1IdzkRVmWAA | youtube | How we taught agents to use good retrieval - Hanna Lichtenberg, Mixedbread AI |
| 478 | dRmWYHuIJxM | youtube | We Cut 94% of AI Coding Tokens With a Local Code Index - Rajkumar Sakthivel, Tesco |
| 514 | UM6sFg_jdlE | youtube | RAG is dead, right?? — Kuba Rogut, Turbopuffer |
| 533 | zKk7sDMGDEQ | youtube | Benchmarking semantic code retrieval on Claude Code — Kuba Rogut, Turbopuffer |
| 612 | ynJyIKwjonM | youtube | Agentic Search for Context Engineering — Leonie Monigatti, Elastic |
| 700 | RFKCzGlAU6Q | ai.engineer | How Claude Code Works - Jared Zoneraich, PromptLayer |
| 706 | ShuJ_CN6zr4 | youtube | Making Codebases Agent Ready – Eno Reyes, Factory AI |
| 721 | tHN44yJoeS8 | youtube | Coding Evals: From Code Snippets to Codebases – Naman Jain, Cursor |
| 738 | rmvDxxNubIg | youtube | No Vibes Allowed: Solving Hard Problems in Complex Codebases – Dex Horthy, HumanLayer |
| 740 | fL1iJHtl51Q | youtube | Building Cursor Composer – Lee Robinson, Cursor |
| 803 | W1MiZChnkfA | youtube | Scaling Enterprise-Grade RAG: Lessons from Legal Frontier - Calvin Qi (Harvey), Chang She (Lance) |
| 805 | w9u11ioHGA0 | youtube | Layering every technique in RAG, one query at a time - David Karam, Pi Labs (fmr. Google Search) |
| 922 | Lue8K2jqfKk | youtube | Claude Code & the evolution of agentic coding — Boris Cherny, Anthropic |
| 941 | 6NIr_cYPglk | youtube | To the moon! Navigating deep context in legacy code with Augment Agent — Forrest Brazeal, Matt Ball |
| 951 | YrUBFXa1KUY | youtube | Vector Search Benchmark[eting] - Philipp Krenn, Elastic |
| 966 | W_CYk2ogcDI | youtube | RAG in 2025: State of the Art and the Road Forward — Tengyu Ma, MongoDB (acq. Voyage AI) |
| 967 | pIPtpBZ6TKk | youtube | The State of AI Powered Search and Retrieval — Frank Liu, MongoDB (prev Voyage AI) |
| 980 | jUv5WSPo9fk | ai.engineer | The Eyes Are The (Context) Window to The Soul: How Windsurf Gets to Know You — Sam Fertig, Windsurf |
| 1070 | kPL-6-9MVyA | youtube | RAG Agents in Prod: 10 Lessons We Learned — Douwe Kiela, creator of RAG |
| 1221 | DuZXbinJ4Uc | youtube | How Codeium Breaks Through the Ceiling for Retrieval: Kevin Hou |
| 1254 | YvobVu1l7GI | youtube | The Hidden Life of Embeddings: Linus Lee |
