# Chapter 5: Semantic Analysis — 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*수업일: 2026-10-16 / 대응 정리노트: `notes/chapter-5.md`*

> `p.N`은 슬라이드 우측 하단 쪽번호 기준이다.

**이번 수업의 목표**: 프로그램이 lexical/syntax를 통과해도 걸리는 오류(선언·타입)를 symbol table과 inference rule로 어떻게 검사하는지 설명할 수 있게 된다.

---

## 0. 선수 개념 복습 *(p.2~5)*

- Lexical analysis: RE로 **명세**, DFA로 **인식**, RE → NFA → DFA(Lex)로 **자동화**
- Parser: CFG로 **명세**, parse tree/AST로 **인식**, top-down/bottom-up parsing(bison)으로 **자동화** (LL(1), LR(0) 등은 이 parsing 방식)
- **Parse tree**는 문법 규칙(derivation)을 그대로 펼친 트리라 괄호나 `E → T` 같은 중간 노드까지 다 들어간다. **AST**는 의미 없는 노드를 쳐내고 연산 구조만 남긴 트리다. `1 + 2 * 3`이면 `Add(1, Mul(2, 3))`.
- 아래 코드는 토큰도 정상이고 문법도 정상이라 lexical/syntax를 **통과**한다.
  ```c
  int a;
  int a;
  b = a;
  ```
- symbol table에는 identifier의 이름, 종류(변수/함수/인자), 타입, scope 같은 정보가 들어간다.

## 1. Semantic Analysis란 *(p.6~7)*

**Semantic analysis는 문법적으로 올바른 프로그램이 선언, 타입, 상속 같은 "구성 요소 사용 규칙"을 지키는지 검사하는 단계다.**

- 모든 identifier가 **사용 전에 선언**됐는가?
- **Type**이 맞는가?
- **Inheritance** 관계가 올바른가?
- 각 class / method가 **한 번만 정의**됐는가?

**Class Exercise (p.7)** — 분류:
```c
(a) int a; int a;     // semantic (같은 블록 중복 선언)
(b) b = a;            // semantic (선언 없이 사용)
(c) in$ a;            // lexical  (허용되지 않는 문자 $)
(d) 1 int x;          // syntax   (토큰 순서가 문법에 안 맞음)
```

## 2. 분석의 두 범주 *(p.8~9, 32)*

- **Scopes**: identifier의 **선언과 사용**을 다룬다 (p.10~31)
- **Types**: 변수, statement, expression의 **값의 타입**을 다룬다 (p.33~79)

## 3. Scope Analysis *(p.10~31)*

### 3-1. 예제로 보는 scope 결정 *(p.15~17)*
```c
int x;                          // (A)

void f (int m) {
    float x, y;                 // (B)
    { int i, j;  x = 1; }       // x = 1 → (B)
    { int x, k;  x = 2; }       // (C) int x. x = 2 → (C)
}

int g (int n) {
    char t;
    x = 3;                      // x = 3 → (A)
}
```
- `{ int x, k; y = 2; }` → 안쪽 블록에 없어도 바깥 함수 f의 `float y`에서 찾아져서 **가능**
- `{ int x, k; i = 2; }` → `i`는 형제 블록에만 있어서 올라가도 못 찾는다 → **Undefined 에러**

**규칙 한 문장**: Identifier의 scope는 그 선언이 속한 lexical scope이고, 사용된 identifier는 현재 block에서 시작해 바깥 block으로 올라가며 처음 만나는 선언으로 결정된다. 끝까지 못 찾으면 Undefined 에러다.

### 3-2. Lexical scope 종류 *(p.10~11)*
**Lexical scope**는 프로그램의 텍스트상 영역이다 (statement block, function body, source file, whole program 등).
- `extern int a;` → 전체 프로그램
- 파일 수준 `int b;` → 현재 파일
- `{ int c; { int d; } }` → c는 바깥 `{}`, d는 안쪽 `{}`
- 함수 매개변수 `int foo(int n)` → 함수 `foo`의 `{}`
- label (`goto lab; … lab:`) → **함수 scope**

### 3-3. Symbol Table *(p.12~14)*
identifier의 속성(scope, type)을 저장할 **environment = symbol table**이 필요하다. entry 하나는 이름 + 추가 정보다. 예: `foo`(kind: func, type: int → int), `m`(arg, int), `tmp`(var, char).

