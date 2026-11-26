# Chapter 6: Code Generation - 1 — 수업노트

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

*수업일: 2026-11-26 / 대응 정리노트: `notes/기말고사/chapter-6.md`*

**목표**: 함수 하나가 호출되고 리턴될 때 stack frame(AR)이 어떻게 쌓이고 풀리는지 직접 그릴 수 있게 되고, struct/변수의 메모리 배치를 손으로 계산할 수 있게 되는 것.

## 1. 컴파일러 전체 구조에서의 위치 *(p.2~4)*

```
Source Code
  → [Front end] Lexical(Scanner) → Syntax(Parser) → Semantic
  → Code Generation-1 / Control·DataFlow Analysis / Optimization   ← Machine Independent
  → Code Generation-2                                               ← Machine Dependent (back end)
  → Assembly Code
```

- 중간고사 범위는 front end. front end 결과물은 "이 프로그램이 문법적으로, 의미적으로 맞다"는 것과 AST, symbol table.
- 이제부터는 이걸 **실제 기계에서 돌아가는 코드**로 바꾸는 단계.
- 모든 단계가 **Context, Symbol Table, CFG**를 같이 참조한다. CFG(control flow graph)는 ch9에서 본격적으로 다룬다.
- ch6(Code Generation-1)은 machine independent 쪽이다. 특정 CPU의 레지스터 이름 같은 건 신경 쓰지 않고 "데이터를 어디에 어떻게 놓을까"라는 일반 원리를 다룬다.

## 2. Microarchitecture vs. ISA *(p.5~6)*

**ISA**: 컴파일러(소프트웨어)가 보는 CPU의 계약서. 어떤 명령어와 레지스터가 있고 메모리를 어떻게 접근하는지 정해둔 인터페이스.

**Microarchitecture**: 그 계약을 실제로 구현한 하드웨어 내부 구조.

p.5에서 microarchitecture 쪽에 숨어 있는 것들:
- CISC→RISC translation, hyper-threading, branch prediction, out-of-order execution (168-entry ROB, 54-entry issue queue, 물리 레지스터 144~160개)
- core당 2 thread, chip당 4~6 core
- L1 i-cache 32KB, L1 d-cache 32KB, L2 256KB, L3 8~12MB

**컴파일러는 이걸 직접 다루지 않는다.** (p.6) 컴파일러 눈에 CPU는 세 가지로 보인다.

| 구성요소 | 의미 |
|---|---|
| Compute Units | 어떤 연산이 가능한가 (add, sub, ...) |
| Register File | 빠르지만 작음. load/store 대상 |
| Memory | 느리지만 큼. 낮은 주소엔 Code, 높은 주소엔 Data |

예: 물리 레지스터가 160개 있어도 ISA가 16개만 노출하면 컴파일러는 16개만 있다고 보고 코드를 짠다. 나머지는 하드웨어가 register renaming으로 알아서 쓴다.

## 3. Storage Class Selection Problem *(p.7)*

**Storage Class Selection**: 각 데이터를 register file에 둘지 memory에 둘지 정하는 문제.

**Standard approach**
- **Globals / Statics → memory**: 어느 함수에서든 같은 객체로 접근돼야 하고 프로그램 내내 살아 있어야 하므로 고정 주소가 필요하다.
- **Locals**
  - **Composite type**(struct, array) → memory
  - **나머지**(int, pointer 같은 스칼라) → **virtual register**

**Composite type이 memory로 가는 이유는 크기 + 주소 기반 접근 두 가지다.**
- register 하나에 다 들어가지 않는다.
- 더 근본적으로, **register에는 주소가 없다.** `a[i]`는 컴파일하면 `*(a + i*4)`처럼 "시작 주소 + offset"으로 계산해서 접근하므로 배열은 주소로 인덱싱할 수 있는 memory에 있어야 한다.
- 작은 배열(`int a[2]`)이라도 `a[i]`처럼 런타임 인덱스로 접근하면 register에 둘 수 없다. 같은 이유로 지역 int라도 `&n`처럼 주소를 꺼내 쓰면 memory로 가야 한다.

**Virtual register**: 개수 제한이 없다고 가정한 가상의 레지스터. 일단 무한하다고 치고 코드를 생성하고, 실제 물리 레지스터로의 매핑은 나중에 **Register Allocation(ch10)** 이 맡는다. 문제를 둘로 나눠 단순하게 만드는 것.

**All memory approach**: 모든 변수를 memory에 두는 방식. 단순하지만 느리다. 이번 챕터 슬라이드 예제들은 이 방식을 가정한다(p.19에서 다시 언급).

