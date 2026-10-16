# Chapter 4: Syntax Analysis - 2 — 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*수업일: 2026-10-13 / 대응 정리노트: `notes/chapter-4.md`*

> 슬라이드에 쪽번호가 없어서 `p.N`은 PDF 페이지 순서 기준이다.

**이번 수업의 목표**: bottom-up parser가 shift/reduce를 어떻게 결정하는지(LR 파싱 테이블이 어떻게 만들어지는지)를 직접 설명하고, LR(0) / SLR / LR(1) / LALR의 차이를 구분할 수 있게 된다.

---

## 0. 선수 개념 복습

**Leftmost vs Rightmost derivation**
유도할 때 non-terminal이 여러 개 남아 있으면 어느 걸 먼저 바꿀지 정해야 한다. 그 규칙의 차이다.
- Leftmost: 항상 **가장 왼쪽** non-terminal을 먼저 전개
- Rightmost: 항상 **가장 오른쪽** non-terminal을 먼저 전개

문법 `E → E + T | T`, `T → id`로 `id + id`를 유도하면:
```
Leftmost : E → E+T → T+T → id+T → id+id
Rightmost: E → E+T → E+id → T+id → id+id
```
결과는 같아도 순서가 다르다. 이 차이가 LL과 LR을 가르는 핵심이다.

**LL(1)**
- 첫 L: 입력을 **L**eft-to-right로 읽음
- 둘째 L: **L**eftmost derivation을 만듦
- 1: lookahead 토큰 **1개**로 어떤 production을 쓸지 결정
- 필요한 변환: **left factoring**(공통 prefix 묶기)과 **좌재귀 제거**(`S → Sa` 형태를 우재귀로)

**First / Follow**
- **First(α)**: α에서 유도되는 문자열의 **맨 앞에 올 수 있는 terminal**들의 집합
- **Follow(X)**: 문장 형태에서 non-terminal X **바로 뒤에 올 수 있는 terminal**들의 집합

**ε-closure**
NFA에서 어떤 state 집합으로부터 **입력 소비 없이(ε 전이만으로) 갈 수 있는 모든 state**를 모은 것. NFA → DFA 변환 시 이 묶음 하나가 DFA state 하나가 된다. 오늘 LR의 closure 연산이 이 아이디어를 그대로 가져온다.

**Parse tree vs AST**
- Parse tree: derivation을 **그대로** 트리로 옮긴 것. non-terminal이 전부 internal node로 남아 있음
- AST: 거기서 **의미 없는 non-terminal 노드를 걷어내고** 연산자와 피연산자 중심으로 남긴 것
```
parse tree:   E            AST:    +
             /|\                  / \
            E + T                id   id
            |   |
            T   id
            |
            id
```

> **주의 (헷갈린 지점)**: 수업 시작 때 위 5개를 확인했는데 모두 확실하지 않다고 해서, 이렇게 간단히 복습하고 넘어갔다.

---

## 1. 복습: Parser의 3대 과제 *(p.2~13)*

Parser가 푸는 문제는 3개다.
- **Specification**: 유효한 토큰열을 어떻게 명시? → **CFG**
- **Recognition**: 명시한 패턴을 어떻게 인식? → **Parse tree / AST**
- **Automation**: CFG에서 parse tree를 어떻게 자동 생성? → **Top-down / Bottom-up parsing** (+ bison 같은 도구)

Top-down(LL)은 **leftmost derivation**을 앞에서부터 만들어가는 방식이었다. 오늘은 Automation의 나머지 한 축인 **Bottom-up(LR)**을 배운다. (CFG, Parse tree, AST, LL(1) 내용은 위 선수 개념 복습으로 대부분 커버된다. 아래는 슬라이드 복습 부분 중 보충할 내용이다.)

**CFG 구성 요소 *(p.5~7)***: terminal은 토큰(keyword, symbol, ID, NUM 등), non-terminal은 program/var/expression/statement 같은 문법 단위, start symbol은 `program`이다. 프로젝트에서 다룰 C 유사 언어의 production은 슬라이드에 29개가 나와 있다(세부 규칙은 프로젝트 자료 참고).

**Parse tree의 특징 *(p.9)***
- terminal은 leaf, non-terminal은 internal node다.
- leaf들을 **in-order로 읽으면 원래 입력이 복원**된다.
- 연산 순서와 결합 관계를 보여준다. 예를 들어 `id · id + id`에서 `·`가 `+`보다 트리 아래쪽에 있다(더 tightly binding).

**LL(1) 변환 예 *(p.12~13)***
- **Left factoring**: 공통 prefix를 묶고 non-terminal `S'`를 추가한다. `S → E+S | E`를 `S → E S'`, `S' → +S | ε`로 바꾼다.
- **좌재귀 제거**: `S →* Sa` 꼴의 left recursion은 derivation이 무한히 이어지므로 우재귀로 바꾼다.

---
## LL(1) 과 다른 방법 소개
## 2. Bottom-Up Parsing 개념 (LR 류)*(p.14~19)*

### 핵심 아이디어 *(p.15~16)*
Bottom-up은 **rightmost derivation을 역순으로** 추적한다. **LR grammar**를 쓰기 때문에 top-down(LL)보다 **더 표현력 있는(more expressive) 문법**을 다룰 수 있다. 동작은 **shift-reduce parser**에 의존한다.

0절의 rightmost 유도를 거꾸로 읽으면:
```
id + id  →  T + id  →  E + id  →  E + T  →  E
```
입력에서 시작해서 production의 **우변(RHS)을 찾아 좌변(LHS)으로 치환**해가며 start symbol까지 올라간다. 이 치환이 **reduce**다. 트리를 leaf에서 root 방향으로 쌓으니까 bottom-up이라고 부르고, LR의 **L**은 입력을 왼쪽에서 오른쪽으로 읽는다는 뜻, **R**은 rightmost derivation(의 역순)이라는 뜻이다.

### 예: `int * int + int`의 rightmost derivation
문법은 `E → T | T+E`, `T → int | int*T | (E)`다. 매 단계에서 **가장 오른쪽 non-terminal**을 전개한다.

```
E ⇒ T + E           E → T+E
  ⇒ T + T           E → T      (맨 오른쪽 E)
  ⇒ T + int         T → int    (맨 오른쪽 T)
  ⇒ int * T + int   T → int*T  (남은 T)
  ⇒ int * int + int T → int    (맨 오른쪽 T)
```

이걸 거꾸로 읽으면 아래 shift-reduce 표의 reduce 순서와 정확히 같다.
```
int*int+int
 → int*T+int   (T → int)     두 번째 int
 → T+int       (T → int*T)
 → T+T         (T → int)     마지막 int
 → T+E         (E → T)
 → E           (E → T+E)
```
그래서 "rightmost derivation을 역순으로 추적한다"는 말은, shift-reduce parser의 reduce 순서가 곧 rightmost derivation을 뒤집은 순서라는 뜻이다.

### `T + E`는 어떻게 선택되나

**유도(derivation) 쪽**: 정답 문자열을 이미 알고 있어서 고른 것이다. 첫 단계에서 `E`를 `T`로 바꿀지 `T+E`로 바꿀지는 **목표 문자열 `int*int+int`에 `+`가 있기 때문에** 정해진다. `E → T`로 가면 `+`를 만들 방법이 없다. 이 선택은 사람이 답을 보고 거꾸로 맞춰 가는 것이라 문법 규칙만으로 자동 결정되는 게 아니다. 이 "어떤 production을 쓸지 알아내는 일"이 곧 parsing이다.

**Parser 쪽**: `T + E`는 stack에 `T + T`가 있을 때 **마지막 `T`를 `E → T`로 reduce해서** 생긴다.
```
stack: T + T    input: $
```
가능한 선택을 따져보면:
- shift: input이 `$`뿐이라 불가능
- `T + T` 전체를 reduce: RHS가 `T+T`인 production이 없어서 불가능
- 마지막 `T` 하나를 `E → T`로 reduce: 가능 → `T + E`
- 이후 `T + E`는 `E → T+E`의 RHS와 정확히 일치해서 reduce → `E`

