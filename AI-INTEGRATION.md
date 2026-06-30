# AI Integration — Build Plan

How the AI/LLM work is layered into this project, sequenced from highest signal-per-effort to capstone. The goal is to move from "I called an LLM API" (which collapses under one interview question) to "I engineered, measured, and red-teamed an AI system." Every keyword you claim from this should be one you can defend in a 30-second follow-up.

This plan folds into the existing `surveillance/BUILD-PLAN.md` — it doesn't replace it. The base surveillance agent (surveillance M4) is the prerequisite for everything here. Don't start these until the rule-based detector + a working single-shot LLM agent exist and you trust their output.

## Guiding principle

Lead with **evaluation and agentic behavior**, not "I used Claude/GPT." Anyone can call an API. What's scarce — and what hiring filters plus a human interviewer are actually probing for — is someone who built an AI system, measured whether it worked, and hardened it. Build in that order.

---

## Stage 1 — Make the agent agentic (tool use / function calling)

**What:** Instead of feeding the agent a flagged event + context in one prompt, give it tools and let it decide what to investigate before writing its report.

Tools to expose to the agent:

- `get_actor_order_history(actor_id, window)` — recent orders/cancels for an actor
- `get_order_to_trade_ratio(actor_id, window)` — the headline manipulation metric
- `fetch_book_snapshot_at(timestamp)` — order book state at a point in time
- `get_cancel_timing(actor_id)` — how fast this actor cancels after placing

**Why it matters:** this is the difference between "an LLM call" and "an AI agent with tool use" — which is what nearly every posting means by "agentic AI." It also mirrors how a real surveillance analyst works (pull the threads that look suspicious), so it demos naturally.

**Keywords earned (honestly):** LLM agents, tool use / function calling, agentic workflows.

**Build notes:** define each tool as a typed function the agent can call; the agent loop is call → tool result → reason → maybe call again → final structured report. Cap the number of tool-call iterations so it can't loop forever. Log the full tool-call trace — it's great demo material and shows the agent's "reasoning path."

---

## Stage 2 — Ground reports in real typologies (retrieval / RAG)

**What:** Build a small knowledge base of manipulation typologies (sourced from the SEC/FCA enforcement cases you're already reading for the bots — see `docs/LEARNING-RESOURCES.md`). When the agent writes a report, it retrieves the closest-matching documented typology to cite.

**Why it matters:** lets you legitimately say "retrieval-augmented," and it sharpens output — the agent grounds its reasoning in documented patterns instead of improvising. Citing a real typology ("this matches the layering pattern described in [case]") is exactly what a compliance report should do.

**Keywords earned:** RAG, retrieval-augmented generation, embeddings/vector search.

**Build notes:** keep it small and honest — a handful of well-summarized typologies in a vector store is enough to demonstrate the technique. Don't over-build the retrieval infra; the point is the pattern, not a production search engine. (You already have embedding/vector experience from your Obsidian MCP setup — reuse that mental model.)

---

## Stage 3 — LLM evaluation harness (the most underrated one)

**What:** Extend the precision/recall harness you're already building for the rule-based detector to also score the **LLM agent's** judgments against ground-truth bot labels. Does the agent correctly identify _which_ manipulation type? Are its explanations accurate? Tune prompts against that number.

**Why it matters:** This is the single most credible AI line you can put on a CV, because it shows rigor instead of vibes. "LLM evaluation" experience is in genuinely short supply — it's what separates someone who _used_ an LLM from someone who can be trusted to _ship_ one. When an interviewer asks "how did you know it worked?", you have a real answer.

**Keywords earned:** LLM evaluation, eval harness, prompt engineering (because now your prompt iteration is measured, not guessed).

**Build notes:** define what "correct" means up front — e.g. correct typology classification (a confusion matrix against bot labels) and explanation quality (a rubric, possibly LLM-as-judge with a spot-check by you). Track the metric across prompt versions so you can show "v1 → v3 improved typology accuracy from X% to Y%." Keep recorded test cases in the repo.

---

## Stage 4 — Expose as an MCP server

**What:** Wrap the surveillance system's queries (the Stage 1 tools, plus report generation) as an MCP server, so any MCP-capable LLM client can investigate trading anomalies through a standard interface.

**Why it matters:** Ties directly into your existing MCP work and is current + differentiated — very few candidates have it. The line is: "I built an MCP server that lets an LLM agent query and reason over live exchange surveillance data."

**Keywords earned:** MCP (Model Context Protocol), AI tooling/integration, standard interfaces for LLM agents.

**Build notes:** the Stage 1 tools are most of the work already — MCP is mostly about exposing them over the protocol's interface. See the `mcp-builder` patterns if you want a reference for structuring a clean server. Keep tool descriptions tight and well-typed; that's what makes the server actually usable by an agent.

---

## Stage 5 — Adversarial agent (capstone / AI red-teaming)

**What:** An agent that, given knowledge of your detection rules, tries to craft order sequences that achieve a manipulative goal _while staying under your thresholds_. You then harden the detectors against what it finds, and iterate. This is `surveillance/BUILD-PLAN.md` Part 4 / M5.

**Why it matters:** A closed-loop adversarial system that attacks and then strengthens its own defenses is genuine AI red-teaming — and maps one-to-one onto your AI Red Teamer study track. This is your capstone AI story.

**Keywords earned:** AI red-teaming, adversarial testing, robustness evaluation.

**Build notes:** build this LAST. You can't measure evasion against a detector you don't trust, so Stages 1-3 (especially the eval harness) must be solid first. Frame each round as: adversary finds a gap → you quantify it → you patch the detector → you re-measure. That measured loop _is_ the story.

---

## Sequencing summary

| Stage                | Adds                               | Prerequisite                              |
| -------------------- | ---------------------------------- | ----------------------------------------- |
| 1 — Agentic tool use | LLM agents, function calling       | base surveillance agent (surveillance M4) |
| 2 — RAG grounding    | retrieval, embeddings              | Stage 1                                   |
| 3 — Eval harness     | LLM evaluation, prompt engineering | detector + agent both working             |
| 4 — MCP server       | MCP, AI integration                | Stage 1 tools exist                       |
| 5 — Adversary        | AI red-teaming                     | Stages 1-3 solid (esp. eval)              |

## The honesty rule (re-stated, because it matters most here)

Add each keyword to your LinkedIn skills and project description **only once the corresponding stage actually exists and you can explain it.** Hiring filters get you in the door; a human asks "walk me through your eval harness" thirty seconds later. Keyword-stuffing you can't back up is the fastest way to fail. Everything in this plan is defensible _if you build it_ — so build it, then claim it.
