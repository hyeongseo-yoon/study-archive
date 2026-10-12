# Chapter 3: Syntax Analysis — 수업노트

*수업일: 2026-10-11 / 대응 정리노트: `notes/chapter-3.md`*

---

## 0. 선수 개념 복습

**Scanner의 3단계 (복습)**
- Scanner는 **RE로 명세**하고, RE로부터 **DFA를 만들어서** 토큰을 인식한다.
- RE와 DFA/NFA는 **표현하는 언어의 범위가 같다**. DFA는 결정적이라 상태 이동마다 O(1)이 걸려 더 빠르기 때문에 최종적으로 DFA를 만든다.

**Terminal / Non-terminal**
```
sentence → subject verb object
subject  → I | you
verb     → read | wrote
object   → book | letter
```
- **Terminal**: 더 이상 쪼개거나 바꿀 수 없는, 최종 문장에 실제로 찍히는 것(`I`, `read`, `book`). 컴파일러에서는 **Scanner가 만든 토큰**이 terminal이다.
- **Non-terminal**: 다른 것으로 바꿔 쓸 수 있는 "범주 이름"(`sentence`, `subject`, `verb`). 화살표 왼쪽에 나오고 결국 terminal로 전개되어야 한다.
- Scanner가 "단어의 종류(토큰)"를 정했다면, Parser는 "그 단어들이 문장 구조에 맞게 배열됐는지" 본다. 그 구조를 적는 도구가 CFG.

**In-order 순회**
이진 트리에서 **왼쪽 자식 → 자기 자신 → 오른쪽 자식** 순서로 방문.
```
    +
   / \
  3   *
     / \
    4   5
```
방문 순서: `3 → + → 4 → * → 5` (수식을 원래 읽는 순서). 3강에서는 "leaf를 왼쪽에서 오른쪽으로 읽으면 원래 입력이 나온다"는 감각만 있으면 된다.

**확인 문제: `S → a S b | ε`**
- terminal은 `a, b`(ε 포함), non-terminal은 `S`.
- 만들어지는 문자열: `ε`, `ab`, `aabb`, ... 규칙을 쓸 때마다 양 끝에 a와 b가 하나씩 붙으므로 `aⁿbⁿ` 꼴만 나온다. (`abab`은 **안 됨**.) 유도: `S → aSb → aaSbb → aabb`.
- 이 성질은 뒤에서 "왜 RE로는 안 되고 CFG가 필요한가"의 근거가 된다.

---

## 1. Syntax Analysis 개요 *(슬라이드 p.2~6)*

### 위치 *(p.2~3)*
Front end의 두 번째 단계. Lexical Analysis(Scanner) 다음에 오는 **Parser**.

### 언어에서의 비유 *(p.4)*
`I gave him the book`
- Scanner: 단어로 쪼개고 품사를 붙인다. `I`(pronoun), `gave`(verb), `him`(pronoun), `the`(article), `book`(noun).
- Parser: 각 단어의 **문법적 기능을 식별하고 문법을 검사**해서 문장 구조 tree로 조직한다. `subject + verb + indirect object + object(article + noun)`.

### 프로그램에서 *(p.5)*
`if (score > 90) then grade = "A" else grade = "D"`
- Scanner: keyword / symbol / identifier / constant / string 토큰으로 나눈다.
- Parser: `program → if (exp) then statement else statement` 구조로 묶고, 각 statement 안쪽도 `var relop const`, `var = const` 같은 구조로 쪼개 tree로 만든다.

Scanner는 "단어가 올바른 모양인가"를, Parser는 "단어들이 올바른 구조로 배열됐는가"를 본다.

### Scanner vs Parser의 3단계 *(p.6~7)*
| | Scanner | Parser |
|---|---|---|
| **Specification** | Regular Expression | **Context-Free Grammar (CFG)** |
| **Recognition** | DFA | **Parse tree, AST** |
| **Automation** | Lex, Thompson/Subset construction | **Top-down / Bottom-up parsing**, bison 같은 도구 |

3강 흐름: CFG(섹션 2) → Parse tree/AST(섹션 3) → Top-down parsing(섹션 5~6). Bottom-up은 다음 강의(Syntax Analysis - 2).

### Parser의 입출력 *(p.14)*
- Scanner의 출력이 Parser의 입력이다.
- **입력**: Scanner가 만든 **토큰 스트림** + 문법(CFG)
- **출력**: 문법에 맞는지 **Valid / Invalid**, 틀렸다면 **에러 메시지**. 맞으면 그 구조를 나타내는 parse tree(AST).
```
Token stream + CFG → [Parser] → Valid/Invalid + Error msg
```

> **주의 (헷갈린 지점)**: Parser의 결과물은 "의미를 지닌 문장"이 아니다. **의미**(타입이 맞는지, 변수가 선언됐는지)를 검사하는 건 뒤 단계인 **Semantic Analysis**(5강). Parser는 토큰들이 **문법 구조에 맞게 배열됐는지**만 본다. `if (score > 90)`에서 `score`가 선언된 변수인지는 신경 쓰지 않는다.

---

## 2. Specification: Context-Free Grammar (CFG) *(슬라이드 p.9~20)*

CFG는 선언적 개념이라 정의와 구성요소가 핵심.

### CFG의 4가지 구성요소 *(p.9~10)*
| 요소 | 뜻 | 예 |
|---|---|---|
| **Terminal** | 토큰 또는 `ε` | keyword, symbol, `ID`, `NUM` |
| **Non-terminal** | 구조를 나타내는 변수(syntactic variable) | expression, if-statement, function |
| **Start symbol** `S` | 유도를 시작하는 특별한 non-terminal | 컴파일러에서는 보통 `program` |
| **Production** | LHS를 RHS로 바꿔 쓰는 규칙 | `type-specifier → int \| float \| bool` |

- LHS(왼쪽)는 **non-terminal 하나**, RHS(오른쪽)는 terminal과 non-terminal을 섞은 **문자열**. `|`는 "또는".
```
type-specifier → int | float | bool
var-declaration → type-specifier ID ; | type-specifier ID [ NUM ] ;
function-declaration → type-specifier ID ( params ) compound-stmt
```

