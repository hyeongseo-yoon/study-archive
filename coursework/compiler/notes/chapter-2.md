# Chapter 2: Lexical Analysis

*2026 Fall, Hunjun Lee, Hanyang University*

## 1. Lexical Analysis 개요 *(슬라이드 p.2~6)*

### 컴파일러 구조 속 위치 *(p.2~3)*
```
Source Code → [Front end: Lexical Analysis(Scanner) → Syntax Analysis(Parser) → Semantic Analysis]
            → Code Generation-1 → [Back end: Control/DataFlow Analysis ↔ Optimization → Code Generation-2]
            → Assembly Code
```
Lexical Analysis(**Scanner**)는 Front end의 첫 단계.

### Language: 문장에서 단어를 인식하듯 *(p.4)*
- 사람 언어: `This is a sentence.` → `This`(article), `is`(verb), `a`(article), `sentence`(noun), `.`(punc)
- 프로그램: `if (b == 0) a = b;` → **token**들로 분할: `if`(Keyword), `(`(Symbol), `b`(Identifier), `==`(Symbol), `0`(Constant), `)`(Symbol), `a`(Identifier), `=`(Symbol), `b`(Identifier), `;`(Symbol)

### 생각보다 까다로운 이유 *(p.5)*
Fortran은 공백을 모두 무시하는 언어라 복잡한 예시가 생김:
```
do 5 I = 1.25        →  Identifier "do5I" (전체가 하나의 식별자로 해석됨, 대입문)
do 5 I = 1,25         →  Keyword(do) Label(5) Identifier(I) (반복문, 25는 반복 종료 조건)
  a = a + 1
end do
```
공백이 유의미한 구분자가 아니므로, `do 5 I = 1.25`와 `do 5 I = 1,25`처럼 겉보기엔 비슷해도 완전히 다르게 토큰화될 수 있음 — 문맥을 더 읽어봐야 정확히 알 수 있음.

### Token의 종류 *(p.6)*
- Identifiers: `x, y11, elsex`
- Keywords: `if, else, while, for, break`
- Integers: `2, 1000, -20`
- Floating-points: `2.0, -0.001, .02, 1e5`
- Symbols: `+, *, {,}, ++, <<, <, <=`
- Strings: `"x", "TEST", "Compiler"`

---

## 2. Specification, Recognition, Automation — 세 가지 하위 문제 *(슬라이드 p.7~8)*

Lexical analysis는 세 개의 하위 문제로 나뉜다:
1. **Specification**: lexical pattern을 어떻게 명시할 것인가? → **Regular Expression (RE)**
2. **Recognition**: 명시된 패턴을 어떻게 인식할 것인가? → **Deterministic Finite Automata (DFA)**
3. **Automation**: RE로부터 DFA를 어떻게 자동 생성할 것인가? → 자동 생성 도구(Lex), Thompson's construction(RE→NFA), Subset construction(NFA→DFA)

---

## 3. Specification: Regular Expression *(슬라이드 p.9~14)*

### RE의 귀납적 정의 *(p.9)*
| 표기 | 의미 |
|---|---|
| `a` | 일반 문자는 자기 자신을 나타냄 |
| `ε` | 빈 문자열 |
| `R\|S` | R 또는 S (alteration), R,S는 RE |
| `RS` | R 다음에 S (concatenation) |
| `R*` | R의 0회 이상 반복(concatenation) — closure |

### Language: RE가 나타내는 문자열 집합 *(p.10)*
RE `R`이 주어지면 `L(R)`이 그 RE가 나타내는 언어(문자열 집합):
```
L(abc) = {abc}
L(hello|goodbye) = {hello, goodbye}
L(1(0|1)*) = 1로 시작하는 모든 이진수
```
각 token은 RE로 정의됨: `Keyword = L(if|else|while|break...)`, `Integer = L((-|+|ε)(1|2|...|9)(0|1|2|...|9)*)`

