# Chapter 6: Code Generation - 1

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

*2025 Fall, Hunjun Lee (슬라이드 표기 기준)*

슬라이드 우측 하단 쪽번호가 PDF 페이지 순서와 같다. 이 강의는 컴파일러 **back end** 쪽으로 넘어와, 컴파일러가 **코드를 생성**하고 **데이터를 메모리에 어떻게 배치(orchestrate)** 하는지 — Runtime Organization(code / static / stack / heap), Activation Record, 호출 규약, 메모리 정렬과 데이터 레이아웃 — 를 다룬다.

## 1. 컴파일러 전체 구조에서의 위치 *(p.2~4)*

- Source Code → **Front end**(Lexical Analysis(Scanner) → Syntax Analysis(Parser) → Semantic Analysis) → **Code Generation-1** / Control·DataFlow Analysis / Optimization (**Machine Independent**) → **Code Generation-2** (**Machine Dependent**, back end) → Assembly Code
- 전 과정에서 **Context & Symbol Table & CFG**와 상호작용
- 이번 강의는 Code Generation - 1 단계 (p.3, 4는 같은 그림의 반복)

## 2. Microarchitecture / ISA: 컴파일러가 아는 것 *(p.5~6)*

- **Microarchitecture (뒤에 숨은 것)** *(p.5)* — 컴파일러는 직접 다루지 않는 하드웨어 내부
  - Core pipeline: CISC→RISC translation, Hyper-threading, Branch prediction, Out-of-order execution (168 Entry ROB & 54 Entry Issue Queue, 144~160 Registers)
  - Multi-core/multi-thread: core당 2 thread, chip당 4~6 core
  - Cache: 32KB L1 i-cache, 32KB L1 d-cache, 256KB L2, 8~12MB L3
- **ISA: 컴파일러가 아는 것** *(p.6)*
  - "소프트웨어 관점"에서 CPU = **compute units + register file + memory**
  - Compute Units: 어떤 종류의 연산이 가능한가 (Add / Sub …)
  - Register File: 빠른 접근, 제한된 용량 (Load / Store 대상)
  - Memory: 느린 접근, 큰 용량. 위쪽(Low Addr)에 Code(Instructions), 아래쪽(High Addr)에 Data

## 3. Storage Class Selection Problem *(p.7)*

- **데이터를 어디에 둘 것인가 (register file vs. memory)** 를 결정하는 문제
- **Standard approach**
  - Globals / Statics → memory
  - Locals
    - Composite types (struct, array 등) → memory
    - 나머지 → **Virtual register** (이후 강의에서 실제 register로 mapping)
- **All memory approach**: 모든 변수를 memory에 둔다

## 4. General Instruction Classes *(p.8)*

- **Arithmetic and logical operations** (add, sub, and, or)
  1. 지정된 위치에서 operand를 load
  2. operand의 함수로 결과를 compute
  3. 결과를 지정된 위치에 store
  4. PC를 다음 sequential instruction으로 update
- **Data movement operations** (load, store)
  1. 지정된 위치에서 operand를 fetch
  2. operand 값을 지정된 위치에 store
  3. PC를 다음 sequential instruction으로 update
- **Control flow operations** (branch, jump)
  1. 지정된 위치에서 operand fetch
  2. branch condition과 target address를 compute
  3. branch condition이 true면 PC ← target address, 아니면 PC ← next sequential instruction

## 5. Compiler Backend와 Runtime Organization *(p.9~10)*

- 컴파일러는 **코드 생성**과 함께, 데이터가 **메모리 공간에 어떻게 할당되는지 관리(orchestrate)** 할 책임이 있다 → 그 데이터를 제대로 다루는 코드를 생성 *(p.9)*
- **The code and data layout are codesigned** — 코드와 데이터 레이아웃은 함께 설계된다 (Code: Low Addr, Data: High Addr)
- **Runtime Organization / Storage Organization** *(p.10)*: 컴파일러의 책임 = 코드 생성 + data area 사용 orchestration. 코드가 메모리의 데이터를 조작한다.

## 6. Executing a Program *(p.11)*

- **OS**가 프로그램 실행을 제어한다
  - Step #1) 프로그램을 위한 메모리 공간 할당
  - Step #2) code와 data를 그 공간에 load
  - Step #3) OS가 entry point(즉, `main`)로 jump

## 7. Execution Sequence *(p.12)*

- 실행은 순차적: control이 프로그램의 한 지점에서 다른 지점으로 **well-defined order**로 이동 (참고: concurrency는 예외적 상황)
- procedure가 호출되면 control은 항상 **호출 직후 지점**으로 돌아온다 (참고: exceptions)

## 8. Activation & Lifetime *(p.13~16)*

