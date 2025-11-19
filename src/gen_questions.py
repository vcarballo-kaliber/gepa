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

all_emotions = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]

emot_compat = dict(
  #        anger disgust fear joy neutral sadness surprise
  anger   =[  0,      1,   1,  0,      1,      1,        1],
  disgust =[  1,      0,   1,  0,      1,      1,        1],
  fear    =[  1,      1,   0,  0,      0,      1,        0],
  joy     =[  0,      0,   0,  0,      0,      0,        1],
  neutral =[  1,      1,   0,  0,      0,      1,        0],
  sadness =[  1,      1,   1,  0,      1,      0,        1],
  surprise=[  1,      1,   0,  1,      0,      1,        0],
)

assert len(all_emotions) == len(emot_compat)

for j, emot in enumerate(all_emotions):
  for i, emot_ in enumerate(all_emotions):
    assert emot_compat[emot][i] == emot_compat[emot_][j], f"Emotion {emot} and {emot_} compatibilities are not symmetric"

def gen_summaries(n_sums_per_field: int, fields: list[str], summary_exs: list[str]):
  data = {}
  for field in fields:
    print(f"Gen summary for field {field}")
    prompt = (
    f"I'm testing a medical assistant agent. The goal of this agent is to deal with patients "
    f"relating to the field of {field.lower()}. For this purpose, I need a series of medical "
    f"histories of these patients to test my system. A medical history is made up of a series "
    f"of varied and concise items and facts about a patient and its clinical history in a bullet "
    f"point list. The items don't all necessarily belong "
    f"to the field of {field.lower()}, but relate mostly to it. I want you to write {n_sums_per_field} "
    f"summaries belonging to different patients. Make sure to make these as realistic as possible "
    f"and containing both positive as well as negative stories. "
    f"Provide ONLY the list of stories, no need for markdown code indicators or dashes, separate examples by two newlines. "
    f"Don't number patients, provide the stories directly. An example of some stories is:\n\n"
    )
    prompt += "\n\n".join(summary_exs)
    res = lm(prompt, temperature=0.7)[0]
    data[field] = res.split("\n\n")
  return data


def get_face_emotion(emotion: str):
  if random.random() > 0.4:
    return emotion
  compat_emot = [all_emotions[i] for i in range(len(all_emotions)) if emot_compat[emotion][i] == 1]
  return random.choice(compat_emot)


def gen_questions(n_q_per_sum: int, summaries: dict[str,list[str]], emotions: list[str]):
  data = {}
  for field, summaries in summaries.items():
    print(f"Gen questions for {field}")
    patients = []
    for summary in summaries:
      questions = []
      for emotion in random.choices(emotions, k=n_q_per_sum):
        face_emotion = get_face_emotion(emotion)

        prompt = (
          f"I'm testing a medical assistant agent. The goal of this agent is to answer patient questions "
          f"relating to the field of {field.lower()}. Imagine which questions a patient would ask to a "
          f"doctor that is treating him. These can be specific or general questions. I want you to write "
          f"a question a patient could ask a medical assistant. The system has detected that the emotion "
          f"the patient is experiencing is "
          f"{emotion}{f' but the face looks {face_emotion}' if face_emotion != emotion else ''}, "
          f"please try to reflect this in the question. "
          f"Please be original, but make them as realistic as possible. "
          f"Write the question without any extra explanation, just the question alone. "
          f"Below is the medical report of the patient, take into consideration the report for the "
          f"question.\n\n"
          f"{summary}"
        )
        question = lm(prompt, temperature=0.7)[0]
        question = question.replace('"', '').replace('\u2019', "'").replace('\u2014', ',')
        questions.append({'emotion': {'text': emotion, 'face': face_emotion}, 'question': question})
      patients.append({'summary': summary, 'questions': questions})
    data[field] = patients
  return data


def load_summary_exs():
  summ = []
  for i in range(1,4):
    with open(f"res/example_summaries/{i}.txt") as f:
      summ.append(f.read())
  return summ


summs = load_summary_exs()

summaries = gen_summaries(n_sums_per_field=5, fields=medical_specialties, summary_exs=summs)
data = gen_questions(n_q_per_sum=5, summaries=summaries, emotions=all_emotions)


with open("res/data.json", "w") as f:
  json.dump(data, f, indent=2)