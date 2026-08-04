---
created: 2026-08-04
tags:
  - review
---

# read/write 시스템콜

## 정의

- POSIX 시스템콜. 유닉스 계열에서 파일 디스크립터로 입출력하는 가장 기본적인 인터페이스
- `<unistd.h>`에 선언됨

## 인터페이스

```c
#include <unistd.h>

ssize_t read(int fd, void *buf, size_t count);
ssize_t write(int fd, const void *buf, size_t count);
```

- **fd**: 파일 디스크립터 (open()으로 얻은 정수, 0=stdin, 1=stdout, 2=stderr) — [[file-descriptor-socket]] 참고
- **buf**: read는 데이터를 채워넣을 버퍼, write는 데이터가 들어있는 버퍼
- **count**: 읽거나 쓰려는 바이트 수

### 반환값 (ssize_t)

signed size_t라서 음수도 가능함

- 양수: 실제로 읽거나 쓴 바이트 수. count와 다를 수 있음 (short read/write)
- 0: read()의 경우 EOF. write()에서 0은 정상적으로 발생 안 함
- -1: 에러 발생, errno 확인 필요

## 원리 (놓치기 쉬운 함정들)

### short read/write는 버그가 아니라 정상 동작

파이프, 소켓, 시그널 인터럽트 등으로 인해 반환값이 count보다 작을 수 있음. 정확히 N바이트를 보장받으려면 루프를 돌려야 함:

```c
size_t total = 0;
while (total < count) {
    ssize_t n = read(fd, buf + total, count - total);
    if (n < 0) {
        if (errno == EINTR) continue;  // 시그널에 인터럽트됐으면 재시도
        return -1;  // 진짜 에러
    }
    if (n == 0) break;  // EOF
    total += n;
}
```

### EINTR

시그널 핸들러가 실행되면 시스템 콜이 중간에 끊기고 -1/EINTR을 반환할 수 있음. 재시도 로직 없으면 데이터 유실됨. — [[signal-handling]] 참고

### read/write는 버퍼링 안 함

`fread`/`fwrite`(stdio) 같은 라이브러리 함수와 다르게 커널 레벨 시스템콜이라 직접 커널 버퍼(또는 디바이스)와 오감. stdio는 이 위에 유저 공간 버퍼링을 얹은 것 — [[stdio-stream]] 참고

### write() 성공 ≠ 디스크 반영 보장

커널 페이지 캐시에만 써진 상태일 수 있음. 진짜 디스크 반영을 보장하려면 `fsync()` 필요.

## 핵심 포인트

- 반환값은 항상 확인해야 함 — count와 같다고 가정하면 안 됨
- short read/write, EINTR 처리를 위한 재시도 루프는 정확성을 위한 필수 패턴
- write()가 성공해도 실제 디스크 반영은 별개 문제 (fsync 필요)
