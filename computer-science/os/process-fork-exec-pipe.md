---
created: 2026-07-24
tags:
  - review
---

# 프로세스 생성 / 파이프 (fork / exec / wait / pipe / dup2)

## 프로세스 생성: fork → exec → wait

### fork()

```c
#include <unistd.h>

pid_t fork(void);
```

- 현재 프로세스를 복제해서 자식 프로세스 생성
- 반환값으로 부모/자식 구분함
  - 부모: 자식의 PID(양수) 반환
  - 자식: 0 반환
  - 실패: -1 반환 (자식 안 생김)
- `fork()` 호출 시점 이후 코드는 부모/자식 양쪽에서 각각 독립적으로 실행됨

```c
pid_t pid = fork();
if (pid < 0) {
    perror("fork");
} else if (pid == 0) {
    // 자식
} else {
    // 부모, pid = 자식의 PID
}
```

- `pid_t`: `<sys/types.h>`에 정의된 typedef (보통 `int`). PID 전용 타입으로 감싸서 이식성 확보 (`size_t`, `off_t` 등과 같은 패턴)
- `fork()`를 N번 연속 호출하면 프로세스 수는 2^N로 늘어남 (fork bomb의 원리)

### exec 계열 (execvp 등)

```c
#include <unistd.h>

int execvp(const char *file, char *const argv[]);
```

- 이름 풀이: `exec` + `v`(vector, 인자를 배열로 받음) + `p`(PATH에서 실행파일 검색)
- `argv`는 반드시 `NULL`로 끝나야 하고, 관례상 `argv[0]`은 프로그램 이름 자신
- **성공하면 리턴하지 않음** — 현재 프로세스의 메모리 이미지(코드/데이터/힙/스택)를 통째로 교체. PID는 유지됨 (새 프로세스가 아니라 같은 프로세스가 다른 프로그램으로 교체되는 것)

```c
char *args[] = {"ls", "-la", NULL};
execvp("ls", args);
// 성공했다면 이 줄은 실행 안 됨
perror("execvp");  // 실패했을 때만 도달
```

**fork+exec가 항상 세트인 이유**: 셸(부모)이 직접 exec 해버리면 셸 자신이 사라져서 다음 명령을 못 받음. 그래서 자식(분신)을 만들고 그 자식만 exec으로 교체, 부모는 살아남아 다음 명령을 기다림.

### wait / waitpid

```c
#include <sys/wait.h>

pid_t wait(int *wstatus);
pid_t waitpid(pid_t pid, int *wstatus, int options);
```

- `options`에 `WNOHANG`을 넣으면 자식이 안 끝났어도 블로킹 안 하고 바로 리턴 (이벤트 루프에서 유용)

`wstatus`는 여러 정보가 비트로 인코딩된 값이라 직접 비교하면 안 되고 전용 매크로로 해석해야 함:

| 매크로 | 이름 풀이 | 의미 |
|---|---|---|
| `WIFEXITED` | Wait status IF EXITED | 자식이 정상 종료했는지 boolean 체크 |
| `WEXITSTATUS` | Wait EXIT STATUS | 정상 종료 시 exit code 꺼냄 |
| `WIFSIGNALED` | Wait IF SIGNALED | 시그널 받고 죽었는지 boolean 체크 |
| `WTERMSIG` | Wait TERMinating SIG | 어떤 시그널로 죽었는지 꺼냄 |

`WIF*`는 항상 확인용 boolean, `W*STATUS`/`W*SIG`는 그 상황의 구체값을 꺼내는 것 — 그래서 `WIFEXITED`가 참일 때만 `WEXITSTATUS`를 호출하는 게 맞는 사용법.

### 좀비 / 고아 프로세스

| 구분 | 정의 | 위험성 / 해결 |
|---|---|---|
| **좀비(zombie)** | 자식이 먼저 종료됐는데 부모가 `wait`를 안 해서 종료 정보가 회수 안 된 상태. 프로세스 테이블에 껍데기만 남음 (`ps`에 `<defunct>`) | 계속 쌓이면 프로세스 테이블 슬롯 고갈 → 새 프로세스 생성 불가. 해결: 부모가 반드시 `wait`/`waitpid` 호출 (1주차에서 SIGCHLD 핸들러로 자동화 예정) |
| **고아(orphan)** | 부모가 먼저 죽어서 자식이 남겨진 상태 | 커널이 자동으로 init(PID 1)의 자식으로 재입양시킴 → init이 대신 wait 해줘서 문제없음 |

방향이 반대: 자식이 먼저 죽으면 좀비, 부모가 먼저 죽으면 고아.

---

## 파이프로 fd 리다이렉션: pipe + dup2 + close

### fd 리다이렉션의 원리

- 프로세스 시작 시 기본으로 열려있는 fd 3개: `0`(stdin), `1`(stdout), `2`(stderr)
- "stdout 리다이렉트"는 결국 **fd 1이 가리키는 대상을 바꿔치기**하는 것뿐 — `printf`/`write` 코드는 안 바뀌고, fd 1이 뭘 가리키는지만 바뀜
- 커널의 fd 할당 정책: **항상 사용 가능한 fd 중 가장 낮은 번호를 할당**함 (`close(1); open(...)`으로도 리다이렉션이 되는 이유이자, `dup2`가 동작하는 배경 원리)

