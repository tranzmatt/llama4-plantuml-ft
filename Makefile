PY=python
LLC=extern/llama.cpp/build/bin

.PHONY: env build-llamacpp extract build-data finetune export adapter pack

env:
	conda create -y -n llama4-plantuml-ft python=3.12 || true
	@echo "Run: conda activate llama4-plantuml-ft && pip install -r requirements.txt"

build-llamacpp:
	cd extern/llama.cpp && mkdir -p build && cd build && \
	cmake .. -DLLAMA_CUBLAS=ON && cmake --build . -j

extract:
	$(PY) scripts/01_extract_from_pdfs.py

build-data:
	$(PY) scripts/02_build_training_jsonl.py

finetune:
	$(LLC)/finetune \
	  -m base/llama4-maverick-base.gguf \
	  --train-data data/processed/train.jsonl \
	  --eval-data  data/processed/eval.jsonl \
	  --data-format alpaca \
	  --lora-out out/plantuml_lora \
	  --threads 16 --batch 64 --epochs 3 --lora-r 64 --lora-alpha 16 --lora-dropout 0.05

export:
	$(LLC)/llama-merge-lora -m base/llama4-maverick-base.gguf -l out/plantuml_lora -o out/plantuml_lora.gguf --just-save-lora

adapter:
	echo "FROM llama4:maverick" > Modelfile
	echo "ADAPTER ./out/plantuml_lora.gguf" >> Modelfile
	ollama create llama4:maverick-plantuml -f Modelfile

pack: extract build-data finetune export adapter

