# 벨로그 발행 워크플로우

사용자가 "완료된 파일 벨로그에 올리자" 같이 velog 발행을 요청하면, `00.inbox/velog-scripts/`의 도구로 아래 과정을 처리한다. (상세/트러블슈팅: `00.inbox/velog-scripts/README.md`)

- 사전 조건: velog-cli 로그인 상태(`~/.local/bin/velog auth status`). 로그아웃이면 재인증을 안내한다. (발행 대상 = `computer-science/`의 `#completed` 노트)

1. **발행**: `python3 00.inbox/velog-scripts/sync.py`로 바로 발행한다(live 공개됨). 별도 승인 없이 진행하고, 발행 결과(create/edit/skip)를 사용자에게 보고한다.
2. **매핑 커밋**: 발행 후 노트 프론트매터에 기록된 `velog_slug`/`velog_hash`(중복 발행 방지용)를, 별도 요청 없이 바로 커밋한다. sync 출력의 `CHANGED\t<경로>` 줄에 나온 **그 파일들만** `git add`한다(폴더 한정 X — 발행한 노트만 정확히 스테이징). 이후 Conventional Commits 규칙(tools/github.md)으로 커밋 (예: `chore: velog 발행 메타 기록`). 이 레포는 main에 직접 커밋함.
3. **시리즈 안내**: sync가 출력한 "시리즈 지정 필요" 목록을 사용자에게 전달한다. 시리즈는 CLI로 자동화 불가 → 사용자가 velog 웹에서 직접 지정해야 한다.

문제 발생 시 `00.inbox/velog-scripts/README.md`의 트러블슈팅 표를 참조하고, 임의 추측 대신 그 문서 기준으로 사용자와 상의한다.
