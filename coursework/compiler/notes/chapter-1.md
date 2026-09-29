# Chapter 1: Instruction Set Architecture & Compiler Basics

*2026 Fall, Hunjun Lee*

> 이 자료는 슬라이드에 쪽번호가 인쇄되어 있지 않아서, 아래 `p.N`은 PDF 파일 자체의 페이지 순서(1부터 시작)를 가리킨다.

## 1. Von Neumann Architecture *(p.3~18)*

### 컴퓨터의 기본 구성요소 *(p.3)*
범용 컴퓨터로 작업을 수행하려면 **컴퓨터 프로그램**(무엇을 할지 명시)과 **컴퓨터 자체**(그 작업을 실행)가 필요하다.
- **Program**: instruction들의 시퀀스
- **Instruction**: 컴퓨터가 수행할 수 있는 가장 작은 단위의 작업
- **Instruction set**: 컴퓨터가 수행하도록 설계된 모든 가능한 instruction들의 집합

### Von Neumann Architecture 구조 *(p.4, p.8, p.10, p.13, p.15, p.18)*
**명령어와 데이터를 모두 메모리에 저장**하는 구조. Instruction이 (1) 어떤 데이터를 어떻게 다룰지, (2) 다음에 실행할 instruction이 무엇인지를 결정한다.

```
Input → [CPU: Control Unit(PC) / ALU / Register] ↔ Memory Unit → Output
```
- ① Memory → Register: instruction 인출
- ② Memory → Register: data 인출
- ③ Register → ALU: 연산
- ④ Register ↔ Memory: data 저장/재인출
- ⑤ Control Unit: 다음 instruction 결정

Register는 **fast access & limited capacity**, Memory는 **slow access & large capacity**로 성격이 대비된다.

### State machine으로서의 컴퓨터 *(p.5)*
컴퓨터는 본질적으로 복잡한 state machine이다. 예: 자판기 — 500원/1000원을 입력받아 누적 금액(state)이 1500원이 되면 아이템을 출력하는 것과 같은 구조.

### Programmer Visible State (= Architectural State) *(p.6)*
- **Memory**: 주소로 인덱싱되는 저장 공간의 배열 (`M[0]` ~ `M[N-1]`)
- **Registers**: ISA에서 (주소가 아니라) 특별한 이름이 붙은 저장공간, general-purpose vs. special-purpose로 구분
- **Program Counter (PC)**: 현재 실행 중인 instruction의 메모리 주소
- Instruction(과 program)은 이 programmer visible state의 값을 어떻게 바꿀지를 명시한다

### 프로그램이 컴퓨터에 로드되는 과정 *(p.7)*
```
C program(*.c) --[Compiler]--> Assembly(*.s) --[Assembler]--> Object file(*.o)
   Object file(*.o) + Library object(*.o) --[Linker]--> Executable(*.exe) --[Loader]--> 메모리에 적재
```
Compiler/Assembler/Linker/Loader가 각 단계에서 "격차를 메우는(bridges the gap)" 역할을 한다.

### Runtime storage organization *(p.9)*
메모리는 (1) program(instructions)과 (2) 실행에 필요한 data를 저장한다.
- 메모리는 bit들의 모음이며, **byte(8bit)**와 **word**(예: 8/16/32bit) 단위로 논리적으로 그룹화됨 — word size가 instruction 폭, register 크기 등을 결정
- **Address space**: 메모리 내에서 고유하게 식별 가능한 위치의 총 개수 (아키텍처마다 다름)
  - LC-3: `2^16` (16bit 주소), MIPS: `2^32` (32bit 주소), x86-64: 최대 `2^48` (48bit 주소)

