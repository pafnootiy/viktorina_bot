import random
import os


def get_random_file(folder_with_files):

    files = os.listdir(folder_with_files)
    file = random.choice(files)
    path_to_answers_and_questions = os.path.join(folder_with_files, file)

    with open(path_to_answers_and_questions, "r", encoding='KOI8-R') as file:
        content = list(filter(None, file.read().split('\n\n')))
    return content


def get_question_answer(content):
    all_questions_answers = []
    for item in content:
        if "Вопрос" in item:
            question = item

        elif "Ответ" in item:
            answer = item
            question_answer = {
                "question": question,
                "answer": answer
            }

            all_questions_answers.append(question_answer)
    return random.choice(all_questions_answers)
