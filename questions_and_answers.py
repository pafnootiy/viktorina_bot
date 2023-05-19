import random
import os


class QuizBot:
    def __init__(self, folder_with_files):
        self.questions = self.parse_questions(folder_with_files)

    def parse_questions(self, folder_with_files):
        files = os.listdir(folder_with_files)
        all_questions = []

        for file in files:
            path_to_file = os.path.join(folder_with_files, file)
            with open(path_to_file, "r", encoding='KOI8-R') as f:
                content = list(filter(None, f.read().split('\n\n')))
                questions = self.extract_questions(content)
                all_questions.extend(questions)

        return all_questions

    def extract_questions(self, content):
        questions = []
        question = None

        for item in content:
            if "Вопрос" in item:
                question = item
            elif "Ответ" in item and question is not None:
                answer = item
                question_answer = {"question": question, "answer": answer}
                questions.append(question_answer)

        return questions

    def get_random_question(self):
        return random.choice(self.questions)