## 4. General Instruction Classes *(p.8)*

세 종류 모두 마지막에 **PC를 어떻게 바꾸는지**가 포인트.

| 종류 | 예 | 하는 일 | PC |
|---|---|---|---|
| Arithmetic / Logical | add, sub, and, or | operand load → 결과 compute → 결과 store | 다음 명령어 |
| Data movement | load, store | operand fetch → 지정 위치에 store | 다음 명령어 |
| Control flow | branch, jump | operand fetch → 조건·target address 계산 | 조건이 true면 target, 아니면 다음 명령어 |

앞의 두 종류는 PC가 항상 순차적으로 증가한다. **control flow만 PC를 다른 곳으로 보낼 수 있다.** 이게 call/return, 그리고 ch9의 basic block 개념의 기반.

## 5. Compiler Backend와 Runtime Organization *(p.9~10)*

**Runtime Organization (Storage Organization)**: 프로그램이 실행될 때 코드와 데이터가 메모리 공간에 어떻게 배치되고 관리되는지에 대한 설계.

- 컴파일러는 코드만 생성하는 게 아니라 **데이터가 메모리 어디에 어떻게 놓일지도 orchestrate** 해야 한다.
- 생성된 코드가 그 데이터를 조작하기 때문. `x = x + 1`을 기계어로 바꾸려면 "x가 어디 있는지"를 알아야 한다.
- **"The code and data layout are codesigned"**: 레이아웃을 먼저 정하고 코드를 짜는 게 아니라 둘이 맞물려 같이 설계된다. (Code는 Low Addr, Data는 High Addr)

## 6. Executing a Program *(p.11)*

프로그램 실행은 **OS**가 제어한다.

1. 프로그램용 메모리 공간 할당
2. code와 data를 그 공간에 load
3. entry point(`main`)로 jump

여기서부터가 컴파일러가 만든 코드의 영역. 실제로는 `_start` 같은 런타임 초기화 코드가 먼저 돌고 `main`을 부르지만 슬라이드는 단순화했다.

## 7. Execution Sequence *(p.12)*

컴파일러가 코드를 생성할 때 깔고 가는 두 가정:

1. **실행은 순차적이다.** control은 well-defined order로 한 지점에서 다른 지점으로 이동한다. (concurrency는 예외)
2. **procedure가 호출되면 control은 항상 호출 직후 지점으로 돌아온다.** (exception은 예외)

2번 가정 덕분에 "돌아올 주소(return address)"를 저장해두면 된다는 설계가 나오고, 그게 stack 구조로 이어진다.

## 8. Activation & Lifetime *(p.13~16)*

### Activation과 Lifetime *(p.13)*

**Activation**: procedure P를 한 번 호출(invocation)한 실행 그 자체.

**Lifetime**: 어떤 것이 실행 중에 존재하는(정의된) 구간.

- **activation of P의 lifetime** = P를 실행하는 모든 단계. **P 안에서 호출한 sub-procedure 실행 시간도 포함.**
  - 예: main이 f를 부르고 f가 g를 부르면, g가 도는 동안에도 f의 activation은 살아 있다.
- **변수 x의 lifetime** = x가 정의되어 있는 실행 구간.
- **Lifetime은 dynamic 개념.** 실행해봐야 알 수 있다.

**scope와 구분**: scope는 **static**(소스 코드상 어디서 이름이 보이나, semantic analysis에서 다룸), lifetime은 **dynamic**(실행 중 언제 존재하나). 재귀함수의 지역변수 `y`는 scope는 하나지만 실행 중에는 호출마다 별개의 `y`가 동시에 여러 개 살아 있을 수 있다.

### Properly nested & Activation Tree *(p.14)*

- P가 Q를 호출하면 **Q가 P보다 먼저 return**한다 → activation lifetime은 **properly nested**. 겹친다면 한쪽이 다른 쪽을 완전히 포함하고, 어긋나게 겹치는 일은 없다.
- nested 구조라서 트리로 그릴 수 있다: **activation tree**.

```c
int g() { return 1; }
int f() { return g(); }
void main() {
    g();
    f();
}
```

```
      main
     /    \
    g      f
           |
           g
```

- 자식은 왼쪽부터 호출된 순서대로.
- g가 두 번 나온다. **트리의 노드는 함수가 아니라 activation(호출 한 번)** 이다.

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

```
main → f(3) → f(2) → f(1) → f(0) → g()
```

재귀라서 일직선. f가 4개 activation으로 동시에 살아 있고 각자 자기 `x`를 갖는다.

