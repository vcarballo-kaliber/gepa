import dspy
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('OPENAI_KEY')
assert key is not None
lm = dspy.LM('openai/gpt-4o-mini', api_key=key)
dspy.configure(lm=lm)


with open("./res/data.json", "r") as f:
    data = json.load(f)


def sample():
    specialty = random.choice(list(data.values()))
    patient = random.choice(specialty)
    question = random.choice(patient['questions'])
    return patient['summary'], question


with open('res/guidelines.md', 'r') as f:
    sys_prompt_template = f.read()

with open('res/prompt.md', 'r') as f:
    prompt_template = f.read()

def get_system_prompt(summary: str):
    sys_prompt = sys_prompt_template.format(medical_summary=summary)
    return sys_prompt


def format_prompt(question: dict, face_emot: str, text_emot: str):
    prompt = prompt_template.format(
        patient_message=question,
        face_emotion=face_emot,
        text_emotion=text_emot,
    )
    return prompt


def generate():
    patient_summary, question = sample()
    sys_prompt = get_system_prompt(patient_summary)
    face_emot = question['emotion']['face']
    text_emot = question['emotion']['text']
    question_text = question['question']
    prompt = format_prompt(question_text, face_emot, text_emot)
    print(f'System prompt:\n\n{sys_prompt}\n\nMessage prompt:\n\n{prompt}')
    answer = lm(sys_prompt + prompt, temperature=0.7)[0].replace('"', '').replace('\u2019', "'").replace('\u2014', ',')
    print(f'\n\nAgent\'s answer:\n\n{answer}')
    return patient_summary, face_emot, text_emot, question_text, answer


results = []
for _ in range(15):
    patient_summary, face_emot, text_emot, question_text, answer = generate()
    results.append(dict(
        patient_summary=patient_summary,
        face_emot=face_emot,
        text_emot=text_emot,
        question_text=question_text,
        answer=answer,
    ))

with open("res/answers.json", "w") as f:
  json.dump(results, f, indent=2)