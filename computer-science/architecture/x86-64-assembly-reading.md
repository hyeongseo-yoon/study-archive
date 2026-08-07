---
created: 2026-08-07
tags:
  - review
---

# x86-64 어셈블리 읽기 (AT&T 문법)

Bomb Lab 리버싱에 필요한 x86-64 어셈블리 독해 기초. gdb `disas`로 뽑은 코드를 C로 역매핑하는 데 필요한 최소 지식.

## 1. 레지스터

### 크기별 이름

물리적으로 64비트 레지스터 하나를 하위 크기별로 다른 이름으로 부름 (`int`=4바이트면 컴파일러가 32비트 이름을 씀).

| 64비트       | 32비트         | 16비트         | 8비트          |
| ---------- | ------------ | ------------ | ------------ |
| `rax`      | `eax`        | `ax`         | `al`         |
| `rdi`      | `edi`        | `di`         | `dil`        |
| `rsi`      | `esi`        | `si`         | `sil`        |
| `rdx`      | `edx`        | `dx`         | `dl`         |
| `rbp`      | `ebp`        | `bp`         | `bpl`        |
| `rsp`      | `esp`        | `sp`         | `spl`        |
| `r8`~`r15` | `r8d`~`r15d` | `r8w`~`r15w` | `r8b`~`r15b` |

- 이름 유래: 16비트 `ax` → 32비트로 확장되며 "extended ax" = `eax` → 64비트로 재확장되며 `rax`.
- **32비트 레지스터를 통해 값을 쓰면 상위 32비트가 자동으로 0으로 채워짐**(zero-extend). `mov %edi, ...`처럼 32비트만 다뤄도 `int` 하나를 안전하게 통째로 옮긴 게 됨.


## 2. 함수 호출 규약 (x86-64 System V ABI)

### 정의
함수 호출 시 인자를 어디에 어떤 순서로 넘기고, 반환값은 어디 담고, 어떤 레지스터를 누가 지켜야 하는지에 대한 약속.

### 인자 전달
앞에서부터 6개 정수/포인터 인자는 레지스터로:
```
rdi, rsi, rdx, rcx, r8, r9
```
7번째부터는 스택. 반환값은 `rax`.

### 레지스터에 저장하는 이유
레지스터가 메모리보다 접근이 빨라서, 인자 개수가 적은 대부분의 경우 스택 접근 자체를 생략할 수 있음.

### 스택 프레임
- `rsp`(stack pointer): 스택의 현재 맨 위
- `rbp`(base pointer): 현재 함수 프레임의 고정 기준점 — 지역변수를 `rbp` 기준 오프셋(`-0x14(%rbp)`)으로 찾음

**Prologue/epilogue 패턴**:
```asm
push   %rbp        # 이전 함수의 rbp 저장
mov    %rsp, %rbp  # 새 프레임 시작점 고정
sub    $0x20, %rsp # 지역변수 공간 확보(sp를 0x20만큼 내려서 공간확보)
...
leave              # mov %rbp,%rsp; pop %rbp 를 실행
ret                # 저장된 리턴 주소로 복귀
```

### Caller-saved vs Callee-saved

호출 전후로 레지스터 값이 깨지지 않아야 할때, "누가 보존 책임을 지는지" 나눠놓은 규칙.

- **Caller-saved** (`rax`, `rcx`, `rdx`, `rsi`, `rdi`, `r8`~`r11`): callee가 마음대로 덮어써도 됨. caller가 호출 후에도 값이 필요하면 caller가 알아서 호출 전에 저장.
- **Callee-saved** (`rbx`, `rbp`, `r12`~`r15`): callee가 이 레지스터를 쓰려면 원래 값을 저장했다가 리턴 전 반드시 복원. caller 입장에선 호출 전후로 값이 안 바뀐 것처럼 보여야 함.

### 레지스터 역할별 정리

| 레지스터 | 역할 | Caller/Callee-saved | 비고 |
|---|---|---|---|
| `rdi` | 1번째 인자 | caller-saved | |
| `rsi` | 2번째 인자 | caller-saved | |
| `rdx` | 3번째 인자 | caller-saved | 곱셈/나눗셈에서 상위비트 결과도 여기 담김 (`mul`, `div`) |
| `rcx` | 4번째 인자 | caller-saved | 전통적으로 반복문 카운터(`loop` 명령어가 자동 사용) |
| `r8` | 5번째 인자 | caller-saved | |
| `r9` | 6번째 인자 | caller-saved | |
| `rax` | 리턴값 | caller-saved | 곱셈/나눗셈 결과 하위비트도 여기 담김. 계산용 accumulator로도 자주 씀 |
| `rsp` | 스택 포인터 | (별도 취급) | push/pop/call/ret이 암묵적으로 관리, 항상 원상복구돼야 함 |
| `rbp` | 프레임(베이스) 포인터 | callee-saved | 지역변수 접근 기준점 |
| `rbx` | 범용 | callee-saved | 특별한 배정 역할 없음 |
| `r12`~`r15` | 범용 | callee-saved | 특별한 배정 역할 없음 |
| `r10`, `r11` | 범용(scratch) | caller-saved | 특별한 배정 역할 없음. 굳이 안 외워도 됨 |

**암기 팁**

- 인자 순서(`rdi, rsi, rdx, rcx, r8, r9`): "Diane's Silk Dress Cost $89" → di-si-dx-cx-8-9. 한글로는 "디-시-디-씨-팔-구" 리듬으로.
- Caller/Callee 구분: **이름에 `b`가 들어가거나(`rbx`, `rbp`) 숫자가 `12` 이상이면(`r12`~`r15`) → callee-saved(보존됨).** 나머지 전부(`rax`,`rcx`,`rdx`,`rsi`,`rdi`,`r8`~`r11`)는 caller-saved(날아감).

