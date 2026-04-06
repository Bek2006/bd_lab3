#!/usr/bin/env python3
"""Project diagnostics for bd_lab3 Django project."""
from __future__ import annotations

import importlib
import inspect
import os
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent


@dataclass
class CheckResult:
    name: str
    status: str = "WARN"
    messages: list[str] = field(default_factory=list)

    def ok(self, message: str) -> None:
        self.status = "OK" if self.status != "FAIL" else self.status
        self.messages.append(f"[OK] {message}")

    def warn(self, message: str) -> None:
        if self.status != "FAIL":
            self.status = "WARN"
        self.messages.append(f"[WARN] {message}")

    def fail(self, message: str) -> None:
        self.status = "FAIL"
        self.messages.append(f"[FAIL] {message}")


class Diagnostics:
    def __init__(self) -> None:
        self.results: dict[str, CheckResult] = {}
        self.context: dict[str, Any] = {
            "django_available": False,
            "settings_module": None,
            "django_ready": False,
            "db_ok": False,
            "imported_modules": {},
            "url_patterns": [],
            "view_names": set(),
            "used_views": set(),
        }

    def section(self, name: str) -> CheckResult:
        result = self.results.setdefault(name, CheckResult(name=name))
        return result

    def _short_tb(self, exc: BaseException, limit: int = 5) -> str:
        lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
        trimmed = "".join(lines[-limit:]).strip()
        return trimmed

    def detect_settings_module(self) -> str:
        default_module = "bd_lab3.settings"
        if (ROOT_DIR / "bd_lab3" / "settings.py").exists():
            return default_module
        for candidate in ROOT_DIR.iterdir():
            if candidate.is_dir() and (candidate / "settings.py").exists():
                return f"{candidate.name}.settings"
        return default_module

    def check_structure(self) -> None:
        result = self.section("Структура проекта")
        required_paths = [
            "manage.py",
            "requirements.txt",
            "bd_lab3",
            "bd_lab3/settings.py",
            "bd_lab3/urls.py",
            "bd_lab3/wsgi.py",
            "bd_lab3/asgi.py",
            "posts",
            "posts/views.py",
            "posts/models.py",
            "posts/urls.py",
            "posts/admin.py",
            "posts/templates",
        ]
        optional_templates = ["courses.html", "students.html", "enrollments.html", "base.html"]

        missing = []
        for path_str in required_paths:
            path = ROOT_DIR / path_str
            if path.exists():
                result.ok(f"Найдено: {path_str}")
            else:
                missing.append(path_str)
                result.warn(f"Не найдено по ожидаемому пути: {path_str}")
                name = Path(path_str).name
                matches = [str(p.relative_to(ROOT_DIR)) for p in ROOT_DIR.rglob(name) if p.is_file() or p.is_dir()]
                if matches:
                    result.warn(f"Похожие пути для '{name}': {', '.join(matches[:5])}")

        template_dir = ROOT_DIR / "posts" / "templates"
        for tpl in optional_templates:
            tpl_path = template_dir / tpl
            if tpl_path.exists():
                result.ok(f"Шаблон на диске найден: posts/templates/{tpl}")
            else:
                result.warn(f"Шаблон на диске не найден: posts/templates/{tpl}")

        if not missing:
            result.ok("Ключевая структура проекта присутствует.")
        elif len(missing) <= 3:
            result.warn("Есть отсутствующие элементы структуры, но проект может быть частично работоспособен.")
        else:
            result.fail("Отсутствует много ключевых файлов/папок; требуется восстановление структуры.")

    def check_imports(self) -> None:
        result = self.section("Импорты")
        settings_module = self.detect_settings_module()
        self.context["settings_module"] = settings_module
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
        if str(ROOT_DIR) not in sys.path:
            sys.path.insert(0, str(ROOT_DIR))

        import_targets = [
            ("django", "django"),
            ("settings", settings_module),
            ("root urls", "bd_lab3.urls"),
            ("posts.models", "posts.models"),
            ("posts.views", "posts.views"),
            ("posts.urls", "posts.urls"),
        ]

        for label, target in import_targets:
            try:
                module = importlib.import_module(target)
                self.context["imported_modules"][target] = module
                result.ok(f"Импорт успешен: {label} ({target})")
                if target == "django":
                    self.context["django_available"] = True
            except Exception as exc:  # noqa: BLE001 - diagnostic script should continue
                result.fail(f"Ошибка импорта {label} ({target}): {exc}")
                result.warn(f"Traceback: {self._short_tb(exc)}")

        if self.context["django_available"]:
            result.ok(f"DJANGO_SETTINGS_MODULE={settings_module}")

    def check_django_setup(self) -> None:
        result = self.section("Django setup")
        if not self.context.get("django_available"):
            result.fail("Django не импортирован; setup недоступен.")
            return

        try:
            import django
            from django.conf import settings
            from django.core.management import call_command

            django.setup()
            self.context["django_ready"] = True
            result.ok("django.setup() выполнен успешно")
            result.ok(f"INSTALLED_APPS count: {len(settings.INSTALLED_APPS)}")

            if "posts" in settings.INSTALLED_APPS:
                result.ok("Приложение 'posts' зарегистрировано в INSTALLED_APPS")
            else:
                result.fail("Приложение 'posts' не найдено в INSTALLED_APPS")

            templates = getattr(settings, "TEMPLATES", [])
            if templates:
                result.ok(f"TEMPLATES настроены (конфигураций: {len(templates)})")
            else:
                result.warn("TEMPLATES пустой или отсутствует")

            try:
                call_command("check", "--deploy", verbosity=0)
                result.ok("django.core.management call_command('check', '--deploy') прошел")
            except Exception as exc:  # noqa: BLE001
                result.warn(f"Команда check --deploy вернула предупреждения/ошибки: {exc}")
        except Exception as exc:  # noqa: BLE001
            result.fail(f"Ошибка при django.setup(): {exc}")
            result.warn(f"Traceback: {self._short_tb(exc)}")

    def _flatten_patterns(self, patterns: list[Any], prefix: str = "") -> list[tuple[str, Any]]:
        items: list[tuple[str, Any]] = []
        for p in patterns:
            route = str(getattr(p, "pattern", ""))
            full_route = f"{prefix}{route}".replace("^", "").replace("$", "")
            if hasattr(p, "url_patterns"):
                items.extend(self._flatten_patterns(list(p.url_patterns), prefix=full_route))
            else:
                items.append((full_route, getattr(p, "callback", None)))
        return items

    def check_urls(self) -> None:
        result = self.section("URL-маршруты")
        if not self.context.get("django_ready"):
            result.fail("Django не инициализирован; проверка URL невозможна.")
            return

        try:
            from django.urls import get_resolver

            resolver = get_resolver()
            flat = self._flatten_patterns(list(resolver.url_patterns))
            self.context["url_patterns"] = flat
            if not flat:
                result.fail("URL patterns не найдены.")
                return

            result.ok(f"Всего обнаружено маршрутов: {len(flat)}")
            required = ["/", "/students", "/enrollments"]

            normalized = []
            for route, callback in flat:
                path = "/" + route.lstrip("/")
                path = path.rstrip("/") if path != "/" else path
                callback_name = getattr(callback, "__name__", str(callback))
                normalized.append((path, callback_name))
                self.context["used_views"].add(callback_name)

            for must in required:
                if any(path == must for path, _ in normalized):
                    target = next(cb for path, cb in normalized if path == must)
                    result.ok(f"Маршрут {must} найден -> {target}")
                else:
                    result.fail(f"Маршрут {must} НЕ найден")

            for extra in ["/queries", "/olap"]:
                hit = [cb for path, cb in normalized if path == extra]
                if hit:
                    result.ok(f"Доп. маршрут {extra} найден -> {hit[0]}")

            preview = ", ".join(f"{p} -> {v}" for p, v in normalized[:12])
            if preview:
                result.ok(f"Первые маршруты: {preview}")
        except Exception as exc:  # noqa: BLE001
            result.fail(f"Ошибка проверки URL: {exc}")
            result.warn(f"Traceback: {self._short_tb(exc)}")

    def check_templates(self) -> None:
        result = self.section("Шаблоны")
        if not self.context.get("django_ready"):
            result.fail("Django не инициализирован; проверка шаблонов невозможна.")
            return

        try:
            from django.template.loader import get_template

            templates = ["courses.html", "students.html", "enrollments.html", "base.html"]
            for tpl in templates:
                try:
                    get_template(tpl)
                    result.ok(f"Шаблон доступен через loader: {tpl}")
                except Exception as exc:  # noqa: BLE001
                    result.warn(f"Шаблон недоступен через loader: {tpl} ({exc})")
        except Exception as exc:  # noqa: BLE001
            result.fail(f"Ошибка проверки шаблонов: {exc}")
            result.warn(f"Traceback: {self._short_tb(exc)}")

    def check_database(self) -> None:
        result = self.section("База данных")
        if not self.context.get("django_ready"):
            result.fail("Django не инициализирован; проверка БД невозможна.")
            return

        try:
            from django.conf import settings
            from django.db import connection

            db = settings.DATABASES.get("default", {})
            result.ok(f"ENGINE: {db.get('ENGINE', '<not set>')}")
            result.ok(f"NAME: {db.get('NAME', '<not set>')}")
            result.ok(f"HOST: {db.get('HOST', '<not set>')}")
            result.ok(f"PORT: {db.get('PORT', '<not set>')}")
            result.ok(f"USER: {db.get('USER', '<not set>')}")
            result.ok("PASSWORD: задан" if db.get("PASSWORD") else "PASSWORD: не задан")

            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    value = cursor.fetchone()
                self.context["db_ok"] = True
                result.ok(f"Подключение к БД успешно, SELECT 1 -> {value}")
            except Exception as exc:  # noqa: BLE001
                result.fail(f"Не удалось подключиться к БД / выполнить SELECT 1: {exc}")
                result.warn(f"Traceback: {self._short_tb(exc)}")
        except Exception as exc:  # noqa: BLE001
            result.fail(f"Ошибка чтения DATABASES/connection: {exc}")
            result.warn(f"Traceback: {self._short_tb(exc)}")

    def check_models(self) -> None:
        result = self.section("Модели")
        if not self.context.get("django_ready"):
            result.fail("Django не инициализирован; проверка моделей невозможна.")
            return

        try:
            from django.apps import apps
            from django.db import connection

            if not apps.is_installed("posts"):
                result.fail("Приложение posts не зарегистрировано в app registry")
                return

            result.ok("Приложение posts зарегистрировано в app registry")
            post_models = apps.get_app_config("posts").get_models()
            model_list = list(post_models)
            if not model_list:
                result.warn("В приложении posts не найдено моделей")
                return

            model_names = [m.__name__ for m in model_list]
            result.ok(f"Модели posts: {', '.join(model_names)}")
            for expected in ["Teacher", "Course", "Student", "StudentCourse"]:
                if expected in model_names:
                    result.ok(f"Модель найдена: {expected}")
                else:
                    result.warn(f"Модель не найдена: {expected}")

            if self.context.get("db_ok"):
                existing_tables = set(connection.introspection.table_names())
                for model in model_list:
                    table_name = model._meta.db_table
                    if table_name in existing_tables:
                        result.ok(f"Таблица существует: {table_name}")
                    else:
                        result.warn(f"Таблица не найдена в БД: {table_name}")
            else:
                result.warn("Проверка таблиц пропущена: нет соединения с БД")
        except Exception as exc:  # noqa: BLE001
            result.fail(f"Ошибка проверки моделей: {exc}")
            result.warn(f"Traceback: {self._short_tb(exc)}")

    def check_views(self) -> None:
        result = self.section("Представления")
        try:
            views_module = importlib.import_module("posts.views")
            public_views = []
            for name, obj in inspect.getmembers(views_module):
                if name.startswith("_"):
                    continue
                if inspect.isfunction(obj) and obj.__module__ == "posts.views":
                    public_views.append(name)
                elif inspect.isclass(obj) and obj.__module__ == "posts.views":
                    public_views.append(name)

            if not public_views:
                result.warn("Публичные view в posts.views не найдены")
                return

            self.context["view_names"] = set(public_views)
            result.ok(f"Публичные view/утилиты в posts.views: {', '.join(public_views)}")

            used = self.context.get("used_views", set())
            if used:
                for view_name in sorted(public_views):
                    if view_name in used:
                        result.ok(f"View используется в URLconf: {view_name}")
                    else:
                        result.warn(f"View не замечен в URLconf: {view_name}")
            else:
                result.warn("Связь views с URLconf не проверена (URL section недоступна)")
        except Exception as exc:  # noqa: BLE001
            result.fail(f"Ошибка проверки views: {exc}")
            result.warn(f"Traceback: {self._short_tb(exc)}")

    def print_report(self) -> None:
        print("=" * 88)
        print("DIAGNOSTIC REPORT: bd_lab3")
        print(f"Root: {ROOT_DIR}")
        print("=" * 88)

        order = [
            "Структура проекта",
            "Импорты",
            "Django setup",
            "URL-маршруты",
            "Шаблоны",
            "База данных",
            "Модели",
            "Представления",
        ]

        for section_name in order:
            result = self.results.get(section_name)
            if not result:
                continue
            print(f"\n## {section_name}: {result.status}")
            for msg in result.messages:
                print(f" - {msg}")

        print("\n" + "=" * 88)
        print("ИТОГ")
        print("=" * 88)

        status_priority = {"OK": 0, "WARN": 1, "FAIL": 2}
        sorted_results = sorted(self.results.values(), key=lambda r: status_priority.get(r.status, 9), reverse=True)

        fail_sections = [r.name for r in sorted_results if r.status == "FAIL"]
        warn_sections = [r.name for r in sorted_results if r.status == "WARN"]
        ok_sections = [r.name for r in sorted_results if r.status == "OK"]

        print(f"Работает точно: {', '.join(ok_sections) if ok_sections else 'нет подтверждённых блоков'}")
        print(f"Требует внимания: {', '.join(warn_sections) if warn_sections else 'нет'}")
        print(f"Не работает / блокировано: {', '.join(fail_sections) if fail_sections else 'нет'}")

        print("\nПриоритет исправлений:")
        if fail_sections:
            for idx, name in enumerate(fail_sections, 1):
                print(f" {idx}. {name}")
        elif warn_sections:
            for idx, name in enumerate(warn_sections, 1):
                print(f" {idx}. {name}")
        else:
            print(" 1. Критичных проблем не обнаружено.")

    def run(self) -> None:
        self.check_structure()
        self.check_imports()
        self.check_django_setup()
        self.check_urls()
        self.check_templates()
        self.check_database()
        self.check_models()
        self.check_views()
        self.print_report()


def main() -> None:
    Diagnostics().run()


if __name__ == "__main__":
    main()
