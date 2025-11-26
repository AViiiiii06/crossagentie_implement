# ==========================================
# RE DEBATE PROMPT (STRICT, PAPER STYLE)
# ==========================================

RE_DEBATE_PROMPT_TEMPLATE = """
CONFLICT DETECTED for:
Head: "{head}"
Tail: "{tail}"

Sentence:
"{sentence}"

Participants:
- Kill Agent → MUST defend "Kill".
- Live-in Agent → MUST defend "Live-in".
- Work-for Agent → MUST defend "Work-for".
- Located-in Agent → MUST defend "Located-in".
- OrgBasedIn Agent → MUST defend "OrgBasedIn".

STRICT RULES:
1. DO NOT repeat or paraphrase these rules.
2. DO NOT restate the prompt or sentence.
3. NO JSON during debate.
4. Each agent MUST argue ONLY for its relation.
5. Each agent MUST attack all other relations.
6. Use ONLY lexical/contextual clues from the sentence.
7. NO world knowledge.
8. Stop after arguments.

FINAL JSON RULE:
- LAST LINE ONLY contains:
{"head": "%s", "relation": "<Kill|Live-in|Work-for|Located-in|OrgBasedIn|no_relation>", "tail": "%s"}

NO text before or after the JSON object.

BEGIN DEBATE BELOW:
"""