이 예시에서는 선택지가 하나뿐이라 자연스럽게 정해졌다. 문법이 `E → T+E`처럼 **우변에 E를 두는 right-recursive 형태**라서, `+` 오른쪽이 반드시 `E`로 reduce되어야 `T+E` 패턴을 완성할 수 있고, 그래서 `T + T`에서 오른쪽 `T`가 `E`로 올라간다. 반대로 **선택지가 둘 이상인 지점**에서는 어느 쪽인지 알 방법이 필요한데, 그게 LR 테이블을 배우는 이유다.

> **주의 (헷갈린 지점)**: 유도 쪽의 "선택"과 parser 쪽의 "선택"은 다르다. 유도에서는 목표 문자열을 알고 production을 고르지만, parser는 목표를 모르는 채로 입력과 stack만 보고 shift/reduce를 골라야 한다.

### Shift-Reduce Parser *(p.17~18)*
문자열을 두 부분으로 나눠서 관리한다.
```
[ stack ]  |  [ 남은 input ]
```
액션은 두 가지뿐이다.
- **Shift**: input의 맨 왼쪽 토큰을 stack으로 옮김
- **Reduce**: stack 맨 위의 기호들이 어떤 production의 RHS와 일치하면, 그걸 LHS 하나로 치환

예시. 문법 `E → T | T+E`, `T → int | int*T | (E)`, 입력 `int * int + int`:

| stack | input | action |
|---|---|---|
| | `int * int + int $` | shift |
| `int` | `* int + int $` | shift |
| `int *` | `int + int $` | shift |
| `int * int` | `+ int $` | reduce `T → int` |
| `int * T` | `+ int $` | reduce `T → int*T` |
| `T` | `+ int $` | shift |
| `T +` | `int $` | shift |
| `T + int` | `$` | reduce `T → int` |
| `T + T` | `$` | reduce `E → T` |
| `T + E` | `$` | reduce `E → T+E` |
| `E` | `$` | accept |

### Action Selection Problem *(p.19)*
매 순간 "shift할까, reduce할까, reduce면 어떤 production?"을 정해야 한다. 이게 어려워서 **conflict**가 생긴다.
- **Shift-reduce conflict**: shift도 되고 reduce도 되는 경우
- **Reduce-reduce conflict**: 서로 다른 두 production으로 reduce 가능한 경우

위 표의 2번째 줄을 보자. stack이 `int`, input이 `* int + int`일 때 정답은 shift다. 그런데 `int`만 보고는 `T → int`로 reduce해야 할지, `T → int*T`를 위해 shift해야 할지 **lookahead 없이는 알 수 없다**. 이 결정을 자동화하는 게 LR 파싱 테이블의 목적이다.

이 지점의 충돌은 정확히 이렇게 쓴다.
- **Reduce**: `T → int` (stack의 `int`를 `T`로 치환)
- **Shift**: `*`를 stack으로 옮김 (`T → int*T`의 `int . * T`를 이어가는 쪽)

둘 다 현재 stack `int`에서 합법적인 선택이라 **shift-reduce conflict**다. 다만 입력을 한 글자 더 보면 풀린다.
- 다음이 `*` → shift (`int*T`로 가야 하니까)
- 다음이 `+` 또는 `$` → reduce (`int` 뒤에 `*`가 안 오니까 `T → int`)

그래서 **"lookahead 없이는 conflict, 1개 보면 해결"**이라는 구도가 LR(0) → SLR(1) → LR(1)의 큰 흐름이다. 이 문법은 LR(0)은 아니고, lookahead를 쓰는 쪽에서 풀린다.

---

## 3. LR(0) Parsing *(p.20~35)*

이 섹션은 **절차적 개념**이라 정의부터 늘어놓지 않고 예제를 먼저 같이 풀면서 진행했다.

**목표**: stack 내용만 보고 shift/reduce를 결정해주는 자동 장치(DFA)를 만든다.

### item = production에 꽂아둔 책갈피 *(p.22)*
"지금 production의 어디까지 왔는지"를 표시할 수 있으면 결정이 쉬워진다. 그래서 production의 우변에 점 `.`을 찍어 **진행 위치**를 표시한다. 이게 **item**이다.

예제 문법:
```
S → ( L ) | id
L → S | L , S
```
parser가 stack에 기호를 쌓다 보면 어떤 production의 우변을 **절반쯤 쌓은 상태**가 된다. 그 위치를 점으로 표시한 게 item이다. `S → ( L )`으로 reduce하려면 stack 맨 위에 `(`, `L`, `)`가 차례로 쌓여 있어야 한다.

| stack 상황 | 이 production에서의 진행도 | item |
|---|---|---|
| 아직 `(`도 안 쌓임 | 0개 봄 | `S → . ( L )` |
| `(` 쌓임 | 1개 봄 | `S → ( . L )` |
| `( L` 쌓임 | 2개 봄 | `S → ( L . )` |
| `( L )` 쌓임 | 3개 다 봄 | `S → ( L ) .` |

점 **왼쪽은 이미 stack에 쌓은 것**, 점 **오른쪽은 앞으로 기대하는 것**이다.

item으로 결정하는 방법:
- 점이 **맨 끝**: 우변을 다 쌓았으니 **reduce**
- 점 **뒤에 terminal**: 그 terminal을 **shift**하면 점이 한 칸 이동
- 점 **뒤에 non-terminal**: 다음에 그 non-terminal이 만들어져야 하니, 그걸 만드는 production들도 같이 고려해야 함 (이게 closure)

"지금 stack 상태에서 가능한 item들의 모음"을 알면 shift/reduce를 정할 수 있다. 이 모음을 state로 삼아 DFA를 만드는 것이 LR(0)의 전체 아이디어다.

item 개수는 **우변 기호 수 + 1**이다(ε production은 1개). `S → id`는 2개(`S → . id`, `S → id .`, 뒤쪽이 reduce item)이고, `L → L , S`는 우변이 3개라 4개다.

> **주의 (헷갈린 지점)**: item은 별도의 새 개념이 아니라 "production + 진행 위치 표시"일 뿐이다. 점의 위치가 곧 "stack에 이미 쌓인 것 / 앞으로 기대하는 것"의 경계라고 읽으면 된다.

### 시작 state와 dummy production *(p.22)*
파서는 start symbol `S`부터 시작한다. 그런데 "입력을 다 읽고 정말 끝났는지"를 알려면 끝 표시가 필요해서, 맨 위에 dummy production을 하나 추가한다.
```
S' → S $
```
처음 상태는 이 production의 점이 맨 앞에 있는 `S' → . S $`다. 아직 아무것도 stack에 없고 `S`를 기대하는 상태다.

**왜 필요한가**: parser가 reduce를 계속하다가 **언제 "성공, 끝!"이라고 말해야 하는지** 정해야 한다. 문법 `S → ( L ) | id`만 보면:
- stack에 `S`가 하나 남았을 때, 이게 **최종 결과**인지 `L → S`로 더 reduce해야 하는 **중간 단계**인지 헷갈린다.
- `S`는 `L → S`의 우변에도 나오니까 "start symbol로 reduce했다 = 끝"이라고 단정할 수 없다.

그래서 "끝"을 판정하는 용도로 규칙을 하나 **인위적으로** 추가한다.
- `S'`: 새로 만든 start symbol (원래 문법엔 없던 기호)
- `$`: 입력의 끝을 나타내는 특수 토큰(end of input)

**`S' → S $ .`처럼 이 규칙의 점이 맨 끝에 도달하면 accept**다. `S`로 reduce했을 뿐 아니라 **입력 끝(`$`)까지 정확히 소비**했다는 확인이 된다.
```
S' → . S $     ← 시작 state의 첫 item (S부터 시작해서 $까지 가면 성공)
S' → S . $     ← S를 하나 완성했고, 이제 $ 기대
S' → S $ .     ← 점이 맨 끝 → accept
```
원래 문법에는 없는데 파서의 편의를 위해 **억지로 만들어 붙인** production이라 dummy(가짜)라고 부른다. 문법이 인식하는 언어는 바뀌지 않고, 파싱 성공 여부를 판정하는 안전장치 역할만 한다. 비유하자면 시험 답안지 마지막에 "끝"이라고 적는 것이다. 답을 다 쓴 것과 "이제 끝났다"고 선언하는 건 별개다.

