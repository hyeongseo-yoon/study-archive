#!/usr/bin/env python3
"""옵시디언 스터디 노트를 velog 발행용 마크다운으로 변환.

- computer-science/ 아래 노트 중 지정한 상태 태그를 가진 것만 대상
- 프론트매터를 파싱해서 velog 제목/태그/멱등 매핑(slug, hash)을 뽑고 본문만 남김
- 결과를 dist/ 에 velog용 .md 로 쓰고, create/update 판정을 요약표로 출력

의존성 없음 (Python 표준 라이브러리만 사용). GitHub Actions 러너에서 그대로 실행 가능.
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

# 이 스크립트 기준 study-archive 루트 (_inbox/velog-scripts/convert.py -> 루트)
ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "computer-science"

# 최상위 폴더 -> velog 시리즈 표시명 (독자에게 보이는 이름, 없으면 폴더명 그대로)
SERIES_NAMES = {
    "os": "OS",
    "network": "Network",
    "algorithm": "Algorithm",
    "architecture": "Architecture",
    "data-structure": "Data Structure",
}



def split_frontmatter(text):
    """맨 앞 --- ... --- 블록을 (frontmatter_lines, body) 로 분리. 없으면 ([], 원문)."""
    if not text.startswith("---\n"):
        return [], text
    end = text.find("\n---", 3)
    if end == -1:
        return [], text
    fm = text[4:end].splitlines()
    body = text[end + len("\n---"):].lstrip("\n")
    return fm, body


def parse_frontmatter(fm_lines):
    """우리 노트 형태에 맞춘 최소 YAML 파서.

    지원 형태:
        created: 2026-07-22
        velog_slug: some-slug
        tags:
          - review
          - completed
    """
    meta = {"tags": []}
    key = None
    for line in fm_lines:
        if not line.strip():
            continue
        if re.match(r"^\s*-\s+", line):  # 리스트 항목 (tags 하위)
            if key == "tags":
                meta["tags"].append(line.split("-", 1)[1].strip())
            continue
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if key == "tags":
            if val.startswith("["):  # inline 리스트: [a, b]
                meta["tags"] = [t.strip() for t in val[1:-1].split(",") if t.strip()]
        else:
            meta[key] = val
    return meta


def transform_body(body):
    """옵시디언 전용 문법을 velog 마크다운으로 변환하고 H1 제목을 분리.

    반환: (title, cleaned_body)
    - H1(첫 '# ...')을 velog 제목으로 뽑고 본문에서 제거
    - 위키링크 [[a|b]] -> b, [[a]] -> a (현재 노트엔 없지만 방어적으로)
    - 콜아웃 '> [!type] 제목' 첫 줄 -> '> **제목/type**'
    - 인라인 #태그 제거는 하지 않음 (본문 C 코드의 #include 등을 깨뜨리므로)
    """
    title = None
    in_fence = False
    out_lines = []
    for line in body.splitlines():
        if re.match(r"^\s*```", line):  # 코드펜스 진입/이탈 토글
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:  # 코드블록 안은 원문 그대로 (# 주석 등을 제목/콜아웃으로 오인 방지)
            out_lines.append(line)
            continue
        if title is None:
            m = re.match(r"^#\s+(.*)$", line)
            if m:
                title = m.group(1).strip()
                continue  # 제목 줄은 본문에서 제외
        # 콜아웃 헤더
        c = re.match(r"^>\s*\[!(\w+)\]\s*(.*)$", line)
        if c:
            label = c.group(2).strip() or c.group(1).capitalize()
            line = f"> **{label}**"
        # 위키링크
        line = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", line)
        line = re.sub(r"\[\[([^\]]+)\]\]", r"\1", line)
        out_lines.append(line)

    cleaned = "\n".join(out_lines).strip() + "\n"
    return title, cleaned


def derive_tags(path):
    """소스 경로의 폴더 구조를 그대로 velog 태그로. 예: computer-science/os/x.md -> ['os']."""
    rel = path.relative_to(SOURCE_DIR)
    return list(rel.parts[:-1])  # 파일명 제외한 폴더 경로 = 태그


def derive_series(path):
    """최상위 폴더 = velog 시리즈. 예: computer-science/os/x.md -> 'OS'. 루트 직속이면 None."""
    rel = path.relative_to(SOURCE_DIR)
    if len(rel.parts) <= 1:
        return None
    folder = rel.parts[0]
    return SERIES_NAMES.get(folder, folder)


def content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="completed",
                    help="발행 대상으로 삼을 상태 태그 (기본: completed)")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "dist"),
                    help="변환 결과 출력 디렉토리")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for md in sorted(SOURCE_DIR.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        fm_lines, body = split_frontmatter(text)
        meta = parse_frontmatter(fm_lines)
        if args.tag not in meta["tags"]:
            continue

        title, cleaned = transform_body(body)
        rel = md.relative_to(ROOT)
        if not title:
            print(f"  ! 제목(H1) 없음, 건너뜀: {rel}", file=sys.stderr)
            continue

        new_hash = content_hash(cleaned)
        slug = meta.get("velog_slug")
        old_hash = meta.get("velog_hash")

        if not slug:
            action = "create"
        elif old_hash != new_hash:
            action = "update"
        else:
            action = "skip (변경 없음)"

        out_file = out_dir / (md.stem + ".md")
        out_file.write_text(cleaned, encoding="utf-8")

        rows.append({
            "title": title,
            "source": str(rel),
            "series": derive_series(md),
            "tags": derive_tags(md),
            "hash": new_hash,
            "action": action,
            "out": out_file,
        })

    # 요약 출력
    if not rows:
        print(f"대상 노트 없음 (태그 '#{args.tag}' 가진 computer-science 노트 0건)")
        return

    print(f"대상 태그: #{args.tag}  |  변환 {len(rows)}건 -> {out_dir}\n")
    for r in rows:
        print(f"[{r['action']:>16}]  {r['title']}")
        print(f"                     src   : {r['source']}")
        print(f"                     series: {r['series']}  tags: {r['tags']}  hash: {r['hash']}")
        print(f"                     out   : {r['out'].relative_to(ROOT)}")
        print()


if __name__ == "__main__":
    main()