scope 계층마다 table을 하나씩 만든다. 위 예제는:
```
Global : x(var,int), f(func, int→void), g(func, int→int)
 ├ f   : m(arg,int), x(var,float), y(var,float)
 │  ├ f.0 : i, j (var,int)
 │  └ f.1 : x, k (var,int)
 └ g   : n(arg,int), t(var,char)
```
같은 이름 `x`가 여러 table에 있어도 충돌하지 않는다. 현재 table에서 시작해 위로 올라가며 찾으니까 이름 충돌이 자동으로 해결된다.

### 3-4. Symbol Table 연산 *(p.18)*
| 연산 | 의미 |
|---|---|
| insert_scope | 새 중첩 scope 시작 |
| exit_scope | 현재 scope 종료 |
| find_symbol(x) | 계층 전체에서 x 검색 |
| add_symbol(x) | 현재 table에 x 추가 |
| check_scope(x) | **현재 scope에만** x가 정의돼 있는지 확인 (optional) |

table은 parsing 중에 만들 수도 있고 AST를 만든 뒤에 만들 수도 있다. 단, semantic analysis 전에는 만들어져 있어야 한다.

**확인 질문 — `check_scope`와 매개변수**
```c
void foo(int a) {
    int a;
}
```
에러가 **안 난다**. 슬라이드(C-Minus) 방식에서는 함수 선언 시 `insert_scope()`로 func scope가 만들어져 매개변수 `a`가 거기 들어가고, 본문 compound statement에 들어가면 `insert_scope()`가 한 번 더 호출돼 func.0이 만들어진다. 안쪽 `int a;`는 func.0에서 `check_scope(a)`를 하는데 func.0은 비어 있으니 통과한다. 매개변수와 본문 지역변수는 **서로 다른 층위**고, 안쪽 `a`가 매개변수를 가린다(shadowing). (실제 C는 매개변수와 본문 최상위 블록을 같은 scope로 취급해서 저 코드가 에러다.)

### 3-5. AST 순회로 Symbol Table 만들기 *(p.19~28)*
```
Program
 ├ FuncDecl func1
 │   ├ VarDecl var1          (매개변수)
 │   └ CompoundStmt
 │        ├ VarDecl var1
 │        └ VarDecl var2
 ├ VarDecl var1              (전역)
 └ FuncDecl func2
     └ VarDecl var3          (매개변수)
```
1. func1: `check_scope` → `add_symbol(func1)` (Global) → `insert_scope()` (func1 scope) *(p.19)*
2. 매개변수 var1: `check_scope`, `add_symbol` (func1 table) *(p.20)*
3. CompoundStmt 진입: `insert_scope()` (func1.0) *(p.21)*
4. 내부 var1, var2: 각각 `check_scope`, `add_symbol` (func1.0) *(p.22~23)*
5. CompoundStmt 끝: `exit_scope()` *(p.24~25)*
6. 전역 var1: Global에 추가 (func1 안의 var1과 다른 scope라 충돌 없음) *(p.26)*
7. func2: Global에 추가, `insert_scope()` *(p.27)*, 매개변수 var3 추가 *(p.28)*

핵심: **중첩 구조 진입 시 `insert_scope`, 이탈 시 `exit_scope`, 선언마다 `check_scope` → `add_symbol`.**

### 3-6. 함수 선언과 사용 순서 *(p.29~31)*
- **C-Minus**: 사용 전에 선언해야 한다.
- **Python 등**: 선언 전에도 사용 가능하다.
- **C**: 따로 **forward declaration**(`int boo(int z);`)을 두면 가능하다.

`boo`가 뒤에 정의된 `foo`를 호출하는 경우, C-Minus에서는 `boo`를 검사하는 시점에 `foo`가 table에 **없어야** 한다.
- **Option #1**: table을 **먼저 전부 만든** 뒤 scope analysis
- **Option #2**: table 생성과 scope analysis를 **동시에** 진행. 그 시점까지 선언된 것만 있는 **부분 table**로 검색

**확인 질문**: C-Minus 규칙을 지키려면 **Option #2**. 미리 다 만들어두면(Option #1) 뒤에 선언된 `foo`까지 table에 있어서 "사용 전 선언" 위반을 못 잡는다. Python처럼 선언 전 사용을 허용하는 언어는 Option #1이 맞다.

