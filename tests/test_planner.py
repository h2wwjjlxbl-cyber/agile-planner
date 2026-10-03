"""Модульные тесты планировщика. Запуск: python -m unittest discover -s tests"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from planner import Planner, PlannerError  # noqa: E402


class PlannerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "data.json"
        self.planner = Planner(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_task_goes_to_backlog(self):
        task = self.planner.add_task("Написать отчёт", priority=1, points=3)
        self.assertEqual(task["id"], 1)
        self.assertEqual(task["status"], "backlog")

    def test_empty_title_is_rejected(self):
        with self.assertRaises(PlannerError):
            self.planner.add_task("   ")

    def test_move_task_changes_status(self):
        self.planner.add_task("Задача")
        self.planner.move_task(1, "in_progress")
        self.assertEqual(self.planner.get_task(1)["status"], "in_progress")

    def test_plan_requires_sprint(self):
        self.planner.add_task("Задача")
        with self.assertRaises(PlannerError):
            self.planner.plan_task(1)

    def test_velocity_counts_done_tasks_of_sprint(self):
        self.planner.add_task("A", points=3)
        self.planner.add_task("B", points=5)
        self.planner.start_sprint("Спринт 1")
        self.planner.plan_task(1)
        self.planner.plan_task(2)
        self.planner.move_task(1, "done")
        self.assertEqual(self.planner.velocity(), 3)

    def test_data_is_saved_and_loaded(self):
        self.planner.add_task("Сохранить меня")
        reloaded = Planner(self.path)
        self.assertEqual(reloaded.get_task(1)["title"], "Сохранить меня")


if __name__ == "__main__":
    unittest.main()
