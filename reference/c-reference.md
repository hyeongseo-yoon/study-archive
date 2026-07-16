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