## 4. Type Analysis *(p.33~79)*

### 4-1. Type checking vs Type inferencing *(p.33~34)*
- **Type checking**: 프로그램 구성 요소 간 타입 일관성을 보장하는 규칙 집합. 정수 변수와 문자열 변수를 더하면 안 되는 식.
- **Type inferencing**: 빠진 타입 정보를 채우는 것. `int + int`의 결과는 `int`.
- 이 수업에서는 두 용어를 혼용한다.

checking이 검사하는 항목:
- 연산자(`+`, `==`, `[ ]`)가 올바른 타입의 피연산자를 받는가
- 함수 호출의 인자 개수와 타입이 맞는가
- return 값이 반환 타입과 일치하는가
- 대입에서 RHS 값이 LHS 변수 타입과 호환되는가
- class member를 올바르게 접근하는가

### 4-2. 언어의 세 종류 *(p.35~38)*
- **Statically typed**: type checking 대부분이 **컴파일 시간**에 수행 (C, Java)
- **Dynamically typed**: 대부분이 **실행 중**에 수행 (Python, Lisp, Perl)
- **Untyped**: type checking 없음 (machine code)

dynamic은 매 실행마다 검사 overhead가 생겨서, 이를 줄이려고 프로세서를 바꾸는 연구까지 있다(*Typed Architectures*, 이 수업 범위는 아님, p.36~37). static은 런타임에 추가 검사 명령이 필요 없어서 overhead가 크게 줄고, 컴파일 시점에 안전함을 보장한다. 다만 Union, void pointer 때문에 현대 언어는 static과 dynamic을 둘 다 필요로 한다 (p.38).

### 4-3. Type이란 *(p.39~40)*
**Type은 값의 집합과 그 값들에 허용되는 연산의 집합에 대한 기술이고, 본질적으로 값에 대한 predicate다.** `int x`는 `-2^31 ≤ x < 2^31`.

- **Type expression**: 프로그램에서 가능한 타입을 기술하는 표현 (`int`, `char*`, `array[]`, `object`)
- **Type system**: 언어 구성 요소(AST의 expression, statement node)에 타입을 정의하는 체계

type expression 만드는 방법: ① **Basic types**(primitive/ground types: `int`, `char`, `double`) ② **Type constructors**(array, structure/object, pointer) ③ **Type aliases** ④ **Function types**

### 4-4. Type 비교 구현 *(p.41)*
- **Option 1**: `Equals(T1, T2)`로 두 type tree를 비교. 객체지향 언어는 **subtyping `SubtypeOf(B, A)`**도 필요. B가 A의 subtype이라는 건 A에 호출할 수 있는 모든 함수를 B에도 호출할 수 있다는 뜻 (Bool은 Int의 subtype).
- **Option 2**: **각 타입마다 유일한 객체**. `array[int]`가 어디서나 같은 객체로 resolve되니까 `==`로 비교 가능하고 더 빠르다.

### 4-5. 타입 동치성 *(p.42)*
```c
typedef struct cs_student { int number; char name[20]; int grade; } cs_stu;
typedef struct ds_student { int number; char name[20]; int grade; } ds_stu;
```
- **Structural equivalence**: 구조(메모리 레이아웃)가 같으면 같은 타입 → `cs_stu`와 `ds_stu`는 **같은 타입**, `s = t` 허용
- **Name equivalence**: 타입 이름이 같아야 같은 타입 → **다른 타입**

**확인 질문**: Python의 `"a" + 1`은 dynamically typed라 type checking이 실행 중에 이뤄지고, 그 줄이 실행되는 순간 `TypeError`가 난다.

### 4-6. Type checking 방법론 *(p.43~51)*
Type checking은 expression에 올바른 타입이 주어졌는지 검증하는 것(예: `int + int`가 `int`인지). 방법은 둘이다.
- **Option 1: SDD(Syntax-Directed Definition)**: parsing 중에 type checking
- **Option 2**: AST를 먼저 만들고 node를 재귀 순회하며 type checking

