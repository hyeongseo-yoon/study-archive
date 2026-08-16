# C

> c 참고용 reference

## sprintf / snprintf

- `sprintf(str, format, ...)`: 포맷 문자열을 채워서 그 결과를 `str` 버퍼에 써넣는 함수. 버퍼 크기 제한이 없음.
- `snprintf(str, size, format, ...)`: `sprintf`와 동일하게 동작하되, `size` 파라미터로 버퍼에 쓸 수 있는 최대 바이트 수를 제한함. C99부터 표준.
- `snprintf`는 `size`를 넘겨받아서, 결과가 아무리 길어도 버퍼 크기를 절대 넘어서 쓰지 않는다. `size`가 1 이상이면 항상 마지막에 `'\0'`을 넣어 널 종료를 보장한다(잘리더라도).
- `sprintf`는 이런 크기 체크가 없어서, 포맷 결과가 버퍼보다 길면 버퍼 밖 메모리(다른 지역 변수, 리턴 주소 등)까지 그대로 덮어써버린다.
- 리턴값 차이: `sprintf`는 실제로 쓴 문자 개수를 리턴. `snprintf`는 "크기 제한이 없었다면 썼을 전체 길이"를 리턴하므로, 리턴값이 `size`보다 크면 잘렸다는 걸 알 수 있다.
- 사용자 입력이나 길이를 예측할 수 없는 문자열을 다룰 때 `sprintf`를 쓰면 버퍼 오버플로우(CWE-120 계열)로 이어질 수 있어서, 실무에서는 `snprintf`가 표준으로 쓰임.
-

## size_t

- 객체의 크기나 배열 인덱스/개수를 표현하기 위한 부호 없는(unsigned) 정수 타입. `<stddef.h>`에 정의되어 있고, `sizeof` 연산자의 결과 타입이기도 함.
- 크기/개수는 음수가 될 수 없다는 전제로 unsigned로 설계됨. 덕분에 같은 비트 수의 `int`보다 표현 가능한 양의 범위가 두 배 넓음.
- 폭은 플랫폼마다 다름 (64비트 시스템: 보통 8바이트, 32비트 시스템: 보통 4바이트). 그래서 오버플로우가 나는 기준값도 플랫폼마다 다름.
- `int`와 `size_t`가 섞인 산술 연산에서는 usual arithmetic conversions 규칙에 따라 `int`가 `size_t`로 변환된 후 계산됨. 이때 음수 `int`는 아주 큰 unsigned 값으로 변환되고, 큰 값끼리 곱하면 `size_t` 범위를 넘어 wrap-around(오버플로우)될 수 있음.

## SIZE_MAX

- `size_t`가 표현할 수 있는 최댓값을 나타내는 매크로. `<stdint.h>`에 정의됨.
- 곱셈으로 인한 정수 오버플로우를 미리 검사할 때 쓰임. `count * size`가 오버플로우 나는지 확인하려고 그 곱셈을 직접 해보면 안 되고(오버플로우 나는 연산 자체로는 검사 불가), 나눗셈으로 뒤집어서 `count <= SIZE_MAX / size` 형태로 검사해야 안전함.
- 표준 라이브러리 `calloc(count, size)`는 이 체크를 내부적으로 이미 해줌 — 그래서 `malloc(count * size)` + 수동 계산보다 `calloc`이 더 안전한 경우가 있음.

## memset

- `void *memset(void *ptr, int value, size_t num);`
- `ptr`이 가리키는 메모리의 첫 `num` 바이트를 전부 `value`로 채우는 함수. 주로 `malloc`으로 받은 메모리를 0으로 초기화할 때 쓰임.
- 세 번째 인자가 `size_t`라서, `count * sizeof(...)` 계산에서 오버플로우가 나면 `memset`도 그 잘못된(너무 작은) 크기를 그대로 믿고 동작함 — malloc이 실제로는 작은 버퍼를 할당했는데 memset이 원래 의도했던 큰 크기만큼 쓰려고 하면 힙 버퍼 오버플로우로 이어짐.

## signal

- `void (*signal(int sig, void (*handler)(int)))(int)`: `<signal.h>`. 특정 시그널(`sig`)이 도착했을 때 실행할 핸들러 함수를 등록. 반환값은 이전에 등록돼 있던 핸들러.
- 핸들러 함수 시그니처는 `void handler(int sig)` 형태로 고정.
- 두 번째 인자로 함수 대신 `SIG_IGN`(해당 시그널 무시), `SIG_DFL`(OS 기본 동작으로 복원)도 넘길 수 있음.

