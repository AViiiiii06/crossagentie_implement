# ==========================================
# CREATE ALL AGENTS (NER + RE + DEBATE)
# ==========================================

from prompt_templates.ner import ner_prompts
from prompt_templates.re import re_prompts
from prompt_templates.ner import debate_summarizer_prompt_ner
from prompt_templates.re import debate_summarizer_prompt_re
from autogen_agentchat.agents import AssistantAgent
import config


# -------------------------------
# Load the base model
# -------------------------------
model_client_ollama = config.get_model2_client()
model_client_deepseek = config.get_model1_client()


# -------------------------------
# Helper to create agents
# -------------------------------
def create_agent_ollama(name: str, system_message: str) -> AssistantAgent:
    return AssistantAgent(
        name=name,
        model_client=model_client_ollama,
        system_message=system_message
    )
def create_agent_deepseek(name: str, system_message: str) -> AssistantAgent:
    return AssistantAgent(
        name=name,
        model_client=model_client_deepseek,
        system_message=system_message
    )
def create_agent_strongollama(name: str, system_message: str) -> AssistantAgent:
    return AssistantAgent(
        name=name,
        model_client=model_client_ollama,
        system_message=system_message
    )

# -------------------------------
# NER TYPE AGENTS (PER / LOC / ORG)
# These agents do BOTH:
#   - NER extraction (JSON output)
#   - Debate participation (natural arguments + final JSON line)
# controlled by the task prompt.
# -------------------------------
per_agent = create_agent_deepseek("PER_Agent", ner_prompts.PER_PROMPT)
loc_agent = create_agent_deepseek("LOC_Agent", ner_prompts.LOC_PROMPT)
org_agent = create_agent_deepseek("ORG_Agent", ner_prompts.ORG_PROMPT)


# -------------------------------
# RELATION EXTRACTION AGENTS (Stage 2)
# -------------------------------
live_in_agent = create_agent_deepseek("LiveIn_Agent", re_prompts.LIVE_IN_RELATION_PROMPT)
kill_agent = create_agent_deepseek("Kill_Agent", re_prompts.KILL_RELATION_PROMPT)
work_for_agent = create_agent_deepseek("WorkFor_Agent", re_prompts.WORK_FOR_RELATION_PROMPT)
located_in_agent = create_agent_deepseek("LocatedIn_Agent", re_prompts.LOCATED_IN_RELATION_PROMPT)
org_based_agent = create_agent_deepseek("OrgBased_Agent", re_prompts.ORG_BASED_IN_RELATION_PROMPT)


# -------------------------------
# DEBATE SUMMARIZER (Meta Agent)
# -------------------------------
debate_summarizer = create_agent_deepseek(
    "Debate_Summarizer",
    debate_summarizer_prompt_ner.DEBATE_SUMMARIZER_PROMPT_NER
)

debate_summarizer_re=create_agent_deepseek(
    "Debate_Summarizer_re",
    debate_summarizer_prompt_re.DEBATE_SUMMARIZER_PROMPT_RE
)