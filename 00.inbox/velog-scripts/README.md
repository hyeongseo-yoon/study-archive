# velog 발행 파이프라인 가이드

study-archive의 CS 노트를 velog 블로그(`@hyeongseoyoon`)에 발행/갱신하는 로컬 도구.
문제 생기거나 사용법 헷갈릴 때 이 문서 참조.

---

## 1. 개요

- **목적**: `#completed`로 졸업한(마스터한) 개념 노트만 velog에 자동 발행
- **방식**: 로컬 수동 실행 (GitHub Actions 안 씀). "올릴 준비 됐다" 싶을 때 명령 한 번
- **왜 로컬 수동?**
  - 스크립트가 `_inbox`(gitignore)에 있어 클라우드(Actions)에선 못 돌림
  - velog 토큰을 클라우드에 안 둬도 됨 (토큰 회전 취약점 회피)
  - 자주 안 올리니 수동으로 충분

---

## 2. 구성 요소

| 항목 | 위치 | 역할 |
|---|---|---|
| `convert.py` | `_inbox/velog-scripts/` | 노트 → velog 마크다운 변환 (미리보기용) |
| `sync.py` | `_inbox/velog-scripts/` | 실제 발행/갱신 (convert 로직 재사용) |
| `velog` (CLI) | `~/.local/bin/velog` | 비공식 velog-cli (`hamsurang/velog-cli`) |
| `dist/` | `_inbox/velog-scripts/dist/` | 변환 결과물 (임시, gitignore) |

---

## 3. 최초 1회 세팅

이미 완료돼 있음. 새 컴퓨터에서 다시 할 때만 필요.

### velog-cli 설치 (prebuilt 바이너리, Rust 불필요)

```bash
# 최신 리눅스 바이너리 다운로드 & 설치
URL=$(curl -s https://api.github.com/repos/hamsurang/velog-cli/releases/latest \
      | grep browser_download_url | grep 'x86_64-unknown-linux-gnu.tar.xz"' | cut -d'"' -f4)
cd /tmp && curl -sL "$URL" -o velog-cli.tar.xz && tar xf velog-cli.tar.xz
mkdir -p ~/.local/bin
cp velog-cli-*/velog ~/.local/bin/velog && chmod +x ~/.local/bin/velog
velog --version
```

### 인증 (토큰은 민감정보 — 직접)

1. 브라우저에서 velog.io 로그인 → **DevTools → Application → Cookies → velog.io**
2. `access_token`, `refresh_token` 값 복사
3. 로그인:

```bash
velog auth login     # access_token, refresh_token 차례로 붙여넣기(숨김)
velog auth status    # "Logged in as hyeongseoyoon" 뜨면 성공
```

---

## 4. 발행 워크플로우 (평소 사용법)

노트가 `#completed`로 졸업하면 아래 순서로.

```bash
cd ~/study-archive   # 또는 study-archive 루트

# ① 계획 먼저 확인 (실제 발행 안 함, 안전)
python3 _inbox/velog-scripts/sync.py --dry-run

# ② 실제 발행 (live 공개)
python3 _inbox/velog-scripts/sync.py

# ③ sync가 출력한 목록대로 velog 웹에서 새 글을 시리즈에 지정
#    (예: 'OS' 시리즈 <- 파일 디스크립터와 소켓)

# ④ 노트 프론트매터에 기록된 velog_slug/hash 확인 후 커밋
git status
git add computer-science/ && git commit -m "chore: velog 발행 메타 기록"
```

> 팁: 처음 여러 개를 한 번에 올릴 땐 **반드시 `--dry-run` 먼저** 돌려서 create/edit 목록 확인.

### 옵션

| 명령 | 동작 |
|---|---|
| `sync.py` | `#completed` 노트를 live 발행/갱신 |
| `sync.py --dry-run` | 계획만 출력 (API 호출·기록 없음) |
| `sync.py --tag review` | 대상 태그 바꿔 테스트 (기본은 completed) |
| `sync.py --no-publish` | draft로 생성 (⚠️ 아래 제약 참고) |

---

## 5. 동작 원리

### create / edit / skip 판정

노트 프론트매터의 `velog_slug` 유무 + `velog_hash` 비교로 결정:

```
velog_slug 없음           → post create  (새 글)
velog_slug 있음 + hash 다름 → post edit    (기존 글 수정 반영)
velog_slug 있음 + hash 같음 → skip          (변경 없으니 건너뜀)
```