### pipe()

```c
#include <unistd.h>

int pipe(int pipefd[2]);
```

- `pipefd[0]`: 읽기 전용(read-end), `pipefd[1]`: 쓰기 전용(write-end)
- 커널 메모리 안의 고정 크기 버퍼(보통 64KB)에 FIFO(먼저 들어온 순서대로 나감)로 접근하는 두 개의 fd
- **단방향**만 지원. `fork()` 이전에 만들어야 부모/자식이 fork로 fd를 복제받아 같은 파이프를 공유하게 됨
- 양방향 통신이 필요하면 파이프 2개(각 방향에 하나씩) 필요 — 파이프 자체를 양방향으로 못 씀. 만약 양쪽이 같은 write-end에 쓰면 데이터가 한 스트림에 뒤섞임(interleave)

### dup2()

```c
#include <unistd.h>

int dup2(int oldfd, int newfd);
```

- `newfd`가 `oldfd`와 같은 커널 객체를 가리키게 만듦 (이미 열려있던 `newfd`는 먼저 닫힘)
- `dup()`은 빈 번호를 커널이 알아서 고르고, `dup2()`는 번호를 직접 지정 가능

```c
dup2(pipefd[1], 1);   // fd 1이 이제 파이프 write-end를 가리킴
```

### 안 쓰는 fd close()

- fd는 유한한 자원 (`ulimit -n`)
- 안 닫으면:
  - **fd 누수**: 계속 쌓이면 결국 fd 한도 초과로 `open`/`pipe`/`socket` 실패 시작
  - **EOF 감지 실패**: 파이프 read-end의 `read()`가 0(EOF) 반환하는 조건은 "write-end를 가리키는 fd가 전부 닫혔을 때". `dup2`로 복제한 fd 1 말고 원본 `pipefd[1]`까지 닫아야 이 조건이 충족됨. 안 닫으면 부모의 `read()`가 EOF를 영영 못 받고 블로킹될 수 있음

### exec 이후에도 fd 테이블이 유지되는 이유

프로세스를 두 층위로 나눠보면:

| 층위               | 내용                     | exec 시               |
| ---------------- | ---------------------- | -------------------- |
| 사용자 공간 메모리 이미지   | 코드/데이터/힙/스택            | 통째로 교체됨 (exec이 하는 일) |
| 커널이 관리하는 프로세스 상태 | PID, fd 테이블, 작업 디렉토리 등 | 그대로 유지됨              |

fd 테이블은 사용자 메모리가 아니라 커널 내부(PCB)에 있는 데이터라 exec의 교체 대상이 아님. 이 덕분에 `dup2` → `exec` 순서로 리다이렉션을 걸어두면, exec된 프로그램도 그 fd 상태를 그대로 물려받음 — 셸의 리다이렉션(`>`, `|`)이 전부 이 원리로 작동함.

예외: `fcntl(fd, F_SETFD, FD_CLOEXEC)`로 특정 fd에 표시해두면 그 fd만 exec 시점에 커널이 자동으로 닫아줌.

---

## 실습: pipe+dup2로 자식 stdout 캡처

**목표**: 부모가 자식을 fork+exec으로 실행하고, 자식의 stdout을 pipe+dup2로 가로채서 문자열로 읽기

**완료 기준**: 임의 커맨드 실행 → 부모가 stdout 내용을 정확히 캡처 / 좀비 프로세스 안 남음

```c
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
  int fd[2] = {0};
  pipe(fd);
  pid_t pid = fork();

  if (pid == 0) {
    close(fd[0]);
    dup2(fd[1], 1);
    close(fd[1]);
    char *args[] = {"ls", "-la", NULL};
    execvp("ls", args);
    printf("error\n");
    return -1;
  } else if (pid > 0) {
    close(fd[1]);
    int status;
    char buf[1024] = {0};
    ssize_t n;
    while ((n = read(fd[0], buf, sizeof(buf))) > 0) {
      write(1, buf, n);
    }
    waitpid(pid, &status, 0);
    close(fd[0]);
    int exit_code = WEXITSTATUS(status);
    printf("종료코드 : %d", exit_code);
  }
}
```

**실습하며 잡은 버그 3개**:
1. `buf`를 `{0}`으로 초기화 안 하면, `read()`가 다 못 채운 뒷부분에 스택 쓰레기값이 남아서 `printf("%s")`가 null terminator를 못 찾고 garbage 출력함

2. `waitpid()`를 `read()`보다 먼저 호출하면, 자식 출력이 파이프 버퍼(64KB)보다 클 때 **데드락** — 자식은 파이프가 꽉 차서 `write()` 안에 블로킹된 채 갇히고, 그걸 풀어줄 유일한 방법(부모의 read)이 더 이상 안 옴. 부모도 자식이 종료를 못 하니 `waitpid()`에 갇혀서 서로 무한 대기. 해결: `read()`를 EOF(0 반환)까지 반복 호출해서 파이프를 다 비운 뒤에 `waitpid()` 호출