> **주의 (헷갈린 지점)**: `S' → S $`는 문법이 하나 늘어난 게 아니라 accept 판정 장치다. 이 규칙의 점이 끝에 오는 순간이 곧 accept다.

### Closure *(p.24)*
시작 state의 점 뒤에는 **non-terminal `S`**가 있다. 이는 앞으로 `S`가 만들어져야 한다는 뜻이므로, `S`를 만드는 방법(production)들의 시작 item도 **같은 state에** 함께 들어 있어야 한다.
```
S' → . S $
S  → . ( L )      ← S를 만드는 방법 1
S  → . id         ← S를 만드는 방법 2
```
이렇게 "점 뒤 non-terminal을 전개한 item들을 추가로 채워 넣는 연산"이 **closure**다. ε-closure와 같은 발상이다. 입력을 안 읽고도(ε) 갈 수 있는 곳을 다 모은다.

**규칙**:
> state에 `A → α . B β`가 있고 `B → γ`라는 production이 있으면, `B → . γ`를 state에 추가한다. (새로 추가한 item 때문에 더 추가할 게 생기면 반복)

**예: `S → ( . L )`이 들어 있는 state의 closure**
- 출발: `S → ( . L )` (점 뒤에 non-terminal `L`)
- 1라운드: `L`을 만드는 production은 `L → S`, `L → L , S` 두 개 → `L → . S`, `L → . L , S` 추가
- 2라운드: 새 item의 점 뒤를 본다.
  - `L → . S`: 점 뒤가 `S` → `S → . ( L )`, `S → . id` 추가
  - `L → . L , S`: 점 뒤 `L`의 시작 item은 이미 들어 있어 추가할 게 없음
- 3라운드: `S → . ( L )`, `S → . id`는 점 뒤가 terminal이라 더 전개할 게 없어 종료

```
S → ( . L )
L → . S
L → . L , S
S → . ( L )
S → . id
```
이 state는 "`(`를 방금 쌓았고, 다음에 `L`이 올 텐데 그 `L`은 `S`로 시작하거나 `L , S` 꼴로 시작한다. 또 `S`는 `(`나 `id`로 시작한다"는 모든 가능성을 한 묶음으로 담고 있다. 이 묶음이 **DFA의 state 하나**다.

### Goto (state 사이 전이)
state에서 다음 입력 기호를 소비하면 점이 한 칸 움직이면서 다른 state로 간다. 예를 들어 stack에 `id`가 shift되면 `S → . id` → `S → id .`이 되어 reduce state가 된다.

**일반 규칙**: 기호 X로 전이하려면 점 뒤가 X인 item의 점을 한 칸 옮기고, 옮긴 item들에 closure를 적용한다.

**예 1: 위 state에서 `(`로 전이**
점 뒤가 `(`인 item은 `S → . ( L )` 하나뿐이다. 점을 옮기면 `S → ( . L )`이고, 여기에 closure를 적용하면 위 state와 **완전히 같은 state**가 된다. 그래서 새 state를 만들지 않고 **자기 자신으로 돌아가는 전이(self-loop)**가 된다.
`((`처럼 괄호가 중첩되어 들어와도 "바로 직전에 `(`를 하나 쌓았다"는 상황이 똑같기 때문이다. "`(` 다음엔 `L`이 오고, 그건 `S`나 `L , S`로 시작"이라는 기대가 계속 반복된다. DFA가 유한한 state로 **임의 깊이의 중첩**을 처리할 수 있는 이유가 이 구조다.

**예 2: 시작 state에서 `S`로 전이**
점 뒤가 `S`인 건 `S' → . S $` 하나뿐이다.
```
S' → . S $   →   S' → S . $
```
점 뒤가 `$`(terminal)라서 closure로 추가할 게 없다. 결과는 **item 하나짜리** state `{ S' → S . $ }`이고, 여기서 `$`를 shift하면 `S' → S $ .`가 되어 **accept**다.

**LR(0) DFA를 만드는 법 정리**
1. dummy production `S' → S $`를 추가하고, 시작 state는 `S' → . S $`에 closure를 적용해 만든다.
2. state에서 기호 X(terminal 또는 non-terminal)마다 점 뒤가 X인 item들의 점을 한 칸 옮기고, closure를 적용하면 **새 state**가 된다 (이미 있는 state와 같으면 그 state로 연결).
3. 더 이상 새 state가 안 생길 때까지 반복한다.

### 이 문법의 전체 LR(0) DFA *(p.25~26)*
state 번호는 임의로 붙였다. ★는 reduce state.
```
state 1 (시작):  S' → . S $ / S → . ( L ) / S → . id
   --S-->  state A: { S' → S . $ }          ($ 만나면 accept)
   --(-->  state 3
   --id--> state 2: { S → id . }            ★ reduce

state 3:  S → ( . L ) / L → . S / L → . L , S / S → . ( L ) / S → . id
   --(-->  state 3 (자기 자신)
   --id--> state 2
   --S-->  state 4: { L → S . }             ★ reduce
   --L-->  state 5: { S → ( L . ) / L → L . , S }

state 5:
   --)-->  state 6: { S → ( L ) . }         ★ reduce
   --,-->  state 7: { L → L , . S / S → . ( L ) / S → . id }

state 7:
   --(-->  state 3
   --id--> state 2
   --S-->  state 8: { L → L , S . }         ★ reduce
```
★ 표시가 **reduce state**(점이 맨 끝)고 나머지는 **shift state**다. (accept용 state까지 합치면 슬라이드의 State 1~9와 같은 개수다.)

**관찰**: reduce state 4개는 전부 **item이 딱 하나뿐**이다(`{ S → id . }` 등). 그래서 이 state에 도착하면 lookahead를 볼 필요 없이 **무조건 그 production으로 reduce**하면 된다. shift와 섞일 일이 없어 conflict가 없고, 이게 **"이 문법은 LR(0)이다"**의 의미다.

**state 5의 동작**: `{ S → ( L . ) / L → L . , S }`에는 reduce item이 없다.
- 입력이 `)` → **shift**해서 state 6 (`S → ( L . )`의 점 뒤가 `)`)
- 입력이 `,` → **shift**해서 state 7 (`L → L . , S`의 점 뒤가 `,`)
- 그 외 토큰 → **error**. 이 state에서 점 뒤에 올 수 있는 기호가 `)`와 `,`뿐이라 다른 토큰은 문법상 올 수 없다. (예: `(a b)`에서 `a` 뒤에 `b`가 오면 걸린다.)

state 5에는 shift item만 있어서 입력을 보고 shift할지 error인지만 정하면 된다. 파싱 테이블에서 state 5 행에 `)`와 `,` 칸만 `Shift`로 채워지고 나머지는 비는 이유다.

### LR 파싱 테이블 생성 *(p.30~31)*
DFA를 표로 바꾸는 규칙은 단순하다.

| DFA에서 | 표에 |
|---|---|
| terminal `c`로 state a → b 전이 | `Action[a, c] = Shift b` |
| non-terminal `N`으로 state a → b 전이 | `Goto[a, N] = b` |
| reduce state(`X → β .`) | `Action[그 state, 모든 terminal] = Reduce X→β` |
| `S' → S . $`에서 `$` | `Accept` |

이 문법의 전체 표 (슬라이드의 State 1~9, `A`는 `S' → S . $` state, `rX`는 해당 production으로 reduce):

| state | `(` | `)` | `id` | `,` | `$` | S | L |
|---|---|---|---|---|---|---|---|
| 1 | s3 | | s2 | | | A | |
| 2 | r(S→id) | r | r | r | r | | |
| 3 | s3 | | s2 | | | 4 | 5 |
| 4 | r(L→S) | r | r | r | r | | |
| 5 | | s6 | | s7 | | | |
| 6 | r(S→(L)) | r | r | r | r | | |
| 7 | s3 | | s2 | | | 8 | |
| 8 | r(L→L,S) | r | r | r | r | | |
| A | | | | | accept | | |