```c
signal(SIGINT, handler);  // Ctrl+C가 오면 handler 실행
```

## volatile

- 변수 선언에 붙이는 타입 한정자(qualifier). 컴파일러에게 "이 변수는 프로그램이 모르는 경로(시그널 핸들러, 하드웨어 등)로 값이 바뀔 수 있으니, 최적화 시 레지스터에 캐싱하지 말고 매번 실제 메모리에서 다시 읽어라"라고 지시.
- 시그널 핸들러가 값을 바꾸는 전역 변수에 주로 사용. 값이 안 바뀌는 것처럼 보이는 루프(`while (!flag)`)를 컴파일러가 최적화로 없애버리는 걸 방지.
- 멀티스레드 환경에서의 동기화(원자성, 메모리 순서)는 보장하지 않음 — 그건 뮤텍스나 atomic 타입이 담당하는 영역.

```c
volatile int flag = 0;   // 매번 메모리에서 실제 값을 다시 읽음
```

## sig_atomic_t

- `<signal.h>`에 정의된 정수 타입. 시그널 핸들러와 메인 실행 흐름 사이에서 읽고 쓰기가 안전하다고 표준이 명시적으로 보장하는 타입.
- 시그널 핸들러 안에서 값을 바꾸고 메인 코드에서 그 값을 읽는 플래그 변수는 `volatile sig_atomic_t`로 선언하는 게 정석 (volatile + 이 타입을 세트로 사용).

```c
volatile sig_atomic_t done = 0;
void handler(int sig) { done = 1; }
```

## write (async-signal-safe 예시)

- `ssize_t write(int fd, const void *buf, size_t count)`: `<unistd.h>`. 버퍼링이나 내부 락 없이 커널에 직접 데이터를 넘기는 저수준 시스템콜.
- `printf` 같은 stdio 함수는 내부 버퍼/락 때문에 시그널 핸들러 안에서 호출하면 재진입 문제가 생길 수 있지만(async-signal-unsafe), `write`는 async-signal-safe 목록에 포함돼 있어 핸들러 안에서 안전하게 출력할 때 사용.

```c
void handler(int sig) {
    write(STDOUT_FILENO, "caught\n", 7);  // printf 대신 사용
}
```

## main(int argc, char *argv[])

- `int main(int argc, char *argv[])`: 프로그램 실행 시 명령줄 인수를 받기 위한 `main` 함수 형태. 인수가 필요 없으면 `int main(void)`로 충분.
- `argc` (argument count): 실행 시 전달된 인자의 개수. 실행 파일 이름 자체도 포함되므로 최소값은 1.
- `argv` (argument vector): 인자 문자열들이 담긴 배열. `argv[0]`은 항상 실행된 프로그램의 경로/이름, `argv[argc]`는 표준상 `NULL`이 보장됨.
- `argv`의 각 원소는 `char *`, 즉 전부 문자열이다. 숫자로 다루려면 `atoi`, `strtol` 등으로 직접 변환해야 함.
- `argc` 체크 없이 바로 `argv[1]`에 접근하면, 인자가 안 들어왔을 때 배열 범위 밖(정확히는 유효하지 않은 인덱스)을 읽어 undefined behavior(대개 segfault)로 이어짐. 그래서 `if (argc < 2)` 같은 검사가 관례.

```c
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("입력받은 인자의 개수: %d\n", argc);

    for (int i = 0; i < argc; i++) {
        printf("argv[%d]: %s\n", i, argv[i]);
    }

    return 0;
}
```

```
$ gcc -o test test.c
$ ./test hello world 123
입력받은 인자의 개수: 4
argv[0]: ./test
argv[1]: hello
argv[2]: world
argv[3]: 123
```

## 헤더(.h) / 구현(.c) 분리

- `.h`: 함수 시그니처, 구조체 정의 등 인터페이스 선언만. `.c`: 실제 구현.
- C 컴파일은 파일(translation unit) 단위로 따로 이루어짐 — 다른 파일의 함수를 쓰려면 컴파일러는 "이런 함수가 존재한다"는 선언만 알면 됨. 실제 연결은 링크 단계에서 처리.
- 이렇게 나누면 구현부(`.c`)만 바뀌었을 때 그 파일만 재컴파일하면 됨(나머지는 재컴파일 불필요) → 빌드 시간 절약. 헤더만 보면 그 모듈이 뭘 제공하는지 알 수 있음.