**Terminal / non-terminal 구분 기준 (헷갈린 지점)**
- `ID`, `NUM`은 **terminal**이다. Scanner가 이미 만들어주는 **토큰의 종류 이름**이고, Parser 입장에서는 더 전개할 게 없는 최종 기호다. `x`가 `ID`인지 아는 건 Scanner(RE/DFA)의 일.
- `ID`는 모든 식별자(`x`, `score`, `main`...)를 대표하는 토큰 종류 이름, `NUM`은 숫자 토큰 종류. Scanner는 "종류는 ID, 내용(lexeme)은 `x`"라고 넘기고, Parser는 **종류만** 본다. 그래서 문법에는 `ID` 하나만 쓰면 된다.
- "토큰이 들어가면 terminal이 된다"가 아니다. 기호는 문법을 쓰는 시점에 이미 terminal인지 non-terminal인지 정해져 있다. 기준은 **그 기호가 production의 LHS에 나오느냐**: LHS에 나오면 non-terminal, 한 번도 안 나오면 terminal.

**예: `int x;`의 유도** (`x`는 `ID` 토큰으로, 토큰 스트림은 `int ID ;`)
```
var-declaration → type-specifier ID ;
                → int ID ;          (type-specifier → int)
```
`var-declaration → type-specifier ID ;`에서 `type-specifier`는 non-terminal, `ID`와 `;`는 terminal.

### C 스타일 언어의 전체 문법 예시 *(p.11~12)*
```
1.  program → declaration-list
2.  declaration-list → declaration-list declaration | declaration
3.  declaration → var-declaration | fun-declaration
4.  var-declaration → type-specifier ID ; | type-specifier ID [ NUM ] ;
5.  type-specifier → int | void
6.  fun-declaration → type-specifier ID ( params ) compound-stmt
...
13. statement → expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt
15. selection-stmt → if ( expression ) statement | if ( expression ) statement else statement
16. iteration-stmt → while ( expression ) statement
...
22. additive-expression → additive-expression addop term | term
24. term → term mulop factor | factor
26. factor → ( expression ) | var | call | NUM
```
(전체 29개 규칙은 `notes/chapter-3.md` 참고.) 눈여겨볼 점:
- 위에서 아래로 **큰 구조 → 작은 구조**로 쪼개져 내려간다.
- `declaration-list → declaration-list declaration | declaration`처럼 자기 자신이 RHS에 들어가는 **재귀**로 "0개 이상 반복"을 표현한다. RE의 `*` 역할.
- 수식이 `additive-expression → term`, `term → factor`로 **계층**이 있다. 이게 나중에 우선순위(precedence)를 만드는 장치.

### CFG가 만드는 Language *(p.13)*
Start symbol에서 시작해 production을 반복 적용하면 terminal 문자열이 만들어진다. **만들어질 수 있는 모든 terminal 문자열의 집합**이 그 문법의 language이고, 문법 `G`의 language를 `L(G)`로 쓴다.
```
S → if C then S | if C then S else S | return; | ID(ID); | E
C → ID==ID | ID>ID | ID<ID
E → ID+ID; | ID*ID; | ID/ID;
```
- `return;`, `ID(ID);`, `if ID==ID then return;`는 `L(G)`에 속한다.
- `if ID then return;`은 `C`가 될 수 없으니 속하지 않는다.
- `if ID>ID then ID(ID);`는 `S → if C then S`, `C → ID>ID`, `S → ID(ID);`로 유도되므로 accept.

### Parser의 역할 용어 *(p.14)*
- **Derivation**: 문자열 속 non-terminal에 production을 적용하는 것
- **Acceptance**: 입력 토큰 스트림이 어떤 derivation으로 만들어질 수 있으면 accept

### CFG Example ① — 균형 중괄호 *(p.15)*
`{{}}`, `{}{}{}`, `{{}{}}` 등 짝이 맞는 문자열.
```
Terminals: {, }    Non-terminals: S
S → ε | { S } S
```
`{{}}`의 유도:
```
S → { S } S
  → { { S } S } S      (안쪽 S에 { S } S 적용)
  → { { } S } S        (가장 안쪽 S → ε)
  → { { } } S          (남은 S → ε)
  → { { } }            (마지막 S → ε)
```
`aⁿbⁿ` 문법과 같은 원리. 중첩 깊이가 몇이든 재귀로 처리한다.

### Side Note: 왜 RE가 아니라 CFG인가 *(p.16)*
- `{ⁱ}ⁱ`(여는 괄호 i개 뒤에 닫는 괄호 i개)는 RE로 못 쓴다. RE도 `a*`처럼 **무한한 집합**은 표현하지만, **개수를 세면서 짝을 맞추는 것(중첩)** 은 못 한다.
- DFA로 만든다고 해도 `i`가 커질 때마다 "몇 개 열었는지" 기억할 상태가 필요해서 **상태가 무한히** 있어야 한다. DFA는 상태가 유한해야 하므로 불가능.
- CFG는 production의 **재귀**로 중첩을 표현한다. 프로그래밍 언어의 `( )`, `{ }`, `if ... else`는 전부 중첩 구조라서 Parser에는 CFG가 필요.

### CFG Example ② — 합 표현식 *(p.17)*
`5+4`, `(5+2)+6`, `3+9+1`.
```
Terminals: number, (, ), +    Non-terminals: S, E
S → E + S | E
E → number | ( S )
```
`E`는 숫자 하나나 괄호로 묶인 합, `S`는 `E`들을 `+`로 이은 것. `3+9+1`은 `S → E+S → E+E+S → E+E+E`.

### Class Exercise *(p.18)*
```
Terminals: a, b, c    Non-terminals: S, X, Y
S → aXa,  X → ε | bY,  Y → ε | cXc
```
| 문자열 | 가능? | 이유 |
|---|---|---|
| `aba` | O | `S → aXa → abYa → aba` |
| `acca` | X | `X`는 ε이거나 `b`로 시작해서 `c`로 시작할 수 없음 |
| `abcba` | X | `Y → cXc`라 `Y`가 만든 부분이 `c`로 끝나야 함 (`abcXca` 꼴) |
| `abcbcba` | X | 같은 이유 |

공통 원인: **Y가 ε이 아니면 항상 `c ... c`로 감싸진다**. `aXa`로 만들 수 있는 건 `aa`, `aba`, `abcca`, `abcbcca`... 꼴.