### Processing Unit / ALU *(p.11~12)*
- Processing unit은 실제 연산을 수행, 여러 **functional unit**으로 구성될 수 있음
- **ALU (Arithmetic and Logic Unit)**: 연산/논리 연산을 실행 (MIPS 예: add, sub, mult, and, nor...)
- ALU가 처리하는 단위를 **word**라 부름 (MIPS의 word 길이 = 32bit)
- ALU는 한 번에 한 기능만 수행하는 여러 산술/논리 연산을 하나의 unit으로 결합한 것

| F[2:0] | Function |
|---|---|
| 000 | Y = A and B |
| 001 | Y = A or B |
| 010 | A + B |
| 100 | A - B |
| 101 | A * B |
| 110 | A / B |
| 111 | SLT |

### Registers: fast storage *(p.14)*
- Memory는 크지만 느리고, register는 빠르지만 작음
- Processing unit은 ALU에 쓰일 값에 빠르게 접근하려고 register를 활용 (임시값 저장)
- **Combinational read & synchronous write** → 한 사이클 내에 read + ALU + write 실행 가능
- **Register Set(Register File)**: instruction이 조작할 수 있는 register들의 집합. MIPS는 **32개 register** 보유 (R0~R31, 5bit register ID, register 크기 = word 길이 = 32bit), `$fp`, `$sp` 같은 특수목적 register도 존재

### Control Unit *(p.16)*
- 프로그램을 **단계별(step-by-step)로 실행**하게 해줌 — instruction을 순서대로 처리
- **instruction register**를 통해 현재 처리 중인 instruction을 추적
- **program counter(PC)**를 이용해 다음에 처리할 instruction을 추적/결정

### Wrap up *(p.17)*
- **Memory Unit**: (1)program(instructions), (2)data 저장
- **ALU**: 실제 연산 수행
- **Control Unit**: 프로그램의 단계별 실행을 가능하게 함

---

## 2. Instruction Set Architecture (ISA) *(p.19~30)*

> "User's manual for the computer"

### Architecture의 정의 *(p.21)*
> "The term architecture is used here to describe the attributes of a system **as seen by the programmer**, i.e., the conceptual structure and functional behavior, as distinct from the organization of the data flow and controls, the logical design, and the physical implementation."
> — Amdahl, Blaauw and Brooks, *Architecture of the IBM System/360* (1964)

### Architecture Level vs. Microarchitecture Level *(p.22)*
- **Architecture Level**: 자동차의 운전 매뉴얼처럼 — 자동차 정비공이 아니어도 운전할 수 있듯, 회로 설계자가 아니어도 컴퓨터를 프로그래밍할 수 있게 해주는 수준(= program manual)
- **Microarchitecture(구현) Level**: 특정 설계가 가지는 구체적인 회로/제어 구성(예: v8 엔진 vs v4 엔진, adder 종류, cache 등)

### ISA에서 규정/결정하는 것들 *(p.23)*
프로그래머가 볼 수 있는 state를 **어떻게 바꿀지**를 규정:
- Data format과 크기 (character, binary, decimal, floating point...)
- "Programmer Visible State" (memory, register, PC 등)
- Instructions: 무엇을 수행할지/다음에 무엇을 수행할지, operand의 위치
- 외부 세계와의 인터페이스 방법, protection/privileged 연산, software convention
- 종종 **미래의 확장성과 호환성을 위해 성능을 일부 타협**한다

### General Instruction Classes *(p.24)*
1. **Arithmetic and logical operations** (add, sub, and, or): 지정된 위치에서 operand 로드 → 연산 → 결과 저장 → PC를 다음 instruction으로 갱신
2. **Data movement operations** (load, store): 지정된 위치에서 operand fetch/store → PC 갱신
3. **Control flow operations** (branch, jump): operand fetch → branch 조건과 target 주소 계산 → 조건이 참이면 `PC ← target address`, 거짓이면 `PC ← next instruction`
- 이 연산들은 일반적으로 **atomic**하게 정의됨