syscall 직접 호출 시엔 4번째 인자가 `rcx` 대신 `r10`으로 바뀜(syscall 명령어 자체가 `rcx`를 clobber하기 때문) — `syscall` 명령어 보일 때 챙기면 됨.

이유: 모든 레지스터를 매번 저장하면 비효율적이라, 자주 값이 오가는 레지스터는 caller가, 함수 내부에서 오래 들고 있을 값은 callee가 책임지는 분업 구조.

### 정리: 레지스터 중 함수 호출되면 거의 항상 쓰이는 그룹과 잘 안 쓰이는 그룹이 있음. 항상 쓰이는 그룹은 어차피 날아간다고 전제하고 날아가면 안 되는 값만 caller가 저장하는 게 caller-saved. 잘 안 쓰이는 그룹은 매번 caller가 방어적으로 저장하면 비효율적이니, 실제로 쓰는 callee가 책임지고 저장하는 게 callee-saved.

실전에서 보이는 패턴 — 함수 맨 앞/뒤에 짝을 이루는 `push`/`pop`:
```asm
push   %rbx        # 함수 시작하며 rbx 원래값 저장
push   %r12
...
pop    %r12        # 리턴 전에 복원
pop    %rbx
ret
```

## 3. AT&T 문법 기본 규칙

- **방향**: `연산 src, dst` — Intel과 반대로 왼쪽이 출발지. `mov %rax, %rbx` → `rbx = rax`
- **레지스터**: `%` 접두사 / **즉시값**: `$` 접두사 / **메모리**: `disp(base,index,scale)` → 주소 = `base + index*scale + disp`
- **크기 접미사**: `b`(1B) `w`(2B) `l`(4B) `q`(8B) — `movl`, `movq` 등

### 핵심 명령어

| 명령어 | 하는 일 |
|---|---|
| `mov` | 값을 그대로 복사 (`dst = src`) |
| `lea` | 메모리 접근 없이 주소 계산값 자체를 저장 (`dst = &(식)`) — 산술 연산 대체로도 자주 쓰임 |
| `cmp` | 두 값을 빼서 결과는 버리고 플래그만 세팅 |
| `test` | 두 값을 AND해서 플래그만 세팅 (`test %rax,%rax`로 rax의 0/음수 여부 체크하는 관용구) |

`cmp`/`test`는 그 자체론 아무것도 안 바꾸고, 바로 다음에 오는 `jX`가 세팅된 플래그를 보고 분기함.

## 4. 조건 분기 읽기

`cmp %rax, %rbx`는 `rbx - rax`를 계산해 플래그만 세팅. 이후 `jX`가 어떤 플래그 조합을 보느냐로 분기 조건이 갈림.

| 기호          | 뜻                         | C 비교연산자 | 예시                                                       |
| ----------- | ------------------------- | ------- | -------------------------------------------------------- |
| `je`/`jz`   | equal / zero              | `==`    | `cmp $0x5,%eax; je L` → `if (eax == 5) goto L;`          |
| `jne`/`jnz` | not equal                 | `!=`    | `cmp $0x0,%eax; jne L` → `if (eax != 0) goto L;`         |
| `jg`        | greater (**signed**)      | `>`     | `cmp $0x64,%eax; jg L` → `if (eax > 100) goto L;`        |
| `jge`       | greater or equal (signed) | `>=`    | `cmp $0xa,%eax; jge L` → `if (eax >= 10) goto L;`        |
| `jl`        | less (signed)             | `<`     | `cmp $0x0,%eax; jl L` → `if (eax < 0) goto L;`           |
| `jle`       | less or equal (signed)    | `<=`    | `cmp $0x64,%eax; jle L` → `if (eax <= 100) goto L;`      |
| `ja`        | above (**unsigned**)      | `>`     | `cmp $0x9,%eax; ja L` → `if ((unsigned)eax > 9) goto L;` |
| `jb`        | below (unsigned)          | `<`     | `cmp $0x9,%eax; jb L` → `if ((unsigned)eax < 9) goto L;` |

- `je`/`jz`, `jne`/`jnz`는 완전히 동일한 명령어(같은 opcode) — 문맥에 따라 다르게 읽을 뿐. `cmp` 뒤엔 equal로, `test` 뒤엔 zero로 읽는 게 자연스러움.
- `jg/jl` 계열과 `ja/jb` 계열이 나뉜 이유: 같은 비트 패턴도 부호있는 수(`int`)와 부호없는 수(`unsigned`)는 "크다/작다" 판단이 다를 수 있어서. Bomb Lab에서 `ja`/`jb`가 나오면 unsigned 취급 힌트.

## 5. 예제 — 어셈블리 → C 재구성

```asm
mov    %edi,-0x14(%rbp)
mov    -0x14(%rbp),%edx
mov    %edx,%eax
add    %eax,%eax
add    %edx,%eax
add    $0x7,%eax
mov    %eax,-0x4(%rbp)
cmpl   $0x64,-0x4(%rbp)
jle    .L1
mov    $0x1,%eax
jmp    .L2
.L1:
mov    $0x0,%eax
.L2:
```

- `edi`(1번째 인자) → 지역변수(`x`)로 저장
- `eax = edx; eax += eax; eax += edx; eax += 7` → `eax = x*3 + 7` (2배 만들고 자기자신 한 번 더 더해서 3배)
- `cmpl $0x64, ...` → `0x64` = 100
- `jle .L1` → 100 **이하**면(등호 포함) `.L1`로 점프해서 0 리턴, 아니면 1 리턴

→ C로: `return (x*3 + 7 > 100) ? 1 : 0;`
