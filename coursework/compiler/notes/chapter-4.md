# Chapter 4: Syntax Analysis - 2

*2025/2026 Fall, Hunjun Lee*

> 이 자료는 슬라이드에 쪽번호가 인쇄되어 있지 않아서, 아래 `p.N`은 PDF 파일 자체의 페이지 순서(1부터 시작)를 가리킨다. 이 강의는 이전 강의(Syntax Analysis - 1)에서 다룬 CFG·Parse Tree·AST·Top-down(LL) parsing을 복습한 뒤, **Bottom-up(LR) parsing**을 본격적으로 다룬다.

## 1. 복습: Parser의 3대 과제 *(p.2~13)*

Compiler front-end에서 Syntax Analysis(Parser)는 Lexical Analysis와 Semantic Analysis 사이에 위치하며, 전체 구조에서 Context & Symbol Table & CFG 저장소와 상호작용한다 *(p.2~3)*.

Parser의 3대 과제 *(p.4)*:
- **Specification**: 유효한 토큰 문자열을 어떻게 명시할까? → **Context-free grammar (CFG)**
- **Recognition**: 명시된 패턴을 어떻게 인식할까? → **Parse tree**와 **Abstract syntax tree (AST)**
- **Automation**: CFG로부터 parse tree를 어떻게 자동 생성할까? → **Top-down / Bottom-up parsing**, 자동 생성 도구(bison)

### CFG 복습 *(p.5~7)*
- Terminal은 토큰(keyword, symbol, ID, NUM 등), Non-terminal은 program/var/expression/statement 등 문법 단위, Start symbol은 "program"
- 프로젝트에서 다룰 C 유사 언어의 전체 production 29개(program → declaration-list부터 arg-list → arg-list , expression | expression까지)가 슬라이드에 명시됨 — 세부 규칙은 프로젝트 자료 참고

### Parse Tree 복습 *(p.9)*
- Derivation을 트리로 표현: **terminal은 leaf, non-terminal은 internal node**
- Leaf들을 in-order traversal하면 원래 입력이 복원됨
- 연산 순서·결합 관계(association)를 보여줌 — 예: `id · id + id`에서 `·`가 `+`보다 트리 하위(더 tightly binding)에 위치

### AST 복습 *(p.10)*
AST는 parse tree에서 **non-terminal 등 불필요한 세부 정보를 제거**해 얻어짐 — 예: `S`, `E` 같은 non-terminal 노드는 사라지고 연산자(`+`, `·`)와 피연산자(`id`)만 남는 트리 구조가 됨

### Top-down (LL) Parsing 복습 *(p.12~13)*
- Token stream을 읽으며 문자열의 **leftmost derivation**을 구성
- **LL(1)**: Left-to-right scanning, Leftmost derivation, 1 look-ahead symbol — 어떤 production을 적용할지 결정하기 위해 토큰 1개를 미리 읽어야 함
- LL(1)로 만들기 위한 변환:
  - **Left factoring**: 공통 prefix를 인수분해해 non-terminal S'를 추가 — 예: `S → E+S | E`를 `S → ES'`, `S' → +S | ε`로 변환
  - **좌재귀 → 우재귀 변환**: `S →* Sa` 형태의 left recursion(무한 derivation을 유발)을 우재귀로 바꿈

---

## 2. Bottom-Up Parsing 개념 *(p.14~19)*

### 개요 *(p.15~16)*
- Bottom-up parsing은 **LR grammar**를 사용해 Top-down parsing보다 더 표현력 있는(more expressive) 문법을 다룰 수 있음
- 프로그램의 **rightmost derivation**을 구성(단, 실제로는 이를 역순으로 추적) — **L**eft-recursive grammar + **R**ightmost derivation에서 이름을 따옴
- **shift-reduce parser**에 의존: 다음 입력 토큰으로 **shift**하거나, 스택의 기호들을 **reduce**함
- Rightmost derivation은 production을 "뒤집어서(inverting)" 기호들을 start symbol로 reduce해나가는 과정 — RHS(production 우변)를 매칭해 LHS(좌변)로 치환 *(p.16)*
  - 예: `int * int + int` → (T→int) → `int * T + int` → (T→int*T) → `T + int` → (T→int) → `T + T` → (E→T) → `T + E` → (E→T+E) → `E`

