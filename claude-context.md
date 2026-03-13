# Claude Context: Course Notebooks and Main Idea

Course context for Claude (e.g., Claude Desktop) that lacks access to the notebooks. Summarizes what was done in each relevant week and how it connects to the main idea (adversarial committees, student development, harmlessness, mechanical use prevention). Focus only on material relevant to the final project.

---

## 1.1 Course Requirements (from instructions.md)

- **Data:** At least three forms of data in a single model
- **Models:** At least three types of models from three separate weeks
- **Validation:** Qualitative interpretation and assessments of inferences or predictions
- **Blog:** 3600 words, 13 figures (single author); presentation: 5 min, 20 slides
- **Deliverables:** Public-facing blog post (Substack/Medium), annotated code appendix, open GitHub or Colab repository; presentation slides

---

## 1.2 Week-by-Week Summary (Relevant Only)

**Explicit tools and architecture per module** — These are course assessments meant to be implemented on our end without depending on paid APIs, or minimal dependency (like with GPT4 for chat proofs). Document the libraries, models, and patterns used so the project can be built with free models and open-source tools:

| Week | Source | What Was Done | Tools & Architecture (Free Models) |
|------|--------|---------------|-----------------------------------|
| **Week 3** | Week_3.ipynb | Multi-agent simulation, agent roles | Custom agent loops or LangGraph; agent roles via system prompts; no API required—can use local Qwen/Llama |
| **Week 6** | week6_2026.ipynb, macs_thesis_corpus | MACSS corpus, embeddings, methodology | **Harvest:** `httpx` + `xml.etree.ElementTree` for OAI-PMH (`ListRecords`, `resumptionToken`); **Scraper:** `httpx` + `BeautifulSoup` for HTML fallback; **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`; **Methodology:** `infer_methodology(title, abstract)` via keyword matching (computational/quantitative/qualitative); **Steering:** TransformerLens + GPT-2 Small for SAE (optional) |
| **Week 7** | Week_7_RL.ipynb | GRPO, societies of thought, multi-agent RL | **GRPO:** `trl` or custom implementation; **Models:** DeepSeek-R1, QwQ-32B, or Llama; **Concepts:** group-relative baseline, no critic; **Deliberation:** multi-persona SFT on debate transcripts; **Societies of thought:** perspective shifts, conflict-reconciliation in reasoning traces |
| **Week 8** | Week_8_Multimodal, memo_w8 | Multimodal skill-diagnostic advisor | **VLM:** Qwen3-VL-8B (`transformers` `AutoModelForImageTextToText`); **ReAct:** Think–Look–Reason–Act loop; **Personas:** Skill Diagnostician, Theorist, Methodologist, Bias Auditor via system prompts; **LangGraph:** `langgraph` for agent graphs (week8 requirements) |
| **Week 9** | Week_9.ipynb, memo_w9 | Skill Diagnostician, Adversarial Critic, Harmlessness Monitor | **LLM:** `Qwen/Qwen2.5-7B-Instruct` (4-bit via `BitsAndBytesConfig`); **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`; **Generation:** `tokenizer.apply_chat_template` + `model.generate`; **Safety:** LLM-as-judge (same Qwen) with `SAFETY_JUDGE_PROMPT`; **AGrail:** optional guardrail with local Qwen backend; **RepE:** `extract_hidden_states`, `steer_generate` with PyTorch forward hooks (optional) |

---

## 1.3 Key Code Patterns from Notebooks

- **Skill Diagnostician:** `skill_diagnostician(thesis)` → 1–2 Socratic questions; prompt targets research skill gaps
- **Adversarial Critic:** `adversarial_critic(thesis, questions)` → targeted critique; uses diagnostician output
- **Harmlessness Monitor:** `harmlessness_monitor(critique, condition)` → LLM-as-judge (`judge_safety_llm`), soften if unsafe, optional visible label
- **Digital doubles:** thesis + condition + trust_sensitivity + methodology
- **Mechanical reliance:** cosine similarity between revision and pure-LLM baseline
- **Trust/Quality:** LLM-rated (1–5)

---

## 1.4 Data Sources Available

- **MACSS theses:** UChicago Knowledge repository, OAI-PMH or HTML scraper; schema: id, url, title, abstract, author, year, methodology
- **GitHub memos:** Course repo "Week N Memo" issues; comments with memo_text, week, author, reactions; used for longitudinal validation
- **Sample abstracts:** Fallback when corpus missing

---

## 1.5 Connection to Adversarial Deliberative Committees Plan

- **Diagnosis:** Extend current Skill Diagnostician to 6 PISA-adapted dimensions (argument construction, evidence evaluation, methodological reasoning, theoretical integration, self-reflexivity, receptivity to critique)
- **Committee:** Current setup = 1 diagnostician + 1 critic; plan adds persona pool (Methodologist, Theorist, Devil's Advocate, Encourager, Generalist) and personalized assembly
- **Output:** Current = feedback → revision; plan = development plan (gap map, exercises, trajectory) — structural anti–mechanical-use
- **Conditions:** Current = 3 (committee_only, silent_monitor, visible_label); plan = 4 (single, homogeneous, random adversarial, prescribed adversarial) — can map C1 ≈ single, C4 ≈ prescribed
- **Simulated students:** Current = trust_sensitivity (low/high); plan = 5 profiles (Passive Accepter, Defensive Arguer, etc.) — extend DoublesLoader