```bash
gcc -c main.c -o main.o          # main.c는 arraylist.h의 시그니처만 보고 컴파일됨
gcc -c arraylist.c -o arraylist.o
gcc main.o arraylist.o -o out    # 링커가 실제 구현과 연결
```

## 헤더 가드

- 같은 헤더가 여러 경로로 두 번 include되면(`#include`는 전처리기가 파일 내용을 그대로 복사) 구조체/함수가 중복 정의돼서 컴파일 에러가 남.
- 매크로로 "이미 한 번 포함됐으면 다시 넣지 않는다"는 표시를 해서 방지함.

```c
#ifndef POINT_H
#define POINT_H

struct Point { int x, y; };

#endif
```

- 매크로 이름은 관례상 `파일명_확장자` 대문자(`ARRAYLIST_H` 등). 모든 `.h` 파일에 예외 없이 적용하는 게 정석.

## valgrind (메모리 누수 검증)

- 프로그램을 가상 CPU 위에서 실행시키며 모든 메모리 접근(할당/해제/읽기/쓰기)을 감시하는 도구.

```bash
gcc -g -o prog prog.c              # -g: 디버그 심볼 필수 (파일:줄번호 추적용)
valgrind --leak-check=full ./prog
```

- `--leak-check=full`: 누수된 블록이 어디서(어느 파일:줄) 할당됐는지까지 상세히 알려줌. `-g` 없이 컴파일하면 함수/주소만 나와서 추적하기 어려움.
- 출력 읽는 법:
  - `HEAP SUMMARY`의 `N allocs, M frees` — 할당/해제 횟수 차이가 누수 후보
  - `definitely lost` — 확실히 샌 메모리(진짜 버그). free 안 한 지점의 파일:줄번호가 콜스택에 표시됨
  - `ERROR SUMMARY: 0 errors` + `All heap blocks were freed` — 깨끗한 상태

## perror / errno

- `perror(const char *s)`: `<stdio.h>`. 시스템 콜/라이브러리 함수 실패 시, 전역 변수 `errno`에 저장된 에러 코드를 사람이 읽을 수 있는 메시지로 변환해서 stderr에 출력하는 함수.
- 출력 형식: `s + ": " + strerror(errno) + "\n"`. `s`가 NULL이거나 빈 문자열이면 에러 메시지만 출력됨.
- `errno`는 문자열이 아니라 **정수(int) 변수**다. `<errno.h>`에 선언돼 있고, 실패 원인을 나타내는 정수 코드(`ENOENT`, `EACCES` 등 매크로 상수)가 저장됨. 이 정수를 문자열로 바꿔주는 게 `strerror(errno)`, 그걸 자동으로 출력까지 해주는 게 `perror`.
- `perror`만 호출할 거면 `<stdio.h>`만 있으면 충분(`errno`는 전역 심볼이라 링크 시 문제없음). 단, `errno`를 직접 비교/참조하려면 (`if (errno == ENOENT)`) `<errno.h>`가 필요함.
- 함수 호출이 성공했다고 `errno`가 자동으로 0으로 리셋되지 않음. 이전 실패의 잔여값이 남아있을 수 있어서, 성공 여부는 반드시 함수의 리턴값으로 먼저 판단하고 `errno`는 실패했을 때만 참고해야 함.
- 최신 시스템에서는 스레드별로 독립된 `errno`를 가짐(thread-local storage) — 멀티스레드에서도 안전.
- `errno`는 다음 라이브러리 호출에서 덮어써질 수 있으므로, 에러 발생 직후 바로 `perror`(또는 `strerror`)를 호출해야 정확한 값을 본다.

```c
#include <stdio.h>
#include <errno.h>

FILE *fp = fopen("nofile.txt", "r");
if (fp == NULL) {
    perror("fopen");   // 출력: fopen: No such file or directory
    exit(1);
}
```

## 표준/POSIX 헤더 파일

### 1. 표준 C 라이브러리 (ISO C)