### Shift-Reduce Parsing *(p.17~18)*
- Bottom-up parser는 rightmost derivation을 **역순**으로 추적하며, 입력 terminal은 **왼쪽에서 오른쪽으로** 스캔
- 문자열을 두 부분으로 나눔: reduce할 기호들의 시퀀스(**stack**) + 남은 토큰들(**input**)
- 두 가지 액션: **Reduce**(스택의 기호들을 사용) / **Shift**(input의 최좌측 토큰을 스택으로 이동)
- 예시(`E → T | T+E`, `T → int | int*T | (E)`, 입력 `int * int + int`): shift, shift, shift, reduce(T→int), reduce(T→int*T), shift, shift, reduce(T→int), reduce(E→T), reduce(E→T+E) 순으로 `int*int+int`가 `E`로 축약됨

### Action Selection Problem *(p.19)*
- 어떤 action을 취해야 할지 결정하는 것이 핵심 과제: shift할지, reduce할지(한다면 어떤 production을), 를 결정해야 함
- **Conflict**가 발생할 수 있음: 주어진 state(stack+input)에서 여러 가능한 action이 존재
  - **Shift-reduce conflict**: shift와 reduce가 모두 가능
  - **Reduce-reduce conflict**: 서로 다른 두 production으로 reduce 가능
  - 예: 스택에 `int`, 입력에 `* int + int`가 남아있을 때 lookahead 없이는 shift/reduce 중 뭘 할지 알 수 없음

---

## 3. LR(0) Parsing *(p.20~35)*

### LR-Style Grammar 계층 *(p.20)*
- **LR(k)**: left-to-right scanning, right-most derivation, k symbol lookahead
- 변형: LALR, SLR 등이 존재
- 포함 관계(바깥→안쪽): All ⊃ Unambiguous ⊃ LR(k>1) ⊃ LR(1) ⊃ LALR(1) ⊃ SLR(1) ⊃ LR(0), 그리고 LL(1)은 이들과 부분적으로 겹치는 별도 영역

### LR(0) 정의 *(p.21)*
LR(0)은 **어떤 lookahead 없이도** action을 결정할 수 있는 문법을 가리킴 — 스택 안의 기호만으로 reduce-reduce, shift-reduce conflict가 전혀 없어야 함

### NFA Representation *(p.22~23)*
- Shift-reduce parsing을 **NFA**로 표현 가능. State는 **item**(production에 구분자 `.`을 RHS에 삽입한 것)
  - 예: `T → (E)`는 4개의 item을 가짐: `T→.(E)`, `T→(.E)`, `T→(E.)`, `T→(E).`
  - `T→(.E)`는 "("가 스택에 있고, 다음 입력으로 "E"를 기대한다는 의미
- 시작/끝 state를 위한 dummy production `S' → S$` 추가
- 두 종류의 state 전이:
  - **Shift transition**: shift action에 의한 전이 — 예: `{T→(.E)}` → `{T→(E.)}` (입력 최좌측 기호가 "E"일 때)
  - **ε-transition**: 기대하는 기호로부터 뻗어나가는 다른 production을 만날 때 — 예: `{T→(.E)}`가 `{E→.T}`와 `{T→.T+E}`로 확장

### LR(0) DFA Representation *(p.24)*
- NFA → DFA 변환: **ε-closure**로 NFA state들을 그룹화(Closure)
- Closure(s) 규칙: `{A→α.Bβ}`가 있고 `B→γ`가 production이면, `{B→.γ}`를 추가

### LR(0) Parsing Using DFA *(p.25~26)*
- 스택 안의 기호를 이용해 DFA state를 traverse하고, 도착한 state로 shift할지 reduce할지 결정
- **Shift state**(파란색): 아직 item이 완결되지 않아 shift가 필요한 state / **Reduce state**(빨간색): item이 완결(`.`이 맨 끝)되어 reduce하는 state
- 예: 입력 `((a),b)`에 대한 stack 진행 — `(` → `((` → `((a` → `((S` 순으로 DFA state 1→3→2(id.)→7(S→id.) 등을 거치며 traverse

