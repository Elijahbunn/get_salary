import os

import requests
from terminaltables import DoubleTable
from dotenv import load_dotenv


POPULAR_LANGUAGES = [
    'JavaScript',
    'Ruby',
    'C++',
    'C#',
    'C',
    'Java',
    'Python',
    'Go',
    '1c'
]


def predict_rub_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return
    elif salary_from and salary_to:
        сalculated_salary = (salary_from + salary_to) / 2
        return сalculated_salary
    elif salary_from:
        return salary_from * 1.2
    else:
        return salary_to * 0.8


def get_table(about_vacancies, title):
    languages = [language for language in about_vacancies]
    table_content = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    ]
    for language in languages:
        about_language = [
            language,
            about_vacancies[language]['vacancy_amount'],
            about_vacancies[language]['vacancies_processed'],
            about_vacancies[language]['average_salary']
        ]
        table_content.append(about_language)
    table_instance = DoubleTable(table_content, title)
    table_instance.justify_columns[2] = 'right'
    return table_instance.table


def predict_rub_salary_hh():
    programming_jobs_hh = {}
    area_id = 1
    days_period = 30
    for language in POPULAR_LANGUAGES:
        vacancies_salaries = []
        page_number = 0
        pages = 1
        while page_number < pages:
            payload = {
                'text': f'Программист {language}',
                'area': area_id,
                'period': days_period,
                'page': page_number,
            }
            response = requests.get('https://api.hh.ru/vacancies/', params=payload)
            response.raise_for_status()
            page = response.json()
            vacancies = page['items']
            vacancies_amount = page['found']
            processed_vacancies = 0
            for vacancy in vacancies:
                vacancy_period_salary = vacancy['salary']
                if not vacancy_period_salary:
                    continue
                if vacancy_period_salary['currency'] != 'RUR':
                    continue
                vacancy_salary = predict_rub_salary(
                    vacancy_period_salary['from'],
                    vacancy_period_salary['to']
                    )
                if vacancy_salary:
                    vacancies_salaries.append(vacancy_salary)
            page_number += 1
            pages = page['pages']
        salaries_amount = sum(vacancies_salaries)
        processed_vacancies = len(vacancies_salaries)
        average_salary = 0
        if processed_vacancies:
            average_salary = salaries_amount / processed_vacancies
        vacancy_details = {
            'vacancy_amount': vacancies_amount,
            'vacancies_processed': processed_vacancies,
            'average_salary': int(average_salary)
        }
        programming_jobs_hh[language] = vacancy_details
    return programming_jobs_hh


def predict_rub_salary_sj(sj_token):
    programming_jobs_sj = {}
    for language in POPULAR_LANGUAGES:
        vacancies_salaries = []
        processed_vacancies = 0
        page_number = 0
        vacancy_amount = 0
        more_pages = True
        town_id = 4
        professions_catalog = 48
        vacancies_number = 100
        while more_pages:
            headers = {
                'X-Api-App-Id': sj_token
            }
            payload = {
                'town': town_id,
                'catalogues': professions_catalog,
                'page': page_number,
                'count': vacancies_number,
                'keyword': language
            }
            response = requests.get(
                'https://api.superjob.ru/3.0/vacancies',
                headers=headers,
                params=payload
                )
            response.raise_for_status()
            page = response.json()
            for vacancy_details in page['objects']:
                if vacancy_details['currency'] == 'rub':
                    vacancy_salary = predict_rub_salary(
                        vacancy_details['payment_from'],
                        vacancy_details['payment_to']
                    )
                if vacancy_salary:
                    vacancies_salaries.append(vacancy_salary)
                    processed_vacancies += 1
            page_number += 1
            vacancy_amount += page['total']
            more_pages = page['more']
        salaries_amount = sum(vacancies_salaries)
        processed_vacancies = len(vacancies_salaries)
        average_salary = 0
        if processed_vacancies:
            average_salary = salaries_amount / processed_vacancies
        vacancy_details = {
            'vacancy_amount': vacancy_amount,
            'vacancies_processed': processed_vacancies,
            'average_salary': int(average_salary)
        }
        programming_jobs_sj[language] = vacancy_details
    return programming_jobs_sj


if __name__ == '__main__':
    load_dotenv()
    sj_token = os.environ['SJ_TOKEN']
    print(get_table(predict_rub_salary_hh(), 'HeadHunter Moscow'))
    print()
    print(get_table(predict_rub_salary_sj(sj_token), 'SuperJob Moscow'))
