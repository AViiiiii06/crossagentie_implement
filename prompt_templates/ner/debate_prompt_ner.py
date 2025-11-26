# ==========================================
# FIXED NER DEBATE PROMPT (all braces escaped)
# ==========================================

DEBATE_PROMPT_TEMPLATE = """
CONFLICT DETECTED for entity span: "{span}"

Sentence:
"{text}"

Participants:
- PER Agent → MUST defend label "PER" and attack "LOC" and "ORG".
- LOC Agent → MUST defend label "LOC" and attack "PER" and "ORG".
- ORG Agent → MUST defend label "ORG" and attack "PER" and "LOC".

STRICT DEBATE RULES (DO NOT VIOLATE):
1. DO NOT repeat or paraphrase these instructions.
2. DO NOT restate the prompt, rules, or sentence.
3. DO NOT output JSON, lists, arrays, or code during the debate.
4. DO NOT output confidence scores.
5. Debate MUST be pure natural-language paragraphs.
6. You MUST argue aggressively for your label and attack the others.
7. Use ONLY lexical and contextual evidence found in the sentence.
8. NO world knowledge, NO invented facts, NO external reasoning.
9. After your final argument, STOP immediately.

FORMAT RULES (MANDATORY):
- The ONLY JSON allowed is the final decision.
- JSON MUST appear on the LAST LINE only.
- The JSON MUST be a SINGLE OBJECT:
  {{ "span": "{span}", "type": "<PER|LOC|ORG>" }}
- NO explanation before or after the JSON.
- If you output anything else, you FAIL.

BEGIN DEBATE BELOW:
"""