### RISC ISA *(p.25)*
- **Simple operations**: 2-input, 1-output 산술/논리 연산, 같은 작업을 하는 대안이 거의 없음
- **Simple data movements**: ALU 연산은 register-to-register(큰 register file 필요), 메모리는 오직 load/store instruction으로만 접근 → **"Load-store architecture"**
- **Simple branches**: 제한된 branch 조건/target 종류
- **Simple instruction encoding**: 모든 instruction이 **같은 bit 수**로 인코딩, 포맷 종류도 적음

### RISC vs. CISC *(p.26)*
- **RISC (Reduced ISA)**: 하드웨어가 기본 연산만 ISA로 노출, 단순한 instruction(+단순 디코딩), 고정 폭 instruction(1 word)
- **CISC (Complex ISA)**: 더 복잡한 연산(여러 RISC 스타일 연산의 조합)을 노출 — 예: 한 instruction이 메모리와 레지스터 양쪽에서 데이터를 로드하고, 덧셈을 수행하고, 결과를 다시 써넣는 것까지 수행 (예: `ADD r2, r1, [2000]`)

### ISA의 진화 *(p.27)*
- **초기 ISA가 단순했던 이유**: 기술적 한계, 경험/선례 부족
- **나중에 복잡해진 이유**: CISC 등장, 어셈블리 프로그래밍의 편의성, 1970~80년대의 메모리 크기/성능 부족, micro-programmed 구현
- **다시 단순해진 이유**: RISC 등장, 메모리 크기/속도 향상(캐시!), **컴파일러**의 발전
- x86(Intel/AMD)은 겉보기엔 CISC지만 내부적으로 RISC 스타일 micro-op으로 변환해 실행하는 등 예외적 사례

### 현대 프로세서의 ISA 확장 *(p.28~29)*
- **Intel AVX**: AVX-512 ISA를 정의해 벡터 연산을 지원 (예: `_mm512_ternarylogic_epi64` 같은 3-input 비트 연산 intrinsic)
- **RISC-V의 RoCC(Rocket Custom Coprocessor) interface**: 컴퓨터 아키텍트가 커스텀 coprocessor(예: NPU 같은 가속기)를 추가할 수 있게 해주는 인터페이스. Processing core가 cmd/resp/busy/interrupt 시그널로 accelerator를 제어

### Wrap-up: Terminologies *(p.30)*
- **ISA**: 프로그래머가 관찰/제어할 수 있는 machine의 동작
- **Instruction Set**: 컴퓨터가 이해하는 명령어들의 집합
- **Assembly Code**: instruction을 "텍스트" 형식으로 표현한 것 (예: `Add r1, r2, r3`) — assembler가 machine code로 변환, machine code와 1:1 대응
- **Machine Code**: instruction을 바이너리로 인코딩한 것(`0101000...`) — 하드웨어가 직접 소비 가능

---

## 3. MIPS ISA (32bit) 예제 *(p.31~40)*

### MIPS architectural state *(p.32)*
- **Memory**: byte-addressable, 32bit address space (`M[0]`~`M[N-1]`, 각 8bit)
- **Register File**: word-addressable, 32bit register 32개
- **Program Counter**: 32bit
- 즉 MIPS는 (1) 32bit word size, (2) 32-entry register file을 갖는 아키텍처

### MIPS instruction formats — 3가지 단순 포맷 *(p.33)*
```
R-type: | 0(6b) | rs(5b) | rt(5b) | rd(5b) | shamt(5b) | funct(6b) |
I-type: | opcode(6b) | rs(5b) | rt(5b) | immediate(16b) |
J-type: | opcode(6b) | immediate(26b) |
```
**Simple Decoding**: 포맷과 무관하게 모든 instruction은 4byte(고정 크기), 4byte 정렬 필요(PC의 하위 2bit는 항상 `00`), 필드를 쉽게 추출 가능.

