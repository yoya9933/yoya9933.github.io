from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    for project in DATA["projects"]:
        for required in ("case_facts", "case_frame"):
            if not isinstance(project.get(required), dict):
                errors.append(f"{project['slug']} missing {required}")
        for locale in ("zh", "en"):
            path = SITE / project["case"][locale].lstrip("/") / "index.html"
            if not path.is_file():
                errors.append(f"missing case page: {path.relative_to(SITE)}")
                continue
            text = path.read_text(encoding="utf-8")
            if f'data-case-facts="{project["slug"]}"' not in text:
                errors.append(f"facts block missing: {path.relative_to(SITE)}")
            if f'data-case-framing="{project["slug"]}"' not in text:
                errors.append(f"framing block missing: {path.relative_to(SITE)}")
            if "00 / Project framing" not in text:
                errors.append(f"framing heading missing: {path.relative_to(SITE)}")

    event_demo = SITE / "projects/event-checkin/index.html"
    ai_case = SITE / "projects/ai-media-pipeline/index.html"
    if event_demo.is_file() and "24 筆虛構資料" not in event_demo.read_text(encoding="utf-8"):
        errors.append("EventOps case framing must preserve the synthetic-data evidence boundary")
    if ai_case.is_file() and "沒有把它強制成 publish blocker" not in ai_case.read_text(encoding="utf-8"):
        errors.append("AI pipeline case framing must preserve the unenforced quality-gate limitation")

    if errors:
        print("Case Study 2.0 checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Case Study 2.0 checks passed for {len(DATA['projects'])} projects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
