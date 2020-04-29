import requests
import os
from multiprocessing import Pool
from tqdm import tqdm
from methods import *

DIR = "tasks"
login = "ewandevyaterikov"
password = '***'
course = 0

style = '<head><link rel="stylesheet" href="https://yastatic.net/s3/lyceum/frontend/static/40.0-rc-39c44ae1/desktop-ru/client.css"><link rel="stylesheet" href="https://yastatic.net/s3/lyceum/frontend/static/40.0-rc-39c44ae1/desktop-ru/material.css"><link rel="stylesheet" type="text/css" href="https://yastatic.net/s3/lyceum/frontend/static/40.0-rc-39c44ae1/desktop-ru/code-mirror-editor.css"><link rel="stylesheet" href="https://yastatic.net/s3/lyceum/frontend/static/40.0-rc-39c44ae1/desktop-ru/vendors.css"></head>'
symb = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]


class Solution:
    def __init__(self, code, path):
        self.code = code
        self.path = path

    def __str__(self):
        return self.path


class Lesson:
    def __init__(self, name, solutions):
        self.solutions = solutions
        self.name = name
        self.material = ''

    def add(self, item):
        if item is not None:
            self.solutions.append(item)

    def __str__(self):
        r = ""
        for i in self.solutions:
            r += i.__str__() + "\n"
        return r


def save_lesson(lesson, dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    if not lesson:
        return
    name = lesson.name
    lesson_path = os.path.join(dir, name)
    os.mkdir(lesson_path)
    for i in lesson.solutions:
        save_task(i, name)
    save_material(lesson)

def save_task(solution, name):
    dir = os.path.join(
        DIR, name, solution.path[: solution.path.rfind("/")]
    )
    if not os.path.exists(dir):
        os.mkdir(dir)
    code = solution.code


    if type(code) is bytes:
        with open(os.path.join(DIR, name, solution.path), "wb") as file:
            file.write(code)
    else:
        with open(os.path.join(DIR, name, solution.path), "w") as file:
            file.write(code)

def save_material(lesson):
    for enc in ['utf-8', 'windows-1252', 'windows-1250', 'ascii']:
        try:
            lesson.material = style + lesson.material.replace('\n', '')
            with open(os.path.join(os.path.join(DIR, lesson.name), 'material.html'), 'wt', encoding=enc) as html:
                html.write(lesson.material)
            break
        except UnicodeEncodeError:
            print("Материал не получилось сохранить из-за Unicode ошибки")
            print("Пробую другую кодировку...")





def download_all_tasks(s, lesson_id, course_id, i):
    lesson_title = get_lesson_info(s, lesson_id, group_id, course_id)["title"]
    lesson_title = str(i) + ". " + lesson_title
    for sym in symb:
        lesson_title = lesson_title.replace(sym, " ")
    lesson = Lesson(lesson_title, [])
    all_tasks = get_all_tasks(s, lesson_id, course_id)
    for tasks_type in all_tasks:
        for task in tasks_type["tasks"]:
            lesson.add(download_task(task, titles[tasks_type["type"]]))

    lesson.material = download_material(s, lesson_id, course_id)

    return lesson

def download_material(s, lesson_id, course_id):
    material_id = get_material_id(s, lesson_id)
    if material_id:
        material_html = get_material_html(s, lesson_id, group_id, material_id)
    else:
        material_html = ''
    return material_html
    

def download_task(task, type_title):
    if not task["solution"] is None:
        task_solution = get_solution(s, task["solution"]["id"])
        task_title = task["title"]
        file = task_solution["file"]
        if not file is None:
            file_type = os.path.split(file["name"])[1].split(".")[-1]
            if file_type == "py":
                code = file["sourceCode"]
            else:
                code = requests.get(file["url"]).content
            for sym in symb:
                task_title = task_title.replace(sym, " ")
            return Solution(code, f"{type_title}/{task_title}.{file_type}")
    return None


os.system('rm -rf tasks')
os.system('mkdir tasks')
s = requests.Session()
auth(s, login, password)


ids = get_courses_groups_ids(s)[course]
course_id = ids["course_id"]
group_id = ids["group_id"]
lesson_ids = get_lesson_ids(s, course_id, group_id)

lesson_ids = lesson_ids[::-1]

bar = tqdm(
    range(len(lesson_ids)),
    desc="yandex",
    unit="lesson",
    bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
)

def download(lesson_id, i):
    lesson = download_all_tasks(s, lesson_id, course_id, i)
    save_lesson(lesson, DIR)

for i in bar:
    download(lesson_ids[i], i)

