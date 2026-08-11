---
created: 2026-07-24
tags:
  - review
---

# TCP 소켓 프로그래밍 기초

관련 노트: [[02.Area/study-archive/computer-science/os/file-descriptor-socket]] · [[02.Area/study-archive/computer-science/network/server-request-handling]]

## TCP : 데이터 전송 프로토콜 중 하나
## TCP의 핵심 특성

- **연결지향(connection-oriented)**: 데이터 주고받기 전에 먼저 연결을 맺고, 끝날 때까지 그 연결로만 통신함
- **바이트 스트림(byte stream)**: 메시지 단위가 아니라 그냥 이어진 바이트 흐름. 프로토콜 자체엔 "여기까지 메시지 하나"라는 경계 개념이 없음

|     | TCP             | UDP                   |
| --- | --------------- | --------------------- |
| 연결  | 연결지향            | 비연결지향(connectionless) |
| 신뢰성 | 순서 보장, 유실 시 재전송 | 보장 없음                 |
| 단위  | 바이트 스트림 (경계 없음) | 데이터그램 (패킷 단위, 경계 있음)  |

### 메시지 경계가 없어서 생기는 문제

`read()` 한 번 호출이 상대의 `send()` 한 번과 항상 대응되지 않음.

- **분할(partial read)**: `"HELLO\n"`을 보냈는데 `read()`가 `"HELL"`까지만 받고, 다음 `read()`에서 `"O\n"`이 옴
- **병합(coalescing)**: `"HELLO\n"` + `"WORLD\n"`을 연달아 보냈는데 `read()` 한 번에 `"HELLO\nWORLD\n"`가 통째로 옴

→ 그래서 애플리케이션 레벨에서 `\n` 같은 구분자를 정해서, 버퍼에 계속 이어붙이다가 구분자를 찾으면 그 앞부분만 완전한 메시지로 뽑아 쓰는 방식이 필요함. (echo 서버처럼 단순 반사만 할 땐 불필요 — job 러너 프로토콜처럼 메시지 단위 파싱이 필요할 때 적용)

## 커널 소켓 버퍼