### CFG Example ③ — if 문 *(p.19~20)*
```
Target: if ( ID == ID ) ID = ID ;

program → statement-list
statement-list → statement-list statement | empty
statement → if-else-statement | assign-statement | cmp-statement
if-else-statement → if ( cmp-statement ) statement
assign-statement → ID = ID ;
cmp-statement → ID == ID
```
유도:
```
program → statement-list
        → statement-list statement      (statement-list → statement-list statement)
        → statement                      (statement-list → empty)
        → if-else-statement
        → if ( cmp-statement ) statement
        → if ( ID == ID ) statement
        → if ( ID == ID ) assign-statement
        → if ( ID == ID ) ID = ID ;
```
모든 심볼이 terminal이 될 때까지 production을 반복 적용해서 목표 문자열이 나오면 유효.

---

## 3. Recognition: Parse Tree & AST *(슬라이드 p.21~34)*

### Parse Tree *(p.22)*
유도 과정을 tree로 그린 것이 Parser의 인식 결과. 문법 `S → S+S | S·S | id`, 입력 `id · id + id`:
```
        S
      / | \
     S  +  S
   / | \    \
  S  ·  S    id
  |     |
  id    id
```
- **terminal은 leaf**, **non-terminal은 internal node**.
- leaf를 **왼쪽에서 오른쪽으로 읽으면** 원래 입력이 나온다.
- tree의 **모양이 연산의 순서/묶임(association)** 을 나타낸다. 위 tree에서는 `·`가 `+`보다 **더 깊은 곳**에 있어서 먼저 계산 → `(id · id) + id`.

### Derivation 순서 *(p.23)*
어떤 non-terminal을 먼저 전개할지는 자유롭게 고를 수 있다.
- **Left-most derivation**: 매번 가장 **왼쪽** non-terminal부터
- **Right-most derivation**: 매번 가장 **오른쪽** non-terminal부터

### Derivation Example — `(1+2+(3+4))+5` *(p.25)*
`S → E+S | E`, `E → number | (S)`로 rightmost derivation:
```
S → E+S → E+E → E+5 → (S)+5 → (E+S)+5 → (E+E+S)+5 → (E+E+E)+5
  → (E+E+(S))+5 → (E+E+(E+S))+5 → (E+E+(E+E))+5
  → (E+E+(E+4))+5 → (E+E+(3+4))+5 → (E+2+(3+4))+5 → (1+2+(3+4))+5
```
괄호 안쪽부터 재귀적으로 `E → ( S )`가 전개되고, 최종적으로 모든 숫자가 leaf가 된다.

### Class Exercise *(p.26)*
> ✏️ **직접 풀어보기** (수업 중 안 풀었음)

`E → number | ( S ) | -S`로 `1 + (2 + -(3+4)) + 5`를 같은 방식으로 유도. 새로 생긴 `E → -S`가 `-(3+4)`를 만든다. `-` 다음의 `S`가 `E → ( S )`를 거쳐 `(3+4)`가 되는 식.

### Ambiguous Grammar *(p.24, 27)*
- 어떤 입력에 대해 **서로 다른 parse tree가 둘 이상** 나오는 문법을 **ambiguous**하다고 한다. (유도 순서가 달라서 tree가 달라질 수도 있다.)
- 하나의 language에 대해 여러 문법이 존재할 수 있다. 한 문법이 ambiguous해도 모호하지 않은 다른 문법으로 바꿔 쓸 수 있는 경우가 많고, 우리가 할 일이 그 **문법을 고쳐 쓰는 것**.
- language 레벨: 그 language를 나타내는 **모든** 문법이 unambiguous하면 unambiguous한 language, 하나라도 ambiguous하면 ambiguous한 language라고 부른다. (슬라이드 정의에 따름)
- 실제 parser를 만들려면 **unambiguous grammar**를 골라야 한다. 모호하면 Parser가 어느 해석을 따를지 정할 수 없다.

**함정: 같은 입력, 다른 tree**
`S → S + S | S · S | id`, 입력 `id · id + id`:
```
tree A:  (id · id) + id          tree B:  id · (id + id)
        +                                  ·
       / \                                / \
      ·   id                            id   +
     / \                                    / \
   id   id                                id   id
```
`id`에 숫자를 넣어 `2 · 3 + 4`로 보면 A는 `(2·3)+4 = 10`, B는 `2·(3+4) = 14`. Parser가 어느 쪽을 고르느냐에 따라 **프로그램의 결과가 달라진다**. 모호함이 생기는 이유는 `S`가 RHS의 **양쪽에 모두** 나와서 `+`와 `·`가 같은 층에서 경쟁하기 때문.

### 모호함의 대표 원인: 연산자 *(p.28)*
- **Precedence(우선순위)**: `·`가 `+`보다 먼저 계산되어야 함.
- **Associativity(결합성)**: 같은 우선순위의 연산자가 연속될 때 어느 쪽부터 묶느냐.
  - Left: `a - b - c = (a - b) - c`
  - Right: `a ^ b ^ c = a ^ (b ^ c)`
  - Non: `a < b < c`는 invalid

### Removing Ambiguity ① — Precedence *(p.29)*
- tree에서 **leaf에 가까운(깊은) 곳의 연산이 먼저 계산**된다. 그러니 우선순위가 높은 연산자를 **더 깊은 층**에 가둔다.
- 층을 만들기 위해 **non-terminal을 추가**한다. root에 가까운 production일수록 낮은 우선순위.
```
Ambiguous:   S → S+S | S·S | id
Unambiguous: S → S + T | T        // S는 + 전담
             T → T · id | id      // T는 · 전담
```
`S`는 `T`를 거쳐야만 `·`에 갈 수 있고, `T`는 `+`를 만들 방법이 없다.

`id + id · id`의 유도:
```
S → S + T → T + T → id + T → id + T · id → id + id · id
```
```
        S
      / | \
     S  +  T
     |    /|\
     T   T · id
     |   |
     id  id
```
`·`가 `+`의 오른쪽 `T` 안쪽(더 깊은 곳)에 있어서 `id + (id · id)`로만 해석된다. `id · (id + id)`처럼 `+`를 먼저 묶으려면 `T`가 `+`를 품어야 하는데 `T`의 production에는 `+`가 없어서 **불가능** → tree가 하나로 정해진다. `id · id + id`도 `S → S + T`로 시작해 왼쪽 `S`가 `T → T · id`로 전개되므로 `(id · id) + id`로만 해석된다.

