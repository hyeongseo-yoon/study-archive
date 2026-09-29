# Chapter 3: Syntax Analysis

*2026 Fall, Hunjun Lee, Hanyang University*

## 1. Syntax Analysis 개요 *(슬라이드 p.2~6)*

### 컴파일러 구조 속 위치 *(p.2~3)*
Syntax Analysis(**Parser**)는 Lexical Analysis(Scanner) 다음 단계 — Front end의 두 번째 단계.

### 언어에서의 Syntax Analysis *(p.4)*
`I gave him the book` → Scanner가 `I`(pronoun), `gave`(verb), `him`(pronoun), `the`(article), `book`(noun)으로 나눔 → Parser가 각 단어의 **문법적 기능을 식별하고 문법을 검사**하여 `sentence → subject + verb + indirect object + object(article+noun)` 구조의 tree로 조직

### 프로그램에서의 Syntax Analysis *(p.5)*
`if (score > 90) then grade = "A" else grade = "D"` → Scanner가 token화(keyword/symbol/identifier/constant/string) → Parser가 `program → if(exp)then statement else statement` 구조로, 각 statement 내부도 `var relop const`, `var = const` 등으로 트리화

### Recap: Scanner의 3단계 vs Parser의 3단계 *(p.6~7)*
Scanner와 동일하게 Parser도 세 층위 문제로 나뉜다:
| | Scanner | Parser |
|---|---|---|
| **Specification**(무엇을 명시) | Regular Expression | **Context-free Grammar (CFG)** |
| **Recognition**(어떻게 인식) | DFA | **Parse tree, Abstract Syntax Tree(AST)** |
| **Automation**(자동 생성) | Lex, Thompson/Subset construction | **Top-down/Bottom-up parsing**, 자동 생성 도구(bison) |

---

## 2. Specification: Context-Free Grammar (CFG) *(슬라이드 p.9~20)*

### CFG의 4가지 구성요소 *(p.9~10)*
- **Terminal symbols**: token 또는 `ε` (예: keyword, symbol, ID, NUM)
- **Non-terminal symbols**: syntactic variable (예: var/function, expression, return-statement/for-loop/if-statement)
- **Start symbol S**: 특별한 non-terminal (컴파일러에서는 보통 `program`)
- **Productions**: LHS를 RHS로 번역하는 규칙(derivation) — LHS는 단일 non-terminal, RHS는 terminal/non-terminal의 문자열
  ```
  type-specifier → int | float | bool ...
  var-declaration → type-specifier ID ; | type-specifier ID [ NUM ] ;
  function-declaration → type-specifier ID ( params ) compound-stmt
  ```

### C 스타일 언어의 전체 문법 예시 (프로젝트에서 다룰 내용) *(p.11~12)*
```
1.  program → declaration-list
2.  declaration-list → declaration-list declaration | declaration
3.  declaration → var-declaration | fun-declaration
4.  var-declaration → type-specifier ID ; | type-specifier ID [ NUM ] ;
5.  type-specifier → int | void
6.  fun-declaration → type-specifier ID ( params ) compound-stmt
7.  params → param-list | void
8.  param-list → param-list , param | param
9.  param → type-specifier ID | type-specifier ID [ ]
10. compound-stmt → { local-declarations statement-list }
11. local-declarations → local-declarations var-declarations | empty
12. statement-list → statement-list statement | empty
13. statement → expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt
14. expression-stmt → expression ; | ;
15. selection-stmt → if ( expression ) statement | if ( expression ) statement else statement
16. iteration-stmt → while ( expression ) statement
17. return-stmt → return ; | return expression ;
18. expression → var = expression | simple-expression
19. var → ID | ID [ expression ]
20. simple-expression → additive-expression relop additive-expression | additive-expression
21. relop → <= | < | > | >= | == | !=
22. additive-expression → additive-expression addop term | term
23. addop → + | -
24. term → term mulop factor | factor
25. mulop → * | /
26. factor → ( expression ) | var | call | NUM
27. call → ID ( args )
28. args → arg-list | empty
29. arg-list → arg-list , expression | expression
```

### CFG가 생성하는 Language *(p.13)*
- Non-terminal에 production을 반복 적용하여 만들어지는 terminal 문자열들의 집합이 **language**. `L(G)`는 문법 `G`가 생성하는 language를 뜻함
- 예: `S → if C then S | if C then S else S | return; | ID(ID); | E`, `C → ID==ID | ID>ID | ID<ID`, `E → ID+ID; | ID*ID; | ID/ID;`로부터 `if ID==ID then return;`, `return;`, `ID(ID);` 등의 문자열이 생성됨