### Activation Tree의 성질 *(p.16)*

- **activation tree는 run-time behavior에 따라 달라진다.** `f(3)` 대신 `f(input)`이면 입력마다 트리 깊이가 다르다. 그래서 컴파일러는 트리를 미리 알 수 없다.
- 대신 **stack**으로 실행 중 "지금 active한 procedure들"을 추적한다. p.14 코드 실행 시:

```
Step1: main
Step2: main, g        ← g 호출
Step3: main           ← g 리턴
Step4: main, f        ← f 호출
Step5: main, f, g     ← f 안에서 g 호출
Step6: main, f        ← g 리턴
Step7: main           ← f 리턴
Step8: (비어 있음)     ← main 리턴
```

**stack의 현재 상태 = activation tree에서 루트부터 현재 실행 중인 노드까지의 경로.** 트리 전체는 실행 내내 DFS로 훑어지고, stack은 그 DFS 경로를 들고 있다. properly nested라서 stack(LIFO)으로 관리할 수 있다.

**properly nested가 아니면 왜 stack이 안 되나?** (수업 중 질문, 사용자 답: 정답) stack은 LIFO라서 맨 위(Q)를 빼기 전엔 그 아래(P)를 뺄 수 없다. properly nested라는 성질이 "나중에 호출된 게 먼저 끝난다"를 보장하므로 LIFO와 딱 맞는다.
- 참고(시험 범위 아님): 이 가정이 깨지는 경우도 있다. 내부 함수가 바깥 함수의 지역변수를 붙잡고 더 오래 사는 closure, coroutine 등. 이런 언어는 해당 frame(또는 붙잡힌 변수)을 heap에 둔다.

## 9. Stack Management *(p.17~23)*

### 기본 구조 *(p.17)*

**Activation Record (AR, frame)**: activation 하나를 관리하는 데 필요한 정보를 stack에 묶어둔 덩어리.

- 호출할 때마다 AR이 push되고, 리턴하면 pop.
- **슬라이드 그림에서는 stack이 Code 아래쪽에서 시작해 주소가 증가하는 방향으로 자란다.** (AR for main → f() → g() 순으로 아래에 쌓임)
  - 실제 x86은 높은 주소 → 낮은 주소로 자라지만, **이 수업 예제는 전부 주소 증가 방향**. `sp = sp+12`로 공간을 확보하는 것도 그래서다. 시험은 슬라이드 기준으로 계산.

### Stack Management Example *(p.18)*

왼쪽 숫자는 각 명령어의 코드 주소.

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

f(3)의 AR (base 0x120)

| 필드 | 값 | 의미 |
|---|---|---|
| Argument x | 3 | 인자 |
| Return for f(3) | (반환값 자리) | f가 리턴할 값을 놓을 곳 |
| Prev FP | 0x100 | 호출한 쪽(main) frame의 base |
| Local data | int y | 지역변수 |
| Return addr | 0x20 | 리턴 후 돌아갈 코드 주소 |

f(2)의 AR (base 0x134): x=2, Return for f(2), **Prev FP = 0x120**, Local data, **Return addr = 0x18**

1. **Return addr가 0x20, 0x18인 이유**
   - f(3)은 main의 0x1c에서 호출 → 돌아갈 곳은 다음 명령 **0x20**.
   - f(2)는 f(3) 안의 0x14(`y = f(x-1)`)에서 호출 → 돌아갈 곳은 **0x18**.
   - **return address는 "호출한 명령의 다음 주소"**. 같은 함수 f여도 누가 어디서 불렀느냐에 따라 달라진다.
2. **Prev FP가 frame들을 체인으로 연결한다.** f(2)의 Prev FP = 0x120 = f(3)의 base. 이 연결을 **control link (dynamic link)** 라고 한다. 리턴할 때 이걸 따라가 caller frame으로 복귀한다.

### About Return Data in x86 *(p.19)*

- 슬라이드에서 반환값을 AR 안(Return for f(3))에 두는 건 **all-memory scheme**을 가정했기 때문.
- 현대 프로세서는 반환값 전용 register **rax**를 쓴다.
  - primitive type(4 또는 8 byte 이하): **값 자체를 rax에**
  - 그보다 큰 데이터(큰 struct 등): **데이터의 주소를 rax에**

### SP와 FP *(p.20~23)*

**Stack Pointer (SP)**: 현재 frame의 top(끝)을 가리키는 register.

**Frame Pointer (FP)**: 현재 frame의 base(시작)를 가리키는 register.

