import re
import json
import asyncio

from autogen_agentchat.teams import RoundRobinGroupChat
from create_agents import per_agent, loc_agent, org_agent, debate_summarizer
from prompt_templates.ner.debate_prompt_ner import DEBATE_PROMPT_TEMPLATE


# -----------------------------------------------------
# Debug printer
# -----------------------------------------------------
def debug_print(tag, data):
    print(f"\n==================== {tag} ====================")
    print(data)
    print("===============================================\n")


# -----------------------------------------------------
# Robust JSON parser for NER agent output
# (No more ### wrappers; tries to find a JSON array)
# -----------------------------------------------------
def parse_json_block(content: str):
    """
    Extracts a JSON list from the model output.

    Strategy:
    1. Try to parse the entire content as JSON.
    2. If that fails, search for the first JSON array substring `[ ... ]`
       and try to parse that.
    3. On failure, log and return [].
    """
    if not content:
        debug_print("PARSE JSON BLOCK FAILED (EMPTY CONTENT)", content)
        return []

    text = content.strip()

    # First attempt: entire string is JSON
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    # Second attempt: find a JSON array substring
    match = re.search(r"\[.*\]", text, re.S)
    if not match:
        debug_print("PARSE JSON BLOCK FAILED (NO JSON ARRAY FOUND)", text)
        return []

    array_str = match.group(0).strip()
    try:
        data = json.loads(array_str)
        if isinstance(data, list):
            return data
        else:
            debug_print("PARSE JSON BLOCK NOT A LIST", data)
            return []
    except Exception as e:
        debug_print("PARSE JSON BLOCK JSON ERROR", f"{array_str}\nERROR: {e}")
        return []


# -----------------------------------------------------
# Parser for debate / summarizer JSON (last-line strict)
# -----------------------------------------------------
def parse_final_json(text: str):
    """
    Robust JSON parser for debate/summarizer final output.
    Accepts:
    - single-line JSON
    - multi-line pretty JSON
    - JSON object anywhere in the string
    """
    if not text:
        debug_print("FINAL JSON PARSE ERROR", "EMPTY TEXT")
        return None

    # ---------- 1) Try last line (original logic) ----------
    last = text.strip().split("\n")[-1].strip()
    try:
        return json.loads(last)
    except:
        pass

    # ---------- 2) Try to find ANY JSON object in output ----------
    m = re.search(r"\{[\s\S]*?\}", text)
    if m:
        candidate = m.group(0)
        try:
            return json.loads(candidate)
        except Exception as e:
            debug_print("FINAL JSON FOUND BUT INVALID", f"{candidate}\nERROR: {e}")

    # ---------- 3) Failure ----------
    debug_print("FINAL JSON PARSE ERROR", text)
    return None

# -----------------------------------------------------
# Intra-Group Debate Pipeline (full version)
# -----------------------------------------------------
async def run_intra_group_ner_pipeline(text_input: str):
    print(f"\n📄 Processing: \"{text_input}\"")

    # ---- Run Per/Loc/Org in parallel (NER extraction) ----
    print("\n⚙️ Launching PER / LOC / ORG NER Agents ...")
    tasks = [
        per_agent.run(task=text_input),
        loc_agent.run(task=text_input),
        org_agent.run(task=text_input),
    ]
    results = await asyncio.gather(*tasks)

    # ---- Raw debug logs ----
    per_raw = results[0].messages[-1].content
    loc_raw = results[1].messages[-1].content
    org_raw = results[2].messages[-1].content

    debug_print("PER RAW OUTPUT", per_raw)
    debug_print("LOC RAW OUTPUT", loc_raw)
    debug_print("ORG RAW OUTPUT", org_raw)

    # ---- Parse JSON blocks (NER outputs) ----
    per_output = parse_json_block(per_raw)
    loc_output = parse_json_block(loc_raw)
    org_output = parse_json_block(org_raw)

    # ---- Attach type tags ----
    all_entities = []
    for ent in per_output:
        ent = dict(ent)
        ent["type"] = "PER"
        all_entities.append(ent)

    for ent in loc_output:
        ent = dict(ent)
        ent["type"] = "LOC"
        all_entities.append(ent)

    for ent in org_output:
        ent = dict(ent)
        ent["type"] = "ORG"
        all_entities.append(ent)

    debug_print("ALL ENTITIES", all_entities)

    # ---- Group by span ----
    span_map = {}
    for ent in all_entities:
        span = ent.get("span")
        if not span:
            continue
        span_map.setdefault(span, []).append(ent)

    debug_print("SPAN GROUPED ENTITIES", span_map)

    final_entities = []

    # ---- Resolve conflicts span-wise ----
    for span, claims in span_map.items():
        debug_print(f"PROCESSING SPAN '{span}'", claims)

        types = {c["type"] for c in claims}

        # No conflict → choose first (they all agree)
        if len(types) == 1:
            chosen = claims[0]
            print(f"✓ No conflict for '{span}' → Auto-selected type {chosen['type']}")
            final_entities.append(chosen)
            continue

        print(f"\n⚠️ Conflict Detected for '{span}' → {types}")

        # ---- Build debate prompt ----
        prompt = DEBATE_PROMPT_TEMPLATE.format(span=span, text=text_input)
        #debug_print("DEBATE PROMPT", prompt)

        # ---- Determine participants based on who claimed the span ----
        participants = []
        if "PER" in types:
            participants.append(per_agent)
        if "LOC" in types:
            participants.append(loc_agent)
        if "ORG" in types:
            participants.append(org_agent)

        print(f"🗣 Starting Debate with: {[p.name for p in participants]}")

        debate_team = RoundRobinGroupChat(participants=participants, max_turns=3)
        debate_result = await debate_team.run(task=prompt)

        # ---- Log debate transcript ----
        debate_text = "\n".join(
            f"[{getattr(m, 'source', getattr(m, 'sender', 'Agent'))}] {m.content}"
            for m in debate_result.messages
        )
        #debug_print("FULL DEBATE TRANSCRIPT", debate_text)

        # ---- Try to parse final JSON from last debate message ----
        last_msg = debate_result.messages[-1].content
        debug_print("DEBATE FINAL MESSAGE", last_msg)

        decision = parse_final_json(last_msg)

        if decision:
            print(f"   ✅ Debate resolved → {decision}")
            final_entities.append(decision)
            continue

        print("   ❌ Debate JSON invalid → invoking summarizer")

        # ---- Summarizer fallback ----
        summary_prompt = (
            f"Span: {span}\n"
            f"Sentence: {text_input}\n\n"
            f"Full Debate Transcript:\n{debate_text}\n"
        )
        #debug_print("SUMMARIZER PROMPT", summary_prompt)

        summary_res = await debate_summarizer.run(task=summary_prompt)
        summary_raw = summary_res.messages[-1].content

        debug_print("SUMMARIZER RAW OUTPUT", summary_raw)

        summary_json = parse_final_json(summary_raw)

        if summary_json:
            print(f"   🟢 Summarizer resolved → {summary_json}")
            final_entities.append(summary_json)
            continue

        print("   ⚠️ Summarizer also failed → Falling back to highest confidence")

        # ---- Final fallback: highest-confidence claimant ----
        fallback = max(
            claims,
            key=lambda x: float(x.get("confidence", 0.0))
        )
        debug_print("FALLBACK ENTITY", fallback)
        final_entities.append(fallback)

    return final_entities