### Removing Ambiguity ② — Associativity *(p.30)*
같은 우선순위의 연산자가 연속될 때는 **재귀를 어느 쪽에 두느냐**로 결합성을 정한다.
```
Left  associative:  S → S - T | T      T → id     // 재귀가 왼쪽
Right associative:  S → T ^ S | T      T → id     // 재귀가 오른쪽
Non   associative:  S → A < A | A      A → id     // 재귀 없음
```
`id - id - id`를 left-recursive 문법으로 유도하면:
```
S → S - T → S - T - T → T - T - T → id - id - id
```
```
          S
        / | \
       S  -  T
     / | \    \
    S  -  T    id
    |     |
    T     id
    |
    id
```
먼저 만들어진 쪽(왼쪽)이 더 깊은 곳에 있어서 먼저 묶인다 → `(id - id) - id`, left associative. 재귀가 오른쪽이면 오른쪽이 깊어져 `id ^ (id ^ id)`. 재귀가 없는 `S → A < A`는 `a < b < c`를 만들 방법 자체가 없어서 invalid.

### Class Exercise *(p.31)*
> ✏️ **직접 풀어보기** (답을 보고 이해만 함)

`S → S – S | S · S | S ^ S | id`를 우선순위 `^ > · > –`, 결합성 `–`, `·`는 left / `^`는 right로 고치기.
```
S → S - T | T        // 가장 낮은 우선순위, left (재귀가 왼쪽)
T → T · F | F        // 중간 우선순위, left
F → G ^ F | G        // 가장 높은 우선순위, right (재귀가 오른쪽)
G → id
```
만든 순서:
1. **우선순위**: 낮은 연산자부터 위층(root에 가까운 쪽)에 둔다. `-`는 `S`, `·`는 `T`, `^`는 `F` 층. 층을 내려갈수록 먼저 묶인다.
2. **결합성**: 각 층에서 재귀의 방향을 정한다. `-`, `·`는 left → 재귀가 왼쪽, `^`는 right → 재귀가 오른쪽.
3. 마지막 층 `G → id`가 가장 안쪽.

검증: `id ^ id ^ id`는 `F → G ^ F → G ^ G ^ F → id ^ id ^ id`로 유도되어 `id ^ (id ^ id)`.

### Dangling Else *(p.32~33)*
```
if E1 then if E2 then E3 else E4
```
`else`가 어느 `then`에 붙는지 모호하다.
```
해석 A: if E1 then ( if E2 then E3 else E4 )   // else가 안쪽 then에 붙음
해석 B: if E1 then ( if E2 then E3 ) else E4   // else가 바깥쪽 then에 붙음
```
언어 규칙은 **else는 가장 가까운(안쪽) then과 매칭** → 해석 A가 맞다.

**해결: then이 모두 짝이 맞았는지로 구분**
```
S   → MIF | UIF
MIF → if Cond then MIF else MIF | Others
UIF → if Cond then S | if Cond then MIF else UIF
```
- **MIF**(Matched): 모든 `then`이 `else`와 짝이 맞은 문장
- **UIF**(Unmatched): `else` 없는 `then`이 남아 있는 문장

**핵심**: UIF를 쓰면 안 되는 게 아니라(UIF도 유효한 문장), **UIF가 어디에 올 수 있는지를 제한**한다. `else`를 가진 production은 둘 다 `then` 바로 뒤에 **MIF만** 허용한다. 그 자리에 UIF는 못 온다. `else` 없는 production(`UIF → if Cond then S`)은 `then` 뒤에 `S`(MIF든 UIF든)가 올 수 있다.
- **해석 B**: `else`를 가진 바깥 `if`의 `then` 자리에 `if E2 then E3`(else 없음 → UIF)가 와야 하는데, 그 자리는 MIF만 허용 → **불가능**.
- **해석 A**: 바깥 `if`는 `else`가 없으니 `UIF → if Cond then S`로 시작하고, 안쪽 `S`가 `MIF → if E2 then E3 else E4`가 되어 **가능**.

그래서 `else`는 항상 안쪽(가장 가까운) `then`에 붙는다. 짝이 안 맞은 `if`가 `then`과 `else` 사이에 끼어들지 못하게 막은 구조(`if Cond then UIF else S` 형태 불가).

### Abstract Syntax Tree (AST) *(p.34)*
Parse tree에는 문법 구조용 non-terminal(`S`, `E`, `T`...)이 잔뜩 들어 있다. 이후 단계(의미 분석, 코드 생성)에 필요한 건 **연산자와 피연산자의 관계**뿐이라, 불필요한 non-terminal을 걷어낸 것이 **AST**.
```
Parse tree                    AST
     S                          +
   / | \                       / \
  E  +  E                     ·   id
 /|\    |                    / \
E · E   id                  id  id
|   |
id  id
```
- 연산자만 internal node로 남고(연산자가 부모, 피연산자가 자식), 문법용 non-terminal은 사라진다. `id · id + id`의 계산 구조는 그대로.
- 이후 단계는 `S`, `E` 같은 문법 장치에 신경 쓸 필요가 없어서 쓰기 편하다.

---

## 4. Error Handling *(슬라이드 p.35~36)*

### 목적과 성질 *(p.35)*
유효하지 않은 프로그램을 **탐지**하는 것이 기본이고, 가능하면 유효한 형태로 **변환**하는 것도 목적. 에러 핸들러가 갖춰야 할 성질:
- 에러를 **정확하고 명확하게 보고**한다
- 에러에서 **빠르게 복구**한다
- **유효한 코드의 컴파일 속도를 떨어뜨리지 않는다**

### 역사적 맥락 *(p.36)*
- **예전**: 컴파일러가 극도로 느려서 오타 하나 고치는 데 하루가 걸리기도 했다. 그래서 한 번의 컴파일에서 **최대한 많은 에러를 찾고, 단순한 에러는 자동으로 고치는** 복잡한 에러 처리 절차가 필요했다.
- **지금**: 재컴파일이 빠르고 사용자가 한 번에 에러 몇 개만 고치는 경향이 있어서, 복잡한 에러 복구 절차는 예전만큼 필요하지 않다.
- 3강에서는 이 정도 개념만 다루고, 에러 복구 기법 자체는 나오지 않는다.