p.20 예시는 f(0)이 g()를 호출한 상태.
- f(0) frame: x(0), Return for f(0), Prev FP(0x15c), y, Return addr(0x18)
- g() frame: Return for g(), Prev FP(0x170), Return addr
- 현재 FP = 0x184 (g frame의 base), SP = 0x190 (g frame의 top)

**리턴할 때 FP, SP 복구** *(p.21)*
1. **FP를 SP로 copy** → 현재 frame을 통째로 버리는 효과 (SP가 frame 시작점으로 돌아감)
2. **ctrl link(Prev FP)에 있던 값을 FP로 copy** → FP가 caller frame의 base로 돌아감
3. 반환값은 **SP를 통해 접근** (`load $sp`)

**왜 포인터가 두 개 필요한가?** *(p.22)*
- **frame 크기가 compile time에 항상 정해지진 않기 때문.** 예: `_alloca(n)`은 런타임 크기 n만큼 stack에 공간을 잡는다.
- frame 크기가 고정이면 SP 하나로 `SP - 고정 offset`처럼 다 계산할 수 있다. 하지만 중간에 SP가 런타임 값만큼 움직이면 SP 기준 offset이 매번 달라진다.
- FP는 frame 시작에 고정돼 있으므로 **지역변수·인자를 FP 기준 고정 offset으로 항상 접근할 수 있다.** SP는 자유롭게 움직이는 top 역할만 한다.

**Layout과 code generator는 함께 설계된다** *(p.23)*
- 컴파일러가 AR layout을 정하고, 그 layout에 맞춰 정확한 위치에 접근하는 코드를 생성해야 한다.
- 예: f(3)의 AR에서 `$fp = 0x120`이면 local data `y`는 `$fp + 0x8 = 0x128`. 코드 생성기는 `y` 접근 시 `[fp+8]` 코드를 생성한다. layout이 바뀌면 이 offset도 바뀌어야 하므로 둘은 같이 설계된다. (5번 섹션 "codesigned"의 구체적 의미)

## 10. Saving Registers *(p.24)*

**문제**: register는 모든 함수가 공유한다. callee가 실행되면서 caller가 쓰던 register 값을 덮어쓸 수 있다.

```
caller:  r1 = 중요한 값
         call foo        ; foo 안에서 r1을 자기 용도로 씀
         r1 사용          ; 값이 망가져 있음
```

**해결**: 생성된 코드가 stack을 이용한다.
- 호출할 때 register를 stack에 저장 (**push**)
- return할 때 복원 (**pop**)

**누가 저장하나?** caller, callee, 또는 **일을 나눠서 둘이 일부씩**. 실제로는 나누는 방식을 쓰고, 그게 13번 섹션(caller-saved vs. callee-saved).

## 11. Pushing / Popping Values on the Stack *(p.25~26)*

**누가(caller/callee) 언제 뭘 하는지**로 기억한다.

### Pushing *(p.25)*

쌓이는 순서: `Params → Reg1, Reg2 → Return Addr → Prev FP → Reg3, Reg4 → Local Variables`

**[caller] Code before call instruction**
1. parameters push
2. caller-saved registers push (Reg1, Reg2)
3. return address(현재 PC) push 후 callee로 jump ← `call` 명령이 하는 일

**[callee] Prologue** (함수 entry 코드)
4. dynamic link(= 현재 FP) push → Prev FP
5. **old SP가 new FP가 된다** (`fp = sp`)
6. callee-saved registers push (Reg3, Reg4)
7. local variables 공간 push

5번이 중요: prologue 시점의 SP 위치가 곧 새 frame의 base.

**4번과 5번 순서를 바꾸면?** (수업 중 질문, 첫 답은 빗나갔다가 재설명 후 정답)
- FP는 register 하나라 값을 하나만 담는다. `push FP`는 **지금 FP register에 든 값**을 stack에 복사하고, `fp = sp`는 FP register를 **덮어쓴다**.
- 순서를 바꾸면:
  ```
  fp = sp      ; ① caller의 FP 값이 덮어써져 사라짐
  push fp      ; ② 이미 바뀐 값(= SP 값, 새 frame의 base)이 저장됨
  ```
- Prev FP 자리에 caller frame이 아니라 자기 자신을 가리키는 값이 들어간다. epilogue에서 old FP를 pop해도 caller frame으로 못 돌아가고 control link 체인이 끊긴다.
- **원칙: 저장(push)이 덮어쓰기보다 먼저.** register 값을 보존하는 코드는 전부 이 원칙을 따른다.

### Popping *(p.26)*

