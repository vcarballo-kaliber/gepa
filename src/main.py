from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, PeftModel
from datasets import load_dataset
from trl import GRPOTrainer, GRPOConfig
from datasets import Dataset
import torch
import re
import json
from random import randint
import random


# Hide all cards except one, as the inter-communication card is extremely slow
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "1"


model_name = "HuggingFaceTB/SmolLM3-3B"
# adapter_path = f"./SmolLM3-{emotion}-lora"
adapter_path = None

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    dtype=torch.bfloat16,
)

if adapter_path is None:
    print("INITIATING NEW TRAINING")
    # Apply LoRA adapters
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(base_model, lora_config)
else:
    print(f"LOADING LORA CHECKPOINT AT {adapter_path}")
    model = PeftModel.from_pretrained(base_model, adapter_path, is_trainable=True)

model.print_trainable_parameters()



def reward_function_emot(**kwargs):
    scores = emot_cls(kwargs['completions'])
    if randint(0,10) == 1:
        print(f"\n\n  [*]  Sample\nPrompt: {kwargs['prompts'][0]}")
        print(f"Completion: {kwargs['completions'][0]}")
        print(f"Emotion score: {scores[0]}")
    return scores



class MyDataset(Dataset):
    def __init__(self, json_path, tokenizer, sys_prompt, prompt, summaries):
        with open(json_path, "r") as f:
            questions = json.load(f)
        self.prompts = sum(list(questions.values()), [])
        self.tokenizer = tokenizer
        self.prompt = prompt
        self.sys_prompt = sys_prompt
        self.summary_for_question = []
        for k,v in summaries.items():
            self.summary_for_question += [(k,i%len(v)) for i in range(len(v))]
        self.summaries = summaries
        
    def __len__(self):
        return len(self.questions)
    
    def __getitem__(self, idx):
        summary_idx = self.summary_for_question[idx]
        summary = self.summaries[summary_idx[0]][summary_idx[1]]
        messages = [
            {"role": "system", "content": self.sys_prompt},
            {"role": "user", "content": f"{self.prompt}\n\nThe user's clinical summary is:\n{summary}\n\nThe user query is: {self.prompts[idx]}"}
        ]
        return messages





print(f"Loaded {len(prompts)} prompts")

# messages_list = [[{"role": "user", "content": text}] for text in prompts[:2000]]
# prompts = [tokenizer.apply_chat_template(msg, tokenize=False, add_generation_prompt=True, enable_thinking=False) for msg in messages_list]
# prompts = prompts[:2000]


# Wrap list of prompts into a Dataset
train_dataset = Dataset.from_dict({"prompt": prompts})

# Optional: small eval dataset (can be a subset of train)
eval_dataset = train_dataset.select(range(min(50, len(train_dataset))))


grpo_config = GRPOConfig(
    num_generations=8,
    learning_rate=1e-5,
    gradient_accumulation_steps=8,
    per_device_train_batch_size=16,
    max_completion_length=64,
    repetition_penalty=1.1,
)

trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    args=grpo_config,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    reward_funcs=reward_function_emot,
)

trainer.train()

model.save_pretrained(f"./SmolLM3-{emotion}-lora")
tokenizer.save_pretrained(f"./SmolLM3-{emotion}-lora")