---

## 5. Automation: Top-Down Parsing *(슬라이드 p.38~53)*

### Top-Down Parsing 개념 *(p.39)*
토큰을 왼쪽에서 오른쪽으로 읽으면서 **left-most derivation**을 구성해가는 방식. 입력을 **이미 맞춘 부분(parsed)** 과 **아직 안 읽은 부분(unparsed)** 으로 나눠서, 매 단계 left-most derivation을 한 칸씩 진행한다. 왼쪽 non-terminal을 먼저 전개하면서, terminal이 입력과 맞으면 parsed 쪽으로 옮겨간다. (예: `S → E+S | E`, `E → num | (S)`로 `(1+2+(3+4))+5`.)

### Recursive Descent *(p.40)*
규칙들을 **순서대로** 시도해보고, 안 맞으면 되돌아가는(**backtrack**) 방식.
```
E → T | T + E
T → int | int · T | ( E )
입력: ( int )
```
1. `E → T → int` 시도: 첫 토큰 `(`와 `int`가 안 맞음 → backtrack
2. `E → T → int · T` 시도: 역시 안 맞음 → backtrack
3. `E → T → ( E )` 시도: `(` 매치 성공
4. 안쪽 `E`에서 다시 `E → T → int`: `int` 맞고, 마지막 `)`도 맞아서 파스 완료

1, 2번이 실패한 이유: `int`로 시작하는 규칙은 첫 토큰이 `(`인 입력과 애초에 안 맞는다. 만약 Parser가 **첫 토큰을 미리 봤다면** `(`로 시작하는 `T → ( E )` 하나만 골라서 처음부터 3번으로 갈 수 있었다. 현재의 recursive descent는 순서대로 다 시도하기 때문에 못 고를 뿐. **첫 토큰 하나만 보고 규칙이 정해지면 backtracking이 필요 없다** = 뒤에 나올 LL(1)의 핵심 아이디어.

### Formal Notation과 구현 *(p.41~42)*
- `next`: 현재 입력 토큰을 가리키는 포인터
- `term(token)`: terminal 하나를 맞추고 포인터를 한 칸 이동. 같으면 true, 다르면 false
- non-terminal `S`의 모든 production을 시도하는 함수 `S()`, 그중 n번째만 시도하는 `S_n()`

```c
// CFG: E → T | T + E,  T → int | int · T | ( E )

bool term(token) { return *next++ == token; }

bool E1() { return T(); }
bool E2() { return T() && term("+") && E(); }
bool E() {
    Token *save = next;
    return (next = save, E1()) || (next = save, E2());
}

bool T1() { return term("int"); }
bool T2() { return term("int") && term("·") && T(); }
bool T3() { return term("(") && E() && term(")"); }
bool T() {
    Token *save = next;
    return (next = save, T1()) || (next = save, T2())
                              || (next = save, T3());
}
```
핵심은 `save`: 각 production을 시도하기 전에 `next`를 저장해두고, 실패하면 `next = save`로 **입력 위치를 되돌린** 다음 다음 production을 시도한다. 이게 backtracking의 실체.

### 한계 *(p.43)*
입력 `int · int`:
```
E() → E1() → T()
        T() → T1() → term("int") → 성공, next는 · 를 가리킴
        T1이 true이므로 || 가 거기서 멈춤 (T2, T3는 시도조차 안 함)
        T()가 true 반환
      E1이 true → E()도 true 반환 (E2는 시도 안 함)
```
`int`만 소비한 채 **성공(true)** 으로 끝나고, 남은 `· int`는 처리되지 않아 최종적으로 입력 전체를 못 읽었다는 에러가 난다. 올바른 정답은 `T2`(`int · T`)였는데도.
- 핵심: **`||`는 앞 항이 false일 때만 다음 항으로 넘어간다.** `T2`로 가려면 `T1`이 false여야 하는데, `T1`은 첫 토큰이 `int`가 아닐 때만 false. 그래서 `int`로 시작하는 입력에서는 `T2`가 영원히 실행되지 않는다. backtracking은 **실패했을 때만** 일어나고, "부분적으로 성공했지만 틀린" 경우는 되돌리지 않는다.
- 해결 방향 두 가지: (1) production 순서를 바꿔 긴 것(`int · T`)을 먼저 시도 — 문법마다 손으로 조정해야 함. (2) **문법 자체를 고쳐서** 첫 토큰 하나만 보고 규칙이 하나로 정해지게 만든다 — 이게 LL(1).

### LL(1) *(p.44)*
- **L**: 입력을 **L**eft에서 오른쪽으로 읽는다
- **L**: **L**eftmost derivation을 만든다
- **1**: **1**개의 lookahead 토큰만 본다
토큰 하나만 미리 봐도 쓸 production이 정해지는 문법. 이러면 backtracking이 필요 없다.

### ① Left factoring *(p.45)*
여러 production이 **같은 접두사**로 시작하면 첫 토큰만으로는 어느 걸 고를지 모른다. 공통 부분을 먼저 빼고 나머지를 새 non-terminal로 분리한다.
```
S → E + S | E        ⟹    S → E S'
                           S' → + S | ε
```
`E`를 먼저 읽고 그 **다음 토큰**(`+`가 있으면 `S' → + S`, 없으면 ε)으로 결정한다.

예: `T → int | int · T | ( E )`
> ✏️ **직접 풀어보기** (답을 보고 이해만 함)

```
T  → int T' | ( E )
T' → · T | ε
```
공통 접두사는 `int`. 이제 첫 토큰이 `int`면 `int T'`, `(`면 `( E )`로 **하나만** 정해져서 앞의 `int · int` 문제가 사라진다.

### ② Left recursion 제거 *(p.46)*
`S → S a`처럼 **LHS가 RHS의 맨 앞에 오는** 재귀를 left recursion이라 한다. Top-down parser에서는 치명적이다.
```c
void parse_S() {      // S → S a | b
    parse_S();        // 첫 토큰도 소비하지 않고 자기 자신을 호출
    ...
}
```
입력을 하나도 읽지 않고 `S()`가 `S()`를 부르므로 **무한 재귀**. 간접 left recursion(`S →* S a`)도 마찬가지.

