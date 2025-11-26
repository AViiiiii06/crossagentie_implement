# intra_group_debate_re.py
import json
import asyncio
import re
from typing import List, Dict, Any

from autogen_agentchat.teams import RoundRobinGroupChat

# your project imports
import create_agents
from prompt_templates.re.debate_prompt_re import RE_DEBATE_PROMPT_TEMPLATE
from intra_group_debate_ner import run_intra_group_ner_pipeline

DEBUG = False
def dprint(tag, x):
    if DEBUG:
        print(f"\n===== {tag} =====\n{x}\n=======================\n")

# ---------------------
# Robust JSON extraction helpers
# ---------------------
_codefence_re = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```")
_json_array_re = re.compile(r"\[[\s\S]*?\]")
_json_object_re = re.compile(r"\{[\s\S]*\}")

def strip_wrappers(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    m = _codefence_re.search(t)
    if m:
        return m.group(1).strip()
    return t.replace("`", "").strip()

def find_first_json_array(text: str):
    t = strip_wrappers(text)
    m = _json_array_re.search(t)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except:
        try:
            return json.loads(m.group(0).replace("'", '"'))
        except:
            return None

def find_last_json_object(text: str):
    t = strip_wrappers(text)
    matches = list(_json_object_re.finditer(t))
    if not matches:
        return None
    last = matches[-1].group(0)
    try:
        return json.loads(last)
    except:
        try:
            return json.loads(last.replace("'", '"'))
        except:
            return None

def parse_json_list_from_agent(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []

    arr = find_first_json_array(text)
    if arr is not None:
        out = []
        for el in arr:
            if isinstance(el, dict):
                out.append(el)
            elif isinstance(el, str):
                s = el.strip()
                if s.startswith("{") and s.endswith("}"):
                    try:
                        out.append(json.loads(s))
                        continue
                    except:
                        pass
                if "->" in s:
                    a, b = [p.strip() for p in s.split("->", 1)]
                    out.append({"head": a, "tail": b})
        return out

    obj = find_last_json_object(text)
    if isinstance(obj, dict):
        return [obj]
    if isinstance(obj, list):
        return obj
    return []

# ---------------------
# Build candidate pairs
# ---------------------
def build_candidate_pairs(entities: List[Dict[str, Any]]):
    spans = [e.get("span") for e in entities if e.get("span")]
    return [(h, t) for h in spans for t in spans if h != t]

# ---------------------
# Main RE pipeline — NO TIMEOUTS
# ---------------------
async def run_intra_group_debate_re(sentence: str, entities: List[Dict[str, Any]]):
    print(f"\n🔗 Running RE pipeline on:\n\"{sentence}\"\n")
    print(f"🧩 Entities:\n{json.dumps(entities, indent=2)}")

    AGENTS = {
        "Kill": create_agents.kill_agent,
        "Live-in": create_agents.live_in_agent,
        "Work-for": create_agents.work_for_agent,
        "Located-in": create_agents.located_in_agent,
        "OrgBasedIn": create_agents.org_based_agent,
    }

    print("\n🚀 Calling RE agents (5 calls total)...")

    payload_text = (
        f"Sentence: {sentence}\n"
        f"Entities: {json.dumps(entities)}\n"
        "Return: ONLY a JSON list of relation objects."
    )

    tasks, names = [], []
    for rel_name, agent in AGENTS.items():
        tasks.append(agent.run(task=payload_text))
        names.append(rel_name)

    # ❌ No timeout here
    results = await asyncio.gather(*tasks)

    claims_map = {}

    for rel_name, res in zip(names, results):
        raw = res.messages[-1].content if res.messages else ""
        dprint(f"RAW {rel_name}", raw)

        parsed = parse_json_list_from_agent(raw)

        for item in parsed:
            if not isinstance(item, dict):
                continue
            head = item.get("head")
            tail = item.get("tail")
            if not head or not tail:
                continue

            claim = {
                "head": head,
                "tail": tail,
                "relation": rel_name
            }
            if "confidence" in item:
                try:
                    claim["confidence"] = float(item["confidence"])
                except:
                    pass

            claims_map.setdefault((head, tail), []).append(claim)

    json_safe = {f"{h} -> {t}": v for (h, t), v in claims_map.items()}
    print(f"\n📌 Raw RE claims:\n{json.dumps(json_safe, indent=2)}")

    if not claims_map:
        print("\n=== No RE claims detected ===")
        return []

    final = []

    for (head, tail), claims in claims_map.items():
        rel_types = {c["relation"] for c in claims}

        if len(rel_types) == 1:
            best = max(claims, key=lambda c: c.get("confidence", 1.0))
            final.append(best)
            continue

        print(f"\n⚠️ Conflict for: {head} → {tail}")
        print(f"   Claims: {rel_types}")

        prompt = RE_DEBATE_PROMPT_TEMPLATE.format(
            head=head, tail=tail, sentence=sentence
        )

        participants = [AGENTS[r] for r in rel_types]

        # ❌ NO timeout
        debate = RoundRobinGroupChat(participants=participants, max_turns=3)
        debate_res = await debate.run(task=prompt)

        debate_last = debate_res.messages[-1].content
        decision = find_last_json_object(debate_last)

        if isinstance(decision, dict) and decision.get("relation"):
            print("   ✅ Debate chose:", decision)
            final.append(decision)
            continue

        print("   ❌ Debate JSON invalid → using summarizer")

        transcript = "\n".join(m.content for m in debate_res.messages)
        summ_payload = (
            f"Head: {head}\nTail: {tail}\nSentence: {sentence}\n\n"
            f"Debate:\n{transcript}"
        )

        # ❌ NO timeout
        sum_res = await create_agents.debate_summarizer_re.run(task=summ_payload)
        sum_last = sum_res.messages[-1].content
        sum_decision = find_last_json_object(sum_last)

        if isinstance(sum_decision, dict):
            print("   🟢 Summarizer chose:", sum_decision)
            final.append(sum_decision)
            continue

        final.append(max(claims, key=lambda c: c.get("confidence", 0.0)))

    return final

# ---------------------
# TEST MAIN
# ---------------------
if __name__ == "__main__":
    async def main():
        text = "During a routine week in the city of Greenhill, Arjun lived in Maple Town with his sister Rina. Every morning, Arjun worked in BrightTech, an organization based in Silver City, while Rina worked for the local news group Daily Echo. One afternoon, a report said that a criminal named Victor was killed by Officer Arjun near the Old Bridge inside North Valley. Daily Echo announced that their main office is located in Central Plaza, and BrightTech is headquartered inside Silver District. Rina later moved to Pine Town, which is inside North Valley, but still worked for Daily Echo. Arjun also visited Lakeview Park, which is located in Greenhill, after finishing his duty."

        print("\n>>> Running NER...")
        ents = await run_intra_group_ner_pipeline(text)

        print("\n>>> NER OUTPUT:")
        print(json.dumps(ents, indent=2))

        print("\n>>> Running RE...")
        rels = await run_intra_group_debate_re(text, ents)

        print("\n=== FINAL RELATIONS ===")
        print(json.dumps(rels, indent=2))

    asyncio.run(main())