**SDD** *(p.45~46)* — CFG의 production마다 semantic rule을 붙인다.
```
L → E $       : L.type = E.type
E → E1 + T    : E.type = if (E1.type == T.type) E1.type else TypeCheckError("+")
E → T         : E.type = T.type
T → T1 * F    : T.type = if (T1.type == F.type) T1.type else TypeCheckError("*")
```
bison:
```
L : E EOF   {$$.type = $1.type;};
E : E1 + T  {if ($1.type == INT && $3.type == INT) $$.type = INT;
             else TypeCheckError("+");};
```
production을 reduce할 때마다 그 규칙이 실행되면서 자식들의 type으로 부모의 type을 계산한다.

**AST 순회** *(p.48)*
```c
static void traverse(TreeNode *t,
        void (*preProc)(TreeNode *),
        void (*postProc)(TreeNode *))
{ if (t != NULL)
  { preProc(t);
    for (i = 0; i < MAXCHILDREN; i++)
        traverse(t->child[i], preProc, postProc);
    postProc(t);
    traverse(t->sibling, preProc, postProc);
  }
}
```
순서는 preProc → 자식들 재귀 → postProc → sibling. type checking은 **postProc에서** 한다.

node별 `type_inference` *(p.50~51)* (AST: `Add(Add(Num(1), Num(2)), Num(3))`)
- `Num`: 숫자면 `Int` 반환, 아니면 `TypeCheckError()`
- `Add`: `t1 = left.type; t2 = right.type; if (t1 == Int && t2 == Int) return Int; else TypeCheckError("+")`

**순회 중 주의점** *(p.49)*
- type 선언이나 class 정의(`class_defn : CLASS ID {decls}`)는 symbol table에 새 identifier와 타입을 추가한다.
- **Forward reference**(`class A { B b; }`가 `class B {...}`보다 먼저 나옴)가 있으면 합법적인 이름을 먼저 모으기 위해 AST를 **여러 번(multiple passes)** 순회한다.

**확인 질문 답**
1. **왜 postProc인가**: `Add`의 타입은 자식 `left`, `right`의 타입이 먼저 정해져야 계산할 수 있다. preProc은 자식을 방문하기 전에 실행되니까 이 시점에 `left.type`, `right.type`은 비어 있다. postProc은 자식 재귀가 끝난 뒤라 타입이 채워져 있다. 그래서 AST를 bottom-up으로 올라가며 계산한다.
2. **Forward reference**: `class A { B b; }`를 처리하는 시점에 `B`는 아직 table에 없다. 한 번만 순회하면 합법적인 타입을 Undefined로 오해해 에러를 낸다. 그래서 1차 순회에서 class 이름을 전부 모으고, 2차 순회에서 검사한다. Scope의 C-Minus 규칙(사용 전 선언)과는 반대 상황으로, 클래스 멤버 타입은 선언 순서와 무관하게 쓸 수 있어야 하는 언어가 많아서 Option #1(미리 다 모으기)에 가까운 처리가 필요하다.

### 4-7. Type rule 명세: Inference Rule *(p.52~64)*
명세 도구: lexical analysis → regular expression, syntax analysis → CFG, **type checking → inference rule(추론 규칙)**.

**형태** *(p.53~55)*: **Inference rule은 가설(hypotheses)이 모두 참이면 결론(conclusion)이 참이라는 형식 규칙이다.**
- 기호: `Λ`는 and, `⟹`는 if-then, `x : T`는 "x는 타입 T를 가진다", `⊢`는 "…가 증명 가능하다"
- 풀어 쓰면 `e1 : int Λ e2 : int ⟹ e1 + e2 : int`
- 관례적 표기는 가설을 분자에, 결론을 분모에, 오른쪽에 [Rule name]
```
⊢ e1 : int     ⊢ e2 : int
──────────────────────────  [Int Add]
      ⊢ e1 + e2 : int
```

**Soundness와 type judgement** *(p.56~58)*
- `e : T`는 "e가 타입 T의 **sound한 expression**"이라는 type judgement. 어떤 T에 대해 `e : T`면 e는 **typable**. (`2 : int`, `True : bool`, `2 * (3 + 4) : int`)
- **Statement도 expression이 될 수 있다.** Python `x = 2 if (b) else 3`. 값이 없는 statement는 **unit type(void)**을 가져서 `S : void`.
- 규칙이 **sound**하다는 건 `⊢ e : T`일 때 e가 실제로 T로 평가된다는 뜻. sound한 규칙만 쓰되 더 좋은 규칙이 있다 (`i is an integer literal ⊢ i : object`도 sound하지만 `int`보다 정보가 약함).

