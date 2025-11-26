
# 🧠 Intra-Group Debate NER + Relation Extraction  
### _A paper-style multi-agent Information Extraction pipeline using LLMs, debates & conflict resolution_

---

## 📌 Overview

This project implements a **research-grade Information Extraction system** consisting of:

1. **Three independent NER Agents**  
   - PER Agent  
   - LOC Agent  
   - ORG Agent  

2. **Five independent RE Agents**  
   - Kill  
   - Live-in  
   - Work-for  
   - Located-in  
   - OrgBasedIn  

3. **Two Debate Stages (NER & RE)**  
   - When agents disagree, they argue in a *round-robin natural-language debate*  
   - A **strict last-line JSON format** is required  
   - If the debate fails → a **Summarizer Agent** resolves conflict

This architecture is built using **AutoGen-AgentChat**, **Ollama**, and custom parsing logic to achieve deterministic, clean JSON outputs.

---

## 🏗 Pipeline Architecture

```

┌──────────────────────────────────────────────┐
│                  INPUT TEXT                  │
└──────────────────────────────────────────────┘
│
▼
┌────────────────────────────────┐
│      NER: 3 Independent Agents │
└────────────────────────────────┘
│
Conflict? → Yes ─┴─→ Run NER Debate → Summarizer
│ No
▼
Final Named Entities (PER/LOC/ORG)
│
▼
┌────────────────────────────────────────┐
│ RE: 5 Independent Relation Agents      │
│ (Kill, Live-in, Work-for, etc.)        │
└────────────────────────────────────────┘
│
Conflict? → Yes ─┴─→ Run RE Debate → Summarizer
│ No
▼
Final Relation Triples

````

---

## ⚙️ Requirements & Dependencies

### ✔ Prerequisites
- Python **3.10+**
- Ollama installed locally
- Virtual environment (recommended)

### ✔ Install Python dependencies

If your project includes `requirements.txt`:
```bash
pip install -r requirements.txt
````

Otherwise:

```bash
pip install autogen-agentchat autogen-ext ollama regex
```

---

## 🤖 Installing & Running the LLM (Ollama)

### 1. Install Ollama

Download from: [https://ollama.com](https://ollama.com)

### 2. Pull a Model

Use any model supported by your system. Example:

```bash
ollama pull gemma3:270m
```

or

```bash
ollama pull llama3
```

### 3. Configure model in `config.py`

```python
from autogen_ext.models.ollama import OllamaClient

def get_model1_client():
    return OllamaClient(model="gemma3:270m")
```

### 4. Test that Ollama works

```bash
ollama run gemma3:270m --prompt "Hello"
```

---

## 📁 Project Structure

```
/project-root
├── create_agents.py                  # Creates all NER & RE agents
├── config.py                         # LLM model configuration
├── intra_group_debate_ner.py         # Full NER pipeline + debates
├── intra_group_debate_re.py          # Full RE pipeline + debates
├── prompt_templates/
│   ├── ner/
│   │   ├── per_prompt.py
│   │   ├── loc_prompt.py
│   │   ├── org_prompt.py
│   │   └── debate_prompt_ner.py
│   └── re/
│       ├── re_prompts.py
│       └── debate_prompt_re.py
├── debate_summarizer_prompt_re.py    # Summarizer for RE
└── README.md
```

---

## ▶️ Running the Project

### **1. Run the full pipeline (NER → RE)**

```bash
python intra_group_debate_re.py
```

This triggers:

* NER agents
* NER debates
* Final NER entity list
* RE agents
* RE debates
* Final relations list

### **2. Run NER only**

```bash
python intra_group_debate_ner.py
```

### **3. Use pipeline manually inside Python**

```python
import asyncio
from intra_group_debate_re import run_intra_group_debate_re
from intra_group_debate_ner import run_intra_group_ner_pipeline

text = "Arjun lives in Maple Town and works for BrightTech."

entities = asyncio.run(run_intra_group_ner_pipeline(text))
relations = asyncio.run(run_intra_group_debate_re(text, entities))

print(relations)
```

---

## 🧪 Example Output (from the provided long paragraph)

```json
[
  {"head":"Victor","tail":"Officer Arjun","relation":"Kill","confidence":1.0},
  {"head":"Arjun","tail":"Maple Town","relation":"Live-in","confidence":1.0},
  {"head":"Rina","tail":"Maple Town","relation":"Live-in","confidence":1.0},
  {"head":"Rina","tail":"Pine Town","relation":"Live-in","confidence":1.0},
  {"head":"Arjun","tail":"BrightTech","relation":"Work-for","confidence":1.0},
  {"head":"Rina","tail":"Daily Echo","relation":"Work-for","confidence":1.0},
  {"head":"BrightTech","tail":"Silver City","relation":"OrgBasedIn","confidence":1.0},
  {"head":"Daily Echo","tail":"Central Plaza","relation":"OrgBasedIn","confidence":1.0}
]
```

---

## 🧩 How it Works Internally

### **NER Stage**

1. Each agent is called **once** per text:

   * PER agent returns all person-like spans
   * LOC agent returns all location spans
   * ORG agent returns all organization spans

2. All results combined

3. For each unique span:

   * If 1 type → accept
   * If multiple types → run **debate**:

     * Agents argue
     * Final JSON on last line decides

---

### **RE Stage**

1. Build all candidate `(head, tail)` entity pairs
2. Call all 5 RE agents **in one batch**
3. Parse claims
4. If multiple relations claimed → run **RE debate**
5. If debate fails → **summarizer fallback**

---

## 🩺 Troubleshooting

### ❗ Script stuck at: “Calling RE agents...”

Increase model responsiveness (use faster models like `gemma2:2b`, `llama3:3b`, `qwen2.5:1.5b`).

Or add timeout suppression as already patched into your pipeline.

---

### ❗ “AttributeError: 'str' object has no attribute 'get'”

Cause: RE agent output wasn’t valid JSON.
Fix: updated prompts + robust parser inside `intra_group_debate_re.py`.

---

### ❗ Debate fails to output final JSON

Fix:

* Your debate prompt **must** require:

  * ❌ No markdown
  * ❌ No explanations before/after JSON
  * ✔ Final line is **exact JSON object**

---

## 🛠 Customization Tips

### Improve NER accuracy

* Add synonyms
* Add entity-type constraints
* Add more examples in the system message

### Improve RE accuracy

* Expand semantic triggers
* Add pattern-based checks
* Add negative examples (“don’t detect employment from visiting an office”)

### Add new relations

Just create:

* a new prompt
* a new agent in `create_agents.py`
* add it to the AGENTS dictionary in `intra_group_debate_re.py`

---

## ⭐ Credits & Design Philosophy

This repository follows the **multi-agent debate** paradigm inspired by:

* Cross-examination
* Adversarial self-evaluation
* Ensemble disagreement reduction

The goal is:

* **Interpretability**
* **Conflict resolution**
* **Realistic paper-style experimentation**

---



Just tell me!