### DFA Traversal Implementation *(p.29)*
- 스택에 **<symbol, state>** 쌍을 저장, top의 <symbol, state>부터 시작
- 두 종류의 표: **goto**(top state + input non-terminal → 다음 state), **action**(top state + input terminal → action)
- 네 가지 action:
  - **Shift x**: `<a, x>`를 스택에 push (a는 현재 입력, x는 상태)
  - **Reduce x → α**: 스택에서 α를 pop하고 `<x, goto[curr_state, x]>`를 push
  - **Accept** (`S'→S$.`) / **Error** (가능한 action 없음)

### LR Parsing Table 생성 *(p.30~31)*
- DFA state를 표의 행 인덱스로 변환
- terminal C에 대한 전이 `S_old → S_new`: `Table[S_old, C] += Shift(S_new)`
- non-terminal N에 대한 전이 `S_old → S_new`: `Table[S_old, N] += Goto(S_new)`
- reduction state `X → β`: `Table[S, *] += Reduce(X→β)` (모든 입력 열에 대해 reduce)
- 예시(`S→(L)|id`, `L→S|L,S` 문법)의 완성된 Action Table + Goto Table이 State1~9로 표현됨

### Parsing Implementation (의사코드) *(p.33)*
```
stack = <dummy, 1>
repeat
    case action[top_state(stack), I[j]]
        shift X: push <I[j++], X>
        reduce X → A:
            pop |A| pairs
            push <X, goto[top_state(stack), X]>
        accept: halt normally
        error: halt and report error
end
```
- 예시(`((a),b)$` 입력)로 `<dummy,1>` → `<dummy,1><(,3>` → … 순으로 stack이 자라나는 과정이 표로 제시됨 *(p.35)*

---

## 4. LR(0)의 한계와 SLR(1) *(p.36~44)*

### LR(0) Limitations *(p.38)*
LR(0) parser는 **reduce action을 갖는 state가 단 하나의 reduction만 가져야**(다른 reduce나 shift가 전혀 없어야) 동작함

### Non-LR(0) 문법 예시 *(p.39~40)*
- Left-associative 문법(`S→S+E|E`)은 LR(0)이지만, **right-associative** 문법(`S→E+S|E`)은 **shift-reduce conflict**가 발생해 LR(0)이 아님
- State2에서 `S→E.`(reduce)와 `S→E.+S`(shift 가능성)가 동시에 존재 → 파싱 테이블에서 `Table[State2, +]`에 `S→E` reduce와 `Shift 3`이 충돌

### Lookahead로 conflict 해결 *(p.41)*
Lookahead 1개 기호를 활용하는 3가지 대표 기법: **SLR(1)**, **LR(1)**, **LALR(1)** — 각각 lookahead를 활용하는 방식이 다름

### SLR(1) Parsing *(p.42~43)*
- LR(0)의 단순한 확장: 각 reduction `X→β`에 대해 다음 기호 γ를 보고, **γ가 Follow(X)에 속할 때만 reduction을 적용**
- 예: `S→E+S|E`, `E→num` 문법에서 `Follow(S)={$}`이므로, State2에서 lookahead가 `+`이면 Shift, lookahead가 `$`이면 `S→E` reduce로 conflict가 해소됨
- SLR parsing table은 LR(0) table처럼 행 전체를 채우지 않고, reduction 열을 Follow 집합에 한정해서 채움

### Class Exercise: SLR 여부 판별 *(p.44)*
문법 `S→L=R | R`, `L→*R | id`, `R→L`에서 "= follows R?"을 확인해야 함 — State5(`S→L.=R`, `R→L.`)에서 reduce `R→L`을 적용할지(lookahead가 Follow(R)에 속할 때) shift `=`할지의 충돌 여부를 Follow 집합으로 판정

---