### R-type Instructions *(p.34, p.40)*
- `funct`: ALU 연산 종류 — Arithmetic({signed,unsigned}×{ADD,SUB,MULT,DIV,...}), Logical(AND,OR,XOR,NOR,...), Shift(Left, Right-Logical, Right-Arithmetic)
- `shamt`: shift 연산에서만 쓰이는 shift amount
- Assembly: `opcode rd rs rt` → `RF[rd] = RF[rs] op RF[rt]`, `PC = PC + 4`
- **Control 버전 R-type**: `jr` — `jal label`(함수 호출 시)과 함께 쓰임. Assembly `jr rs` → `PC = RF[rs]`

### I-type Instructions *(p.35~36, 38)*
- **ALU ver.**: opcode에 `addi, addiu, andi, ori, xori, slti, sltiu, lui` 등. Assembly `opcode rt rs immediate` → `RF[rt] = RF[rs] op sign-extend(immediate)`, `PC = PC+4`
  - 32bit immediate가 필요하면: `lui`로 상위 16bit 저장 후 `ori`로 하위 16bit 저장 (예: `lui`로 `0xABCD`, `ori`로 `0x1234`)
- **Memory ver.**: opcode에 `lw, lh, lhu, lb, lbu`(load) / `sw, sh, sb`(store). Assembly `load/store rt offset(rs)`:
  ```
  RF[rt] = MEM[RF[rs] + sign-extend(offset)]     // load
  MEM[RF[rs] + sign-extend(offset)] = RF[rt]      // store
  PC = PC + 4
  ```
- **Control ver.**: opcode에 `bne, beq` 등(branch equal/not equal). Assembly `beq rs rt label`:
  ```
  target = (PC+4) + sign-extend(label) x 4   // word-aligned
  if (RF[rs]==RF[rt]) PC = target else PC = PC+4
  ```
  더 멀리(18bit 이상) jump하려면 J-type을 사용해야 함

### Control Flow와 Basic Block *(p.37)*
`if-else` 같은 소스코드는 control flow graph로 표현되고, 이는 다시 선형화된 assembly code(각 분기에 `goto`)로 변환됨. 분기/합류 지점 없이 순차 실행되는 코드 조각을 **basic block**이라 부름(code A, B, C, D 각각이 하나의 basic block).

### J-type Instructions *(p.39)*
- opcode: `j`, `jal`
- Assembly `j label`:
  ```
  target = (PC+4)[31:28] x 2^28 |bitwise-or zero-extend(label) x 4
  PC = target
  ```
  (PC의 상위 4bit + label×4를 이어붙임)
- Assembly `jal label`: `RF[ra] = PC+4` (다음 PC를 전용 register `ra`에 저장) 후 `PC = target`

---

## 4. Compiler Basics *(p.41~52)*

### Compiler가 메우는 간극(Filling the Gap) *(p.41)*
컴파일 툴체인은 사람이 이해할 수 있는 프로그램(고수준 언어)을 컴퓨터가 실행 가능한 바이너리 형태로 번역한다.
```
int sum; int a=1; int b=3; sum=a+b;   --[Compiler]-->   0100010000101...(binary)
```

### Compiler vs. Interpreter *(p.42)*
```
Compiler:    Program → [Compiler] → Executable, 이후 (Executable + Input Data) → Output Data
Interpreter: (Program + Input Data) → [Interpreter] → Output Data (바로 실행)
```

### Compiler의 Front-End / Back-End *(p.43)*
- **Front-End**: 고수준 언어로 프로그래밍할 수 있게 해줌 — 1970년대엔 펀치카드를 써야 했지만, 지금은 Fortran, C, C++, Java, Python, R, Tex, Html 등 다양한 언어 지원
- **Back-End**: 하드웨어별 세부사항이나 최적화를 고려하지 않고도 프로그래밍할 수 있게 해줌 — 내부 컴퓨터 아키텍처는 프로그래머가 완전히 이해하기 어려우므로, 컴파일러가 중복 코드를 최적화