| 헤더 | 어원 | 기본 설명 |
|---|---|---|
| `stdio.h` | **st**an**d**ard **i**nput/**o**utput | 표준 입출력. `printf`, `scanf`, `fopen`, `perror` 등 |
| `stdlib.h` | **st**an**d**ard **lib**rary | 범용 유틸리티. `malloc`/`free`, `atoi`, `exit`, `rand` 등 |
| `string.h` | string | 문자열·메모리 조작. `strcpy`, `strlen`, `memcpy`, `memset` 등 |
| `stddef.h` | **st**an**d**ard **def**initions | 공통 타입/매크로. `size_t`, `NULL`, `ptrdiff_t`, `offsetof` |
| `stdint.h` | **st**an**d**ard **int**eger | 고정폭 정수 타입. `int32_t`, `uint8_t`, `SIZE_MAX` 등 (C99) |
| `stdarg.h` | **st**an**d**ard **arg**ument | 가변 인자 매크로. `va_list`, `va_start`, `va_arg`, `va_end` — `printf`류 직접 구현할 때 씀 |
| `ctype.h` | **c**haracter **type** | 문자 분류/변환. `isalpha`, `isdigit`, `toupper` 등 |
| `math.h` | mathematics | 수학 함수. `sqrt`, `pow`, `sin`, `floor` 등 |
| `float.h` | floating point | 부동소수점 한계값 매크로. `FLT_MAX`, `DBL_EPSILON` 등 |
| `limits.h` | integer limits | 정수 타입 한계값 매크로. `INT_MAX`, `CHAR_BIT` 등 |
| `assert.h` | assertion | `assert()` 매크로 — 조건 실패 시 중단+메시지. `NDEBUG` 정의하면 비활성화됨 |
| `errno.h` | **err**or **no**mber | 전역 변수 `errno`와 에러 코드 매크로(`ENOENT` 등) |
| `signal.h` | signal | 시그널 처리. `signal()`, `sig_atomic_t`, `SIGINT` 등 |
| `setjmp.h` | **set** **j**u**mp** | 비지역 점프. `setjmp`/`longjmp` — 함수 호출 스택을 건너뛰는 탈출(에러 복구·예외 흉내) |
| `time.h` | time | 시간/날짜. `time()`, `clock()`, `strftime` 등 |
| `getopt.h` | **get** **opt**ion | 명령줄 옵션 파싱. `getopt()` (GNU 확장) |

### 2. POSIX 시스템/프로세스

| 헤더 | 어원 | 기본 설명 |
|---|---|---|
| `unistd.h` | **UNI**X **st**an**d**ard | POSIX 시스템 콜 핵심. `read`, `write`, `fork`, `exec*`, `close`, `sleep` 등 |
| `fcntl.h` | **f**ile **c**o**ntr**o**l** | 파일 열기/제어. `open()`, `fcntl()`, `O_RDONLY` 등 플래그 |
| `sys/types.h` | system types | 시스템 공용 데이터 타입. `pid_t`, `off_t`, `ssize_t` 등 |
| `sys/stat.h` | system stat(us) | 파일 상태 정보. `stat` 구조체, `stat()` 함수, 퍼미션 매크로 |
| `sys/wait.h` | system wait | 자식 프로세스 대기. `wait`, `waitpid`, `WNOHANG`, `WIFEXITED` 등 |
| `sys/mman.h` | system **m**e**m**ory-**m**apped | 메모리 매핑. `mmap()`, `munmap()` |
| `sys/select.h` | system select | I/O 멀티플렉싱. `select()`, `fd_set` |
| `sys/time.h` | system time | 정밀 시간 구조체. `struct timeval`, `gettimeofday()` — `time.h`보다 세밀한 단위 |
| `sys/times.h` | system times | 프로세스 CPU 시간 측정. `times()`, `struct tms` |
| `dirent.h` | **dir**ectory **ent**ry | 디렉터리 읽기. `opendir`, `readdir`, `struct dirent` |
| `termios.h` | **term**inal **i**nput/**o**utput **s**ettings | 터미널 속성 제어(raw mode 등). `struct termios` |
| `pthread.h` | **P**OSIX **thread** | 스레드. `pthread_create`, 뮤텍스 등 |
| `semaphore.h` | semaphore | 세마포어. `sem_init`, `sem_wait`, `sem_post` |

### 3. 네트워크 (POSIX 소켓)

| 헤더 | 어원 | 기본 설명 |
|---|---|---|
| `sys/socket.h` | system socket | 소켓 API 핵심. `socket`, `bind`, `listen`, `accept` 등 |
| `netinet/in.h` | **net**work **in**ternet | 인터넷 프로토콜 구조체. `sockaddr_in`, `htons` 등 |
| `arpa/inet.h` | **ARPA**net internet | IP 주소 변환. `inet_addr`, `inet_ntoa`, `inet_pton` — ARPA(미 국방부 고등연구계획국)가 초기 인터넷(ARPANET)을 만든 데서 유래한 이름 |
| `netdb.h` | **net**work **d**ata**b**ase | 네트워크 이름 해석. `gethostbyname`, `getaddrinfo` |