- **slug** = 노트 파일명 (예: `file-descriptor-socket.md` → slug `file-descriptor-socket`). 고정이라 매핑 예측 가능
- **hash** = 변환된 본문의 sha256 앞 12자리. 본문 안 바뀌면 재발행 안 함
- 발행 후 `sync.py`가 노트 프론트매터에 `velog_slug`/`velog_hash`를 **자동 기록** → 다음 실행 때 이걸로 판정

### 변환 규칙 (`convert.py`)

- 프론트매터(`created`, `tags` 등) 제거
- 첫 `# H1` → velog **제목**으로 분리 (본문에선 제거)
- 코드펜스(``` ```) 안은 원문 그대로 (C 코드의 `#include` 등 보호)
- 위키링크 `[[a|b]]`→`b`, 콜아웃 `> [!note]` 변환 (현재 노트엔 없지만 대비)

### 태그 / 시리즈

- **태그**: 폴더명 자동 (`computer-science/os/` → 태그 `os`)
- **시리즈**: 최상위 폴더 → 시리즈 (`os` → "OS"). **단, 자동 지정 불가 → 웹에서 수동** (아래 제약 참고)

---

## 6. 제약 & 주의사항 (중요)

### ⚠️ 시리즈는 CLI로 자동화 불가

- velog-cli에 "글을 시리즈에 넣는" 명령이 **없음**
  - `series edit --order` = 기존 멤버 **재정렬만** (새 글 추가 X)
  - `post create/edit` = series 옵션 없음
- → 새 글 발행 후 **velog 웹 에디터에서 "시리즈에 추가" 수동 지정**
- `sync.py`가 "어느 글을 어느 시리즈에 넣어야 하는지" 목록을 출력해줌

### ⚠️ `post edit`는 published 글만 됨

- draft 상태 글은 slug로 edit 시도 시 `editPost: null` 실패
- 그래서 **실전은 live 발행(`--publish`)이 기본**
- `--no-publish`(draft)로 올리면, 나중에 그 글 수정 반영(edit)이 안 됨. 임시 확인용으로만.

### ⚠️ ASCII 박스 다이어그램은 velog에서 어긋남

- 한글(전각 2칸) + 영문/숫자(반각 1칸) + 박스문자 섞이면 폰트 폭 차이로 정렬 깨짐
- 변환으로 못 고침 (폰트 렌더링 문제)
- **표 구조는 애초에 마크다운 표로 작성** → 폰트 무관하게 깔끔

### ⚠️ velog-cli는 비공식

- velog 내부 GraphQL을 감싼 비공식 도구. velog가 API 바꾸면 깨질 수 있음
- 그때는 velog-cli 새 버전 확인 or 이슈 검색

---

## 7. 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `velog auth status`가 로그아웃 | 토큰 만료. 3장 인증 다시 (`velog auth login`) |
| edit 시 `editPost: null` | draft 글을 edit하려 함. `velog post publish <slug>`로 공개 후 재시도 |
| 같은 글이 중복 발행됨 | 노트에 `velog_slug`가 없어 create로 처리됨. 프론트매터에 `velog_slug`/`velog_hash` 수동 기록하면 이후 edit로 감 |
| 제목 없이 건너뜀 | 노트에 `# H1` 제목 줄이 없음 (빈 스텁이면 정상) |
| velog 렌더링 깨짐 | ASCII 다이어그램이면 6장 참고 (표로 전환) |
| CLI 자체가 안 뜸 | `~/.local/bin`이 PATH에 없을 수 있음. 전체 경로 `~/.local/bin/velog` 사용 |

---

## 8. velog-cli 주요 명령 레퍼런스

```bash
# 인증
velog auth login | status | logout

# 글
velog post create --title "제목" --file post.md --tags "os" --slug my-slug [--publish] [--private]
velog post edit <slug> --file updated.md --title "새 제목" --tags "os"
velog post publish <slug>       # draft → 공개
velog post delete <slug> [-y]   # 삭제

# 시리즈
velog series list
velog series show <slug>
velog series create "이름" --slug 슬러그
velog series edit <slug> --name "새이름" --order slug1,slug2   # 기존 멤버 재정렬만
velog series delete <slug>       # 시리즈만 삭제 (글은 유지)

# 출력 형식: --format compact(JSON) | pretty(기본) | silent
```

---

## 관련

- velog-cli: https://github.com/hamsurang/velog-cli
- 내 velog: https://velog.io/@hyeongseoyoon