state 2는 **모든 칸이 reduce**다. LR(0)은 lookahead를 안 보니까 어떤 토큰이 와도 똑같이 reduce한다. 이 점이 뒤에 나올 SLR과의 차이가 된다.

### LR(0)이 깨지는 상황
`E → T | T+E`, `T → int | int*T | (E)` 문법에서 stack에 `int`가 쌓인 state에는 이 두 item이 **같이** 들어 있다.
```
T → int .          ← 다 봤으니 reduce 가능
T → int . * T      ← 아직 '*'를 기대하니 shift 가능
```
LR(0) 표 규칙은 "reduce item이 있는 state는 **모든 terminal 칸**에 reduce를 채운다"이므로 이 state의 `*` 칸에:
- reduce 규칙 때문에 `Reduce T→int`
- shift item 때문에 `Shift (int * 뒤 state)`

가 **동시에** 들어가려 한다. 한 칸에 액션이 둘이라 **shift-reduce conflict**고, 이 문법은 LR(0)이 아니다. 원인은 LR(0)이 reduce를 정할 때 **다음 입력 토큰을 전혀 안 본다**는 점이다.

**해결 아이디어**: reduce를 "모든 칸"이 아니라 "**reduce해도 되는 토큰이 올 때만**" 채운다. 어느 토큰이 와야 reduce가 맞는지를 알려주는 게 **Follow 집합**이다. 이 문법에서 `T`의 Follow는 `{ +, $, ) }`다(`T` 뒤에 올 수 있는 건 `T+E`의 `+`, 문장 끝 `$`, `(E)`의 `)`뿐).
- 다음이 `+`, `$`, `)` → `Reduce T→int`
- 다음이 `*` → Follow(T)에 없으니 reduce 칸에 안 들어가고 shift만 남아 **충돌이 사라짐**

이게 다음 섹션의 **SLR(1)**이다.

### 파싱 구현 *(p.29, p.33, p.35)*
- stack에 **<symbol, state>** 쌍을 저장한다. top state와 입력으로 action/goto 표를 조회해서 shift / reduce / accept / error를 수행한다.
- **Reduce**는 우변 길이만큼 pop한 뒤 `<X, goto[top_state, X]>`를 push한다.
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

**`((a),b)$` 따라가기** (`a`, `b`는 토큰 `id`)
시작은 `<dummy,1>`이다. 첫 `(`가 들어오면 `Action[1, (] = s3`이라 shift 3, 즉 `<(,3>`을 push한다.
```
<dummy,1>   →   <dummy,1> <(,3>
```
다음 `(`도 top state가 3이고 `Action[3, (] = s3`(self-loop)이라 또 push한다.
```
<dummy,1> <(,3>   →   <dummy,1> <(,3> <(,3>
```
이후 전체 과정이다. goto는 `Goto[3,S]=4`, `Goto[3,L]=5`, `Goto[7,S]=8`, `Goto[1,S]=accept 직전 state`다. stack은 `기호+상태`로 적는다.

| # | stack | 남은 입력 | action |
|---|---|---|---|
| 1 | `1` | `( ( id ) , id ) $` | shift 3 |
| 2 | `1 (3` | `( id ) , id ) $` | shift 3 |
| 3 | `1 (3 (3` | `id ) , id ) $` | shift 2 |
| 4 | `1 (3 (3 id2` | `) , id ) $` | reduce `S→id` (1개 pop, top=3, goto[3,S]=4) |
| 5 | `1 (3 (3 S4` | `) , id ) $` | reduce `L→S` (1개 pop, top=3, goto[3,L]=5) |
| 6 | `1 (3 (3 L5` | `) , id ) $` | shift 6 |
| 7 | `1 (3 (3 L5 )6` | `, id ) $` | reduce `S→(L)` (**3개** pop, top=3, goto[3,S]=4) |
| 8 | `1 (3 S4` | `, id ) $` | reduce `L→S` (top=3, goto[3,L]=5) |
| 9 | `1 (3 L5` | `, id ) $` | shift 7 |
| 10 | `1 (3 L5 ,7` | `id ) $` | shift 2 |
| 11 | `1 (3 L5 ,7 id2` | `) $` | reduce `S→id` (top=7, goto[7,S]=8) |
| 12 | `1 (3 L5 ,7 S8` | `) $` | reduce `L→L,S` (**3개** pop, top=3, goto[3,L]=5) |
| 13 | `1 (3 L5` | `) $` | shift 6 |
| 14 | `1 (3 L5 )6` | `$` | reduce `S→(L)` (3개 pop, top=1, goto[1,S]) |
| 15 | `1 S` | `$` | `$`에서 accept |

볼 포인트:
- reduce는 **우변 길이만큼 pop한 뒤**, 그때 드러난 top state와 LHS로 goto를 조회해서 push한다. (7번, 12번이 우변 3개인 예)
- 7번에서 안쪽 `(a)`가 `S`로 접히고, 바깥 `(`는 stack에 남아 이후 바깥 괄호가 이어서 처리된다. 중첩 처리 방식이다.

**4번 단계의 goto**: stack top은 `id2`이고 state 2는 reduce state다. `S → id`의 우변은 `id` 하나라 `<id,2>` 한 쌍만 pop하고, 그 밑의 `<(,3>`이 드러나 **top state는 3**이 된다.
```
1 (3 (3 id2   →pop 1개→   1 (3 (3
```
state 3의 item 중 점 뒤가 `S`인 건 `L → . S` 하나이고, 점을 옮기면 `L → S .`, 즉 **state 4**다. 그래서 `Goto[3, S] = 4`다.

직관: state 3은 "`(`를 방금 쌓았고, 다음에 `L`이 와야 하며 그건 `S`로 시작할 수 있다"는 상태다. 여기서 `id`를 읽어 `S`로 reduce했다는 건 **이 자리에서 `S`를 shift한 것과 똑같은 효과**다. 그래서 reduce 뒤에는 방금 pop해서 드러난 state를 기준으로 goto를 조회한다. 지금 top state가 "다음에 뭘 기대하고 있었는지"를 알려주기 때문이다.

> **주의 (헷갈린 지점)**: reduce 직후에 보는 state는 reduce가 일어난 state(여기선 2)가 아니라, **pop한 뒤 드러난 state(3)**다. 헷갈리면 "`S`를 그 자리에서 shift했다고 치면 어디로 가는가"로 생각한다.

### NFA 표현 (보충) *(p.22~23)*
LR(0)을 설명할 때 건너뛴 부분이라 체크리스트 점검 후 보충했다. **item을 NFA state로 본다**는 관점이다. item을 state로 보면 shift-reduce parser를 **NFA**로 그릴 수 있고, 전이는 두 종류다.
- **Shift transition**: 점 뒤 기호를 소비하는 전이. 예: `S → ( . L )` --`L`--> `S → ( L . )`
- **ε-transition**: 점 뒤가 non-terminal `B`일 때, 입력 소비 없이 `B`를 만드는 production의 시작 item으로 가는 전이. 예: `S → ( . L )` --ε--> `L → . S`, `L → . L , S`

NFA는 한 시점에 여러 곳에 동시에 있을 수 있어서 결정적으로 쓰기 어렵다. 그래서 **ε-closure로 같이 있을 수 있는 item들을 묶으면 DFA state**가 된다. 앞에서 closure로 item을 채우고 goto로 전이한 과정이 바로 이 NFA→DFA 변환이었다. 즉 LR(0) DFA는 "NFA state(item)들의 ε-closure 묶음"이다.

---

## 4. LR(0)의 한계와 SLR(1) *(p.36~44)*

