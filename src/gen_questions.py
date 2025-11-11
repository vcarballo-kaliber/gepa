import dspy
import os
import json
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('OPENAI_KEY')
assert key is not None
lm = dspy.LM('openai/gpt-4o-mini', api_key=key)
dspy.configure(lm=lm)

# print(lm("Make a list of 30 specialties in medicine, just the names in a python list format", temperature=0.7))

medical_specialties = [
    "Allergy and Immunology",
    "Anesthesiology",
    "Dermatology",
    "Emergency Medicine",
    "Family Medicine",
    "Internal Medicine",
    "Medical Genetics",
    "Neurology",
    "Nuclear Medicine",
    "Obstetrics and Gynecology",
    "Ophthalmology",
    "Orthopedic Surgery",
    "Otolaryngology",
    "Pediatrics",
    "Physical Medicine and Rehabilitation",
    "Plastic Surgery",
    "Psychiatry",
    "Radiology",
    "Surgery",
    "Thoracic Surgery",
    "Urology",
    "Pathology",
    "Public Health",
    "Preventive Medicine",
    "Geriatrics",
    "Sports Medicine",
    "Infectious Disease",
    "Endocrinology",
    "Hematology"
]

# n_questions = 100
# questions = {}
# for field in medical_specialties:
#     prompt = (
#         f"I'm testing a medical assistant agent. The goal of this agent is to answer patient questions "
#         f"relating to the field of {field.lower()}. Imagine which questions a patient would ask to a "
#         f"doctor that is treating him. These can be specific or general questions. I want you to write "
#         f"{n_questions} questions. Make sure not to repeat any and to make them as realistic as possible. "
#         f"Write them without any extra explanation, with only a newline separating samples."
#     )
#     questions[field] = lm(prompt, temperature=0.7)[0].split('\n\n')

# with open("questions.json", "w") as f:
#     json.dump(questions, f, indent=2)

with open("questions.json", "r") as f:
    questions = json.load(f)

for k in questions.keys():
    if len(questions[k]) == 1:
        questions[k] = questions[k][0].split('\n')
    questions[k] = [vi.split('.')[-1].strip() for vi in questions[k]]


with open("questions_new.json", "w") as f:
    json.dump(questions, f, indent=2)