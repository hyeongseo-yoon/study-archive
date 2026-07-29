---
created: 2026-07-23
tags:
  - review
---

# 표준 입출력 스트림 (FILE)

## 정의

- **스트림(stream)**: 데이터를 앞에서부터 순서대로 주고받는 흐름. 임의의 위치로 바로 접근(랜덤 액세스)하는 게 아니라, 내부에 "지금 어디까지 읽었/썼는지" 위치(커서)를 유지하면서 read/write할 때마다 그 위치가 자동으로 앞으로 이동하는 방식. 파이프·소켓·터미널은 되감기 자체가 불가능한 진짜 스트림이고, 일반 파일도 관례상 같은 인터페이스로 다룸
- **표준 입출력(stdio)**: ISO C 언어 표준(ISO/IEC 9899)에 명세된 입출력 라이브러리. `<stdio.h>`에 정의된 `fopen`, `fprintf`, `fread` 등이 여기 속함. "표준"인 이유는 C 표준 자체에 정의돼 있어서 OS·컴파일러가 달라도 동일하게 동작함이 보장되기 때문 — `open()`/`read()`/`write()` 같은 시스템콜은 POSIX 표준이지 C 언어 표준이 아니라서 이 보장이 없음 (Windows엔 없음)
- **FILE\: stdio에서 스트림 개념을 구현한 구조체. 
	-> 사용할 때는 포인터를 이용함.
- fd는 커널이 관리하는 저수준 자원 핸들(정수)이고, FILE\*는 그 fd를 감싸서 버퍼링을 얹은 유저 공간(glibc) 객체 — [[file-descriptor-socket|fd 자체 개념]] 참고

## FILE 구조체 인터페이스

```c
FILE *fopen(const char *pathname, const char *mode);   // 파일 열어서 새 FILE* 생성
FILE *fdopen(int fd, const char *mode);                 // 이미 있는 fd를 FILE*로 감싸기
int   fclose(FILE *stream);                             // 버퍼 flush 후 스트림 닫기

int    fprintf(FILE *stream, const char *format, ...);  // 포맷 문자열 출력
size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream);   // 읽기
size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream); // 쓰기

int fflush(FILE *stream);   // 버퍼에 쌓인 내용을 강제로 write() 시스템콜로 내보냄
int fileno(FILE *stream);   // FILE 구조체 안의 fd 필드 값을 꺼내옴
```

```c
FILE *fp = fopen("data.txt", "w");
fprintf(fp, "hello %d\n", 42);
fclose(fp);
```

## 원리

### FILE 구조체가 들고 있는 것

```c
struct _IO_FILE {          // 개념적 표현 (실제 glibc 구현은 더 복잡함)
    int fd;                 // 이 스트림이 감싸고 있는 실제 fd
    char *buffer;           // 데이터 임시 저장용 버퍼 (malloc)
    size_t buffer_size;
    size_t buffer_pos;      // 버퍼 내 현재 위치
    int flags;              // 읽기/쓰기 모드, EOF/에러 여부 등
    ...
};
```

FILE 구조체는 **파일 자체가 아님**. 디스크의 실제 데이터·inode 등은 전부 커널이 관리하고, FILE 구조체는 그걸 하나도 모름. 아는 건 fd 하나와 버퍼뿐. 그래서 소켓이나 파이프의 fd도 `fdopen()`으로 감싸면 똑같이 FILE\*로 다룰 수 있음.

### fopen 동작 흐름

```c
FILE *fp = fopen("data.txt", "w");
```

1. `open()` 시스템콜로 fd 하나 받음 (예: fd=3)
2. `malloc()`으로 `FILE` 구조체 생성, 버퍼도 할당
3. 구조체의 fd 필드에 3 저장
4. 그 구조체의 주소를 `fp`로 리턴

### 버퍼링을 통한 효율화

```c
fprintf(stdout, "hi");
```

1. `stdout`이 가리키는 FILE 구조체를 찾음
2. 버퍼에 "hi"를 복사 (이 시점엔 시스템콜 없음)
3. 버퍼가 차거나 flush 조건(개행, `fflush()` 등)이 되면 → 구조체의 fd(=1)를 이용해 `write(1, buffer, ...)` 시스템콜 한 번 호출
4. 커널이 fd table[1]을 룩업해서 실제 자원에 씀

`write()` 시스템콜은 호출할 때마다 커널 진입(context switch) 비용이 드는데, 한 글자씩 매번 호출하면 비쌈. stdio는 유저 공간 버퍼에 데이터를 모았다가 한 번에 시스템콜을 호출해서 이 비용을 줄임 — 이게 스트림/FILE\*가 존재하는 이유.

### fd ↔ FILE\* 대응은 선택적

fd table의 모든 fd에 FILE 구조체가 자동으로 대응되는 게 아님.

- `open()` + `read()`/`write()`로 fd를 직접 쓰면 → FILE 구조체 없음
- `fopen()`을 호출하거나, 이미 있는 fd를 `fdopen()`으로 감싸야만 → 그 fd를 감싼 FILE 구조체가 생김

### stdin / stdout / stderr

```c
extern FILE *stdin;   // fd 0을 감싼 FILE*
extern FILE *stdout;  // fd 1을 감싼 FILE*
extern FILE *stderr;  // fd 2를 감싼 FILE*
```

프로그램 시작 시 glibc가 미리 만들어두는 FILE\* 전역 변수. `fprintf(stderr, ...)`에서 넘기는 `stderr`는 fd 2가 아니라 **fd 2를 감싼 FILE\***임 — `fd 2 = stderr`라는 말은 개념적으로만 맞고, 타입 레벨에서는 정수(fd)와 포인터(FILE\*)로 서로 다름.

## 핵심 포인트

- 유저 공간은 커널의 fd table을 직접 dereference 못 함. fd는 시스템콜 호출 시 커널에 넘기는 "핸들"일 뿐이고, 실제 룩업은 시스템콜이 커널에 진입한 순간 커널이 수행함
- `fileno(FILE*)`로 FILE 구조체 안의 fd 값을 꺼낼 수 있음
