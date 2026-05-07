# Learning Notes — AI Agents Journey

---

## JSON Parsing in LLM Agents

### The Problem

When you call an LLM and ask it to return JSON, it doesn't always return clean JSON. It can:
- Wrap the JSON in markdown code fences (` ```json ... ``` `)
- Output the same JSON object **twice** on separate lines
- Add trailing text after the JSON
- Return completely garbled output

`json.loads()` is strict — it breaks on all of the above.

---

### The Solution — `json.JSONDecoder.raw_decode()`

`raw_decode()` reads one complete JSON object from the **start** of a string and **stops there**, ignoring everything after it.

It returns a tuple: `(parsed_object, end_index)`
- `parsed_object` → the Python dict you want
- `end_index` → where the JSON ended in the string (you discard this with `_`)

---

### Code Breakdown

```python
def _parse_json(self, content):
    # --- Step 1: Strip markdown code fences ---
    # LLM sometimes wraps output like:
    # ```json
    # {"Action": "search", ...}
    # ```
    if content.startswith("```"):
        content = content.split("```")[1]   # take the middle part
        if content.startswith("json"):
            content = content[4:]           # strip the word "json"

    # --- Step 2: Extract only the first JSON object ---
    # raw_decode() stops at the end of the first valid JSON object
    # so duplicate output, trailing text etc. are all safely ignored
    decoder = json.JSONDecoder()
    content = content.strip()
    try:
        parsed, _ = decoder.raw_decode(content)
        return parsed

    # --- Step 3: Graceful fallback ---
    # If even raw_decode fails (completely garbled), don't crash the agent.
    # Return a fake Final Answer so the loop exits cleanly.
    except json.JSONDecodeError:
        return {"Final Answer": f"Failed to parse response: {content}"}
```

---

### Scenario Comparison

| Scenario | `json.loads()` | `raw_decode()` |
|----------|:--------------:|:--------------:|
| Clean JSON | ✅ | ✅ |
| JSON wrapped in ` ```json ``` ` | ❌ | ✅ (after fence strip) |
| JSON duplicated on two lines | ❌ | ✅ (takes first object only) |
| Trailing text after JSON | ❌ | ✅ (stops at end of first object) |
| Completely garbled output | ❌ | ❌ → returns fallback dict |

---

### Concrete Example

**LLM outputs this (duplicate JSON bug):**
```
{"Thought": "I need to calculate this.", "Action": "calculate", "Action Input": "2+2"}
{"Thought": "I need to calculate this.", "Action": "calculate", "Action Input": "2+2"}
```

**`json.loads()` result:**
```
❌ JSONDecodeError: Extra data at line 2
```

**`raw_decode()` result:**
```python
✅ {"Thought": "I need to calculate this.", "Action": "calculate", "Action Input": "2+2"}
# Stopped after the first object, ignored the second line entirely
```

---

### Key Takeaway

> In production LLM applications, **never assume the model returns perfectly formatted output**.
> Always write defensive parsers. `raw_decode()` is one tool — others include regex extraction,
> retry loops, and asking the model to self-correct on parse failure.

---

*Project: 01_vanilla_react | File: agent.py → `_parse_json()`*