```
i is an integer literal
───────────────────────  [Int]
        ⊢ i : int
```

**Proof tree** *(p.59~60)*: `1 + 2`
```
1 is int literal      2 is int literal
──────────────        ──────────────
 ⊢ 1 : int [Int]       ⊢ 2 : int [Int]
 ───────────────────────────────────── [Int Add]
              ⊢ 1 + 2 : int
```
- **Type checking = `e : T`를 증명하는 과정**
- proof tree는 **AST 구조를 따른다.** AST node 하나당 규칙 하나.
- AST를 **bottom-up(post-processing)**으로 순회한다. 각 node의 가설은 하위 expression의 타입 증명, 결론은 그 node의 타입. (앞의 postProc 순회와 같은 구조)

**더 많은 규칙** *(p.63~64)*
- `⊢ false : bool` [False], `⊢ new T : T` [New], `⊢ e : bool ⟹ ⊢ !e : bool` [Not]
- **If-then-else**: `⊢ e1 : bool`, `⊢ e2 : T`, `⊢ e3 : T` ⟹ `⊢ if e1 then e2 else e3 : T`
- **If-then**: `⊢ e1 : bool`, `⊢ e2 : T` ⟹ `⊢ if e1 then e2 : void` (값을 쓰려는 걸 막는다)

**연습 (p.65~68)**

(1) while:
```
⊢ e1 : Bool     ⊢ e2 : T
─────────────────────────────  [while]
 ⊢ while (e1) { e2 } : Void
```
조건 `e1`은 `Bool`, 본문 `e2`는 아무 타입 `T`, while 전체는 값이 없으니 `Void`.

(2) `if iszero 0 then 0 else pred 0 : int`
```
 ⊢ 0 : int           ⊢ 0 : int          ⊢ 0 : int
 ──────────── [iszero] ───────────       ────────── [pred]
 ⊢ iszero 0 : bool    ⊢ 0 : int          ⊢ pred 0 : int
 ───────────────────────────────────────────────────── [if-then-else]
        ⊢ if iszero 0 then 0 else pred 0 : int
```
조건 `iszero 0`은 `bool`, then 분기 `0`과 else 분기 `pred 0`이 둘 다 `int`라서 `T = int`.