### RE Notational Shorthand — 더 간단한 표기법 *(p.11)*
| 표기 | 의미 |
|---|---|
| `R+` | R의 1회 이상 반복: `R(R*)` |
| `R?` | R 또는 없음(optional): `(R\|ε)` |
| `[abcd]` | 나열된 문자 중 하나: `(a\|b\|c\|d)` |
| `[a-z]` | 범위 내 하나: `(a\|b\|...\|z)` |
| `[^ab]` | 나열된 문자를 제외한 아무 문자 |
| `[^a-z]` | 범위에 속하지 않는 아무 문자 |

### Shorthand 예시 — 정수/실수 표현 *(p.12)*
```
digit    [0-9]  (또는 \d)
digits   digit+
pos_int  [1-9]digit*
int      (-? pos_int) | 0
real     int (.(pos_int | 0))?
```

### Class Exercise *(p.13)*
- Q1. `[abc]` vs `abc`의 차이: `[abc] = {a,b,c}`(한 글자 중 하나) vs `abc`는 문자열 `{abc}`(3글자 연속) — 완전히 다름
- Q2. 과학적 표기법(예: `-1.4E+17`, `-2.3E1`, `8.3E-2`) 기술:
  ```
  int          (-? pos_int) | 0
  opt_frac     (.digits)
  opt_exponent (E(+|-)?digits)
  sci_note     int opt_frac opt_exponent
  ```

### Multiple Matches — 여러 토큰이 매치될 때 *(p.14)*
- 예: `elsex = 0`을 나눌 때 `else / x / = / 0 / ;`로 볼 수도, `elsex / = / 0 / ;`로 볼 수도 있음
- 규칙: **가장 긴 매치(longest matching token)**를 선택, 동점이면 **명세 순서(specification order)상 우선순위가 높은 것** 선택 (예: Keyword `{if|else|while...}`가 Identifier `[a-zA-Z]+`보다 먼저 명세되어 있으면 Keyword 우선)

---

## 4. Recognition: Finite State Automata *(슬라이드 p.15~22)*

### FSA의 구성요소 *(p.16)*
- An input
- A finite set of states
- A start state
- A set of accepting states
- A set of transitions from states to states

예: input이 1이면 state 0→1(accepting)로, 0이면 자기 자신 유지, accepting state에서 다시 0을 받으면 state 0으로 복귀.

### FSA의 동작 3가지 케이스 *(p.17)*
- **Case 1**: 최종적으로 non-accepting state에 도달하면 입력을 reject
- **Case 2**: 입력 시퀀스에 대응하는 transition이 아예 없으면 reject
- **Case 3**: 최종적으로 accepting state에 도달하면 입력을 accept

### 두 가지 FSA: DFA vs NFA *(p.18)*
- **DFA (Deterministic FA)**: state당 입력당 transition이 **하나만** 존재, ε-move 없음
- **NFA (Non-deterministic FA)**: state당 입력당 transition이 **여러 개** 가능, ε-move(입력을 소비하지 않는 transition) 가능. 여러 선택지 중 **하나라도** accepting state에 도달하면 accept

### DFA/NFA 예시 — `AA* | B | AB` *(p.19~20)*
- DFA는 상태 0에서 A/B로 각각 갈라져 명확한 하나의 경로만 존재
- NFA는 ε-move로 여러 경로를 동시에 탐색(state 1,2,3 등이 동시에 활성화됨, 3단계에 걸쳐 최종 accepting state로 수렴)

### DFA vs NFA 비교 *(p.21)*
| | DFA | NFA |
|---|---|---|
| state 수 | (일반적으로) NFA보다 많음 | DFA보다 적음 |
| 구현 | 쉬움, 단순 순회 | 어려움, 복잡한 순회 |
| RE로부터 변환 | - | **RE에서 쉽게 변환 가능** |

### 전체 Lexical Analysis 절차 미리보기 *(p.22)*
```
RE → (Thompson's construction) → NFA → (Subset construction) → DFA → Table
```
DFA를 **transition table**로 만들면, 구현은 단순한 while 루프가 됨:
```c
i = 0;
state = 0;
while (input[i]) {
    state = Table[state, input[i]];
    if (state == invalid) break;
    i++;
}
```

---

