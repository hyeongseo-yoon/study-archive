## 구조

- Working Directory
	add/reset
- Staging Area
	commit/amend
- Repository

## 기본 사용법
git clone [URL] -> 가져오기
git add .  (add 취소 : git restore --staged <파일명>)
git commit -m "message"
git push origin main

최근 커밋으로 돌아가기 - git restore <파일명>

## Conventional Commits

| **타입(Type)**   | **의미**          | **공부 아카이브 활용 예시**           |
| -------------- | --------------- | --------------------------- |
| **`feat`**     | 새로운 내용 추가       | `feat: 가상 메모리 페이징 개념 정리 추가` |
| **`docs`**     | 문서 수정 (오타, 서식)  | `docs: README.md 학과 정보 수정`  |
| **`fix`**      | 잘못된 정보 수정       | `fix: 세마포어 동작 원리 오개념 수정`    |
| **`refactor`** | 내용의 구조나 가독성 개선  | `refactor: 알고리즘 폴더 구조 재배치`  |
| **`chore`**    | 설정 변경 (인증 정보 등) | `chore: .gitignore 파일 업데이트` |
Ex) 

git commit -m "feat: OS 데드락(Deadlock) 발생 조건 4가지 정리"
git commit -m "feat: 백준 1234번 C언어 그리디 풀이 추가"
git commit -m "refactor: 옵시디언 템플릿 적용 및 Mermaid 차트 추가"

여러 내용이면

git commit -m "feat: 운영체제 및 알고리즘 학습 노트 추가" -m "- OS: 데드락 발생 조건 4가지 정리 - Algorithm: 백준 1234번(그리디) 풀이 추가 - CS: 캐시 메모리 매핑 방식 요약"

근데 나눠서 하는게 나을 듯

- `git add OS_note.md` -> `git commit -m "feat: OS 데드락 정리"`
    
- `git add Algo_1234.c` -> `git commit -m "feat: 백준 1234번 풀이"`
    
- `git push origin main` (푸시는 한 번에!)

## 협업 워크플로우 (팀 프로젝트)

**정의**
여러 명이 하나의 저장소를 같이 개발할 때, 브랜치를 나눠 독립적으로 작업하고 PR(Pull Request)을 통해 리뷰받은 뒤 main에 합치는 방식.

**기본 흐름**
```
1. 이슈/작업 확인
        │
2. 브랜치 생성 (main에서 분기)
        │
3. 로컬에서 작업 (commit 여러 번)
        │
4. 원격에 push
        │
5. Pull Request(PR) 생성
        │
6. 코드 리뷰 (동료가 코멘트/승인)
        │
7. main에 merge
        │
8. 브랜치 삭제
```

**원리**
- `main`은 항상 배포 가능한 안정 상태로 유지하고, 새 기능/수정은 별도 브랜치(`feature/login`, `fix/navbar-bug` 등)에서 작업한다.
-
- 여러 개발자가 각자 브랜치를 파서 **동시에 독립적으로** 작업 가능 (서로 기다릴 필요 없음).
 
- **Fork vs Branch**
    - 오픈소스 기여: 남의 저장소를 내 계정으로 fork → 내 fork에서 브랜치 작업 → 원본 저장소로 PR
    - 같은 팀 프로젝트: 하나의 저장소를 공유하고 각자 브랜치만 나눠서 작업 (fork 불필요)
- **Pull Request(PR)**: "내 브랜치의 변경사항을 main에 합쳐줘"라는 요청이자 리뷰가 이루어지는 공간. PR 자체는 아직 main에 반영된 상태가 아니고, **승인 후 merge를 실행해야** 실제로 main에 반영됨.
- **Merge 방식**
    - Merge commit: 브랜치 히스토리를 그대로 합침
    - Squash and merge: 여러 커밋을 하나로 뭉쳐서 합침 (히스토리 깔끔)
    - Rebase and merge: 브랜치 커밋들을 main 위에 재배치 (선형 히스토리)
- **충돌(Conflict)**: 여러 브랜치가 같은 파일의 같은 부분을 고치면 merge 시 충돌 발생 → 수동으로 해결 필요.

**핵심 포인트**
- PR을 작게, 자주 만들수록 리뷰도 쉽고 충돌 위험도 줄어듦
- `git pull`을 자주 해서 main과 크게 벌어지지 않게 유지