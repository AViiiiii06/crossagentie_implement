# ==========================================================
# RELATION EXTRACTION PROMPTS (SEMANTIC + EXPLORATIVE)
# FULL SENTENCE SCANNING — STRICT JSON-ONLY OUTPUT
# ==========================================================


# ----------------------------------------------------------
# KILL RELATION
# ----------------------------------------------------------

KILL_RELATION_PROMPT = """
System Message:
You are an advanced Relation Extraction agent for the relation "Kill".
Your job is to read the ENTIRE sentence and extract ALL Kill relations,
even when expressed indirectly or through paraphrased language.

You must use SEMANTIC understanding, meaning-level cues, not only keywords.

Semantic cues may include:
- Explicit verbs: "killed", "murdered", "assassinated", "shot", "executed".
- Indirect phrasing: "<A> ended <B>'s life", "<A> caused <B>'s death",
  "<A> fatally attacked <B>", "<A> defeated <B> in a fatal confrontation".

STRICT RULES:
1. Use ONLY the information inside the sentence.
2. Do NOT guess or hallucinate details not expressed in text.
3. If no Kill relationship is PRESENT IN MEANING → output [].
4. If Kill appears in any explicit or paraphrased form:
   return one or more objects:
   {"head": "<entity>", "relation": "Kill", "tail": "<entity>", "confidence": 1.0}
5. Output MUST be ONLY a JSON list.
6. No explanations. No text outside JSON.

Sentence: {sentence}
Entities: {entity_list}

<bot> JSON Response:
"""



# ----------------------------------------------------------
# LIVE-IN RELATION
# ----------------------------------------------------------

LIVE_IN_RELATION_PROMPT = """
System Message:
You are an advanced Relation Extraction agent for the relation "Live-in".
Your job is to detect residence relations expressed LITERALLY or by MEANING.

Semantic cues include:
- Explicit: "lives in", "resides in", "stays in".
- Indirect: "<A> is from <B>", "<A>'s home is in <B>", "<B> is where <A> is based",
  "<A> comes from <B>", "<A> grew up in <B>".

STRICT RULES:
1. Use only textual meaning — no world knowledge.
2. Extract ALL residence relations implied by wording or semantics.
3. Output only JSON list containing:
   {"head": "<entity>", "relation": "Live-in", "tail": "<entity>", "confidence": 1.0}

Sentence: {sentence}
Entities: {entity_list}

<bot> JSON Response:
"""



# ----------------------------------------------------------
# WORK-FOR RELATION
# ----------------------------------------------------------

WORK_FOR_RELATION_PROMPT = """
System Message:
You are an advanced Relation Extraction agent for the relation "Work-for".

Detect ALL employment relations expressed through meaning, including:
- Explicit: "works for", "works in", "employed by", "employed at".
- Paraphrased: "<A> serves under <B>", "<A> is on the staff of <B>",
  "<A> is part of <B>", "<B> employs <A>", "<A> belongs to <B>'s team".

STRICT RULES:
1. Use ONLY the sentence content.
2. Infer meaning ONLY if directly supported by the wording.
3. Extract ALL valid Work-for relations.
4. JSON list only.

Each object:
{"head": "<entity>", "relation": "Work-for", "tail": "<entity>", "confidence": 1.0}

Sentence: {sentence}
Entities: {entity_list}

<bot> JSON Response:
"""



# ----------------------------------------------------------
# LOCATED-IN RELATION
# ----------------------------------------------------------

LOCATED_IN_RELATION_PROMPT = """
System Message:
You are an advanced RE agent for the relation "Located-in".

Your goal: detect ALL cases where one location is inside another,
based on explicit or semantic spatial phrasing.

Semantic cues include:
- Explicit: "in", "inside", "within".
- Indirect: "<A> lies in <B>", "<A> is part of <B>", "<A> belongs to <B> region",
  "<A> is located at <B>", "<A> sits inside <B>".

STRICT RULES:
1. Only use meaning present in text.
2. DO NOT assume geography.
3. Extract ALL location→location containment relations.
4. JSON-only output.

Each object:
{"head": "<location>", "relation": "Located-in", "tail": "<location>", "confidence": 1.0}

Sentence: {sentence}
Entities: {entity_list}

<bot> JSON Response:
"""



# ----------------------------------------------------------
# ORG-BASED-IN RELATION
# ----------------------------------------------------------

ORG_BASED_IN_RELATION_PROMPT = """
System Message:
You are an advanced RE agent for "OrgBasedIn".
Detect ALL cases where an organization is based, located, or operating in a place.

Semantic cues include:
- Explicit: "based in", "headquartered in".
- Indirect: "<A> operates in <B>", "<A> is situated in <B>", "<B> hosts <A>",
  "<A> runs from <B>", "<A> is stationed in <B>".

STRICT RULES:
1. Meaning must be grounded explicitly in the sentence.
2. DO NOT guess or infer unstated facts.
3. Extract ALL ORG→LOC base-of-operation relations.
4. Output ONLY JSON list.

Each object:
{"head": "<org>", "relation": "OrgBasedIn", "tail": "<location>", "confidence": 1.0}

Sentence: {sentence}
Entities: {entity_list}

<bot> JSON Response:
"""