해결은 left recursion을 **right recursion**으로 바꾸는 것.
```
S → S a | b        ⟹    S → b S'
                         S' → a S' | ε
```
언어는 그대로(`b`, `ba`, `baa`...)인데 항상 **`b`를 먼저 소비**하고 시작해서 무한 재귀가 없다.

일반형:
```
S → S a1 | S a2 | ... | S an | b1 | b2 | ... | bm
     ⟹
S  → b1 S' | b2 S' | ... | bm S'
S' → a1 S' | a2 S' | ... | an S' | ε
```
`b`들은 left recursion이 아닌 "시작이 되는" 선택지, `a`들은 뒤에 반복되는 부분.

> 이 변환으로 parse tree 모양이 바뀌어 결합성이 뒤집힌 것처럼 보일 수 있다. 슬라이드에서는 **언어(생성되는 문자열)가 같다**는 점까지만 다루고, 결합성 복원은 나중에 AST를 만들 때 따로 처리한다.

### 문법 계층 *(p.46)*
모든 문법이 LL(1)로 바뀌는 건 아니다.
```
All ⊃ Unambiguous ⊃ LR(k>1) ⊃ LR(1) ⊃ LALR(1) ⊃ SLR(1) ⊃ LR(0)
```
`LL(1)`은 이 사슬과 별개로 SLR(1)~LALR(1) 근방에 걸치는 독립적인 부분집합. LR 계열은 다음 강의(bottom-up)에서 다룬다.

### Class Exercise — LL(1) 변환 *(p.47)*
> ✏️ **직접 풀어보기** (답을 보고 이해만 함)

**1. `A → A A a | b`**: `S → S α | β`에 `α = A a`, `β = b`를 대입.
```
A  → b A'
A' → A a A' | ε
```
`A'`의 첫 항이 `a A'`가 아니라 `A a A'`(α 전체)라는 점에 주의.

**2. `E → E + E | E x E | a`**
```
// ① left factoring: 앞의 두 production이 E로 시작
E → E T | a
T → + E | x E
// ② left recursion 제거: α = T, β = a
E  → a E'
E' → T E' | ε
T  → + E | x E
```
(`T`를 풀어 써도 같다: `E' → + E E' | x E E' | ε`.) 이 문법은 변환 기법 연습용이고, 우선순위/결합성 문제는 그대로 남아 있어서 진짜 LL(1)은 아니다.

### Predictive Parsing *(p.48)*
- 문법이 LL(1)이면 어떤 상황에서도 **적용 가능한 production이 최대 하나**.
- 그러면 backtracking 없이 그 production 하나만 적용하는 파서를 만들 수 있고, 이것이 **predictive parsing**. 기능(정확성)을 해치지 않으면서 backtracking만 없앤다.

### Parsing Table *(p.49)*
"지금 이 non-terminal을 전개해야 하는데 다음 토큰이 이거다 → 이 production을 써라"를 표로 만든다. 행은 non-terminal, 열은 lookahead terminal, `$`는 입력의 끝(EOF).
```
S  → E S'
S' → + S | ε
E  → num | ( S )
```
| | num | + | ( | ) | $ |
|---|---|---|---|---|---|
| **S** | E S' | | E S' | | |
| **S'** | | + S | | ε | ε |
| **E** | num | | ( S ) | | |

- `E`를 전개해야 하는데 다음 토큰이 `(`이면 `( S )`.
- `S'`를 전개해야 하는데 다음 토큰이 `num`이면 빈 칸 → **ParseError**(문법 에러).

### Recursive-Descent Parser 구현 *(p.50~53)*
non-terminal마다 함수 하나, 함수 안에서 lookahead 토큰으로 switch. 표의 그 행을 그대로 옮긴 것.
```c
void parse_S() {
    switch (token) {
    case num: parse_E(); parse_S'(); return;
    case '(': parse_E(); parse_S'(); return;
    default:  ParseError();
    }
}

void parse_S'() {
    switch (token) {
    case '+': token = input.next(); parse_S(); return;
    case ')': return;      // S' → ε
    case EOF: return;      // S' → ε
    default:  ParseError();
    }
}

void parse_E() {
    switch (token) {
    case number: token = input.next(); return;
    case '(':    token = input.next(); parse_S();
                 if (token != ')') ParseError();
                 token = input.next(); return;
    default:     ParseError();
    }
}
```
backtracking 버전과 비교:
- `save`/`next = save` 되돌리기 코드가 없다. 토큰을 **소비할 때만** `token = input.next()`로 전진하고 되돌리지 않는다.
- production을 순서대로 다 시도하지 않고 **`token` 하나로 즉시 결정**한다.
- `S' → ε`은 아무것도 소비하지 않고 `return`. 이때 허용되는 토큰 집합(`)`, `EOF`)이 바로 다음 섹션의 Follow.

**입력 `( num ) $` 추적**
> ✏️ **직접 해보기**: 호출 순서를 먼저 직접 적어보고 아래와 비교 (수업 중엔 답을 보고 이해만 함)

```
parse_S()            token='('  → case '(' : parse_E(); parse_S'()
 ├ parse_E()         token='('  → case '(' : token을 다음(num)으로, parse_S() 호출
 │   ├ parse_S()     token=num  → case num : parse_E(); parse_S'()
 │   │   ├ parse_E()   token=num → case number : token을 다음())으로, return
 │   │   └ parse_S'()  token=')' → case ')' : ε, return
 │   └ (parse_E로 복귀) token==')' 확인 OK → token을 다음($)으로, return
 └ parse_S'()        token=$    → case EOF : ε, return
```
에러 없이 끝나고 `token`이 `$` → accept. **호출 구조가 곧 parse tree** (`parse_S`가 `parse_E`와 `parse_S'`를 부르는 건 `S → E S'`). 어느 지점에서도 되돌아가지 않고 매번 `token` 하나로 분기가 결정된다.

---

## 6. Parsing Table 자동 생성: Nullable, First, Follow *(슬라이드 p.54~77)*