### 슬라이드 예제로 본 LR(0)의 한계 *(p.38~40)*
```
S → E + S | E
E → num
```
(오른쪽에 재귀가 있는 right-recursive 문법이다.) `E → num`을 reduce한 직후 state에는 이런 item이 같이 들어간다.
```
S → E .          ← reduce
S → E . + S      ← shift '+'
```
이 state `{ S → E . ,  S → E . + S }`에서:
- **입력이 `+`일 때 → shift**가 맞다. `E` 다음에 `+`가 왔다는 건 `E + S` 꼴을 계속 쌓아야 한다는 뜻이다. `S → E`로 reduce하면 stack이 `S`가 되고 뒤에 `+`가 남는데, `S` 바로 뒤에 `+`가 올 수 있는 규칙은 문법에 없어 파싱이 실패한다.
- **입력이 `$`일 때 → reduce `S → E`**가 맞다. 더 읽을 게 없으니 `E`를 `S`로 접어서 마무리해야 한다.

LR(0)은 reduce item이 있는 state의 **모든 terminal 칸**에 reduce를 채우므로 `+` 칸에 두 개가 겹친다.
```
Table[state2, +]  =  Reduce S→E   (reduce item 규칙 때문에)
                     Shift 3      (S → E . + S 때문에)
```
한 칸에 액션이 둘이니 shift-reduce conflict다. 그래서 **left-recursive 문법 `S → S + E | E`는 LR(0)인데, right-recursive 문법 `S → E + S | E`는 LR(0)이 아니다.**

### SLR(1): reduce를 Follow로 제한 *(p.41~43)*
LR(0)이 틀린 건 "reduce가 맞는 토큰인지 확인 없이 모든 칸에 reduce를 채운 것"이다. SLR(1)은 이렇게 고친다.

> reduce item `X → β .`는 **다음 토큰이 Follow(X)에 속할 때만** reduce 칸을 채운다.

위 문법에서 Follow(S)는:
- `S' → S $`이니까 `$`가 들어감
- `S → E + S`에서 `S`는 우변 맨 끝이라 Follow(S) 자신 외에 새로 추가되는 건 없음

그래서 **Follow(S) = `{ $ }`**이고, 표는 이렇게 채워진다.

| state 2 | `+` | `$` |
|---|---|---|
| LR(0) | Reduce **와** Shift (충돌) | Reduce |
| SLR(1) | **Shift 3**만 | **Reduce S→E**만 |

`+`는 Follow(S)에 없으니 reduce 칸에서 빠지고 shift만 남아 충돌이 해소된다. 앞의 `T → int .` 예시와 같은 원리다. SLR 표는 LR(0)처럼 행 전체를 채우는 게 아니라 **Follow 집합에 해당하는 열만** 채운다. 나머지 칸은 error다.

### Follow 구하는 법
Follow(X)는 "문장 형태에서 X 바로 뒤에 올 수 있는 terminal"이다. 규칙 세 가지:
1. start symbol의 Follow에는 `$`가 들어간다.
2. `A → α X β`에서 **X 뒤에 β가 있으면** First(β)가 Follow(X)에 들어간다.
3. `A → α X`처럼 **X가 우변 맨 끝**이면(또는 β가 ε이 될 수 있으면) Follow(A)가 Follow(X)에 들어간다.

> **주의 (헷갈린 지점)**: 수업에서 Follow(R)을 직접 구해보라고 했을 때 구하는 방법 자체가 확실하지 않았다. 위 세 규칙을 적용하는 것이 전부이고, 서로를 포함하는 순환(예: Follow(L) ⊆ Follow(R) ⊆ Follow(L))이 나오면 두 집합은 같다.

### Class Exercise: SLR인지 판별 *(p.44)*
> ✏️ **직접 풀어보기** (수업 중 안 풀었음, 풀이를 보고 이해만 함)

```
S → L = R | R
L → * R | id
R → L
```
(`L`은 대입의 좌변(변수), `R`은 우변(값)이라고 보면 된다.) 이 문법의 한 state에는 이 두 item이 같이 들어 있다.
```
S → L . = R      ← '=' 를 shift
R → L .          ← reduce
```

SLR(1)이 이 state를 해결하려면 `= ∈ Follow(R)`인지 확인해야 한다. Follow를 구하면:

- **Follow(S)** = `{ $ }` (start symbol이고 우변에 나오는 곳이 없음)
- **Follow(L)**: `S → L = R`에서 `L` 바로 뒤가 `=` → `=` ∈ Follow(L). `R → L`에서 `L`이 우변 끝 → Follow(R) ⊆ Follow(L)
- **Follow(R)**: `S → L = R`, `S → R`에서 `R`이 끝 → Follow(S) ⊆ Follow(R), 즉 `$`. `L → * R`에서 끝 → **Follow(L) ⊆ Follow(R)**

Follow(L) ⊆ Follow(R)이고 Follow(R) ⊆ Follow(L)이라 둘은 같은 집합이고, `=`와 `$`가 들어 있으므로
```
Follow(L) = Follow(R) = { =, $ }
```

**판정**: 충돌하는 state에서
```
S → L . = R      입력 '=' → shift
R → L .          입력 Follow(R) = { =, $ } 일 때 reduce
```
`=`가 Follow(R)에 **들어 있으므로** `=` 칸에 shift와 reduce가 둘 다 채워진다. SLR(1)에서도 shift-reduce conflict가 남아서, **이 문법은 SLR(1)이 아니다.**

**그런데 이상한 점**: 이 state에서 `R → L`로 reduce가 정말 필요할까? 이 state는 start 근처에서 `L`을 하나 읽은 상태다. 거기서 `R`로 reduce한 뒤 뒤에 `=`가 오는 문장은 없다. `R = ...`라는 형태는 문법상 불가능하기 때문이다. `=`가 Follow(R)에 들어간 이유는 `* R = ...`처럼 **다른 문맥**의 `R` 때문이다. (`*id = id` 같은 문장에서 `*` 뒤의 `R`은 `=` 앞에 올 수 있다.)

즉 **SLR은 Follow(R)이라는 문법 전체에 대한 전역 정보를 쓰기 때문에, 이 state의 구체적인 문맥에서는 불가능한 reduce까지 허용해서** 충돌을 일으킨다. 필요한 건 "이 state에 이 item이 있을 때만 유효한 lookahead"를 item마다 따로 붙이는 것이고, 그게 **LR(1)**이다.

---

## 5. LR(1) Parsing *(p.45~52)*

### 아이디어 *(p.45)*
item에 lookahead를 직접 붙인다.
```
[ X → α . β , γ ]
```
의미: "α는 stack에 쌓였고, 앞으로 β가 오고, 그 다음에 **γ가 올 때만** 이 production이 쓰인다."

reduce는 점이 끝에 온 `[X → α . , γ]`에서 **lookahead가 γ일 때만** 한다. 전역 Follow가 아니라 **이 문맥의 lookahead**를 쓴다.

앞의 예에서 start 근처의 `R → L .`은 실제로 `$`일 때만 reduce가 맞으므로 LR(1) item으로는 **`[R → L . , $]`**가 된다. `=`일 때는 reduce 대상이 아니고 그 자리는 shift만 남는다.

### LR(1) Closure *(p.46)*
closure 규칙이 LR(0)과 다른 점은 **새로 추가되는 item에 lookahead를 계산해서 붙인다**는 것이다.

> `[A → α . B β, λ]`가 있고 `B → γ`가 production이면, `[B → . γ, First(β λ)]`를 추가한다.

핵심은 `First(β λ)`다. 점 뒤 `B` 다음에 `β`가 오고 그 다음에 원래 lookahead `λ`가 오니까, `B`를 다 만든 직후에 올 수 있는 토큰은 그 둘을 이어 붙인 문자열의 첫 terminal이다. 초기 state는 `[S'→.S, $]`에서 closure를 적용해 구성한다.

> ✏️ **직접 풀어보기** (수업 중 안 풀었음, 풀이를 보고 이해만 함)

**예: `S → L = R | R`, `L → * R | id`, `R → L`의 시작 state** (시작 item `[S' → . S, $]`)
1. `[S' → . S, $]`에서 `B=S`, `β=ε`, `λ=$` → `First($)=$` → `[S → . L = R, $]`, `[S → . R, $]`
2. `[S → . L = R, $]`에서 `B=L`, `β="= R"`, `λ=$` → `First(= R $) = {=}` → `[L → . * R, =]`, `[L → . id, =]`
3. `[S → . R, $]`에서 `B=R`, `β=ε` → `$` → `[R → . L, $]`
4. `[R → . L, $]`에서 `B=L`, `β=ε`, `λ=$` → `$` → `[L → . * R, $]`, `[L → . id, $]`