### Parser의 역할 *(p.14)*
```
Token stream (from lexer) + CFG → [Parser] → Valid/Invalid + Error msg
```
- **Derivation**: 문자열 내 non-terminal에 production을 적용하는 것
- **Acceptance**: 입력 토큰 스트림이 어떤 derivation으로 만들어질 수 있으면 accept

### CFG Example — 균형 중괄호 *(p.15)*
`{{}}`, `{}{}{}` 등을 정의:
```
Terminals: {, } / Non-Terminals: S
S → ε | { S } S
```
입력 `{{}}`의 유도: `S → {S}S → {{S}S}S → {{ε}S}S → {{}S}S → {{}}S → {{}} `(S→ε로 마무리)

### Side Note: 왜 RE가 아니라 CFG인가 *(p.16)*
RE는 nested construct(예: `{i}i` — 여는 괄호 i개, 닫는 괄호 i개)를 표현할 만큼 표현력이 충분하지 않다 — **RE는 unbounded counting을 지원하지 못하기** 때문. FSA로 표현하면 무한히 많은 state가 필요해짐.

### CFG Example — 합 표현식 *(p.17)*
`5+4`, `(5+2)+6`, `3+9+1` 등을 정의:
```
Terminals: number, (, ), + / Non-Terminals: S, E
S → E + S | E
E → number | (S)
```

### Class Exercise *(p.18)*
```
Terminals: a, b, c / Non-Terminals: S, X, Y
S → aXa,  X → ε | bY,  Y → ε | cXc
```
- `abcba`: X ✗, `S→aXa→abYa→abcXca ???`
- `acca`: X ✗, `S→aXa→abYa ???`
- `aba`: O — `S→aXa→abYa→aba`
- `abcbcba`: X ✗

### CFG Example — if 문 *(p.19~20)*
```
Target: if ( ID == ID ) ID = ID ;
program → statement-list
statement-list → statement-list statement | empty
statement → if-else-statement | assign-statement | cmp-statement
if-else-statement → if ( cmp-statement ) statement
assign-statement → ID = ID ;
cmp-statement → ID == ID
```
Derivation 과정에서 모든 심볼이 terminal이 될 때까지 production을 반복 적용 — 최종적으로 원하는 프로그램 문자열이 나오면 유효.

---

## 3. Recognition: Parse Tree & Abstract Syntax Tree *(슬라이드 p.21~34)*

### Parse Tree *(p.22)*
Input `id · id + id`, `S → S+S | S·S | id`에 대한 derivation을 트리로 표현한 것.
- **terminal이 leaf**, **non-terminal이 internal node**에 위치
- leaf를 **in-order로 순회**하면 원래 입력이 나옴
- 연산의 **순서/결합(association)**을 트리 구조로 보여줌 — 예: `·`가 `+`보다 더 깊은(더 안쪽) 서브트리에 있으면 `·`가 더 tightly bind (`· > +`)

### Derivation Order와 Parse Tree *(p.23)*
non-terminal에 production을 적용하는 순서는 자유롭게 선택 가능:
- **Left-most derivation**: 가장 왼쪽 non-terminal부터 선택
- **Right-most derivation**: 가장 오른쪽 non-terminal부터 선택
- 둘 다 **같은 parse tree**를 만들 수 있음(트리 자체는 순서와 무관하게 하나로 정해질 수도 있음)

### Ambiguous Grammars *(p.24)*
문법 `G`가 **ambiguous**하다는 것은 어떤 입력에 대해 순서(left-most vs right-most derivation)에 따라 **서로 다른 parse tree**가 나온다는 뜻 — 이 경우 "어느 쪽이 맞는 해석인가?"라는 문제가 생김.

### Derivation Example — `(1+2+(3+4))+5` *(p.25)*
`S → E+S | E`, `E → number | (S)` 문법으로 rightmost derivation을 그림으로 추적: 괄호 안쪽부터 재귀적으로 `E→(S)`를 전개하며 최종적으로 모든 숫자를 leaf로 갖는 트리 완성.

### Class Exercise *(p.26)*
`S → E+S | E`, `E → number | (S) | -S`로 `1 + (2 + -(3+4)) + 5`의 rightmost derivation을 트리로 구성 — `-S`(단항 마이너스) production이 추가되어 `-(3+4)` 부분을 처리.