**[callee] Epilogue** (return 코드)
1. callee-saved registers pop (복원)
2. return value를 적절한 곳에 store (Return Val 자리 또는 rax)
3. old SP 복원 (locals 버림)
4. old FP pop
5. return address pop 후 그 주소로 jump ← `ret` 명령

**[caller] Code after call**
6. caller-saved registers pop (복원)
7. return value 사용

**pop은 push의 정확한 역순**이고, 경계는 대칭이다.

```
caller가 push  │ callee가 push      callee가 pop       │ caller가 pop
Params, Reg1/2,│ Prev FP, Reg3/4,  Reg3/4, locals,     │ Reg1/2, (Params)
Return Addr    │ Locals            Prev FP, Return Addr│
```

자기가 push한 건 자기가 pop한다. Return Addr만 예외로, caller의 `call`이 push하고 callee의 `ret`이 pop한다.

## 12. Example Call *(p.27~28)*

`foo(3,5)` 호출. 가정:
- register는 r1, r2 두 개
- **둘 다 callee-saved** → caller는 register를 저장하지 않음 (Reg1, Reg2 단계 생략)
- int는 4 byte, **stack은 주소 증가 방향** (그래서 `sp = sp + ...`로 공간 확보)
- foo에는 local int가 3개

### Example Call - 1 *(p.27)*

**[caller] Code before call**
```
[sp]   = 3        ; push arg1
[sp+4] = 5        ; push arg2
sp = sp + 12      ; arg 2개(8) + return address(4) 공간 확보
call foo          ; return address 저장 후 jump
```
- 12 = arg 2개 × 4 + return address 4. 공간을 먼저 잡아두고 `call`이 return address를 그 자리에 넣는다고 보면 된다.

**[callee] Prologue**
```
[sp]   = fp       ; old FP push
fp = sp           ; new FP = 현재 SP
[sp+4] = r1       ; r1 push (callee-saved)
[sp+8] = r2       ; r2 push
sp = sp + 24      ; frame 생성
```

24의 구성:

| 내용 | 크기 |
|---|---|
| old FP | 4 |
| r1 | 4 |
| r2 | 4 |
| local int × 3 | 12 |
| **합계** | **24** |

슬라이드 주석은 "local int 3개를 위한 frame"이지만 sp가 움직이는 24 byte에는 FP, r1, r2 저장 공간까지 들어 있다.

prologue 후 frame 모양 (fp 기준):
```
fp - 12 ~ fp - 8 : arg1 = 3, arg2 = 5 (caller 영역)
fp - 4           : return address     (caller 영역)
fp + 0           : old FP             ← fp
fp + 4           : r1
fp + 8           : r2
fp + 12 ~ +20    : local × 3
fp + 24                               ← sp
```

### Example Call - 2 *(p.28)*

**[callee] Epilogue**
```
r1 = [sp-20]      ; r1 pop
r2 = [sp-16]      ; r2 pop
fp = [sp-24]      ; old fp 복원
sp = sp - 24      ; frame pop
rts               ; return address pop + 그 주소로 jump
```

offset 검산 (sp = fp + 24):
- `sp - 24` = fp + 0 → old FP ✓
- `sp - 20` = fp + 4 → r1 ✓
- `sp - 16` = fp + 8 → r2 ✓

**SP 기준으로 접근하는 이유**: `fp = [sp-24]`로 FP를 복원하는 순간 FP는 caller의 FP로 바뀌므로 그 뒤로는 FP 기준으로 이 frame에 접근할 수 없다. 그래서 **r1, r2를 먼저 꺼내고 FP는 나중에** 복원한다.

**[caller] Code after call**
```
(return value 사용)
sp = sp - 12      ; args + return address 공간 pop
```
caller가 잡은 12는 caller가 푼다 ("자기가 push한 건 자기가 pop").

## 13. Caller-saved vs. Callee-saved Registers *(p.29)*

**Caller-saved register** (= volatile, call-clobbered): call을 건너면 값이 깨져도 되는 register. 보존이 필요하면 caller가 저장·복원한다.

**Callee-saved register** (= non-volatile, call-preserved): call 전후로 값이 유지돼야 하는 register. 쓰려면 callee가 저장했다가 복원한다.

| | Caller-saved | Callee-saved |
|---|---|---|
| 다른 이름 | volatile, call-clobbered | non-volatile, call-preserved |
| 용도 | **임시값**(temporary). call 건너서 안 살아도 되는 값 | **오래 사는 값**(long-lived). call 건너서 살아야 하는 값 |
| 저장 책임 | caller (필요하면) | callee (그 register를 쓸 거면) |