## 5. Automation ①: Lex/Flex를 이용한 자동 생성 *(슬라이드 p.24~32)*

### Automatic Generation of Lexers *(p.24)*
Bell Labs의 두 대표 프로그램:
- **Lex**: 입력 프로그램을 Yacc가 처리할 문법의 alphabet으로 변환 (Flex = Lex의 더 빠른 구현체)
- **Yacc/Bison**: "Yet Another Compiler/Compiler"
- **입력**: 우선순위 순서의 정규표현식 목록 + 각 RE에 연관된 action
- **출력**: 입력을 읽어 RE에 따라 token으로 나누는 프로그램

### Lex/Flex 동작 흐름 *(p.25)*
```
User-Provided Spec(foo.l: Definition Section %% Rules Section %% User Func Section)
  → [Flex] → lex.yy.c(Lexer: User Defs / Tables / Lexer&action routines / User code)
  → Input을 받아 Tokens(yylex())와 Token names 등을 출력
```

### Lex Specification의 3개 섹션 *(p.26)*
- **Definition section**: `%{`와 `%}` 사이에서 변수/enum 등을 선언하거나 include, 복잡한 패턴에 이름(sub-rule)을 붙여둠
- **Rules section**: token을 위한 lexical pattern과, 매치됐을 때 수행할 action을 담음
- **User function section**: 결과 lexer 프로그램에 그대로 복사될 함수들을 정의
- 세부사항은 man page 참고: `https://man.freebsd.org/cgi/man.cgi?query=lex&sektion=1`

### Partial Flex 예시 *(p.27)*
```
// partial.l
digit    [0-9]
letter   [a-zA-Z]
%%
if          {return "IF";}
{letter}+   {return "Identifier";}
{digit}+    {return "decimal";}
...
%%
...
```
왼쪽이 Pattern, 오른쪽이 Action.

### Flex Program 예제 — count.l *(p.28)*
```
// count.l
%{
    #include <stdio.h>
    int num_lines = 0;
    int num_chars = 0;
%}
%%
\n    {++num_lines; ++num_chars}
.     {++num_chars;}
%%
main()
{
    // executes rules section
    yylex();
    printf("%d, %d", num_chars, num_lines)
}
```
빌드/실행:
```
flex count.l
gcc lex.yy.c -lfl
./a.out examples.txt
```

### More Complex Example *(p.29)*
```
// complex.l
%{
    #include <stdio.h>
    int num_lines = 0;
%}
%%
[ \t]     {//skip whitespace}
a |
an |
the       {printf("%s: is an article\n", yytext);}
[a-z]+    {printf("%s: ???\n", yytext);}
%%
main() { yylex(); }
```
- `yytext`: 매치된 token의 첫 글자를 가리키는 포인터
- `yyleng`: token의 길이

### Lex 정규표현식 메타문자 *(p.30)*
| Meta Char | Meaning |
|---|---|
| `.` | 줄바꿈(`\n`) 제외 아무 문자 하나 |
| `*` | Kleene closure (0회 이상) |
| `[]` | 대괄호 안 문자 중 하나 매치. 첫 위치의 `-`는 그대로 매치, `^`는 집합 반전 |
| `^` | 줄의 시작에 매치 |
| `$` | 줄의 끝에 매치 |
| `{a,b}` | 앞 패턴을 a~b회 반복 매치 (b는 생략 가능) |
| `\` | 메타문자 이스케이프 |
| `+` | positive closure (1회 이상) |
| `?` | 0회 또는 1회 매치 |
| `\|` | alteration |
| `/` | lookahead 제공 |
| `()` | RE 그루핑 |
| `<>` | 특정 상태에서만 매치되도록 패턴 제한 |

### 실용적인 정규표현식 활용 — Linux 명령어 *(p.31~32)*
- `grep`: `grep -n '\(TEST\)\+' test.txt` — `(TEST)+`를 포함하는 줄 찾기
- `find`: `find -name "test*"` — test로 시작하는 파일명 찾기
- `sed`: `sed -i 's/\(TEST\)\+/BEST/' test.txt` — `(TEST)+`를 BEST로 치환
- `awk`: `awk 'pattern {action}' filename` — 예: `awk '$1 ~ /fail/ {print $2}' file.txt`로 첫 필드가 "fail"을 포함하는 줄의 두번째 필드만 출력

---

## 6. Automation ②: Thompson's Construction (RE → NFA) *(슬라이드 p.33~40)*

### 개요 *(p.33~36)*
Thompson's construction algorithm은 RE로부터 NFA를 자동 생성한다: **base RE에 대한 규칙**을 정의하고, 더 복잡한 RE는 이를 **조합**해서 만든다. 임의의 RE `E`는 시작상태 `S`와 종료상태 `F`를 갖는 하나의 NFA 블록으로 표현된다.

### Thompson Construction Primitives *(p.38~39)*
```
RE: ε (empty string)     →  NFA: S --ε--> F
RE: x (alphabet symbol)  →  NFA: S --x--> F
RE: E1 E2 (concat)       →  NFA: S_E1 -[E1]-> F_E1 --ε--> S_E2 -[E2]-> F_E2
RE: E1 | E2 (alteration) →  NFA: S --ε--> [E1] --ε--> F
                                  S --ε--> [E2] --ε--> F