## 5. LR(1) Parsing *(p.45~52)*

### 개념 *(p.45)*
- Lookahead 정보를 더 적극적으로 활용
- LR(1)은 lookahead를 이용해 shift/reduce 여부를 결정
- 더 복잡한 state `[X → α.β, γ]` 사용: "α는 이미 스택 top에서 매칭되었고, 다음으로 β, 그 다음 γ를 기대한다"는 의미. `[X→α.β, {x₁,…,xₙ}]`는 사실상 `X→α.β,x₁` ~ `X→α.β,xₙ`의 상태 집합을 가리킴
- ε-closure와 goto 연산이 이 lookahead를 포함하도록 확장됨

### LR(1) Closure *(p.46)*
- `Closure(S)=S`에서 시작해, S의 각 item `[X→α.Bβ,λ]`에 대해 `{B→.γ, First(βλ)}`를 추가
- 초기 state는 `[S'→.S, $]`에서 closure를 적용해 구성 — 예: `S'→S$`, `S→E+S|E`, `E→num` 문법의 초기 closure는 `S'→.S {$}`, `S→.E+S {$}`, `S→.E {$}`, `E→.num {+,$}`

### LR(1) Goto *(p.47)*
`Goto/Shift(I, B) = Closure([X→αB.β, λ])` — state I 안의 item `[X→α.Bβ,λ]`에 대해, B로 전이한 뒤 다시 closure를 적용

### LR(1) DFA 예시와 Reduction *(p.48~49)*
- 위 문법에 대해 State1~5(+Accept)로 구성된 DFA가 만들어지고, 각 item에는 lookahead 집합이 함께 표시됨
- Reduction은 lookahead가 명시적으로 붙은 item에서 발생 — 예: `S→E. {$}`는 lookahead가 `$`일 때만 reduce (SLR처럼 Follow(S) 전체가 아니라, 해당 item에 붙은 정확한 lookahead 집합만 사용)

### LR(1) Parsing Table *(p.50)*
- LR(0) table 생성과 동일하되 reduction 규칙만 다름: state I가 `[X→α., β]`를 포함하면 `Table[I, β] = Reduce(X→α)`
- **LR(1) vs SLR 비교**: LR(1)은 lookahead가 정확히 `$`일 때만 reduce하지만, SLR은 Follow(S)={$} 전체를 사용 — 동일한 예제에서는 결과가 같지만, 더 복잡한 문법에서는 LR(1)이 더 정밀하게 구분 가능

### Class Exercise: LR(1) DFA 구성 *(p.51~52)*
문법 `S→L=R|R`, `L→*R|id`, `R→L`에 대해 RL(1) DFA를 그리는 연습 — **LR(1)은 `[S→L.=R]`과 `[R→L.]`을 서로 다른 lookahead(State2: `$`만, State8: `$,=`)로 구분**할 수 있어, SLR(0)에서 발생했던 shift-reduce conflict가 해소됨

---

## 6. LALR(1) Parsing *(p.53~54)*

- **LR(1)은 state 수가 너무 많다**는 문제가 있음
- **LALR(1)**은 lookahead LR — LR(1) DFA를 구성한 뒤, **production rule은 같지만 lookahead만 다른** 두 LR(1) state를 병합함
  - 예: `[S→id., +]`와 `[S→E., $]`를 각각 가진 두 state가 `[S→id., {$,+}]`, `[S→E., {$,+}]`를 가진 하나의 state로 합쳐짐
- Parser table entry 수를 줄여줌 (병합 결과 state 수 감소)
- 이론적으로는 LR(1)보다 표현력이 약간 낮음(less powerful)
- 실전 비교(Pascal 기준): **SLR은 수백 개 state, LR(1)은 수천 개 state**가 필요한 반면, **LALR(1)은 SLR과 비슷한 state 수**를 가지면서도 **LR(1)과 동일한 lookahead 능력**을 가져 SLR보다 훨씬 강력함 — (세부 구현은 본 강의에서 다루지 않음)

---

## 7. LL/LR Grammar 비교와 계층 *(p.55~57)*