- 이름이 헷갈리면 "**누가 저장 책임을 지나**"로 외운다. caller-saved는 caller가 저장.
- 둘 다 "필요하면"이 핵심. call 뒤에 안 쓸 임시값이면 caller는 저장 안 해도 되고, callee가 어떤 callee-saved register를 아예 안 쓰면 저장 안 해도 된다. 둘로 나누면 불필요한 push/pop이 줄어든다.
- 참고: x86-64 System V에서 rax, rcx, rdx, rsi, rdi, r8~r11은 caller-saved, rbx, rbp, r12~r15는 callee-saved. 그래서 prologue에 `push rbp`, `push rbx`가 자주 보인다.

**Example Call에서 foo가 r1만 쓰고 r2를 안 쓴다면?** (수업 중 질문, 답을 알려줌)
- callee-saved는 callee가 쓸 때만 저장하면 되므로 r2 저장/복원 코드를 빼고, frame도 4 byte 줄어든다.
  ```
  ; Prologue
  [sp]   = fp
  fp = sp
  [sp+4] = r1
  sp = sp + 20      ; old FP 4 + r1 4 + local 12 = 20

  ; Epilogue
  r1 = [sp-16]      ; fp+4 = (fp+20)-16
  fp = [sp-20]      ; fp+0
  sp = sp - 20
  rts
  ```
- **24 → 20.** frame 크기가 바뀌면 epilogue의 SP 기준 offset도 같이 바뀐다 → "layout과 code generator는 함께 설계된다". 안 쓰는 register의 저장 비용이 0이라는 게 callee-saved의 장점.

## 14. Accessing Stack Variables *(p.30)*

stack 변수는 **FP로부터의 offset**으로 접근한다. SP는 움직이지만 FP는 frame 안에서 고정이기 때문.

```
fp - 24 : param 1
  ...
fp - 8  : param n
fp - 4  : return addr
fp + 0  : prev FP          ← fp
fp + 4  : local 1
  ...   : local n
        : (다음 호출용) param 1 ~ n
                           ← sp
```

- `[fp-8]` = param n
- `[fp-24]` = param 1
- `[fp+4]` = local 1

**FP 기준 음수 offset은 caller가 넣어준 것(인자, return addr), 양수 offset은 내 것(지역변수).** 컴파일러는 symbol table에 각 변수의 offset을 기록해두고, `y`가 나오면 `[fp+offset_y]` 코드를 생성한다.

(p.31은 p.17 stack 구조 복습 슬라이드)

## 15. Global Variables *(p.32~33)*

- global 변수는 어느 함수에서 참조하든 **같은 객체**를 가리킨다. activation마다 생기는 게 아니므로 AR에 넣는 건 불가능하거나 비효율적.
- 그래서 **고정 주소를 한 번 할당**받는다: **statically allocated**.
- 언어에 따라 다른 값도 statically allocated될 수 있다 (C의 `static` 지역변수, 문자열 리터럴 등).

**Storage Organization 변화** *(p.33)*: static data는 **code 뒤에** 둔다.
```
이전: Code / Stack
이후: Code / Static Data / Stack
```

global `g` 접근 시 FP offset이 아니라 **고정 주소(또는 라벨)** 를 쓰는 코드를 생성한다. 예: `load r1, [g_addr]`.

## 16. Dynamic Allocation *(p.34)*

- 동적으로 할당된 값은 (미리 해제하지 않는 한) **자기를 만든 procedure보다 오래 산다.**
  ```c
  int *make() {
      int *p = malloc(4);   // make가 리턴해도 이 4 byte는 살아 있어야 함
      return p;
  }
  ```
- AR에 넣으면 make가 리턴할 때 frame과 함께 사라진다. lifetime이 properly nested를 따르지 않는 데이터(8번 섹션 질문과 같은 논리).
- 그래서 **heap**에 저장한다.
```
Code / Static Data / Stack / Heap     (Heap이 가장 High Addr 쪽)
```

## 17. Recap: Organization of Storage *(p.35)*

| 영역 | 내용 | 특징 |
|---|---|---|
| **code** | object code | 대부분 고정 크기, read-only |
| **static** | 고정 주소를 갖는 데이터 (global 등) | 크기가 compile time에 결정 |
| **stack** | active한 procedure마다 AR 하나씩 | 호출/리턴에 따라 push/pop |
| **heap** | 나머지 동적 할당 데이터 | C는 `malloc`/`free` |