RE: E* (closure)         →  NFA: S --ε--> A --ε--> [E] --ε--> A (반복)
                                  S --ε--> A --ε--> F
```

### 예시 — `(x|y)*`의 NFA 구성 *(p.40)*
```
Step#1: x → (0 --x--> 1),  y → (2 --y--> 3)
Step#2: (x|y) → 0 --ε--> 1 --x--> 2 --ε--> 5
                0 --ε--> 3 --y--> 4 --ε--> 5
Step#3: (x|y)* → 전체를 감싸는 ε-loop 추가 (start 0 --ε--> 7, 7 --ε--> 1(x|y)블록--ε--> 6 --ε--> 7 반복, 7 --ε--> 8 종료)
```

### Exercise — `(+|-)?d+`의 NFA *(p.41)*
```
(+|-)?  : 0에서 ε로 갈라져 +(1→2) 또는 -(3→4)를 거쳐 5로 합류, 또는 곧바로 5로 가는 ε(옵셔널)
d       : 5 --ε--> 6 --d--> 7
d*      : 7 --ε--> 8, 8↔9,10 loop(d), 8 --ε--> 11(최종)
```

---

## 7. Automation ③: Subset Construction (NFA → DFA) *(슬라이드 p.42~48)*

### NFA→DFA 변환의 핵심 과제 *(p.42~43)*
**non-deterministic transition(특히 ε-transition으로 인한 다중 경로)을 제거**하는 것이 핵심 과제. 예: `(a*|b*)c*`의 NFA는 ε로 두 경로(a-loop, b-loop)가 갈라졌다가 다시 합류하는 구조를 가짐.

### ε-closure를 이용한 변환 *(p.44)*
- DFA의 각 state는 **NFA state들의 집합**이 된다
- **ε-closure(S)**: state S로부터 ε-transition만으로 도달 가능한 모든 state의 집합 — 이 집합 전체가 DFA의 하나의 "큰 state"를 이룸
- 집합 안에 하나라도 accepting state가 있으면, 그 큰 state도 accepting state가 됨

예시 (`a*b*`):
```
ε-closure(0) = {0,1,2},  ε-closure(1) = {1,2},  ε-closure(2) = {2}
Δ(ε-closure(0), a) → ε-closure(1)
Δ(ε-closure(0), b) → ε-closure(2)
Δ(ε-closure(1), a) → ε-closure(1)
Δ(ε-closure(1), b) → ε-closure(2)
Δ(ε-closure(2), b) → ε-closure(2)
```

### NFA to DFA 상세 예시 *(p.45)*
NFA state 0(ε→1,ε→4), 1(a→2), 4(a→5, accepting, a-loop), 2(b→3, accepting)에 대해:
```
Step#1: ε-closure(0)={0,1,2,4} =: A
        Δ(A, a) → ε-closure(2)|ε-closure(5)
        Δ(A, b) → ε-closure(3)