### 현대 컴파일러의 일반적 구조 *(p.44)*
```
Source Code
  → [Front end: Lexical Analysis(Scanner) → Syntax Analysis(Parser) → Semantic Analysis(High-Level IR)]
  → Code Generation-1 (Machine Independent)
  → [Back end: Control/DataFlow Analysis ↔ Optimization → Code Generation-2 (Machine Dependent)]
  → Assembly Code
```
모든 단계는 **Context & Symbol Table & CFG**를 공유하며 참조/갱신한다.

### Lexical Analysis (Scanner) *(p.45~46)*
- 언어에서 문장을 단어로 나누듯, 프로그램을 **token**으로 나눔
  - 예: `if (b == 0) a = b;` → `if`(Keyword), `(`(Symbol), `b`(Identifier), `==`(Symbol), `0`(Constant), `)`(Symbol), `a`(Identifier), `=`(Symbol), `b`(Identifier), `;`(Symbol)
- 가장 낮은 수준의 lexical element를 추출/식별: 예약어(for, if, switch), 식별자(i, j, table), 상수(3.14159, 17, "%d\n"), 구두점 기호
- 공백/주석 등 비문법적 요소 제거
- **유한 상태 자동자(FSA)**로 구현됨 — 부분 입력을 나타내는 state 집합 + state 간 이동을 위한 transition function

### Syntax Analysis (Parser) *(p.47~48)*
- token들 사이의 **관계**를 결정 — 예: `if (b==0) a=b;`에서 `if(b==0)`는 Condition, `a=b`는 Assignment, 전체는 If Stmt로 구조화
- 프로그램의 **문법적 정확성**을 검사, 이후 semantic 처리를 위한 틀을 제공
- 다양한 구현 방식: 손으로 작성한 recursive descent, table 기반(top-down vs. bottom-up)

### Semantic Analysis *(p.49)*
여러 구분되는 작업을 지원: identifier 정의 확인/정확성 검증, type checking, declaration scope 처리, 오버로드된 연산자의 모호성 해소, source → intermediate representation(IR) 변환 등

### Optimization *(p.50)*
코드 품질을 최적화 — 상수 값을 식별해 미리 계산, 사용되지 않는 변수 제거, loop-invariant 변수 계산, 재계산되는 변수 제거 등

### Code Generation *(p.51)*
- machine-independent intermediate representation을 target architecture에 매핑
- **Virtual → physical binding**: instruction selection(범용 opcode를 구현할 최적의 machine opcode 선택), register allocation(무한한 가상 register를 N개의 물리 register에 매핑), assembly emission
- 결과물인 machine assembly를 이후 assembler/linker가 넘겨받아 binary를 생성

---

## 핵심 요약

- **Von Neumann architecture**는 instruction과 data를 모두 메모리에 저장하며, Memory Unit(느림/큼) - Register(빠름/작음) - ALU - Control Unit(PC)로 구성됨
- **ISA**는 "programmer가 보는 관점"에서 컴퓨터를 정의하는 명세로, programmer visible state(memory, register, PC)를 instruction이 어떻게 바꾸는지를 규정
- **RISC vs CISC**: 단순한 고정폭 instruction과 load-store 구조(RISC) vs 복잡하고 가변적인 instruction(CISC) — 역사적으로 기술 한계 → CISC 전성기 → 캐시/컴파일러 발전으로 RISC 재부상의 흐름을 보임
- **MIPS**는 32bit RISC ISA의 대표 예시: R-type(register 연산)/I-type(immediate, load-store, branch)/J-type(jump) 세 가지 고정폭 포맷
- **Compiler**는 고수준 언어를 기계어로 번역하는 도구로, Front-end(Lexical→Syntax→Semantic Analysis)와 Back-end(최적화, Code Generation)로 나뉘며, 이후 assembler/linker/loader를 거쳐 실행 가능한 바이너리가 된다