### Activation & Lifetime - 1 *(p.13)*
- procedure P의 **invocation**이 P의 **activation**이다 → procedure P와 연관된 데이터의 **lifetime**을 결정
- activation of P의 lifetime = P를 실행하는 모든 단계 (**P 안에서 호출된 모든 sub-procedure 포함**)
- 변수 x의 lifetime = 실행 중 x가 정의된(defined) 구간
- **Lifetime은 동적(dynamic) 개념**

### Activation & Lifetime - 2 *(p.14)*
- P가 Q를 호출하면 **Q가 P보다 먼저 return**한다 → activation lifetime은 **properly nested**
- activation lifetime은 트리로 그릴 수 있다: **activation tree**
- 예시
  ```c
  int g() { return 1; }
  int f() { return g(); }
  void main() {
      g();
      f();
  }
  ```
  트리: main → g(), f() (f 아래에 g())

### Complex Example *(p.15)*
```c
int g() { return 1; }
int f(int x) {
    if (x==0) return g();
    else      return f(x-1);
}
void main() {
    f(3);
}
```
트리: main → f(3) → f(2) → f(1) → f(0) → g() (일직선 재귀)

### Activation Tree *(p.16)*
- activation tree는 **run-time behavior**에 따라 달라진다 → **program input마다 tree 구조가 다르다**
- **stack**을 이용하면 현재 active한 procedure를 알 수 있다
- 예시(p.14 코드): Step1~8에서 stack이 `main` → `main,g()` → `main` → `main,f()` → `main,f(),g()` → … 처럼 push/pop 된다

## 9. Stack Management *(p.17~23)*

### 기본 구조 *(p.17, 31 복습)*
- stack data는 **Low address 쪽에서 시작해 아래로(주소 증가 방향으로) 자란다** (슬라이드 그림: Code 아래 Stack, AR for main → f() → g() 순)
- 하나의 activation을 관리하는 정보를 **activation record (AR)** 또는 **frame**이라 한다

### Stack Management Example *(p.18)*
```c
        int g() {
0x00:       return 1; }
        int f(int x) {
0x04:       int y;
0x08:       if (x==0) {
0x0c:           y = g();
0x10:           return y; }
            else {
0x14:           y = f(x-1);
0x18:           return y; }}
        void main() {
0x1c:       f(3);
0x20:       …}
```
- AR for f(3) (base 0x120), 위에서 아래로 쌓이는 필드: **Argument x (3)** / **Return for f(3)** (반환값 자리) / **Prev FP (0x100)** / **Local data (int y)** / **Return addr (0x20)**
- 이어서 AR for f(2) (base 0x134): Argument x(2), Return for f(2), Prev FP (0x120), Local data, Return addr (0x18) — 재귀 호출 주소 0x14 다음 명령 0x18이 return addr
- 즉 호출마다 자기 AR이 쌓이고, **Prev FP**가 이전 frame을 가리키는 연결(control/dynamic link) 역할

### About Return Data in x86 *(p.19)*
- 슬라이드는 **all-memory scheme**을 가정해 return data도 메모리에 저장하는 것으로 예시를 든 것
- 현대 프로세서에서는 반환값 전용 register(**rax**)가 있다
  - primitive type(4 또는 8 byte 이하)은 **데이터를 직접 rax에 저장**
  - 그보다 큰 데이터는 **데이터의 주소를 rax에 저장**

### Stack Management Using Register File *(p.20~23)*
- **p.20 — 두 개의 special register로 frame을 index**
  - **Stack pointer (SP)**: frame의 **top**을 가리킴
  - **Frame pointer (FP)**: frame의 **base**를 가리킴
  - 이 포인터들로 stack 안의 데이터를 index
  - 예: f(0) frame 최상단 = Argument x(0), Return for f(0), Prev FP(0x15c), Local data(int y), Return addr(0x18); 그 아래 g() frame(Return for g(), Prev FP(0x170), Return addr(0x18)). FP = 0x184, SP = 0x190
- **p.21 — procedure가 끝난 뒤 FP, SP 수정**
  - **FP를 SP로 copy**
  - ctrl link(Prev FP)에 있는 데이터를 **FP로 copy**
  - 반환 데이터는 **SP를 통해 접근** (`load $sp`)
- **p.22 — 왜 stack pointer가 두 개인가?**
  - stack frame 크기가 **compile time에 항상 알려진 것은 아니기 때문** (예: `_alloca`)
- **p.23 — 설계의 함께함**
  - 컴파일러는 **AR layout을 결정**하고 AR 내 위치를 정확히 접근하는 코드를 생성해야 한다 → **layout과 code generator는 함께 설계**되어야 한다
  - 예: f(3)의 AR에서 `$fp = 0x120`, `$fp + 0x8 = 0x128` (Local data 위치), Return addr (0x1c)