지금까지는 표를 손으로 채웠다. 이제 문법만 주면 표를 자동으로 만드는 알고리즘.

### 세 가지 속성 *(p.54)*
| 속성 | 뜻 |
|---|---|
| **Nullable(x)** | `x`가 빈 문자열을 유도할 수 있으면 true (`x →* ε`) |
| **First(x)** | `x`에서 유도되는 문자열의 **맨 앞에 올 수 있는 terminal 집합** `{t \| x →* ty}` |
| **Follow(x)** | 어떤 유도에서든 `x` **바로 뒤에 올 수 있는 terminal 집합** `{t \| S →* yxtz}` |

직관 예 (`S → E S'`, `S' → + S | ε`, `E → num | ( S )`):
- `S'`는 `S' → ε`이 있으니 Nullable. `S`는 `E`가 nullable이 아니라서 Nullable이 아니다.
- `First(S') = {+}`. ε은 terminal이 아니라서 First에 아무것도 안 더하고, "nullable이다"라는 정보로 따로 관리한다.
- `First(E) = {num, (}`.
- `E` 바로 뒤에는 `S'`가 오고 `S'`는 `+`로 시작하거나 ε이니, `Follow(E)`에 `+`가 들어간다.
- `)`와 `$`가 `Follow(S')`에 속하는 이유: `S`는 start symbol이라 뒤에 `$`가 올 수 있고, `S'`는 `S → E S'`에서 `S`의 맨 끝이라 `S` 뒤에 오는 것은 `S'` 뒤에도 온다. 또 `E → ( S )`에서 `S` 바로 뒤에 `)`가 오므로 `) ∈ Follow(S)`이고 같은 이유로 `Follow(S')`에도 들어간다.

### Nullable 계산 *(p.55)*
- `ε`은 nullable.
- `X → A1 A2 ... An`에서 **모든 Ai가 nullable이면 X도 nullable**.

### First 계산 *(p.56)*
- terminal `t`는 `First(t) = {t}`.
- `X → A1 A2 ... An`에서 `A1 ... A(i-1)`이 **모두 nullable이면** `First(X) += First(Ai)`. 앞의 기호들이 사라질 수 있어서 그 다음 기호가 맨 앞에 올 수 있다.

### Follow 계산 *(p.57)*
- `Follow(S) = {$}` (S는 start symbol)
- `X → A1 ... An`에서 `A(i+1) ... An`이 **모두 nullable이면** `Follow(Ai) += Follow(X)`. `Ai` 뒤가 다 사라질 수 있으면 `X` 뒤에 오는 게 `Ai` 바로 뒤에도 올 수 있다.
- `A(i+1) ... A(j-1)`이 **모두 nullable이면** `Follow(Ai) += First(Aj)`. 사이가 다 사라지면 `Aj`가 `Ai` 바로 뒤에 온다.

### 통합 알고리즘 *(p.58)*
```
// 초기화
모든 기호 X: First(X)={}, Follow(X)={}, Nullable(X)=false
Follow(S) = {$}
모든 terminal t: First(t) = {t}
Nullable(ε) = true

// 반복
Repeat
    각 production X → A1 A2 ... An 에 대해:
        모든 Ai가 Nullable이면          Nullable(X) = true
        A1..A(i-1)이 Nullable이면       First(X)  += First(Ai)
        A(i+1)..An이 Nullable이면       Follow(Ai) += Follow(X)
        A(i+1)..A(j-1)이 Nullable이면   Follow(Ai) += First(Aj)
Until First, Follow, Nullable에 변화가 없을 때까지
```
값이 더 늘어나지 않을 때까지 반복해서 **고정점(fixed point)** 에 도달한다.

**연습: `X → Y Z`, `Y → a | ε`, `Z → b`**
> ✏️ **직접 풀어보기**: Nullable / First / Follow (수업 중엔 답을 보고 이해만 함)

| | Nullable | First | Follow |
|---|---|---|---|
| **Y** | true (`Y → ε`) | {a} | {b} |
| **Z** | false | {b} | {$} |
| **X** | false (`Z`가 nullable이 아님) | {a, b} | {$} |

- `First(X) = {a, b}`: `Y`가 nullable이라 `Y`가 사라지면 `Z`의 `b`가 맨 앞에 올 수 있어서 `First(Z)`도 더해진다.
- `Follow(Y) = First(Z) = {b}`: `Y` 바로 뒤에 `Z`가 오고 `Z`는 nullable이 아니라서 `Follow(X)`는 안 더해진다.
- `Follow(Z) = Follow(X) = {$}`: `Z`는 `X → Y Z`의 맨 끝.

### 예시: 반복 계산 *(p.59~67)*
> ✏️ **직접 해보기**: 노트를 덮고 First/Follow를 고정점까지 반복 계산 (수업 중엔 답을 보고 이해만 함)

`S → E S'`, `S' → + S | ε`, `E → num | ( S )`
- **Nullable**: `S' → ε` 하나만 true. `S`, `E`는 false.
- **First**: `First(S') = {+}`, `First(E) = {num, (}`, `First(S) = First(E) = {num, (}` (`E`가 nullable이 아니라서 `S'`까지는 안 봄).
- **Follow**: 초기 `Follow(S) = {$}`.
  - `S → E S'`: `S'`는 맨 끝이라 `Follow(S') += Follow(S) = {$}`.
  - 같은 규칙에서 `E` 뒤에 `S'`가 오니 `Follow(E) += First(S') = {+}`. `S'`가 nullable이라 `Follow(E) += Follow(S) = {$}`도 된다.
  - `E → ( S )`: `S` 뒤에 `)`가 오니 `Follow(S) += {)}`.
  - 갱신된 `Follow(S) = {$, )}`을 `Follow(S')`와 `Follow(E)`에 다시 전파해야 한다. 한 바퀴로 안 끝나서 변화가 없을 때까지 반복.

| | First | Follow | Nullable |
|---|---|---|---|
| **S** | {num, (} | {$, )} | False |
| **S'** | {+} | {$, )} | **True** |
| **E** | {num, (} | {$, ), +} | False |

`parse_S'`에서 `)`와 `$`를 ε로 처리하던 근거가 `Follow(S') = {$, )}`.