### 파싱 테이블 구성 비교 *(p.55)*
- **LL parsing table**: `Table[non-terminal, terminal] = 적용할 production` — First/Follow로 계산
- **LR parsing table**: `Table[LR state, terminal] = {shift/reduce/error/accept}`, `Table[LR state, non-terminal] = {goto/error}` — closure & goto 연산으로 계산

### 문법 계층 관계 *(p.56~57)*
- 포함 관계(바깥→안): All ⊃ Unambiguous ⊃ LR(k>1) ⊃ LR(1) ⊃ LALR(1) ⊃ SLR(1) ⊃ LR(0)
- **LL(1)은 이 LR 계열 집합들과 일부만 겹치는 별도의 영역** — LL(1)이면서 동시에 LR(0)/SLR/LALR/LR(1)에 속하지 않는 문법도, 반대의 경우도 존재
- **Ambiguous grammar**는 이 모든 (Unambiguous 이하) 카테고리 바깥에 위치 — 구조적으로 parsing table 충돌 없이는 처리 불가능

---

## 8. Ambiguous Grammar 다루기 *(p.58~63)*

### Precedence로 모호성 제거 *(p.58)*
- 트리의 **root에 가까운(상위) production일수록 우선순위가 낮은** 연산자를 가짐 (그 반대도 성립)
- Non-terminal을 추가로 삽입해 우선순위를 강제 — 예: `S→S+S|S·S|id`(ambiguous) → `S→S+T|T`, `T→T·id|id`(unambiguous)로 변환하면 `·`가 `+`보다 먼저 묶임

### Associativity로 모호성 제거 *(p.59)*
재귀를 어느 쪽에 둘지로 결합 방향을 결정:
- **Left associative**: 재귀를 왼쪽에 배치 — `S→S-T|T`
- **Right associative**: 재귀를 오른쪽에 배치 — `S→T^S|T`
- **Non associative**: 재귀를 아예 사용하지 않음 — `S→A<A|A`

### Dangling Else 문제 *(p.60~61)*
- `if/then/else`와 `if/then`이 공존할 때 올바른 closure(어느 if에 else가 붙는지)를 찾아야 함 — "else는 가장 가까운 then과 매칭"되도록 강제해야 함
- 문법을 두 non-terminal로 분리해 해결:
  ```
  S → MIF               // 모든 then이 매칭된 경우
    | UIF                // 매칭 안 된 then이 있는 경우
  MIF → if Cond then MIF else MIF | Others
  UIF → if Cond then S
      | if Cond then MIF else UIF
  ```
  이렇게 하면 `if Cond then UIF else S` 형태에서 else가 자동으로 가장 가까운(안쪽) then과 짝지어짐

### Automatic Disambiguation (yacc/bison 방식) *(p.62~63)*
- 문법을 명시적으로 재작성하지 않고도, **precedence 선언**만으로 shift-reduce conflict 없이 ambiguous grammar를 그대로 사용할 수 있음
- **Precedence**: 서로 다른 terminal 종류 간, 그리고 **stack의 terminal vs. input의 terminal** 간 우선순위를 정의 — 예: `Input(^) > Stack(^) > Stack(*) > Input(*) > Stack(+) > Input(+)`
- **Precedence 규칙**: input token의 precedence가 stack의 마지막 terminal보다 높으면 shift를 우선(그 반대는 reduce 우선) — 예: `*`가 `+`보다 우선순위가 높으므로 `E→E+E.`(stack에 `+`) 상태에서 입력이 `*`면 shift
- **Associativity 규칙**: 연산자가 left-associative면 **stack 위의 연산자에 더 높은 precedence**를 부여(reduce 우선) — 예: `*`가 left-associative면 `Stack(*) > Input(*)`. Right-associative면 반대로 `Input(^) > Stack(^)`

---

## 9. AST 구성 *(p.64~69)*

### AST 복습 *(p.64)*
Parse tree에서 non-terminal 등 불필요한 세부정보를 제거하면 AST가 됨