데이터가 어디 가는지는 **lifetime이 뭐랑 맞물리냐**로 정해진다.
- 프로그램 전체 → static
- activation 하나 → stack
- 프로그래머가 정함 → heap

## 18. Memory Addressing *(p.36~37)*

- 현대 machine은 대부분 32 또는 64 bit. 1 byte = 8 bit, 1 word = 4 또는 8 byte.

**Byte addressable**: 주소 하나가 1 byte를 가리키는 방식.

**Word addressable**: 주소 하나가 1 word를 가리키는 방식. 데이터가 항상 word boundary에서 시작한다(word-aligned).

addressing format이 데이터가 memory에서 어떻게 align되는지를 결정한다.

예시 *(p.37)*: `"Hello"` = `'H' 'e' 'l' 'l' 'o' '\0'` (6 byte)

**Byte Addressing** (memory에서 채택)
```
0x00 'H'  0x01 'e'  0x02 'l'  0x03 'l'  0x04 'o'  0x05 '\0'
```

**Word Addressing** (register file에서 채택, word = 4 byte)
```
0x00 : 'H' 'e' 'l' 'l'
0x01 : 'o' '\0' PAD PAD
```

word addressing에서는 주소 1 증가가 4 byte 이동. 마지막 word의 남는 칸은 PAD.

## 19. Memory Alignment *(p.38, 41)*

**Alignment**: 변수의 주소가 그 변수 크기의 배수가 되도록 배치하는 규칙.

| 타입 | 크기 | 정렬 | 주소 조건 |
|---|---|---|---|
| char | 1 | byte aligned | 아무 주소나 |
| short | 2 | halfword aligned | 주소의 최하위 1 bit = 0 (2의 배수) |
| int | 4 | word aligned | 주소의 하위 2 bit = 00 (4의 배수) |

- "하위 2 bit = 0" = 4의 배수. 4 = 100(2)이므로 4의 배수는 끝 두 자리가 항상 00.
- C/C++ 기준이며 언어마다 조금 다를 수 있다 *(p.41)*.
- 그래서 변수를 임의로 빽빽하게 packing할 수 없다. 정렬이 안 맞는 접근은 하드웨어가 두 번 읽어야 하거나 fault를 낸다 *(p.41)*.

예시 *(p.38)*
```c
char x;    // 1 byte
int y;     // 4 byte
char z;    // 1 byte
short w;   // 2 byte
```

| 주소 | 0 | 1 | 2 | 3 | 4~7 | 8 | 9 | 10~11 |
|---|---|---|---|---|---|---|---|---|
| | x | PAD | PAD | PAD | y | z | PAD | w |

- x는 0. y(int)는 4의 배수여야 해서 1~3은 PAD.
- z는 8. w(short)는 2의 배수여야 해서 9는 PAD, w는 10~11.
- 실제 데이터 8 byte, 차지하는 공간 12 byte.

## 20. Big Endian vs. Little Endian *(p.39)*

`0x12345678` 저장 (MSB = 12, LSB = 78)

| 방식 | 낮은 주소 → 높은 주소 | 슬라이드 표현 |
|---|---|---|
| Big Endian | `12 34 56 78` | pointer가 **big end**(MSB)를 가리킨다 |
| Little Endian | `78 56 34 12` | pointer가 **little end**(LSB)를 가리킨다 |

"pointer가 가리킨다" = 변수의 주소(가장 낮은 주소)에 어느 쪽 byte가 있냐.

## 21. Data Layout *(p.40)*

- **naive layout strategy**: 프로그래머가 **선언한 순서대로** 배치.
- 신경 쓸 두 가지: **size**, **alignment**.
- **Size**: 데이터 항목이 몇 byte인가?
  - base type(char, int, float, double)은 고정 크기
  - composite type(struct, union, array)은 구성요소 크기의 합인데 **padding 때문에 정확히 합은 아니다.** 각 field의 **offset**을 계산해야 한다.
- 이 offset이 코드 생성에 쓰인다. `s.y` 접근 → `[s의 주소 + offset_y]`.

## 22. Structure Alignment (for C) *(p.42~43)*

**Golden Rule**
1. 각 field는 **선언 순서대로**, 각자의 alignment 규칙(19번)에 맞춰 배치.
2. **가장 큰 field**를 찾는다.
   - struct **시작 주소**는 가장 큰 field 기준으로 align
   - struct **전체 크기**는 가장 큰 field 크기의 **배수**
3. 이유: **struct 배열**을 만들 수 있게. `arr[1]`은 `arr[0]` 바로 뒤에서 시작하므로 전체 크기가 배수가 아니면 `arr[1]`의 int field가 misalign된다.