### Ambiguity in Grammar and Language *(p.27)*
- 하나의 language에 대해 여러 문법이 존재할 수 있음
- 어떤 language가 **unambiguous**하다는 것은 그 language를 나타내는 모든 문법이 unambiguous하다는 뜻이고, 그중 하나라도 ambiguous하면 그 language 자체는 **ambiguous**하다고 부름 (문법의 성질을 language 레벨로 확장)
- 실제 parser를 만들려면 **unambiguous grammar**를 선택해서 ambiguity를 제거해야 함

### Ambiguity의 대표 사례 — Operator *(p.28)*
- **Precedence(우선순위)**: 곱셈/나눗셈이 덧셈/뺄셈보다 먼저 적용되어야 함
- **Associativity(결합성)**: 연산자는 left/right/non-associative 중 하나
  - Left: `a - b - c = (a - b) - c`
  - Right: `a ^ b ^ c = a ^ (b ^ c)`
  - Non: `a < b < c`는 invalid

### Removing Ambiguity ① — Precedence *(p.29)*
- 트리에서 **root에 가까운(높은 레벨의) production일수록 낮은 우선순위**를 갖게, **root에서 먼(낮은 레벨) production일수록 높은 우선순위**를 갖게 만든다
- 우선순위를 강제하기 위해 **non-terminal을 추가로 삽입**:
  ```
  Ambiguous:   S → S+S | S·S | id
  Unambiguous: S → S+T | T
               T → T·id | id
  ```
  (`·`가 `+`보다 우선순위가 높음을 문법 계층 구조로 표현)

### Removing Ambiguity ② — Associativity *(p.30)*
재귀를 어느 쪽에 두느냐로 결합성을 결정:
- **Left associative**: 재귀를 **왼쪽**에 둠 → `S → S - T | T`, `T → id`
- **Right associative**: 재귀를 **오른쪽**에 둠 → `S → T^S | T`, `T → id`
- **Non associative**: 재귀를 아예 사용하지 않음 → `S → A < A | A`, `A → id`

### Class Exercise *(p.31)*
`-`, `·`, `^` 연산자에 대해 precedence와 associativity를 모두 고려한 unambiguous grammar 작성 (ambiguous 버전: `S → S–S | S·S | S^S | id`)

### Ambiguity의 또 다른 사례 — Dangling Else *(p.32~33)*
- `if E1 then if E2 then E3 else E4`처럼 if/then/else와 if/then이 섞이면 else가 어느 then에 붙는지 모호함
- 규칙: **else는 가장 가까운(안쪽) then과 매칭**되어야 함 — 잘못된 트리(else가 바깥쪽 then에 붙음) vs 올바른 트리(else가 안쪽 then에 붙음)
- 해결법: **"모든 then이 매칭된 상태(MIF)"와 "일부 then이 안 매칭된 상태(UIF)"를 구분**하는 non-terminal 도입
  ```
  S → MIF | UIF
  MIF → if Cond then MIF else MIF | Others
  UIF → if Cond then S | if Cond then MIF else UIF
  ```
  (`if Cond then UIF else S` 형태가 되지 않도록 구조적으로 방지)

### Abstract Syntax Tree (AST) *(p.34)*
- AST는 syntax analysis에 불필요한 정보를 버려서(non-terminal 제거) parse tree를 단순화한 것
- 예: parse tree `S(E(E(id)·E(id)) + E(id))` → AST `+ 아래에 (· 아래에 id,id) 와 id` — 연산자만 internal node로 남고 문법적 구조(S, E 등)는 제거됨

---

## 4. Error Handling *(슬라이드 p.35~36)*

### 컴파일러에서 에러 처리의 목적 *(p.35)*
- 유효하지 않은 프로그램을 **탐지**하고, 가능하면 유효한 형태로 **변환**하는 것도 목적
- Error handler가 갖춰야 할 성질: 에러를 **정확하고 명확하게 보고**, **빠르게 복구**, **유효한 코드의 컴파일 속도를 저하시키지 않음**

### 왜 에러 처리가 중요했는가 (역사적 맥락) *(p.36)*
- 예전엔 컴파일러가 극도로 느려서, 사소한 오타 하나 고치는 데 하루가 걸리기도 했음 → 복잡한 에러 처리 절차가 필요했음(한 번의 컴파일에서 최대한 많은 실수를 찾아내고, 단순한 에러는 자동으로 고쳐주는 등)
- 오늘날은 **빠른 재컴파일**이 가능하고 사용자가 보통 한 번에 몇 개의 에러만 고치는 경향이 있어, 복잡한 에러 복구 절차가 예전만큼 필요하지 않음