2번과 4번에서 같은 production에 lookahead만 다르게 나왔으니 합쳐서 표기한다.
```
[S' → . S,     $]
[S  → . L = R, $]
[S  → . R,     $]
[R  → . L,     $]
[L  → . * R,   = / $]
[L  → . id,    = / $]
```

### LR(1) Goto *(p.47)*
`Goto(I, B) = Closure([X → α B . β, λ])`. state I 안의 `[X→α.Bβ, λ]`의 점을 옮기고(lookahead는 그대로 따라감) closure를 적용한다.

위 시작 state에서 `L`로 전이하면:
```
[S → L . = R, $]      점 뒤가 '=' → '=' 입력이면 shift
[R → L . ,    $]      점이 끝 → '$' 입력일 때만 reduce
```
- 입력 `=` → shift (reduce 칸에는 `$`만 있으니 겹치지 않음)
- 입력 `$` → reduce `R → L`

SLR에서는 Follow(R) = `{=, $}` 때문에 `=` 칸에서 충돌했지만, LR(1)은 "이 문맥의 `R → L`은 `$`일 때만"이라고 item이 이미 알고 있어서 충돌이 없다 *(p.51~52: State2는 `$`만, State8은 `$,=`)*. 같은 `R → L .`도 문맥에 따라 lookahead가 달라서 **state가 따로 만들어진다**는 점도 눈여겨볼 부분이다.

### LR(1) 파싱 표 *(p.50)*
LR(0)과 같은 방식으로 만들되 reduce만 달라진다.
> state에 `[X → α . , β]`가 있으면 `Table[state, β] = Reduce(X → α)`

즉 `Follow(X)` 전체가 아니라 **item에 붙은 lookahead 열에만** reduce를 채운다.

### 슬라이드 예제: `S → E+S | E`, `E → num` *(p.46~50)*
SLR 때 쓴 문법에 LR(1)을 적용해 보자. 초기 state는 `[S' → . S, $]`에 closure를 적용해 만든다.
```
[S' → . S,     $]
[S  → . E+S,   $]
[S  → . E,     $]
[E  → . num,   + / $]     ← S→.E+S에서 First(+S $)=+, S→.E에서 $
```
`E`로 전이하면 `[S → E . + S, $]`와 `[S → E . , $]`가 같은 state에 들어간다.
- 입력 `+` → shift
- 입력 `$` → `[S → E . , $]`의 lookahead가 `$`이므로 reduce `S → E`

SLR은 Follow(S) = `{$}` 전체를, LR(1)은 item에 붙은 lookahead `$`를 쓴다. 이 예제에서는 결과가 같지만, `S → L=R | R` 같은 복잡한 문법에서는 LR(1)이 더 정밀하게 구분한다.

### 대가
같은 core(`R → L .`)가 lookahead만 달라서 별개 state로 갈라지므로 LR(1)은 **state 수가 크게 늘어난다.** 이게 LALR의 동기다.

---

## 6. LALR(1) *(p.53~54)*

LR(1) DFA를 구성한 뒤 **production rule(core)은 같고 lookahead만 다른 state들을 병합**한 것이 LALR(1)이다. 병합하면 lookahead 집합이 **합집합**이 된다.
```
P: [R → L . , $]
Q: [R → L . , = / $]
       ↓ 합침
   [R → L . , = / $]
```
(슬라이드 예: `[S→id., +]`와 `[S→E., $]`를 각각 가진 두 state가 `[S→id., {$,+}]`, `[S→E., {$,+}]`를 가진 하나로 합쳐짐. 위 구조와 같은 모양이다.)

### 병합의 위험
위 경우는 P의 `$`가 Q 안에 이미 있어서 큰 문제가 없지만, 일반적으로는 **"원래는 이 문맥에서 안 쓰이던 lookahead가 다른 문맥에서 넘어와 붙는" 문제**가 생긴다. SLR의 약점(문맥 무시)과 같은 종류다.

core가 같은 두 state가 아래처럼 생겼다고 하자(`a`, `b`는 terminal).
```
state P: [A → α . , a]     state Q: [A → α . , b]
         [B → β . , b]              [B → β . , a]
```
- P에서는 `a`면 `A`로, `b`면 `B`로 reduce → 충돌 없음
- Q에서는 `b`면 `A`로, `a`면 `B`로 reduce → 충돌 없음

LR(1)에서는 둘 다 깨끗하다. 그런데 core가 같다고 합치면
```
merged: [A → α . , a / b]
        [B → β . , a / b]
```
`a`가 와도 `b`가 와도 **A로 reduce할지 B로 reduce할지** 모르는 **reduce-reduce conflict**가 된다. 합치기 전에는 없던 충돌이 합쳐서 생긴 것이다.

**shift-reduce 충돌은 새로 안 생긴다.** shift는 점 뒤의 기호(core)만 보고 정해지는데 core가 같은 state끼리 합치니까 shift 쪽 정보는 그대로고, lookahead는 reduce에만 쓰인다. 그래서 병합으로 새로 생기는 건 **reduce-reduce뿐**이다.

### LALR(1)의 위치

| | state 수 | lookahead 정밀도 |
|---|---|---|
| SLR(1) | 적음 (LR(0)과 같음) | Follow 전체 (부정확) |
| LALR(1) | 적음 (SLR과 비슷) | state별 합쳐진 lookahead (SLR보다 정밀) |
| LR(1) | 매우 많음 | 가장 정밀 |

- 이론적으로 LR(1)보다 **약간 약하다**. 위처럼 합쳐서 reduce-reduce가 생기는 문법이 있기 때문이다.
- 실전(Pascal)에서는 SLR이 수백 개, LR(1)이 수천 개 state인데, LALR은 SLR과 비슷한 state 수를 가지면서 실제로 만나는 거의 모든 문법을 처리한다. 그래서 **yacc/bison이 LALR(1)을 쓴다.** 본 강의에서는 구현 세부까지는 다루지 않는다.

---

## 7. LL / LR 문법 비교와 계층 *(p.55~57)*

**표 만드는 방식 비교** *(p.55)*
- **LL 표**: `Table[non-terminal, terminal] = 쓸 production` (First/Follow로 계산)
- **LR 표**: `Table[state, terminal] = shift/reduce/accept/error`, `Table[state, non-terminal] = goto` (closure & goto 연산으로 계산)

**문법 포함 관계** (바깥 → 안) *(p.20, p.56~57)*
```
All ⊃ Unambiguous ⊃ LR(k>1) ⊃ LR(1) ⊃ LALR(1) ⊃ SLR(1) ⊃ LR(0)
```
- `LL(1)`은 이 사슬과 **일부만 겹치는 별도 영역**이다. (LL(1)이지만 LR(0)이 아닌 문법, 반대 경우도 존재)
- **Ambiguous grammar**는 Unambiguous 바깥이라 LR(k)로도 충돌 없이 처리할 수 없다.

사슬이 이렇게 놓이는 건 지금까지 배운 내용 그대로다. LR(0) → SLR은 Follow로 lookahead 추가, SLR → LALR은 state별 lookahead 사용, LALR → LR(1)은 병합 제거. 그래서 뒤로 갈수록 처리 가능한 문법이 늘어난다.

**`SLR(1) ⊂ LALR(1)`인 이유**: reduce에 쓰는 lookahead를 비교한다.
- **SLR**: `[X → α .]`에서 **Follow(X) 전체**를 사용
- **LALR**: 그 item이 실제로 속한 state에서 계산된 lookahead를 사용. 이 값은 **항상 Follow(X)의 부분집합**이다(문맥상 실제로 가능한 토큰만 모은 거라 전역 Follow보다 클 수 없다).