### AST Data Structure *(p.65)*
- 객체지향 클래스 계층으로 표현: `abstract class expr {}`을 상속하는 `Add`(left, right 필드), `Num`(value 필드) 등
- 예: `id * id + id`의 AST는 root `Add(left=Add(Num,Num)... )` 형태가 아니라, 실제로는 `Add(left=Num(1) 또는 Mult 결과, right=Num)` 형태의 포인터 트리로 구성됨 (슬라이드 예시는 `Add(Num(v), Add(Num(v), Num(v)))` 구조)

### Implicit AST Construction *(p.66)*
- LL/LR parsing 기법은 AST를 **암묵적으로(implicitly)** 구축함 — parse tree 정보가 derivation 과정에 이미 담겨 있음
  - **LL parsing**: AST가 적용된 production들로 표현됨
  - **LR parsing**: AST가 적용된 reduction들로 표현됨
- parsing 단계에서 AST를 암묵적으로 함께 구성해야 함

### AST Construction: LL *(p.67)*
- 각 non-terminal을 파싱하는 함수(`parse_S()` 등)가, LL parsing table을 참고해 token에 따라 분기하고 재귀적으로 child를 parsing한 뒤, 그 결과로 새 AST 노드(`new S(child1, child2)`)를 생성해 반환
```
expr parse_S() {
    switch (token) {
      case num:
      case '(':
        expr child1 = parse_E();
        expr child2 = parse_S'();
        return new S(child1, child2);
      default: ParseError(); }}
```

### AST Construction: LR *(p.68~69)*
- **메커니즘**: 트리의 부분들을 stack에 저장 — 스택의 각 non-terminal X마다 X에 대응하는 subtree를 함께 저장. production `X→α`에 대한 reduce가 일어난 뒤, X에 대한 AST 노드를 새로 생성
- 예: `S→E+S` reduction 전, stack에는 `E`(subtree: `Add(Num(1),Num(2))`), `+`, `S`(subtree: `Num(3)`)가 쌓여있음 → reduction 후에는 이 셋이 pop되고 `S`(subtree: `Add(Add(Num(1),Num(2)), Num(3))`) 하나로 합쳐짐
- **Semantic action 코드**로 구현: reduce action 시 스택에서 `$3, $2, $1`(각각 S, +, E에 대응하는 subtree)을 pop하고, `$$ = new S($1, $3)`으로 새 노드를 만들어 다시 push
  ```
  $3 = pop_stack(); // S
  $2 = pop_stack(); // +
  $1 = pop_stack(); // E
  $$ = new S($1, $3);
  push_stack($$);
  ```

---

## 핵심 요약

- **Bottom-up(LR) parsing**은 rightmost derivation을 역순으로 추적하며, shift(입력을 스택으로)와 reduce(스택의 기호들을 production 좌변으로 치환) 두 액션으로 동작
- **LR(0)**: lookahead 없이 item(production+`.`)의 NFA→DFA(closure/goto)로 action을 결정. reduce state가 유일한 reduction만 가질 때만 동작
- **SLR(1)**: reduce 가능 여부를 Follow(X) 집합으로 제한해 LR(0)의 일부 충돌 해소
- **LR(1)**: item에 정확한 lookahead 집합을 붙여(`[X→α.β,λ]`) 더 정밀하게 충돌 해소하지만 state 수가 폭증
- **LALR(1)**: LR(1) state 중 production은 같고 lookahead만 다른 state를 병합 — SLR 수준의 state 수로 LR(1) 수준의 lookahead 능력을 확보 (실무에서 가장 널리 쓰임)
- **Ambiguous grammar**는 precedence/associativity 삽입으로 문법 자체를 다시 쓰거나(dangling-else는 MIF/UIF 분리), yacc/bison처럼 **precedence 선언**으로 파서가 shift/reduce를 자동 결정하게 할 수 있음
- **AST**는 parse tree에서 non-terminal을 제거한 형태이며, LL은 production 함수의 반환값으로, LR은 reduce 시 semantic action(`$1,$2,…→$$`)으로 파싱과 동시에 암묵적으로 구축됨