---

## 5. Automation: Top-Down Parsing *(슬라이드 p.38~53)*

### Top-Down Parsing 개념 *(p.39)*
토큰 스트림을 읽으면서 문자열의 **left-most derivation**을 구성해나가는 방식. 예: `S → E+S | E`, `E → num | (S)`로 `(1+2+(3+4))+5`를 파싱할 때, 매 단계 parsed part(이미 검증된 부분)와 unparsed part(아직 안 읽은 부분)를 갱신하며 진행.

### Recursive Descent Parsing *(p.40)*
- **규칙들을 순서대로 시도**해보고, 해당 production이 올바른 token을 만들어내지 못하면 **backtrack**
- 예: `E → T|T+E`, `T → int|int·T|(E)`, 입력 `(int)`에 대해:
  1. `E→T→int` 시도 → `int`가 `(`와 매치 안 됨 → backtrack
  2. `E→T→int·T` 시도 → 역시 `int`가 `(`와 매치 안 됨 → backtrack
  3. `E→T→(E)` 시도 → `(` 매치 성공
  4. 내부적으로 `E→T→int` 재귀 적용해 최종 파스 완성

### Formal Notation *(p.41)*
- `next`: 입력 토큰을 가리키는 포인터
- terminal을 만들 때: `bool term(token) {return *next++ == token;}`
- non-terminal `S`에 대한 production 집합과 그 n번째 원소: `bool S() {...}`, `bool S_n() {...}`

### Top-Down Parsing 구현 예시 — Backtracking *(p.42)*
```
CFG: E → T|T+E,  T → int|int·T|(E)

bool E1() {return T();}
bool E2() {return T() && term("+") && E();}
bool E() {
    Token *save = next;
    return (next = save, E1()) || (next = save, E2());
}
bool T1() {return term("int");}
bool T2() {return term("int") && term("·") && T();}
bool T3() {return term("(") && E() && term(")");}
bool T() {
    Token *save = next;
    return (next = save, T1()) || (next = save, T2())
                              || (next = save, T3());
}
```
각 production을 시도하기 전에 `next` 포인터를 저장(`save`)해두고, 실패하면 되돌려서 다음 production을 시도.

### Limitation of (일반) Top-Down Parsing *(p.43)*
**여러 production이 동시에 매치될 수 있는 경우** top-down parsing이 실패할 수 있음: `E → T|T+E`, `T → int|int·T|(E)`, 입력 `int · int`에 대해 첫 production `T→int`만 시도하고 멈추면 `int`까지만 파싱된 **부정확한** 결과가 나옴 — `T→int·T`까지 봐야 **정확한** 파스 완성. 순서를 잘못 고르면 문제가 생김.

### Making a Grammar LL(1) *(p.44~46)*
- **LL(1)**: **L**eft-to-right scanning, **L**eftmost derivation, **1**개의 lookahead 심볼 — 토큰 하나만 미리 봐도 어떤 production을 적용할지 결정 가능한 문법. 이러면 backtracking 없이 파싱 가능
- **Left factoring**: 공통 접두사(prefix)를 분리하고 새 non-terminal `S'`를 추가
  ```
  S → E + S | E   ⟹   S → ES'   and   S' → +S | ε
  ```
- **Left recursion 제거**: `S → Sa` 같은 left recursion(`S →* Sa`)은 무한 유도로 이어짐 → right recursion으로 변환
  - 대표 예시: "b로 시작하고 이후 임의 개수의 a가 붙는 문자열" `S → Sa | b` ⟹ `S → bS'`, `S' → aS' | ε`
  - 일반형: `S → Sa1 | Sa2 | ... | San | b1 | b2 | ... | bn` ⟹ `S → b1S' | b2S' | ... | bnS'`, `S' → a1S' | a2S' | ... | anS' | ε`
- 모든 문법이 LL(1)이 될 수 있는 것은 아님 — **문법 계층 구조**: All ⊃ Unambiguous ⊃ LR(k>1) ⊃ LR(1) ⊃ LALR(1) ⊃ SLR(1) ⊃ LR(0), 이와 별개로 **LL(1)**은 SLR(1)~LALR(1) 근방에 걸치는 독립적인 부분집합

