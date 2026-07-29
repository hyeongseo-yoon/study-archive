#!/usr/bin/env python3
"""#completed 스터디 노트를 velog에 발행/갱신 (로컬 수동 실행).

convert.py 의 변환 로직을 재사용해서:
  1. 노트 -> velog용 마크다운 변환
  2. 프론트매터의 velog_slug/velog_hash 로 create / edit / skip 판정
  3. velog-cli 로 발행한 뒤 slug·hash 를 노트 프론트매터에 기록
  4. 폴더 = 시리즈로 묶음 (series create -> series edit --order)

전제: velog-cli 설치 + 로그인 완료 (`velog auth status` 로 확인).
사용:
  python3 sync.py --dry-run    # API 호출 없이 계획만 출력 (먼저 이걸로 확인)
  python3 sync.py              # 실제 발행/갱신
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from convert import (
    ROOT, SOURCE_DIR,
    split_frontmatter, parse_frontmatter, transform_body,
    derive_tags, derive_series, content_hash,
)

VELOG = str(Path.home() / ".local" / "bin" / "velog")


def run_velog(args):
    """velog-cli 실행 (compact 출력). 실패 시 예외."""
    res = subprocess.run([VELOG, "--format", "compact", *args],
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"velog {' '.join(args)} 실패:\n{res.stderr or res.stdout}")
    return res.stdout


def upsert_fm_fields(text, fields):
    """프론트매터 블록 안에서 key: value 들을 갱신/추가하고 나머지 원문은 보존."""
    if not text.startswith("---\n"):
        raise ValueError("프론트매터 없음")
    end = text.find("\n---", 3)
    head_lines = text[4:end].splitlines()
    rest = text[end:]  # '\n---' 이후 전부
    for key, value in fields.items():
        pat = re.compile(rf"^{re.escape(key)}:")
        new_line = f"{key}: {value}"
        for i, ln in enumerate(head_lines):
            if pat.match(ln):
                head_lines[i] = new_line
                break
        else:
            head_lines.append(new_line)
    return "---\n" + "\n".join(head_lines) + rest


def collect(tag):
    """대상 노트 수집 + 변환 + create/edit/skip 판정."""
    notes = []
    for md in sorted(SOURCE_DIR.rglob("*.md")):
        raw = md.read_text(encoding="utf-8")
        fm_lines, body = split_frontmatter(raw)
        meta = parse_frontmatter(fm_lines)
        if tag not in meta["tags"]:
            continue
        title, cleaned = transform_body(body)
        if not title:
            print(f"  ! 제목(H1) 없음, 건너뜀: {md.relative_to(ROOT)}", file=sys.stderr)
            continue

        new_hash = content_hash(cleaned)
        published = bool(meta.get("velog_slug"))
        if not published:
            action = "create"
        elif meta.get("velog_hash") != new_hash:
            action = "edit"
        else:
            action = "skip"

        notes.append({
            "path": md, "raw": raw, "title": title, "body": cleaned,
            "tags": derive_tags(md), "series": derive_series(md),
            "slug": md.stem, "hash": new_hash, "created": meta.get("created", ""),
            "action": action,
        })
    return notes


def publish(note, do_publish):
    """단일 노트를 velog에 create/edit 하고 프론트매터에 slug·hash 기록."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(note["body"])
        tmp = f.name
    tags = ",".join(note["tags"])
    try:
        if note["action"] == "create":
            args = ["post", "create", "--title", note["title"], "--file", tmp,
                    "--tags", tags, "--slug", note["slug"]]
            if do_publish:
                args.append("--publish")
            run_velog(args)
        elif note["action"] == "edit":
            run_velog(["post", "edit", note["slug"], "--file", tmp,
                       "--title", note["title"], "--tags", tags])
    finally:
        Path(tmp).unlink(missing_ok=True)

    new_text = upsert_fm_fields(note["raw"],
                                {"velog_slug": note["slug"], "velog_hash": note["hash"]})
    note["path"].write_text(new_text, encoding="utf-8")


def print_series_reminder(notes):
    """새로 만든 글은 velog 웹에서 수동으로 시리즈에 넣어야 함 (CLI 미지원).

    어떤 글을 어느 시리즈에 넣을지 안내만 출력한다.
    """
    new = {}
    for n in notes:
        if n["action"] == "create" and n["series"]:
            new.setdefault(n["series"], []).append(n["title"])
    if not new:
        return
    print("\n[velog 웹에서 시리즈 지정 필요 — 새로 올린 글]")
    for series, titles in new.items():
        for t in titles:
            print(f"  '{series}' 시리즈  <-  {t}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="completed", help="발행 대상 상태 태그 (기본: completed)")
    ap.add_argument("--dry-run", action="store_true", help="API 호출 없이 계획만 출력")
    ap.add_argument("--no-publish", action="store_true", help="공개하지 않고 draft로 생성")
    args = ap.parse_args()

    notes = collect(args.tag)
    if not notes:
        print(f"대상 노트 없음 (#{args.tag} computer-science 노트 0건)")
        return

    todo = [n for n in notes if n["action"] != "skip"]
    print(f"대상 태그 #{args.tag} | 전체 {len(notes)}건 "
          f"(create/edit {len(todo)}, skip {len(notes) - len(todo)})"
          f"{'  [DRY-RUN]' if args.dry_run else ''}\n")
    for n in notes:
        print(f"  [{n['action']:>6}] {n['title']}  (slug={n['slug']}, series={n['series']}, tags={n['tags']})")
    print()

    if args.dry_run:
        print("dry-run이라 실제 발행/기록 안 함.")
        return

    for n in todo:
        publish(n, do_publish=not args.no_publish)
        print(f"  ✓ {n['action']}: {n['title']}")
    print_series_reminder(notes)

    # 매핑(velog_slug/hash)이 기록된 노트 = 이번에 발행/갱신한 것들.
    # 이 목록만 git add 하면 폴더 구조와 무관하게 정확히 커밋됨.
    changed = [str(n["path"].relative_to(ROOT)) for n in todo]
    print("\n[매핑 기록된 파일 — 이 목록만 커밋]")
    for c in changed:
        print(f"CHANGED\t{c}")
    print("\n완료.")


if __name__ == "__main__":
    main()