Step#2: ε-closure(2)|ε-closure(5) = {2,5} =: B
        ε-closure(3) = {3}
        Δ(B, a) → ε-closure(5),  Δ(B, b) → ε-closure(3)
Step#3: ε-closure(5) = {5}
        Δ(ε-closure(5), a) → ε-closure(5)
결과: 4개 state A, B, 5, 3으로 이루어진 DFA
```

### Class Exercise *(p.46)*
NFA를 `ε(0)`, `ε(3|8)`, `ε(5)`, `ε(5|9)` 네 개의 DFA state로 축약하는 예시 — a/b 입력에 따라 각 state 간 전이를 계산.

### DFA Optimization — 상태 최소화 *(p.47~49)*
DFA에는 **redundant/equivalent state**가 있을 수 있어 최적화 여지가 있다.
- **핵심**: 두 state가 **구분 불가능(indistinguishable)**한지 판별 — 모든 입력에 대해 같은 목적지 state로 가면 구분 불가능 → merge 가능
  ```
  Δ(2,a)=4 & Δ(2,b)=3,  Δ(3,a)=4 & Δ(3,b)=3  →  2와 3을 merge
  Δ(0,a)=2 & Δ(0,b)=1,  Δ(1,a)=3(==2) & Δ(1,b)=1  →  0과 1을 merge
  ```
- **반복적 최소화 알고리즘**:
  1. state를 non-accepting/accepting 두 집합으로 분할
  2. 각 집합 내에서 state 쌍을 순회하며, **구분 가능(distinguishable)**하면 다른 집합으로 분리 — 두 state (i,j)가 구분 가능하다는 것은, 어떤 입력 a에 대해 `Δ(i,a)`와 `Δ(j,a)`가 서로 다른 집합에 속한다는 뜻
  3. 집합이 더 이상 바뀌지 않을 때까지 2번을 반복
  - 예시: `{0,3,5},{1,2,4}` → `{0,3},{5},{1,2,4}` → 변화 없음 → 최종 확정

### 여러 RE를 동시에 처리하기 *(p.50)*
- 모든 RE의 NFA를 **하나의 NFA로 결합**(공통 시작 state `s`에서 각 token별 NFA로 ε-transition) 후 DFA로 변환
- **Token Matching Rules**:
  1. 각 최종(accepting) state에 token을 연관시킴
  2. final state에 있을 때, **더 진행 가능한 transition이 있는지** 확인(더 긴 매치를 우선)
  3. 하나의 final state가 여러 token에 해당하면 **우선순위(priority)**에 따라 선택

### Recall: DFA to Implementation *(p.51)*
전체 파이프라인 요약: `RE → (Thompson's construction) → NFA → (Subset construction) → DFA → Table` — Table 기반 구현은 위 while 루프 구조 그대로.

---

## 핵심 요약

- Lexical Analysis(Scanner)는 소스코드를 **token**(Identifier, Keyword, Constant, Symbol 등)으로 분할하는 컴파일러 프론트엔드의 첫 단계
- 문제는 세 층위로 나뉜다: **Specification**(RE로 패턴 명시) → **Recognition**(DFA로 패턴 인식) → **Automation**(RE→NFA→DFA 자동 변환)
- **RE**는 `ε`, `R|S`, `RS`, `R*` 네 가지 귀납적 규칙과, `+`,`?`,`[]` 등의 shorthand로 확장됨
- 매치가 여러 개일 때는 **longest match 우선, 동점이면 명세 순서 우선**
- **DFA**(결정적, 구현 쉬움)와 **NFA**(비결정적, RE에서 변환 쉬움)는 표현력은 같지만 트레이드오프가 다름
- **Thompson's construction**(RE→NFA)과 **Subset construction/ε-closure**(NFA→DFA)로 자동 변환되며, 이후 **상태 최소화**로 중복 state를 merge해 최적화함
- 실제로는 **Lex/Flex** 같은 도구가 RE 명세(`.l` 파일)로부터 이 과정을 전부 자동화해 lexer(`lex.yy.c`)를 생성해줌
