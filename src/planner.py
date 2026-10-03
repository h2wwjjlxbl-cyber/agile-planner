#!/usr/bin/env python3
"""Agile Planner — персональный Agile-планировщик (консольная версия)."""

import argparse
import json
from datetime import date
from pathlib import Path

DATA_FILE = Path("planner_data.json")

STATUSES = {
    "backlog": "Бэклог",
    "todo": "К выполнению",
    "in_progress": "В работе",
    "done": "Готово",
}


class PlannerError(Exception):
    """Ошибка выполнения операции планировщика."""


class Planner:
    """Логика планировщика: задачи, спринты, канбан-доска."""

    def __init__(self, path=DATA_FILE):
        self.path = Path(path)
        self.tasks = []
        self.sprint = None
        self.load()

    # ---------- хранение данных ----------

    def load(self):
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.tasks = data.get("tasks", [])
            self.sprint = data.get("sprint")

    def save(self):
        data = {"tasks": self.tasks, "sprint": self.sprint}
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ---------- задачи ----------

    def add_task(self, title, priority=3, points=1):
        if not title.strip():
            raise PlannerError("Название задачи не может быть пустым")
        if not 1 <= priority <= 5:
            raise PlannerError("Приоритет задаётся числом от 1 до 5")
        task = {
            "id": max((t["id"] for t in self.tasks), default=0) + 1,
            "title": title.strip(),
            "priority": priority,
            "points": points,
            "status": "backlog",
            "sprint": None,
            "created": date.today().isoformat(),
        }
        self.tasks.append(task)
        self.save()
        return task

    def get_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        raise PlannerError(f"Задача с номером {task_id} не найдена")

    def move_task(self, task_id, status):
        if status not in STATUSES:
            raise PlannerError(f"Неизвестный статус: {status}")
        task = self.get_task(task_id)
        task["status"] = status
        self.save()
        return task

    def delete_task(self, task_id):
        self.tasks.remove(self.get_task(task_id))
        self.save()

    # ---------- спринты ----------

    def start_sprint(self, name, days=7):
        if days <= 0:
            raise PlannerError("Длительность спринта должна быть больше нуля")
        self.sprint = {"name": name, "start": date.today().isoformat(), "days": days}
        self.save()
        return self.sprint

    def plan_task(self, task_id):
        if self.sprint is None:
            raise PlannerError("Сначала необходимо начать спринт")
        task = self.get_task(task_id)
        task["sprint"] = self.sprint["name"]
        task["status"] = "todo"
        self.save()
        return task

    def velocity(self):
        """Сумма оценок выполненных задач текущего спринта."""
        if self.sprint is None:
            return 0
        return sum(
            t["points"]
            for t in self.tasks
            if t["sprint"] == self.sprint["name"] and t["status"] == "done"
        )

    # ---------- доска ----------

    def board(self):
        columns = {status: [] for status in STATUSES}
        for task in sorted(self.tasks, key=lambda t: (t["priority"], t["id"])):
            columns[task["status"]].append(task)
        return columns


def print_board(planner):
    if planner.sprint:
        print(f"Текущий спринт: {planner.sprint['name']} ({planner.sprint['days']} дн.)")
    for status, tasks in planner.board().items():
        print(f"\n[{STATUSES[status]}]")
        if not tasks:
            print("  —")
        for t in tasks:
            print(f"  #{t['id']} {t['title']} (приоритет {t['priority']}, оценка {t['points']})")


def build_parser():
    parser = argparse.ArgumentParser(description="Персональный Agile-планировщик")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="добавить задачу в бэклог")
    p_add.add_argument("title")
    p_add.add_argument("-p", "--priority", type=int, default=3)
    p_add.add_argument("-e", "--points", type=int, default=1)

    sub.add_parser("board", help="показать канбан-доску")

    p_sprint = sub.add_parser("sprint", help="начать новый спринт")
    p_sprint.add_argument("name")
    p_sprint.add_argument("-d", "--days", type=int, default=7)

    p_plan = sub.add_parser("plan", help="включить задачу в текущий спринт")
    p_plan.add_argument("id", type=int)

    p_move = sub.add_parser("move", help="изменить статус задачи")
    p_move.add_argument("id", type=int)
    p_move.add_argument("status", choices=list(STATUSES))

    sub.add_parser("stats", help="выполненный объём работ за спринт")

    p_del = sub.add_parser("delete", help="удалить задачу")
    p_del.add_argument("id", type=int)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    planner = Planner()
    try:
        if args.command == "add":
            task = planner.add_task(args.title, args.priority, args.points)
            print(f"Добавлена задача #{task['id']}: {task['title']}")
        elif args.command == "board":
            print_board(planner)
        elif args.command == "sprint":
            sprint = planner.start_sprint(args.name, args.days)
            print(f"Начат спринт «{sprint['name']}» на {sprint['days']} дн.")
        elif args.command == "plan":
            task = planner.plan_task(args.id)
            print(f"Задача #{task['id']} включена в спринт «{task['sprint']}»")
        elif args.command == "move":
            task = planner.move_task(args.id, args.status)
            print(f"Задача #{task['id']}: статус «{STATUSES[task['status']]}»")
        elif args.command == "stats":
            print(f"Выполнено за спринт: {planner.velocity()} ед.")
        elif args.command == "delete":
            planner.delete_task(args.id)
            print(f"Задача #{args.id} удалена")
    except PlannerError as error:
        print(f"Ошибка: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
