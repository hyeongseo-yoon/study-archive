## 기본 사용법
git add .
git commit -m "message"
git push origin main

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

나눠서도 가능!

- `git add OS_note.md` -> `git commit -m "feat: OS 데드락 정리"`
    
- `git add Algo_1234.c` -> `git commit -m "feat: 백준 1234번 풀이"`
    
- `git push origin main` (푸시는 한 번에!)