예시 *(p.43)*
```c
struct {          // 가장 큰 field: int (4 byte)
    char w;       // → 크기는 4의 배수, 시작은 word aligned
    int x[3];
    char y;
    short z;
}
```

| offset | 0 | 1~3 | 4~7 | 8~11 | 12~15 | 16 | 17 | 18~19 |
|---|---|---|---|---|---|---|---|---|
| | w | PAD | x[0] | x[1] | x[2] | y | PAD | z |

- 총 **20 byte**, 4의 배수라 끝 padding 없음.
- `int x[3]`은 배열이지만 alignment 기준은 **원소 타입 int(4)**. "가장 큰 field"도 배열 전체(12)가 아니라 int 기준.

**계산 순서**: offset 0부터 각 field를 "자기 크기의 배수 위치"로 밀어서 놓고, 마지막에 전체 크기를 가장 큰 field의 배수로 올림.

### 연습: struct offset 계산 (종료 확인 질문, 답을 알려줌)

```c
struct {
    char a;     // 1
    short b;    // 2
    char c;     // 1
    int d;      // 4
    char e;     // 1
}
```

| offset | 0 | 1 | 2~3 | 4 | 5~7 | 8~11 | 12 | 13~15 |
|---|---|---|---|---|---|---|---|---|
| | a | PAD | b | c | PAD | d | e | PAD |

- a: 0
- b: short → 2의 배수, 1은 PAD, **b = 2**
- c: **4**
- d: int → 4의 배수, 5~7은 PAD, **d = 8**
- e: **12**
- 13 byte에서 끝나지만 가장 큰 field가 int(4)라 4의 배수로 올림 → 13~15 PAD → **총 16 byte**

**함정**: 끝의 13~15 PAD. field 기준 padding만 하면 13으로 끝나는데, "전체 크기는 가장 큰 field의 배수"에서 3 byte가 더 붙는다. 그래야 `arr[1].d`가 16+8 = 24로 4의 배수가 된다.

참고(실무 팁): 선언 순서를 `int d; short b; char a; char c; char e;`로 바꾸면 4+2+1+1+1 = 9 → 12 byte. 큰 타입부터 선언하면 padding이 줄어든다.

## 종합: 함수 호출 하나의 전체 과정 (종료 확인 질문, 답을 알려줌)

**[caller] 호출 전**
1. 인자(params) push
2. call 뒤에도 써야 하는 caller-saved register push
3. `call`: **return address**(호출 명령 다음 주소) push 후 callee로 jump

**[callee] Prologue**
4. 현재 FP(= caller frame의 base)를 **Prev FP**로 push. FP를 덮어쓰기 전에 해야 한다.
5. `fp = sp`: 지금 SP 위치가 새 frame의 base
6. 자기가 쓸 **callee-saved register** push
7. 지역변수 공간 확보 (SP 이동)

**[callee] 본체 실행**: 인자·지역변수는 FP 기준 offset으로 접근 (음수 = 인자, 양수 = 지역변수)

**[callee] Epilogue** (prologue의 역순)
8. **callee-saved register 복원**
9. 반환값을 정해진 곳에 저장 (all-memory scheme이면 AR의 return 자리, x86이면 rax)
10. SP를 되돌려 지역변수 공간 해제
11. **Prev FP를 꺼내 FP 복원** → FP가 caller frame으로 돌아감
12. `ret`: **return address를 pop해서 그 주소로 jump**

**[caller] 호출 후**
13. caller-saved register 복원
14. 반환값 사용, 인자 공간 해제

핵심 원칙
- **자기가 push한 건 자기가 pop한다.** 예외는 return address: caller의 `call`이 push, callee의 `ret`이 pop.
- **Prev FP가 frame들을 체인(control link)으로 연결해서** 리턴할 때 caller frame으로 정확히 돌아간다.

## Self-study

1. Example Call(p.27~28)에서 foo가 r1만 쓰고 r2는 전혀 안 쓰는 함수라면, prologue/epilogue 코드는 어떻게 바뀔 수 있을까? 그리고 그때 `sp = sp + 24`의 24는 몇이 될까?
2. 아래 struct의 각 field offset과 전체 크기를 구해봐.
   ```c
   struct {
       char a;
       short b;
       char c;
       int d;
       char e;
   }
   ```
3. 함수 호출 하나에서 AR이 만들어지고 사라지기까지의 과정을 caller/callee 역할을 나눠서 네 말로 설명해봐. (Prev FP, return address, callee-saved register가 각각 언제 저장·복원되는지 포함해서)