그러면 LALR의 reduce 칸은 SLR보다 같거나 **적다**. SLR 표에서 충돌이 없었다면 reduce 칸이 더 적은 LALR 표에도 충돌이 있을 수 없다. 그래서 SLR이면 반드시 LALR이다. 거꾸로 `S → L = R | R` 문법은 SLR은 아니지만 LALR은 되는 예다(Follow(R)의 `=`가 빠지고 `$`만 남는다).

**`LALR(1) ⊂ LR(1)`인 이유**: 병합의 부작용인 **reduce-reduce conflict** 때문이다. LR(1)에서는 core가 같아도 lookahead가 다르면 별개 state라 충돌이 없었는데, 병합하면 lookahead가 합쳐져 `A → α .`와 `B → β .`가 같은 칸에서 겹칠 수 있다. 이런 문법은 LR(1)이지만 LALR은 아니다.

```
LR(0) ⊂ SLR ⊂ LALR ⊂ LR(1)
   lookahead 없음 → Follow(전역) → 병합된 문맥별 → 문맥별(정확)
```

---

## 8. Ambiguous Grammar 다루기 *(p.58~63)*

지금까지는 충돌이 "표를 만드는 방식이 부족해서" 생겼다. 이번엔 **문법 자체가 모호해서** 어떤 LR(k)로도 해결이 안 되는 경우다.

```
S → S + S | S · S | id
```
`id + id · id`를 파싱하면 트리가 두 가지로 나온다: `(id + id) · id`, `id + (id · id)`. **stack이 `S + S`이고 입력이 `·`일 때** reduce해서 `S`로 접으면 앞의 형태, shift하면 뒤의 형태가 된다. 둘 다 문법상 합법이라 lookahead를 아무리 늘려도 정해지지 않는, 본질적인 shift-reduce conflict다.

### 해결법 1: 문법을 다시 쓴다 (precedence) *(p.58)*
우선순위가 높은 연산자일수록 트리 **아래쪽**에서 묶여야 하니, 우선순위 단계마다 non-terminal을 하나씩 둔다. (원리: root에 가까운 production일수록 우선순위가 낮은 연산자를 가진다.)
```
S → S + T | T
T → T · id | id
```
`·`는 `T` 층에서 먼저 묶이고 `+`는 그 위 `S` 층에서 묶여, `id + id · id`는 `id + (id · id)` 하나로만 파싱된다.

### 해결법 2: 결합 방향은 재귀 위치로 *(p.59)*
- Left associative: 재귀를 **왼쪽**에 → `S → S - T | T`
- Right associative: 재귀를 **오른쪽**에 → `S → T ^ S | T`
- Non associative: 재귀 없음 → `S → A < A | A`

**예: `S → S - T | T`, `T → num`으로 `1 - 2 - 3` 파싱**

| stack | 남은 입력 | action |
|---|---|---|
| | `1 - 2 - 3 $` | shift |
| `1` | `- 2 - 3 $` | reduce `T → num` |
| `T` | `- 2 - 3 $` | reduce `S → T` |
| `S` | `- 2 - 3 $` | shift `-` |
| `S -` | `2 - 3 $` | shift |
| `S - 2` | `- 3 $` | reduce `T → num` |
| `S - T` | `- 3 $` | **reduce `S → S - T`** ← 첫 번째 `-`가 먼저 reduce됨 |
| `S` | `- 3 $` | shift `-` |
| `S -` | `3 $` | shift |
| `S - 3` | `$` | reduce `T → num` |
| `S - T` | `$` | reduce `S → S - T` |
| `S` | `$` | accept |

**가장 먼저 reduce되는 건 첫 번째 `-`(`1 - 2`)**다. 그 결과 `S`가 `(1-2)`를 대표하고, 그 `S`가 다시 두 번째 `-`의 왼쪽 피연산자로 쓰인다. 트리는 왼쪽으로 깊어진다.
```
        S
      / | \
     S  -  T
   / | \    |
  S  - T    3
  |    |
  T    2
  |
  1
```
즉 `(1 - 2) - 3`이고 left associative다.
- `S → S - T`는 우변의 **맨 왼쪽이 `S`(자기 자신)**라서, 왼쪽 `S`가 이미 reduce된 결과여야 오른쪽 `- T`와 합쳐질 수 있다. 그래서 앞쪽(왼쪽)부터 차례로 묶인다.
- 반대로 `S → T - S`(right recursion)면 오른쪽 `S`가 먼저 완성되어야 하니까, 첫 `-`는 stack에 남은 채 끝까지 shift가 이어지고 마지막 것부터 reduce되어 `1 - (2 - 3)`이 된다.

참고로 stack이 `S - T`이고 lookahead가 `-`인 순간에 shift가 아니라 reduce가 되는 건 충돌이 아니다. `T`는 `num` 하나로만 만들어져 더 shift할 게 없고, state에 `S → S - T .` 하나뿐이라 reduce가 유일하다.

### Dangling Else *(p.60~61)*
모호성의 대표 사례다.
```
S → if Cond then S
  | if Cond then S else S
  | Others
```
입력 `if a then if b then X else Y`에서 `else Y`가 **어느 `if`에 붙는지** 두 해석이 가능하다.
```
(1) if a then ( if b then X else Y )     ← 안쪽 if에 붙음
(2) if a then ( if b then X ) else Y     ← 바깥 if에 붙음
```
stack이 `if a then if b then X`이고 lookahead가 `else`일 때 **reduce(`if b then X`를 `S`로)** 할지 **shift(`else`)** 할지 갈린다. 전형적인 shift-reduce conflict이자 문법 자체의 모호성이다. 프로그래밍 언어의 관례는 "**else는 가장 가까운 then에 붙는다**"(안쪽)이다.

**문법을 고쳐서 해결** (슬라이드 방식)
```
S   → MIF | UIF                          ← 모든 then이 짝지어졌거나(MIF), 아니거나(UIF)
MIF → if Cond then MIF else MIF | Others
UIF → if Cond then S
    | if Cond then MIF else UIF
```
- MIF(matched): then마다 else가 이미 있는 완성된 문장
- UIF(unmatched): else가 없는 then이 남아 있는 문장

핵심은 `else`가 있는 production에서 `then` 바로 뒤에 **MIF만** 허용한다는 점이다. then 안쪽에 else 없는 if(UIF)가 들어오면 그 else는 바깥 if가 아니라 안쪽 if에 붙을 수밖에 없게 강제된다.

**`if a then if b then X else Y` (`X`, `Y`는 `Others`)로 확인**
- **else를 바깥 `if a`에 붙이는 시도** (`if a then (if b then X) else Y`): 바깥 `if`가 else를 가지려면 `MIF → if C then MIF else MIF` 또는 `UIF → if C then MIF else UIF`를 써야 하고, 둘 다 `then` 바로 뒤가 **반드시 `MIF`**다. 그런데 then 뒤의 `if b then X`는 else가 없는 if라서 `MIF`가 될 수 없다(`MIF`는 else 필수 또는 `Others`뿐). `UIF → if C then S`로만 만들어져 **`UIF`**이고, `UIF`는 then 자리에 올 수 없어 파싱이 막힌다. 바깥 `if`에 else를 붙이는 길이 문법에서 사라진 것이다.
- **else를 안쪽 `if b`에 붙이는 경우**: 안쪽 `if b then X else Y`는 `MIF → if C then MIF else MIF`(`X`, `Y`는 `MIF → Others`)로 만들어져 `MIF`가 된다. 바깥은 `UIF → if C then S`로 `S`(= 안쪽 MIF)를 받으면 끝이다. else 없는 바깥 if다.

그래서 결과는 유일하게 `if a then (if b then X else Y)`다. "else가 있는 if의 then 안에는 else 없는 if를 못 넣는다"는 규칙을 non-terminal(MIF/UIF)로 문법에 박아 넣어서, 모호하던 선택지를 문법 차원에서 지운 것이다.

### Automatic Disambiguation: yacc/bison 방식 *(p.62~63)*
문법을 위처럼 복잡하게 다시 쓰는 건 번거롭고 읽기도 어렵다. 그래서 도구들은 **모호한 문법을 그대로 두고, 충돌 지점에서 shift/reduce를 선언으로 정하는** 방식을 지원한다.
```
E → E + E | E * E | E ^ E | num
```
stack이 `E + E`, lookahead가 `*`이면 shift-reduce conflict가 난다. 이를 이렇게 푼다.