### Class Exercise — LL(1) 변환 *(p.47)*
```
1. A → AAa | b  ⟹  A → bA',  A' → AaA' | ε
2. E → E+E | ExE | a
   E → ET | a,  T → +E | xE   // left factoring
   E → aE',  E' → TE' | ε
```

### Predictive Parsing *(p.48)*
- **Predictive parsing**: backtracking 없이 **단일 production만 적용**하는 방식 — 어떤 production을 고르느냐가 파서의 기능(정확성)에 영향을 줄 수 있음
- **LL(1) 문법**은 "**최대 하나의 production만 적용 가능**"하다는 성질을 가지므로, functionality에 영향 없이 predictive parsing 적용 가능

### Predictive Parsing for LL(1) — Parsing Table *(p.49)*
- non-terminal × terminal(lookahead)의 **parsing table**을 사용
- 예: `S → ES'`, `S' → +S|ε`, `E → num|(S)`에 대한 테이블:

| | num | + | ( | ) | $ (EOF) |
|---|---|---|---|---|---|
| **S** | ES' | | ES' | | |
| **S'** | | +S | | ε | ε |
| **E** | num | | (S) | | |

### Parser Implementation — Recursive-Descent Parser *(p.50~53)*
테이블을 이용해 `parse_S()`, `parse_S'()`, `parse_E()` 세 함수를 구현:
```c
void parse_S() {
    switch (token) {
    case num: parse_E(); parse_S'(); return;
    case '(': parse_E(); parse_S'(); return;
    default: ParseError(); }}

void parse_S'() {
    switch (token) {
    case '+': token = input.next(); parse_S(); return;
    case ')': return;
    case EOF: return;
    default: ParseError(); }}

void parse_E() {
    switch (token) {
    case number: token = input.next(); return;
    case '(': token = input.next(); parse_S();
              if (token != ')') ParseError();
              token = input.next(); return;
    default: ParseError(); }}
```
각 함수는 테이블의 해당 행(non-terminal)을 그대로 switch문으로 옮긴 형태 — backtracking 없이 lookahead token 하나로 분기.

---

## 6. Automation: Parsing Table 자동 생성 — Nullable, First, Follow *(슬라이드 p.54~77)*

### 필요한 세 가지 속성 *(p.54)*
- **Nullable(x)**: `x`가 empty string을 유도할 수 있으면(`x →* ε`) true
- **First(x)**: `x`로부터 유도될 수 있는 문자열의 **첫 번째 위치에 올 수 있는 terminal들의 집합** — `First(x) = {t | x →* ty}`
- **Follow(x)**: 적어도 하나의 유도에서 `x` **바로 뒤에 나타날 수 있는 terminal들의 집합** — `Follow(x) = {t | S →* yxtz}` (`S`는 start symbol)

### Nullable 계산 *(p.55)*
- Case 1) `ε`은 nullable
- Case 2) production `X → A1A2...An`에서 `A1...An`이 모두 nullable이면 `X`도 nullable (각 Ai가 차례로 nullable임을 이용해 `X →* ε`까지 유도 가능함을 보임)

### First 계산 *(p.56)*
- Step 1) terminal `t`에 대해 `First(t) = {t}`
- Step 2) production `x → A1A2...An`에서 `A1...Ai-1`이 모두 nullable이면 `First(x) += First(Ai)` (그 앞의 nullable한 심볼들을 건너뛰고 `Ai`가 첫 non-nullable 위치에 오는 경우까지 반영)
- 변화가 없을 때까지 반복

### Follow 계산 *(p.57)*
- Step 1) `Follow(S) = {$}` (start symbol S)
- Step 2) production `x → A1A2...An`에서 `Ai+1...An`이 모두 nullable이면 `Follow(Ai) += Follow(x)` (x 뒤에 오는 것이 결국 Ai 뒤에도 올 수 있으므로)
- Step 3) production `x → A1A2...An`에서 `Ai+1...Aj-1`이 모두 nullable이면 `Follow(Ai) += First(Aj)` (그 사이 nullable한 것들을 건너뛰고 Aj가 Ai 바로 뒤에 올 수 있는 경우)