(2') `pred succ iszero pred 0 : int` (p.67~68)

이 연습에서 `[succ]`은 가설이 `⊢ e1 : bool`, 결론이 `⊢ succ e1 : int`다 (슬라이드 p.67에서 확인). 그래서 이 식은 type error가 아니라 정상적으로 증명된다.
```
⊢ 0 : int
⊢ pred 0 : int                   [pred]
⊢ iszero pred 0 : bool           [iszero]
⊢ succ iszero pred 0 : int       [succ]   (bool을 받아 int)
⊢ pred succ iszero pred 0 : int  [pred]
```
"규칙에 적힌 가설을 그대로 따라 proof tree를 만든다"가 요령이다.

### 4-8. Type Environment *(p.69~75)*
**문제** *(p.69)*: 변수 참조 `x;`의 타입을 어떻게 정의할까? `⊢ x : ?` [Var]에서는 x만 봐서는 타입을 알 수 없다. 규칙에 더 많은 정보를 줘야 한다.

**정의** *(p.70)*: **Type environment `O`는 free variable의 타입을 제공하는 함수(object identifier → type)이고, 본질적으로 symbol table이다.**
- 변수가 expression 안에서 정의되지 않으면 그 expression에서 **free**. `x`는 x가 free, `x+y`는 x, y가 free, `int z = x`는 x만 free.
- **`O ⊢ e : T`**: 변수들이 O가 주는 타입을 가진다고 가정할 때 e의 타입이 T임이 증명된다.

**예시** *(p.72)*: `int x; int y; … z = x + y;`
```
O(x) = int          O(y) = int
───────────         ───────────
O ⊢ x : int [Var]   O ⊢ y : int [Var]
───────────────────────────────────── [Int Add]
          O ⊢ x + y : int
```
Var 규칙은 `O(x) = T ⟹ O ⊢ x : T`.

**선언이 있는 경우** *(p.73)*: `O[T/x]`는 O에 "x : T"를 추가(또는 덮어쓴) environment. `O[T/x](x) = T`, `O[T/x](y) = O(y)` (x ≠ y). symbol table의 entry를 추가/수정하는 것과 같다.
```
O[T1/i] ⊢ exp : T2
──────────────────────────────
O ⊢ for(T1 i = 0;;) { exp } : T2
```

**Class 환경** *(p.74~75)*
- **`O_c`**: class 전체 scope. class C의 모든 attribute `x : T`가 `O_c(x) = T`. `O_c(x1) = T1`, `O_c ⊢ exp : T1 ⟹ O_c ⊢ x1 = exp : T1`
- **`M`**: method를 기술하는 별도 scope. `M(C, f) = (T1, …, Tn, Tn+1)`은 class C의 method f가 `f(x1:T1, …, xn:Tn)`이고 반환 타입이 `Tn+1`.
  ```
  O,M ⊢ e0 : T0   O,M ⊢ e1 : T1 … O,M ⊢ en : Tn   M(T0, f) = (T1,…,Tn,Tn+1)
  ─────────────────────────────────────────────────────────────────────────
                 O,M ⊢ e0.f(e1, …, en) : Tn+1
  ```

**확인 질문 답**
1. `O`는 **symbol table**이다. `O(x) = int`는 `find_symbol(x)`에 해당하고, scope 계층을 위로 올라가며 찾는 규칙도 `O`에 들어 있다.
2. `exp` 안에서 `i`를 쓰면 `i`의 타입을 알아야 하는데 원래 `O`에는 `i`가 없다. 그래서 for문 헤더의 선언을 반영해 `i : T1`을 추가한 환경 `O[T1/i]`로 검사한다. 코드로는 for 블록 진입 시 `insert_scope()` 후 `add_symbol(i)`를 한 상태와 같고, 블록을 나가면 `exit_scope()`로 `O`로 돌아오므로 `i`는 for 밖에서 안 보인다.

### 4-9. Subtyping *(p.76~79)*
**Subtype 관계 `X ≤ Y`는 X가 Y의 subtype이라는 뜻이고, 다음 세 성질을 가진다.**
- `X ≤ X` (반사)
- `X ≤ Y` (X가 Y를 상속)
- `X ≤ Y`이고 `Y ≤ Z`이면 `X ≤ Z` (전이)

예: `float ≤ double`, `char ≤ int`

**더 관대한 규칙** *(p.76)*: 초기값 타입이 선언 타입과 정확히 같아야 하던 것을 완화한다.
```
O ⊢ y : T0     T0 ≤ T1     O[T1/x] ⊢ exp : T2
──────────────────────────────────────────────
     O ⊢ for(x : T1 = y) { exp : T2 }
```

**Subtyping과 type conversion** *(p.77)*: `char ≤ int ≤ float ≤ double`
- **subtype → supertype**은 **암시적 변환** 가능 (char→int, int→float, float→double)
- **supertype → subtype**은 **명시적 변환** 필요
- B가 A의 subtype이면 A에 쓸 수 있는 모든 함수를 B에도 쓸 수 있으므로 B 값을 A 자리에 넣어도 안전하다.

**lub (least upper bound)** *(p.78)*: `if e0 then e1 else e2`에서 e1과 e2의 타입이 다르면 둘을 포괄하는 가장 작은 supertype을 결과 타입으로 쓴다.
- `lub(X, Y) = Z`: ① `X ≤ Z`이고 `Y ≤ Z` ② 임의의 `Z'`가 `X ≤ Z'`이고 `Y ≤ Z'`이면 `Z ≤ Z'`
```
O ⊢ e0 : bool   O ⊢ e1 : T1   O ⊢ e2 : T2
─────────────────────────────────────────
 O ⊢ if e0 then e1 else e2 : lub(T1, T2)
```

**Inheritance와 subtyping** *(p.79)*: subtyping을 가능케 하는 일반적 방법은 상속(overriding이 없다고 가정).
```
class A
class B inherits A
class C inherits A
class D inherits C
```
- `lub(B, D) = A`
- `lub(C, D) = C` (D ≤ C라서 한쪽이 다른 쪽의 subtype이면 lub는 위쪽 타입)
- `lub(B, C) = A` (B와 C는 형제 관계라 공통 부모 A뿐)

**확인 질문 답**
1. `if cond then (char) else (double)`의 결과 타입은 **double** (`char ≤ int ≤ float ≤ double` 체인).
2. `lub(C, D) = C`, `lub(B, C) = A`.
3. `int x = 3.5;`는 `double → int`, 즉 supertype → subtype 방향이라 **명시적 변환**이 필요하다 (소수부 손실 위험).

## 5. Static Scoping vs. Dynamic Scoping *(p.80~84)*

- **Static scoping**: symbol table을 정적으로 만들고, 그 table로 변수가 어디서 선언됐는지 추론한다. 사용이 **컴파일 시간**에 결정된다.
- **Dynamic scoping**: 변수의 scope가 **함수 호출에 따라 동적으로** 바뀐다. 사용이 **call stack(가장 가까운 선언)**에 기반한다.

```c
int x = 50;

int func2() { return x; }

int func1() {
    int x = 10;
    int y = func2();
    return y;
}

int main() { func1(); }
```
- **Static scoping** *(p.82)*: `func2`의 `x`는 `func2`가 **선언된 위치** 기준이라 Global `x = 50`을 가리킨다. → func1은 **50** 반환.
- **Dynamic scoping** *(p.83)*: `func2`에 `x` 선언이 없으면 call stack을 거슬러 올라간다. main → func1(x=10) → func2 순서로 호출됐으므로 func1의 `x = 10`을 찾는다. → func1은 **10** 반환.

**Perl** *(p.84)*은 둘 다 지원한다.
- `local $x`: 변수가 call stack에서 보임 (dynamic)
- `my $x`: 변수가 그 scope 안에서만 쓰임 (static)
- 같은 코드에서 `func1`이 `local $x = 10`이면 func2는 10을, `my $x = 10`이면 50을 본다.

---

## 핵심 요약

- **Semantic analysis**는 문법적으로 맞는 프로그램이 선언·타입·상속 규칙을 지키는지 검사하며, **Scope**와 **Type** 두 갈래로 나뉜다.
- **Scope**: 사용된 identifier는 현재 scope에서 시작해 바깥으로 올라가며 처음 만나는 선언으로 결정된다. scope 계층마다 symbol table을 두고 `insert_scope / exit_scope / find_symbol / add_symbol / check_scope`로 AST를 순회하며 만든다. C-Minus는 사용 전 선언이라 table 생성과 scope analysis를 동시에(Option #2) 한다.
- **Type**은 값의 집합과 허용 연산의 집합이다. static typing은 컴파일 시간에 대부분 검사해 런타임 overhead가 없다. 동치성은 structural(구조)과 name(이름) 두 방식이 있다.
- **Type checking 구현**은 SDD(parsing 중) 또는 AST를 postProc(bottom-up)으로 순회하는 방식이다. forward reference가 있으면 multiple passes가 필요하다.
- **Inference rule**(가설 ⟹ 결론)로 type을 명세하고, type checking은 AST 구조를 따라 `e : T`를 증명하는 proof tree를 만드는 과정이다. 변수 타입은 **type environment `O`(= symbol table)**가 제공하며 `O[T/x]`는 선언 추가를 뜻한다.
- **Subtyping** `≤`로 암시적 변환(subtype → supertype)을 허용하고, 분기 타입이 다르면 **lub**를 쓴다.
- **Static scoping**은 선언 위치(컴파일 시간), **Dynamic scoping**은 call stack(실행 시간)으로 변수를 결정한다. Perl은 `my`(static)와 `local`(dynamic) 둘 다 지원한다.

---

## 수업에서 다룬 섹션

1. 복습: Specification / Recognition / Automation
2. Semantic Analysis란
3. 분석의 두 범주 (Scope / Type)
4. Scope Analysis (Lexical scope, Symbol Table, 계층 표현, 예제, 연산, AST 순회로 생성, 함수 선언 순서, 생성 시점)
5. Type Analysis (Type checking/inferencing, 언어 종류, Type이란, 비교 구현, 동치성, SDD / AST 순회, Inference Rule, Proof tree, Type Environment, Subtyping, lub)
6. Static vs Dynamic Scoping
