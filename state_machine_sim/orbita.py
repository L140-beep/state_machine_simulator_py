# Подключение библиотек
# В данном случае мы работаем со стандартным вводом и выводом, а тестовые данные у нас в формате JSON
import os
import sys
import io
import json
# def get_log(user_exception_str=None):
#     return '\\n'.join([s for s in [sys.stdout.getvalue(), user_exception_str] if s])

# # Функция, формирующая в случае ошибки результат с начислением 0 баллов и соответствующим "достижением"


# def return_user_error(user_error, user_exception_str=None):
#     return {'score': 0, 'message': user_error, 'log': get_log(user_exception_str)}

# Основная функция запуска пользовательских программ, проверки и начисления очков, вызываемая для каждого теста
# Ключевые параметры
# input - данные для проверки решений (входящие)
# output - данные для проверки решений (исходящие)
# user_programs - массив программ участника в составе решения
def run(run_index, iteration_index, input, output, user_programs):
    SCORE = 0
    xml = user_programs[0]
    return {'score': score, 'message': message, 'log': get_log()}
