# 02_build_training_jsonl.py
import json, pathlib, random, re
from tqdm import tqdm

SAMPLES = pathlib.Path("data/extracted/plantuml_samples.jsonl")
CORPUS  = pathlib.Path("data/extracted/corpus.txt")
TRAIN   = pathlib.Path("data/processed/train.jsonl")
EVAL    = pathlib.Path("data/processed/eval.jsonl")
TRAIN.parent.mkdir(parents=True, exist_ok=True)

def guess_type(code: str) -> str:
    code_l = code.lower()
    if "class" in code_l: return "class diagram"
    if "sequence" in code_l or "->" in code_l: return "sequence diagram"
    if "usecase" in code_l or "actor" in code_l: return "use-case diagram"
    if "state" in code_l and "@startuml" in code_l: return "state machine diagram"
    if "component" in code_l: return "component diagram"
    if "activity" in code_l: return "activity diagram"
    return "UML diagram"

def make_instruction(context: str, code: str) -> str:
    dtype = guess_type(code)
    context = re.sub(r"\s+", " ", context).strip()
    return (
        "Using PlantUML, produce a valid {dtype} that matches this description. "
        "Return ONLY PlantUML code between @startuml and @enduml."
    ).format(dtype=dtype) + (f" Description: {context}" if context else "")

def main():
    rows = []
    with open(SAMPLES, "r", encoding="utf-8") as f:
        for line in f:
            ex = json.loads(line)
            inst = make_instruction(ex.get("context",""), ex["plantuml"])
            rows.append({"instruction": inst, "input": "", "output": ex["plantuml"]})

    # add a few format policy flashcards to nail output formatting
    policy = [
        {
            "instruction": "Return a minimal, syntactically correct empty PlantUML diagram.",
            "input": "",
            "output": "@startuml\n@enduml",
        },
        {
            "instruction": "Show the correct syntax for declaring two classes A and B with an association in PlantUML. Return ONLY PlantUML.",
            "input": "",
            "output": "@startuml\nclass A\nclass B\nA --> B\n@enduml",
        },
    ]
    rows.extend(policy)

    random.shuffle(rows)
    split = int(0.95 * len(rows)) if len(rows) > 20 else max(1, len(rows) - 1)
    train, evals = rows[:split], rows[split:]

    with open(TRAIN, "w", encoding="utf-8") as f:
        for r in train: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(EVAL, "w", encoding="utf-8") as f:
        for r in evals: f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"train: {len(train)} | eval: {len(evals)}")
    print(f"Wrote {TRAIN} and {EVAL}")

if __name__ == "__main__":
    main()

