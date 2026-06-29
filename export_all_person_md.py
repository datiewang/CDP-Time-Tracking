import csv
import os
import sys
from collections import defaultdict


def sanitize_filename(name: str) -> str:
    base = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name)
    base = "_".join(base.split())
    return base or "person"


def main(detail_csv: str, output_dir: str):
    if not os.path.exists(detail_csv):
        print(f"Detail CSV not found: {detail_csv}")
        return

    os.makedirs(output_dir, exist_ok=True)

    rows_by_person = defaultdict(list)

    with open(detail_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            person = (row.get("Person") or "").strip()
            if not person:
                continue
            # 只导出 /ONHM 相关用户
            if not person.upper().endswith("/ONHM"):
                continue
            rows_by_person[person].append(row)

    for person, rows in rows_by_person.items():
        rows.sort(key=lambda r: (r.get("Date", ""), r.get("Start", "")))

        filename = f"{sanitize_filename(person)}.md"
        path = os.path.join(output_dir, filename)

        with open(path, "w", encoding="utf-8", newline="") as md:
            md.write(f"# {person}\n\n")
            md.write("| Date | Start | End | Month | Duration (hours) | Subject |\n")
            md.write("| ---- | ----- | --- | ----- | ---------------- | ------- |\n")
            for r in rows:
                date = r.get("Date", "")
                start = r.get("Start", "")
                end = r.get("End", "")
                month = r.get("Month", "")
                dur = r.get("DurationHours", "")
                subj = (r.get("Subject") or "").replace("\n", " ").strip()
                md.write(f"| {date} | {start} | {end} | {month} | {dur} | {subj} |\n")

        print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python export_all_person_md.py detail_csv output_dir")
        sys.exit(1)

    detail_csv = os.path.join(os.getcwd(), sys.argv[1])
    output_dir = os.path.join(os.getcwd(), sys.argv[2])
    main(detail_csv, output_dir)

