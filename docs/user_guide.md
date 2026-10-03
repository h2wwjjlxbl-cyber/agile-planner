# Руководство пользователя

## 1. Установка

1. Установить Python версии 3.9 или выше.
2. Получить копию репозитория командой `git clone`.
3. Перейти в каталог проекта.

## 2. Типовой сценарий работы

    python src/planner.py add "Подготовить отчёт" -p 1 -e 3
    python src/planner.py add "Разобрать почту" -p 3 -e 1
    python src/planner.py sprint "Спринт 1" -d 7
    python src/planner.py plan 1
    python src/planner.py move 1 in_progress
    python src/planner.py move 1 done
    python src/planner.py board
    python src/planner.py stats

## 3. Статусы задач

| Статус | Значение |
| --- | --- |
| `backlog` | задача находится в бэклоге |
| `todo` | задача включена в спринт и ожидает выполнения |
| `in_progress` | задача в работе |
| `done` | задача выполнена |

## 4. Хранение данных

Данные сохраняются в файле `planner_data.json` в текущем каталоге. Файл
является личным и не передаётся в репозиторий (исключён в `.gitignore`).

## 5. Проверка работоспособности

    python -m unittest discover -s tests