**Precedence 규칙**: stack의 맨 위 terminal(여기선 `+`)과 **입력 토큰**(`*`)의 우선순위를 비교한다.
- 입력 토큰이 더 높으면 → **shift** (입력 연산자를 먼저 묶어야 하니까)
- stack 쪽이 더 높으면 → **reduce**

`*`가 `+`보다 높으니 `E + E`를 reduce하지 않고 `*`를 shift해서 `E + (E * E)`로 간다.

**Associativity 규칙** (같은 연산자끼리 만났을 때)
- left associative (예: `*`): stack의 `*`에 더 높은 우선순위 → **reduce 먼저** (`(a*b)*c`)
- right associative (예: `^`): 입력의 `^`에 더 높은 우선순위 → **shift 먼저** (`a^(b^c)`)

슬라이드의 우선순위 순서 예:
```
Input(^) > Stack(^) > Stack(*) > Input(*) > Stack(+) > Input(+)
```
- `^`끼리: Input(^) > Stack(^) → right assoc
- `*`끼리: Stack(*) > Input(*) → left assoc
- `+`끼리: Stack(+) > Input(+) → left assoc
- 다른 연산자끼리: `^` > `*` > `+`

규칙은 하나다. **Input과 Stack 중 순서에서 더 앞(높은) 쪽이 이긴다.** Input이 이기면 shift, Stack이 이기면 reduce.

- **stack `E + E`, 입력 `*`**: Input(`*`) vs Stack(`+`) → `Input(*) > Stack(+)`라서 Input이 이겨 → **shift**. `*`를 올려 `E + E *`로 가고, 결국 `E * E`가 먼저 reduce되어 `E + (E * E)`가 된다.
- **stack `E * E`, 입력 `+`**: Stack(`*`) vs Input(`+`) → `Stack(*) > Input(+)`라서 Stack이 이겨 → **reduce**. `E * E`를 먼저 `E`로 접고 나서 `+`를 처리해 `(E * E) + ...`가 된다.
- 같은 연산자끼리는 `Stack(*) > Input(*)` → reduce → `(a*b)*c`(left), `Input(^) > Stack(^)` → shift → `a^(b^c)`(right)

한 줄로 정리하면 **"먼저 묶여야 하는 쪽에 높은 순위를 준다"**이다. yacc/bison에서는 이를 `%left '+'`, `%left '*'`, `%right '^'` 같은 선언을 위에서부터 낮은 우선순위 순으로 써서 표현한다.

---

## 9. AST 구성 *(p.64~69)*

파싱의 목적은 "맞는 문장인지 확인"만이 아니라, 뒤 단계(Semantic Analysis 등)가 쓸 **AST를 만들어 넘기는 것**이다.

### AST 자료구조 *(p.65)*
객체지향 클래스 계층으로 표현한다.
```
abstract class expr {}
class Add extends expr { expr left, right; }
class Num extends expr { int value; }
```
`1 + 2`는 `Add(Num(1), Num(2))`처럼 **포인터로 연결된 트리**로 메모리에 만들어진다.

### 암묵적 구성 *(p.66)*
LL이든 LR이든 파싱 과정 자체가 parse tree 정보를 담고 있다.
- LL: AST는 **적용된 production들의 열**로 표현
- LR: AST는 **적용된 reduction들의 열**로 표현

그래서 production(또는 reduction)을 적용할 때마다 노드를 하나씩 만들면 AST가 완성된다.

### LL에서 *(p.67)*
non-terminal마다 함수(`parse_S()` 등)가 있고, 그 함수가 자식 non-terminal 함수를 호출해 받은 결과로 새 노드를 만들어 return한다.
```
expr parse_S() {
    switch (token) {
      case num: case '(':
        expr child1 = parse_E();
        expr child2 = parse_S'();
        return new S(child1, child2);
      default: ParseError();
    }
}
```

### LR에서 *(p.68~69)*
stack에 기호만 쌓는 게 아니라, **각 non-terminal 옆에 그 non-terminal에 대응하는 subtree도 같이 저장**한다. reduce할 때 우변의 subtree들을 꺼내 새 노드를 만들고, 그 노드를 LHS의 subtree로 다시 push한다. 이 코드가 **semantic action**이다. `S → E + S`를 reduce할 때:
```
$3 = pop_stack();   // S  (우변 3번째 기호의 subtree)
$2 = pop_stack();   // +
$1 = pop_stack();   // E  (우변 1번째 기호의 subtree)
$$ = new S($1, $3); // 새 노드 (LHS의 subtree)
push_stack($$);
```
`$1, $2, $3`은 우변 기호의 순서, `$$`는 좌변이다. `+`(`$2`)는 노드 종류(`Add`)가 이미 담고 있어 노드에 안 쓰이고 버려진다.

stack이 `... E[Add(Num1,Num2)]  +  S[Num3]`일 때 reduce하면 우변이 3개라 **3개를 pop하고 1개를 push**한다.
```
pop:   $3 = S[Num(3)],  $2 = +,  $1 = E[Add(Num(1), Num(2))]

Before:  ... E[Add(1,2)]   +   S[Num(3)]
After :  ... S[Add( Add(1,2), Num(3) )]
```
`1 + 2`를 만든 subtree와 `3`이 합쳐져 **`Add(Add(Num1, Num2), Num3)`** 하나의 subtree가 되고, 이게 `S`와 한 쌍으로 stack에 올라간다. 이 `S`가 이후 reduce에서 다시 `$1`이나 `$3`이 되어 위로 계속 합쳐지고, 끝까지 가면 stack에 start symbol 하나와 **전체 AST의 root**가 남는다. 파싱이 끝나는 순간 AST가 같이 완성되는 방식이다.

(슬라이드 예시는 설명용으로 `new S(...)` 노드를 만들었지만, 실제 컴파일러에서는 보통 production마다 `Add`, `Num` 같은 의미 있는 노드를 직접 만들어 non-terminal 노드는 AST에 남기지 않는다.)

---

## 핵심 요약

- **Bottom-up(LR)**은 rightmost derivation을 역순으로 추적하며 shift/reduce 두 액션으로 동작한다. 어떤 액션을 고를지가 Action Selection Problem이고, 충돌은 shift-reduce와 reduce-reduce 두 종류다.
- **item**(production + 점)은 "어디까지 봤는지"를 나타내는 책갈피다. closure(ε-closure와 같은 발상)와 goto로 DFA를 만들고, 점이 끝에 온 state가 reduce state다. **dummy production** `S' → S $`는 accept 판정용 장치다.
- reduce 뒤에는 pop해서 **드러난 top state**와 LHS로 goto를 조회해 push한다.
- **LR(0)**: lookahead 없이 reduce state의 모든 칸에 reduce를 채운다. 한 state에 shift와 reduce(또는 reduce 둘)가 섞이면 충돌한다.
- **SLR(1)**: reduce를 Follow(X)로 제한한다. 문법 전체의 전역 정보라 문맥상 불가능한 reduce까지 허용해 충돌이 남을 수 있다.
- **LR(1)**: item에 문맥별 정확한 lookahead(`First(βλ)`)를 붙인다. 정밀하지만 state가 폭증한다.
- **LALR(1)**: core가 같은 LR(1) state를 병합한다. state 수는 SLR 수준이고, 병합 부작용은 reduce-reduce만 생긴다. bison이 사용한다.
- 포함 관계: `LR(0) ⊂ SLR ⊂ LALR ⊂ LR(1)`, LL(1)은 일부만 겹친다.
- **모호한 문법**은 precedence(non-terminal 계층), associativity(재귀 방향), dangling-else(MIF/UIF)로 문법을 고치거나, yacc/bison처럼 precedence 선언으로 shift/reduce를 자동 결정한다.
- **AST**는 파싱 중 암묵적으로 구성된다. LL은 production 함수의 반환값으로, LR은 reduce 시 semantic action(`$1,$2,…→$$`)으로 만든다.