### Parsing Table 생성 규칙 *(p.68~69)*
각 production `X → A1 A2 ... An`마다:
1. **First 규칙**: `First(A1 ... An)`에 속한 모든 terminal `t`에 대해 `table[X, t] = (이 production)`.
   - `First(A1 ... An)`: `A1`이 nullable이 아니면 `First(A1)`, nullable이면 `First(A1) + First(A2 ... An)`.
2. **Follow 규칙**: **모든 `Ai`가 nullable이면**(ε production 포함) `Follow(X)`의 모든 terminal `t`에 대해서도 `table[X, t] = (이 production)`.
   - 이유: 파스 중간 문자열이 `X t Y`일 때 `X → A1...An`을 적용하면 `Ai`들이 모두 사라져서 결국 `t Y`가 남고, `t`가 맨 앞 terminal이 되기 때문.

적용 예:
```
S' → + S   : First = {+}                          → table[S', +] = + S
S' → ε     : 모두 nullable → Follow(S') = {$, )}  → table[S', $] = ε, table[S', )] = ε
E  → num   : First = {num}                        → table[E, num] = num
E  → ( S ) : First = {(}                          → table[E, (] = ( S )
S  → E S'  : First(E) = {num, (}                  → table[S, num] = table[S, (] = E S'
```
앞서 손으로 채운 표와 정확히 같다.

**Follow가 왜 필요한가 (헷갈린 지점)**
First만으로 표를 만들면, `S' → ε`의 First는 **비어 있어서** 어느 칸에도 못 들어간다. 그러면 `table[S', )]`가 빈 칸 → ParseError. 즉 `( num )`처럼 **문법에 맞는 유효한 입력인데도 에러로 거부**된다. ε production은 "아무것도 안 만들고 사라지는" 규칙이라 lookahead가 뭔지 알려줄 First가 없다. 그래서 **"`S'`가 사라지면 그 뒤에 이어질 토큰(= Follow)이 lookahead일 때 ε을 쓰도록"** 한다. 정리하면 **Follow는 nullable한 production을 표에 넣기 위해 필요하다.**

### Class Exercise — 종합 예제 *(p.70~77)*
> ✏️ **직접 풀어보기**: Nullable/First/Follow 계산 + parsing table 작성 (수업 중엔 답을 보고 이해만 함)

```
E → T X
T → ( E ) | int Y
X → + E | ε
Y → * T | ε
```
- **Nullable**: `X`, `Y`가 true. `E`, `T`는 false.
- **First**: `T = {(, int}`, `E = First(T) = {(, int}`, `X = {+}`, `Y = {*}`.
- **Follow**:
  - `E`: 시작 심볼이라 `$`, 그리고 `T → ( E )`에서 `)`가 들어와 `{$, )}`.
  - `X`: `E → T X`에서 맨 끝이라 `Follow(E)`를 받아 `{$, )}`.
  - `T`: `E → T X`에서 뒤에 `X`가 와서 `First(X) = {+}`가 들어오고, `X`가 nullable이라 `Follow(E)`도 들어와 `{+, $, )}`.
  - `Y`: `T → int Y`에서 맨 끝이라 `Follow(T)`를 받아 `{+, $, )}`.

| | First | Follow | Nullable |
|---|---|---|---|
| **E** | {(, int} | {$, )} | False |
| **T** | {(, int} | {+, $, )} | False |
| **X** | {+} | {$, )} | True |
| **Y** | {*} | {+, $, )} | True |

**Parsing table**
- `E → T X`: First = `{(, int}`
- `T → ( E )`: `{(}`, `T → int Y`: `{int}`
- `X → + E`: `{+}`, `X → ε`: Follow(X) = `{$, )}`
- `Y → * T`: `{*}`, `Y → ε`: Follow(Y) = `{+, $, )}`

| | ( | ) | int | + | * | $ |
|---|---|---|---|---|---|---|
| **E** | T X | | T X | | | |
| **T** | ( E ) | | int Y | | | |
| **X** | | ε | | + E | | ε |
| **Y** | | ε | | ε | * T | ε |

한 칸에 production이 **둘 이상** 들어가면 그 문법은 LL(1)이 아니다. 이 표는 모든 칸이 최대 하나라서 LL(1).

---

## 수업 종료 확인

- **Left factoring**은 공통 접두사 때문에 **첫 토큰 하나로 production을 못 고르는** 문제를 해결한다.
- **Left recursion 제거**는 입력을 소비하지 않고 자기 자신을 부르는 **무한 재귀**를 해결한다.
- **Follow**는 ε production(nullable)을 parsing table에 넣기 위해 필요하다.

---

## 핵심 요약

- Parser도 Scanner처럼 **Specification(CFG) → Recognition(Parse tree/AST) → Automation(Top-down/Bottom-up)** 3층 구조.
- **CFG**는 terminal, non-terminal, start symbol, production 4요소. RE와 달리 **unbounded nesting**(중첩)을 재귀로 표현한다.
- 한 입력에 parse tree가 둘 이상이면 **ambiguous**. precedence는 non-terminal **층**으로, associativity는 **재귀 위치**로, dangling else는 **MIF/UIF 구분**으로 해결.
- **AST**는 parse tree에서 문법용 non-terminal을 걷어내고 연산자-피연산자 구조만 남긴 것.
- **Recursive descent**는 순서대로 시도하고 실패하면 backtrack. 부분 성공 후 틀린 경우는 못 고친다.
- 문법을 **LL(1)**(left factoring + left recursion 제거)로 만들면 lookahead 1개로 production이 정해져 **predictive parsing**이 가능.
- **LL(1) parsing table**은 Nullable/First/Follow를 고정점 반복으로 구해, First 규칙과(nullable이면) Follow 규칙으로 채운다.

---

## 수업에서 다룬 섹션

1. Syntax Analysis 개요 (Scanner vs Parser 3단계)
2. Specification: Context-Free Grammar (구성요소, 예제, RE vs CFG)
3. Recognition: Parse Tree, Derivation 순서, Ambiguity (우선순위/결합성/Dangling Else), AST
4. Error Handling
5. Automation: Top-Down Parsing (Recursive Descent, LL(1), Predictive Parsing, Parsing Table, Recursive-Descent Parser 구현)
6. Parsing Table 자동 생성: Nullable, First, Follow
