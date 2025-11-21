import json
from markdown_pdf import MarkdownPdf, Section


with open("./res/questionnaire_template.md", "r") as f:
    questionnaire_template = f.read()

with open("./res/answer_template.md", "r") as f:
    answer_template = f.read()

with open("./res/answers.json", "r") as f:
    data = json.load(f)

md_str = questionnaire_template

n_answers = 10

for i, answer in enumerate(data[:n_answers]):
    md_str += answer_template.format(
        n_scenario=(i+1),
        patient_summary=answer['patient_summary'],
        face_emotion=answer['face_emot'],
        text_emotion=answer['text_emot'],
        patient_question=answer['question_text'],
        answer=answer['answer'].replace('\n', ' '),
    )

with open('questionnaire.md', 'w') as f:
    f.write(md_str)

pdf = MarkdownPdf()
pdf.add_section(Section(md_str))
pdf.save("questionnaire.pdf")