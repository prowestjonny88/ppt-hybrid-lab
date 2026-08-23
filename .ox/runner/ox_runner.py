#!/usr/bin/env python3

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    tasks_dir = root / ".ox" / "tasks"
    reports_dir = root / ".ox" / "reports"
    print(f"OX runner ready. tasks={tasks_dir} reports={reports_dir}")


if __name__ == "__main__":
    main()