### 알고리즘 통합 (Combine Together) *(p.58)*
```
// Initialize
for each symbol X: First(X)={}, Follow(X)={}, Nullable(X)=false
Follow(S) = {$}
for each terminal t: First(t) = {t}
Nullable(ε) = true
// Iterate
Repeat
    for each production X → A1A2...An
        if all Ai are Nullable:          Nullable(X) = True
        if A1...Ai-1 are Nullable:       First(X) += First(Ai)
        if Ai+1...An are Nullable:       Follow(Ai) += Follow(X)
        if Ai+1...Aj-1 are Nullable:     Follow(Ai) += First(Aj)
Until there is no change in First, Follow, and Nullable
```

### 예시 — Nullable/First/Follow 계산 과정 *(p.59~67)*
`S → ES'`, `S' → +S|ε`, `E → num|(S)`에 대해 초기화 후 반복적으로 갱신:
- 초기: 모든 First/Follow = `{}`, Nullable = False, `Follow(S)={$}`, terminal의 First만 자기 자신
- 반복하며 `S → ES'` 규칙에서 `First(S) += First(E)`, `Follow(S') += Follow(S)`, `Follow(E) += First(S')` 등을 계속 적용
- 최종 수렴 결과:

| | First | Follow | Nullable |
|---|---|---|---|
| **S** | {num, (} | {$, )} | False |
| **S'** | {+} | {$, )} | True |
| **E** | {num, (} | {$, ), +} | False |

### Parsing Table 생성 규칙 (Putting It Together) *(p.68)*
- production `X → A1A2...An`에서, `t ∈ First(A1A2...An)`인 모든 terminal `t`에 대해 `table[X, t] = A1A2...An`
- `First(A1A2...An)` 계산법: `Nullable(A1)==False`면 `First(A1)`, `Nullable(A1)==True`면 `First(A1) + First(A2...An)`
- 모든 `Ai`가 nullable이면, `Follow(X)`의 모든 `t`에 대해서도 `table[X, t] = A1A2...An` (partly-derived string이 `XtY`일 때 `X→A1...An` 적용 후 모든 Ai가 nullable이면 결국 `tY`가 되어 t가 leftmost terminal이 되기 때문)

### 최종 예시 — 완성된 Parsing Table *(p.69)*

| | num | + | ( | ) | $ |
|---|---|---|---|---|---|
| **S** | ES' | | ES' | | |
| **S'** | | +S | | ε | ε |
| **E** | num | | (S) | | |

### Class Exercise — 종합 예제 *(p.70~77)*
```
CFG:
E → TX
T → (E) | int Y
X → + E | ε
Y → * T | ε
```
Nullable/First/Follow를 위 알고리즘대로 반복 계산한 최종 결과:

| | First | Follow | Nullable |
|---|---|---|---|
| **E** | {(, int} | {$, )} | False |
| **T** | {(, int} | {+, $, )} | False |
| **X** | {+} | {$, )} | True |
| **Y** | {*} | {+, $, )} | True |

이로부터 생성된 최종 parsing table:

| | ( | ) | int | + | * | $ |
|---|---|---|---|---|---|---|
| **E** | TX | | TX | | | |
| **T** | (E) | | int Y | | | |
| **X** | | ε | | +E | | ε |
| **Y** | | ε | | ε | *T | ε |

---

## 핵심 요약

- Syntax Analysis(Parser)도 Scanner와 마찬가지로 **Specification(CFG) → Recognition(Parse tree/AST) → Automation(Top-down/Bottom-up parsing)**의 3층 구조로 접근
- **CFG**는 terminal, non-terminal, start symbol, production 4요소로 구성되며, RE와 달리 **unbounded nesting**(중첩 구조)을 표현할 수 있음
- 문법이 입력에 따라 여러 개의 parse tree를 만들 수 있으면 **ambiguous** — precedence(non-terminal 계층으로 해결), associativity(재귀 위치로 해결), dangling-else(MIF/UIF 구분으로 해결) 문제를 non-terminal 설계로 없애야 함
- **Parse tree**는 derivation의 트리 표현이고, **AST**는 여기서 non-terminal을 제거해 핵심 구조(연산자와 피연산자)만 남긴 것
- **Top-down parsing**은 leftmost derivation을 구성하며 진행 — **recursive descent**(backtracking 필요)와, 문법을 **LL(1)**(left factoring + left recursion 제거)로 만들면 backtracking 없는 **predictive parsing**이 가능해짐
- LL(1) parsing table은 **Nullable, First, Follow** 세 속성을 고정점(fixed-point) 반복으로 계산한 뒤, 이를 이용해 각 (non-terminal, lookahead terminal) 쌍에 적용할 production을 결정해서 만든다
