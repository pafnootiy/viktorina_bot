def get_question_answer():

    with open("quiz_questions/test.txt", "r", encoding='KOI8-R') as file:
        content = list(filter(None, file.read().split('\n\n')))
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
    return all_questions_answers


print(get_question_answer())