- 소켓마다 커널이 **수신 버퍼**/**송신 버퍼**를 따로 가짐. 네트워크로 도착한 데이터는 일단 이 커널 버퍼에 쌓이고, `read()`는 그 버퍼에서 꺼내오는 동작
- partial read가 생기는 근본 원인 — `read()`는 호출 시점에 버퍼에 쌓인 만큼만 돌려줌
- 크기는 고정이 아니라 범위(min/default/max)로 설정되고 커널이 자동 조절(auto-tuning).

## 소켓 API

### 서버 흐름
```
socket() → bind() → listen() → 반복[accept() → read()/write()  → close()]
```

### 클라이언트 흐름
```
socket() → connect() → read()/write() → close()
```

| 함수                                | 역할                           | 비고                                                                           |
| --------------------------------- | ---------------------------- | ---------------------------------------------------------------------------- |
| `socket(AF_INET, SOCK_STREAM, 0)` | 소켓 fd 발급                     | `AF_INET`=IPv4, `SOCK_STREAM`=TCP(바이트 스트림)                                   |
| `bind(fd, addr, addrlen)`         | fd를 특정 주소/포트에 고정             | 서버만 사용. `htons()`로 포트를 네트워크 바이트 순서로 변환 필요                                    |
| `listen(fd, backlog)`             | 연결요청 처리하도록 listening 소켓으로 등록 | `backlog` = 처리 못하고 밀린 연결 대기 큐 크기                                             |
| `accept(fd, NULL, NULL)`          | connected 소켓 생성              | **blocking syscall**. 원래 fd(listening socket)와 다른 새 fd(connected socket)를 리턴 |
| `connect(fd, addr, addrlen)`      | 서버에 연결 시도                    | 클라이언트만 사용                                                                    |

```c
// 서버 예시
int sockfd = socket(AF_INET, SOCK_STREAM, 0);

struct sockaddr_in server_addr;
server_addr.sin_family = AF_INET;
server_addr.sin_addr.s_addr = INADDR_ANY;
server_addr.sin_port = htons(8080);

bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr));
listen(sockfd, 5);

while(1){
	int client_fd = accept(sockfd, NULL, NULL);  // 여기서 blocking
```

### `struct sockaddr_in` 필드

서버가 어느 주소·포트로 연결을 받을지 커널에 알려주는 구조체.
 - sockaddr_in 은 IPv4 전용 주소 구조체임.

| 필드                             | 의미                                                                                                                                                                                 |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sin_family = AF_INET`         | 이 주소가 IPv4 체계임을 나타내는 타입 태그. `bind()`는 범용 `struct sockaddr*`를 받는데, 커널이 이 필드를 보고 실제로는 구조체`sockaddr_in`으로 해석해야 한다고 판단함 → 그래서 `bind()` 호출 시 `(struct sockaddr*)&server_addr`로 캐스팅해서 넘김 |
| `sin_addr.s_addr = INADDR_ANY` | 바인드할 IP. `INADDR_ANY`(`0.0.0.0`)는 "이 서버가 가진 모든 네트워크 인터페이스에서 오는 연결을 다 받는다"는 뜻. 특정 인터페이스로 제한하려면 그 IP를 직접 넣으면 됨                                                                       |
| `sin_port = htons(8080)`       | 포트 번호. `htons()`(host to network short) 변환이 필수 — 아래 참고                                                                                                                             |

**byte order 변환이 필요한 이유**: CPU마다 숫자를 메모리에 저장하는 순서(byte order)가 다름 — x86 계열은 little-endian(하위 바이트 먼저)인데 네트워크 프로토콜은 항상 big-endian(network byte order)으로 통일되어 있음. `htons()`로 변환 안 하면 8080이 다른 컴퓨터에는 완전히 다른 숫자로 읽힘.

- `INADDR_ANY`는 값이 0이라 순서 상관없이 변환 불필요하지만, 특정 IP를 넣을 땐 `inet_addr()`나 `htonl()`로 변환 필요
- 세트로 쓰이는 함수: `htons`/`ntohs`(16비트, 포트용), `htonl`/`ntohl`(32비트, IP 주소용)

### listening / connected socket
- linstening socket을 통해서 connected socket을 생성.
- **listening socket** (`sockfd`): 새 연결을 받는 창구역할 하는 소켓
- **connected socket** (`client_fd`): 새 클라이언트 연결마다 하나씩 생성. 그 클라이언트 전용 통로

## 블로킹 I/O의 한계/

`accept()`, `read()`, `write()` 전부 blocking syscall. 프로세스가 하나뿐이면 지금 처리 중인 작업이 끝날 때까지 다른 어떤 것도 처리 못함.

- **busy waiting이 아님** — blocking 상태에선 프로세스가 WAITING으로 전환되며 CPU에서 내려가고, 인터럽트+스케줄러가 깨워줌
- 클라이언트1의 요청을 처리하고 있을 때 클라이언트2가 접속을 시도하면, TCP 3-way handshake는 `listen()`의 backlog 큐에 쌓여서 성공할 수 있어도, 서버는 클라이언트1의 `read()` 루프에 갇혀있어서 `accept()`를 다시 호출하지 않음 → 클라이언트2는 연결은 됐지만 완전히 방치됨. 결국 여러 클라이언트의 요청을 동시에 처리할 수 없음.
- select에서 이 한계를 해결

### 예시

```c
// 블로킹 I/O만 쓰는 echo 서버 — select() 없음
int sockfd = socket(AF_INET, SOCK_STREAM, 0);

struct sockaddr_in server_addr;
server_addr.sin_family = AF_INET;
server_addr.sin_addr.s_addr = INADDR_ANY;
server_addr.sin_port = htons(8080);

bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr));
listen(sockfd, 5);

while (1) {
    int client_fd = accept(sockfd, NULL, NULL);  // 여기서 blocking

    char buf[1024];
    ssize_t n;
    while ((n = read(client_fd, buf, sizeof(buf))) > 0) {  // 여기서도 blocking
        write(client_fd, buf, n);
    }
    close(client_fd);
    // 이 client_fd가 닫혀야만 루프 맨 위로 돌아가서 다음 accept() 호출됨
}
```

클라이언트1이 접속만 해놓고 아무것도 안 보내면 (`nc localhost 8080` 띄워놓고 입력 안 하는 식), 서버는 안쪽 `while (read...)`에 갇혀서 `accept()`를 다시 호출하지 못함. 이 상태에서 클라이언트2가 접속을 시도하면:

- OS 레벨: 3-way handshake는 `listen()`의 backlog 큐 안에서 완료됨 (`connect()`는 성공한 것처럼 리턴)
- 애플리케이션 레벨: 서버 프로세스는 그 연결의 존재조차 모름 — `accept()`를 호출해야 커널이 큐에서 꺼내서 넘겨주는데, 그 호출 자체가 안 일어나고 있으니까

즉 클라이언트2 입장에선 "연결은 됐는데 아무 응답도 안 옴"처럼 보임 — 데드락이 아니라 그냥 서버가 한 번에 fd 하나만 볼 수 있는 구조적 한계. fd가 여러 개일 때 "어떤 게 준비됐는지"를 알려주는 게 없으니 순서대로 처리할 수밖에 없고, 앞 클라이언트가 안 끝내면 뒤는 무한정 대기.

## TCP half-close (부록)

연결 종료 시 한쪽만 먼저 닫는 것도 가능함(half-close). OpenBSD `nc`는 기본적으로 stdin EOF(`Ctrl+D`)를 받아도 소켓 쓰기 쪽을 자동으로 안 닫음 — `-N` 옵션을 줘야 EOF 시 소켓도 같이 shutdown해서 FIN을 보냄. FIN이 안 가면 서버의 `read()`는 계속 blocking 상태로 남아있음.

## `select()` 다중 I/O 멀티플렉싱

블로킹 I/O 한계(위 참고) — 프로세스 하나로 여러 fd를 동시에 처리하려면, "지금 어떤 fd가 준비됐는지"를 알려주는 방법이 필요함. (**준비된 fd에서 read를 하면 blocked되지 않고 바로 리턴하기 때문에 반복문 탈출하고 다른 요청 처리 가능해짐**)`select()`가 그 역할.

### 인터페이스

```c
int select(int nfds, fd_set *readfds, fd_set *writefds,
           fd_set *exceptfds, struct timeval *timeout);
```

| 파라미터                     | 의미                                   |
| ------------------------ | ------------------------------------ |
| `nfds`                   | 감시할 fd 중 최댓값 + 1                     |
| `readfds`                | read 준비 여부를 감시할 fd 집합                |
| `writefds` / `exceptfds` | write 준비 / 예외 상황 감시 (에코 서버 실습에선 안 씀) |
| `timeout`                | `NULL`이면 준비된 fd 생길 때까지 무기한 블록        |
| 반환값                      | 준비된 fd 개수 (`0`=타임아웃, `-1`=에러)        |

### fd_set 매크로

| 매크로                  | 역할                         |
| -------------------- | -------------------------- |
| `FD_ZERO(&set)`      | 집합 비우기                     |
| `FD_SET(fd, &set)`   | 집합에 fd 추가                  |
| `FD_ISSET(fd, &set)` | select 호출 후 이 fd가 준비됐는지 확인 |
| `FD_CLR(fd, &set)`   | 집합에서 fd 제거                 |

### "fd 준비됨(readable)"의 기준

POSIX 정의: **그 fd에 read()/accept()를 호출했을 때 블록되지 않고 즉시 리턴되는 상태**.

| 상황                         | 결과                                       |
| -------------------------- | ---------------------------------------- |
| 수신 버퍼에 데이터 있음              | `read()` → `n > 0`                       |
| 상대가 연결 끊음(FIN)             | `read()` → `n == 0` (준비됨으로 취급되지만 데이터 아님) |
| 에러 상태(RST 등)               | `read()` → `n < 0`                       |
| (리스닝 소켓) accept 큐에 연결 대기 중 | `accept()`가 블록 없이 리턴                     |

→ "연결 끊김"도 select 기준으로는 "준비됨"이라 반드시 `n == 0` 체크해서 `close()` 처리해야 함.

### select()는 인자를 파괴적으로 수정함

호출 전엔 "감시하고 싶은 fd 목록"이던 `readfds`가, 호출 후엔 "그중 실제로 준비된 fd만 남은 목록"으로 덮어써짐. 그래서 **매 루프마다 `FD_ZERO` → `FD_SET` 반복해서 통째로 재설정**해야 함 — 안 그러면 다음 루프에서 감시 대상 정보가 유실됨.

### 이벤트 루프 패턴 (리스닝 소켓 + 다중 클라이언트)

```c
int client_fds[N] = { -1, -1, -1, ... };  // -1 = 빈 슬롯
int maxfd = listen_fd;

while (1) {
    FD_ZERO(&readfds);
    FD_SET(listen_fd, &readfds);
    for (int i = 0; i < N; i++)
        if (client_fds[i] >= 0) FD_SET(client_fds[i], &readfds);

    int ready = select(maxfd + 1, &readfds, NULL, NULL, NULL);
    if (ready < 0) {
        if (errno == EINTR) continue;  // 시그널에 의한 인터럽트, 재시도
        break;                          // 그 외 에러
    }

    if (FD_ISSET(listen_fd, &readfds)) {
        int new_fd = accept(listen_fd, NULL, NULL);  // backlog 큐에 있던 연결이라 블록 없이 즉시 리턴
        for (int i = 0; i < N; i++) {
            if (client_fds[i] < 0) {
                client_fds[i] = new_fd;
                if (new_fd > maxfd) maxfd = new_fd;
                break;
            }
        }
    }
    for (int i = 0; i < N; i++) {
        if (client_fds[i] < 0) continue;      // 유효하지 않은 fd는 스킵
        if (FD_ISSET(client_fds[i], &readfds)) {
            char buf[1024];
            ssize_t n = read(client_fds[i], buf, sizeof(buf));  // readable로 확인된 fd라 블록 없이 즉시 리턴
            if (n <= 0) {                      // 0=연결 종료, <0=에러
                close(client_fds[i]);
                client_fds[i] = -1;
            } else {
                write(client_fds[i], buf, n);  // echo
            }
        }
    }
}
```

### 실습에서 걸린 버그: `FD_ISSET`에 유효하지 않은 fd 전달

`client_fds[i]`가 `-1`(빈 슬롯)인 상태에서 그대로 `FD_ISSET(client_fds[i], &readfds)`를 호출하면 **undefined behavior**임 — `fd_set`은 fd 값으로 비트를 인덱싱하는 구조라, 음수 인덱스가 들어가면 배열 범위 밖 접근이 됨. 실행 시 우연히 안 터질 수 있지만 표준상 정의되지 않은 동작.

**해결**: `if (fd < 0) continue;` 가드로 유효하지 않은 fd는 아예 `FD_ISSET` 호출 전에 걸러냄.

**이런 UB를 자동으로 잡는 도구**:
```bash
gcc -fsanitize=address,undefined -g select_echo.c -o select_echo_debug
```
- **AddressSanitizer**(`-fsanitize=address`): out-of-bounds 접근, use-after-free 등 감지
- **UBSan**(`-fsanitize=undefined`): 배열 음수 인덱싱, 정수 오버플로우 등 표준 위반 감지
- **Valgrind**: 재컴파일 없이 런타임에 메모리 접근 감시