## 10. Saving Registers *(p.24)*

- **문제**: callee가 caller의 유용한 register 값을 **덮어쓸 수 있다**
- 생성된 코드는 **stack을 수정**해서 해결
  - 함수 호출 시 register 저장 (**Push**)
  - callee가 return할 때 복원 (**Pop**)
- 가능한 방식: callee 또는 caller가 저장/복원, 혹은 **일을 나눠서(둘 다 일부씩)** 수행

## 11. Pushing / Popping Values on the Stack *(p.25~26)*

### Pushing *(p.25)* — stack 위(아래로 쌓이는 순서): Params, Reg1, Reg2, Return Addr, Prev FP, Reg3, Reg4, Local Variables
- **Code before call instruction**
  - **Parameters push**
  - **caller-saved registers push** (Reg1, Reg2)
  - **return address (현재 PC) push 후 callee code로 jump**
- **Prologue = 함수 entry의 코드**
  - **dynamic link(= FP) push** (Prev FP)
  - **old stack pointer가 new frame pointer가 된다**
  - **callee-saved registers push** (Reg3, Reg4)
  - **local variables push**

### Popping *(p.26)* — 마지막에 Return Val이 추가된다
- **Epilogue = return instruction의 코드**
  - callee-saved registers pop (복원)
  - return value를 적절한 곳에 store
  - old stack pointer 복원
  - old frame pointer pop
  - return address pop 후 해당 주소로 jump
- **Code after call**
  - caller-saved registers pop (복원)
  - return value 사용

## 12. Example Call *(p.27~28)*

`foo(3,5)` 호출, machine에 r1, r2 두 register가 있고 **둘 다 callee save**라고 가정.

### Example Call - 1 *(p.27)*
- **Code before call instruction**
  - push arg1: `[sp] = 3`
  - push arg2: `[sp+4] = 5`
  - return address와 2 args를 위한 공간 확보: `sp = sp+12`
  - `call foo`
- **Prologue**
  - old frame pointer push: `[sp] = fp`
  - new fp 계산: `fp = sp`
  - r1, r2 push: `[sp+4] = r1, [sp+8] = r2`
  - local int 변수 3개를 위한 frame 생성: `sp = sp+24`

### Example Call - 2 *(p.28)*
- **Epilogue**
  - r1, r2 pop: `r1 = [sp-20], r2 = [sp-16]`
  - old fp 복원: `fp = [sp-24]`
  - frame pop: `sp = sp-24`
  - return address pop 후 return 실행: `rts`
- **Code after call**
  - return value 사용
  - args pop: `sp = sp-12`

## 13. Caller vs. Callee Saved Registers *(p.29)*

- **Caller-saved registers** (= volatile, call-clobbered): call을 가로질러 보존될 필요 없는 **임시값(temporary quantities)** 저장용
  - register를 저장/복원할 책임은 **caller** (caller가 원한다면)
- **Callee-saved registers** (= non-volatile, call-preserved): call을 가로질러 보존되어야 하는 **오래 사는 값(long-lived values)** 저장용
  - 저장/복원할 책임은 **callee** (필요하다면)

## 14. Accessing Stack Variables *(p.30)*

- stack 변수 접근은 **FP로부터의 offset** 사용
- 예시 (frame 구성: Params 1~n / Return Addr / Prev FP(=FP 위치) / Local 1~n / Param 1~n / SP)
  - `[fp-8] = param n`
  - `[fp-24] = param 1`
  - `[fp+4] = local 1`
  - (FP-4는 Return Addr, FP-24는 Params 시작 위치)

## 15. Global Variables *(p.32~33)*

- global 변수에 대한 모든 reference는 **같은 객체**를 가리킨다 → global activation을 activation record에 저장하는 것은 불가능하거나 비효율적
- global 변수는 한 번 **고정된 주소**가 할당된다 (**statically allocated**)
- 언어에 따라 다른 statically allocated 값도 있을 수 있다
- **Storage Organization** *(p.33)*: static variable은 **code memory 뒤에 할당**한다
  - 이전: Code / Stack → 이후: Code / **Static Data** / Stack

## 16. Dynamic Allocation *(p.34)*

- dynamically allocated 값은 (미리 삭제하지 않는 한) **생성한 procedure보다 오래 산다**
- 따라서 **heap**에 저장한다
- Storage Organization: Code / Static Data / Stack / **Heap** (그림에서 Heap이 가장 아래 High Addr 쪽)

## 17. Recap: Organization of Storage *(p.35)*

- **code area**: object code. 대부분 고정 크기이며 read-only
- **static area**: 고정 주소를 갖는 데이터 (예: global variables)
- **stack**: 현재 active한 각 procedure마다 AR 하나씩
- **heap**: 나머지 모든 (dynamically allocated) 데이터. 예) C는 `malloc`, `free`에 의존

## 18. Memory Addressing *(p.36~37)*

- 대부분의 현대 machine은 32 또는 64 bit
  - 1 byte = 8 bits
  - 1 word = 4 또는 8 bytes
- machine은 **byte addressable** 또는 **word addressable**
  - addressing format이 데이터가 memory에서 **어떻게 align** 되는지 결정
  - word addressable memory는 데이터를 **word-aligned**로 유지한다 (word boundary에서 시작)
- 예시 *(p.37)*: 문자열 `"Hello"` (`'H' 'e' 'l' 'l' 'o' '\0'`)
  - **Byte Addressing** (memory에서 채택): 0x00 'H', 0x01 'e', 0x02 'l', 0x03 'l', 0x04 'o', 0x05 '\0'
  - **Word Addressing** (register file에서 채택): 0x00 = 'H' 'e' 'l' 'l', 0x01 = 'o' '\0' PAD PAD

## 19. Memory Alignment *(p.38, 41)*

- 변수의 주소는 **변수의 크기에 따라 aligned** 된다 (변수를 임의로 packing할 수 없으므로 alignment를 고려해야 함 *(p.41)*)
  - **char**: byte aligned (아무 주소나 OK)
  - **short**: halfword aligned (byte addr의 LSB가 0이어야 함)
  - **int**: word aligned (byte addr의 하위 2 bit가 0이어야 함)
  - 이 규칙은 C/C++ 기준이며 다른 언어는 약간 다를 수 있음 *(p.41)*
- 예시 *(p.38)*
  ```c
  char x;    // size 1 byte
  int y;     // size 4 byte
  char z;    // size 1 byte
  short w;   // size 2 byte
  ```
  배치: `x PAD PAD PAD` / `y` (4 byte) / `z PAD w(2 byte)`

## 20. Big Endian vs. Little Endian *(p.39)*

- 32-bit signed/unsigned 정수는 4 byte (**MSB**(most significant) … **LSB**(least significant), 각 8-bit)
- `0x12345678` 저장 시
  - **Big Endian**: 낮은 주소부터 `12 34 56 78` (MSB가 낮은 주소). **pointer가 big end를 가리킨다**
  - **Little Endian**: 낮은 주소부터 `78 56 34 12` (LSB가 낮은 주소). **pointer가 little end를 가리킨다**

## 21. Data Layout *(p.40)*

- 일반적으로 쓰는 **naive layout strategy**: 프로그래머가 선언한 **순서대로** 데이터를 배치
- 두 가지 문제: **size, alignment**
- **Size** — 데이터 항목이 몇 byte인가?
  - base type은 고정 크기 (char, int, float, double 등)
  - composite type (struct, union, array): 전체 크기는 구성요소 크기의 합 (**정확히는 아니다 — padding 때문**). 각 field의 **offset**을 계산한다

## 22. Structure Alignment (for C) *(p.42~43)*

- 각 field는 선언된 순서대로 **Golden Rule for aligning**을 사용해 배치
- **가장 큰 field**를 찾는다
  - struct 전체의 **시작 주소**는 가장 큰 field 기준으로 align
  - struct 전체 **크기**는 가장 큰 field의 **배수**
  - 이유: **struct 배열**을 만들 수 있게 하기 위해서
- **Structure Example** *(p.43)*: struct는 word-aligned 주소에서 시작
  ```c
  struct {              // Largest field is int (4 bytes)
      char w;           // Struct size is multiple of 4
      int x[3];         // Struct's starting address is word aligned
      char y;
      short z;
  }
  ```
  배치: `w PAD PAD PAD` / `x[0]` / `x[1]` / `x[2]` / `y PAD z(2 byte)` → 총 20 byte

## 수업에서 다룬 섹션 (2026-11-26)

1. 컴파일러 전체 구조에서의 위치
2. Microarchitecture / ISA: 컴파일러가 아는 것
3. Storage Class Selection Problem
4. General Instruction Classes
5. Compiler Backend와 Runtime Organization
6. Executing a Program
7. Execution Sequence
8. Activation & Lifetime (Activation Tree 포함)
9. Stack Management (AR, Return Data in x86, SP/FP)
10. Saving Registers
11. Pushing / Popping Values on the Stack
12. Example Call
13. Caller vs. Callee Saved Registers
14. Accessing Stack Variables
15. Global Variables
16. Dynamic Allocation
17. Recap: Organization of Storage
18. Memory Addressing
19. Memory Alignment
20. Big Endian vs. Little Endian
21. Data Layout
22. Structure Alignment (for C)
