# Chapter 5: Semantic Analysis

*2026 Fall, Hunjun Lee*

> 슬라이드 우측 하단 쪽번호가 PDF 페이지 순서와 같다. 이 강의는 lexical/syntax analysis 다음 단계인 **Semantic Analysis**를 **Scope(식별자 선언·사용)**와 **Type(값/식의 타입)** 두 갈래로 나눠 다루고, 마지막에 Static vs Dynamic scoping을 덧붙인다.

## 1. 복습: Specification / Recognition / Automation *(p.2~5)*

- Compiler 구조: Source Code → **Front end**(Lexical Analysis(Scanner) → Syntax Analysis(Parser) → **Semantic Analysis**) → Code Generation-1 / Control·DataFlow Analysis / Optimization (machine independent) → Code Generation-2 → Assembly Code (machine dependent, back end). 전 과정에서 **Context & Symbol Table & CFG**와 상호작용 *(p.2, 5)*
- **Lexical analysis의 3대 요소** *(p.3)*
  - Specification: lexical pattern을 어떻게 명시? → **Regular expression (RE)**
  - Recognition: 어떻게 인식? → **DFA**
  - Automation: RE에서 DFA를 어떻게 생성? → Thompson's construction(RE → NFA), Subset construction(NFA → DFA), 자동 생성 도구 **Lex**
- **Parser의 3대 요소** *(p.4)*
  - Specification: 유효한 token 시퀀스를 어떻게 명시? → **CFG**
  - Recognition → **Parse tree와 AST**
  - Automation → **Top-down / Bottom-up parsing**, 자동 생성 도구 **bison**

## 2. Semantic Analysis란 *(p.6~7)*

- lexical/syntax analysis를 통과해도 **여전히 오류가 있을 수 있다** — 변수, 객체, 함수의 올바른 사용 등
- Semantic analysis는 프로그램이 **프로그래밍 구성 요소의 사용에 관한 규칙**을 만족하는지 확인한다
  - 모든 identifier가 **사용 전에 선언**되었는가?
  - **Type**은 맞는가?
  - **Inheritance 관계**는 올바른가?
  - 각 class / method가 **한 번만 정의**되었는가? 등
- **Class Exercise** *(p.7)*: 주어진 코드 조각의 오류를 **lexical / syntax / semantic / correct**로 분류하라 (예: 같은 블록에서 `int a;`를 두 번 선언, `a = 1.0;`, 선언 없이 `b = a;`, 함수 이름에 대입 `foo = 3;`, `in$ a;` 같은 잘못된 문자, `1 int x;` 같은 문법 오류 등 — 정답은 슬라이드에 없음)

## 3. 분석의 두 범주 *(p.8~9, 32)*
- **Scopes**: identifier의 **선언과 사용**을 특징짓는다
- **Types**: 변수, statement, expression 등에 해당하는 **값의 타입**을 특징짓는다
- 이 순서로 진행: p.10~31 Scope, p.33~79 Type, p.80~84 Static vs Dynamic scoping

## 4. Scope Analysis *(p.10~31)*

### Scope 정보 *(p.10~11)*
- **Lexical scope**: 프로그램의 **텍스트상 영역** — statement block, function body, method body, source file, whole program 등
- **Identifier의 scope**: 그 identifier의 선언이 가리키는 lexical scope
  - 변수의 정의는 **그것을 포함하는 block/함수에서 먼저 찾고, 실패하면 바깥 block으로** 올라가며 찾아 결정
- 예시 *(p.11)*:
  - `extern int a;` → scope a: **전체 프로그램**
  - 파일 수준의 `int b;` → scope b: **현재 파일**
  - `{ int c; { int d; } }` → scope c: 바깥 `{~}`, scope d: 안쪽 `{~}`
  - 함수 매개변수 `int foo(int n)` → scope n: **함수 `foo`의 `{~}`**
  - `goto lab; … lab: i++;` → **label은 함수 scope** (conventional labels have function scope)

### Symbol Table *(p.12)*
- semantic check는 프로그램 안 identifier의 **속성(scope, type)**을 참조한다 → identifier 정보를 저장할 **environment = symbol table**이 필요
- 각 entry = identifier **이름 + 추가 정보**
  - 예: `foo`(Kind: func, Type: int → int), `m`(arg, int), `n`(arg, int), `tmp`(var, char)

### Symbol Table로 scope 표현 *(p.13~14)*
- **lexical scope 계층에 따라** symbol table을 만든다. 각 table은 그 scope에서 선언된 symbol을 담는다
- 예시 *(p.13)*:
  ```c
  int x;
  void f (int m) {
      float x, y; …;
      {int i,j; …;}
      {int x,k; …;}
  }
  int g (int n) { char t; …; }
  ```
  - Global: x(var, int), f(func, int → void), g(func, int → int)
  - Function f: m(arg, int), x(var, float), y(var, float)
  - f.0: i, j (var, int) / f.1: x, k (var, int)
  - Function g: n(arg, int), t(var, char)
- **같은 이름의 identifier** *(p.14)*: 계층 구조 덕분에 이름 충돌이 자동으로 해결된다. **현재 scope에서 시작해 같은 이름을 찾을 때까지 계층을 위로** 올라가며 선언을 결정

### 예제 *(p.15~17)*
- **Example 1** *(p.15)*: `{int x,k; i=2;}` — 안쪽 블록 f.1에서 `i`를 찾으면 f.1, f, Global 어디에도 없다 (`i`는 형제 블록 f.0에만 있음) → **Error! (Undefined)**
- **Example 2** *(p.16)*: `{int x,k; y=2;}` — f.1에 `y`가 없지만 **상위 scope인 함수 f에 `y`(float)가 있으므로 거기서 찾아진다** (그림에서 f.1의 `y=2`가 함수 f의 `y` 행으로 연결됨). 정상이며, Global 위의 `Error! (Undefined)`는 끝까지 못 찾았을 때 도달하는 지점일 뿐이다
- **Class Exercise** *(p.17)*: 각 `x`의 정의(`x=1`, `x=2`, g 안의 `x = 3`)를 알맞은 symbol entry에 연결하라 — 규칙대로 가장 가까운 상위 scope의 `x`
  - `{int i,j; x=1;}` → 함수 f의 `float x` / `{int x,k; x=2;}` → 자기 블록 f.1의 `int x` / g 안 `x = 3` → Global의 `int x`

### Symbol Table 구현 *(p.18)*
- 5가지 연산:
  - **Insert scope**: 새 중첩 scope 시작
  - **Exit scope**: 현재 scope 종료
  - **Find symbol(x)**: 계층에서 x를 검색
  - **Add symbol(x)**: table에 symbol x 추가
  - **Check scope(x)**: 현재 scope에 x가 정의되어 있는지 확인 (optional)
- symbol table은 parsing 중에 만들 수도 있고 **AST를 만든 뒤**에도 만들 수 있다. 단, **semantic analysis 전에는 생성**되어 있어야 한다

### AST를 순회하며 Symbol Table 만들기 *(p.19~28)*
- 예시 AST: Program의 자식이 Func Decl(func1), Var Decl(var1)(전역 변수), Func Decl(func2) 셋. func1의 자식은 Var Decl(var1)(매개변수)과 Compound Stmt(자식: Var Decl(var1), Var Decl(var2)), func2의 자식은 Var Decl(var3)
- 순회 과정 *(각 단계에서 check_scope → add_symbol)*:
  1. func1 선언: `check_scope(func1)`, `add_symbol(func1)` → Global에 func1 *(p.19)*; `insert_scope()` → func1 scope 생성
  2. 매개변수 var1: `check_scope(var1)`, `add_symbol(var1)` → func1 table에 var1 *(p.20)*
  3. 함수 본문 Compound statement 진입: `insert_scope()` → **func1.0** *(p.21)*
  4. 내부 var1: `check_scope(var1)` — **현재 scope(func1.0)에서만** 검사하므로 바깥 func1의 var1과 충돌하지 않고 `add_symbol(var1)` *(p.22)*
  5. var2: `check_scope(var2)`, `add_symbol(var2)` → func1.0에 var2 *(p.23)*
  6. Compound statement 종료: `exit_scope()` *(p.24~25)*
  7. Program 바로 아래의 **전역 Var Decl(var1)** *(p.26)*: `check_scope(var1)`, `add_symbol(var1)` → Global에 func1, var1 (func1 내부의 var1과는 다른 scope라 충돌 없음)
  8. func2 선언: `check_scope(func2)`, `add_symbol(func2)`, `insert_scope()` → Global에 func2, func2 scope 생성 *(p.27)*
  9. func2 매개변수 var3: `check_scope(var3)`, `add_symbol(var3)` → func2 table에 var3 *(p.28)*

### 함수 선언과 사용 순서 *(p.29)*
- scope를 구현하는 방법이 두 가지:
  - **C-Minus**: 함수를 **사용하기 전에 선언**해야 함 (`foo`를 `boo`보다 앞에 정의)
  - **Python 등**: 선언 전에도 함수를 **사용 가능**
  - **C**: 본문과 별도의 **forward declaration**(`int boo(int z);`)을 두면 사용 가능

### Scope analysis와 Symbol Table의 관계 *(p.30~31)*
- **완성된 full symbol table**을 쓰면 별도 scope를 만들어야 한다. 예: `boo`가 `foo`를 호출하는데 `foo`가 `boo` 뒤에 정의되어 있으면, C-minus에서는 `foo`가 global scope에 **존재하면 안 된다** *(p.30)*
- 방법 *(p.31)*:
  - **Option #1**: symbol table을 **먼저 생성**한 뒤 scope analysis
  - **Option #2**: symbol table 생성과 scope analysis를 **동시에** 수행 — **부분적으로 만들어진 table**(그 시점까지 선언된 것)로 선언을 찾는다

## 5. Type Analysis *(p.33~79)*

### Type 정보 *(p.33~34)*
- **Type checking**: 프로그램 각 구성 요소 간 **타입 일관성**을 보장하는 규칙 집합. 예: 정수 변수와 문자열 변수를 더하면 안 됨
- **Type inferencing**: **빠진 타입 정보를 채움**. 예: int + int의 결과는 int
- 이 수업에서는 두 용어를 **혼용**한다. 예: `int x; float y; double z = x + y;`
- Type checking 예시 *(p.34)*:
  - unary/binary 연산자(`+`, `==`, `[ ]`)는 **올바른 타입의 피연산자**를 받아야 함
  - 함수는 **인자의 개수와 타입**이 맞게 호출되어야 함
  - return문은 **반환 타입**과 일치해야 함
  - 대입에서 대입되는 값은 LHS 변수의 타입과 **호환**되어야 함
  - class member를 올바르게 접근해야 함

### 언어의 세 종류 *(p.35)*
- **Statically typed**: type checking 대부분이 **컴파일 시간**에 수행 (C, Java)
- **Dynamically typed**: type checking 대부분이 **프로그램 실행** 중에 수행 (Python, Lisp, Perl)
- **Untyped**: type checking이 없음 (machine code)

### Type checking과 프로세서 *(p.36~37)*
- **Dynamic type checking은 overhead**가 있다
- 그 overhead를 줄이기 위해 **프로세서를 바꾸는** 연구가 있다 (논문: *Typed Architectures: Architectural Support for Lightweight Scripting*). "재밌는 주제지만 이 수업의 범위는 아니다"

### Static type checking의 장점 *(p.38)*
- **런타임에 추가 type checking 명령이 필요 없다** → overhead가 크게 감소
- 실행이 **컴파일 시점에 안전**함을 보장
- 단, 현대 언어는 **static과 dynamic type checking을 모두** 필요로 한다 (Union, Void pointer 등)

### Type이란 *(p.39~40)*
- **Type** = **값의 집합과 그 값들에 허용되는 연산의 집합**에 대한 기술. 본질적으로 **값에 대한 predicate**. 예: `int x`는 `-2^31 ≤ x < 2^31`을 뜻함
- **Type expression**: 프로그램에서 가능한 타입을 기술 (예: `int`, `char*`, `array[]`, `object`)
- **Type system**: 언어 구성 요소(AST의 node — expression, statement)에 타입을 정의
- Type expression을 만드는 방법 *(p.40)*:
  - **Basic types**(= primitive types, ground types): `int`, `char`, `double`
  - **Type constructors**: Array types, Structure/object types, Pointer types
  - **Type aliases**
  - **Function types**

### Type 비교 구현 *(p.41)*
- **Option 1**: `Equals(T1, T2)` 메서드 구현 — T1, T2의 **type tree를 비교**. 객체지향 언어는 **subtyping `SubtypeOf(B, A)`**도 필요
  - B가 A의 subtype: A 객체에 호출할 수 있는 **모든 함수를 B 객체에도 호출**할 수 있음 (예: Bool은 Int의 subtype)
- **Option 2**: **각 타입마다 유일한 객체**를 사용 — 각 type expression(예: `array[int]`)이 어디서나 같은 type 객체로 resolve됨. 비교가 `==`로 가능해 **더 빠름**. 객체지향이면 type 객체의 subtyping을 검사

### 타입 동치성 *(p.42)*
- **Structural equivalence**: **구조(메모리 레이아웃)가 같으면** 같은 타입
- **Name equivalence**: **타입 이름이 같아야** 같은 타입. 이름이 다르면 메모리 레이아웃이 같아도 다른 타입
- 예: `typedef struct cs_student {int number; char name[20]; int grade;} cs_stu;`와 `typedef struct ds_student {…같은 필드…} ds_stu;` — 구조는 같고 이름은 다름

### Type checking 방법론 *(p.43~51)*
- Type checking = expression에 **올바른 타입이 주어졌는지 검증** (예: int + int가 int인지)
- **Option 1: Syntax-Directed Definition (SDD)** — type checking을 **parsing 중에** 수행
- **Option 2: AST를 먼저 만들고**, AST node를 **재귀 순회**하며 type checking

**SDD** *(p.45~46)*
- CFG의 production마다 **semantic rule**을 연결
  - `L → E $`: `L.type = E.type`
  - `E → E1 + T`: `E.type = if (E1.type == T.type) E1.type else TypeCheckError("+")`
  - `E → T`: `E.type = T.type`
  - `T → T1 * F`: `T.type = if (T1.type == F.type) T1.type else TypeCheckError("*")`
- production에 붙은 semantic rule로 type을 검사. bison 스타일 예:
  ```
  L : E EOF   {$$.type = $1.type;};
  E : E1 + T  {if ($1.type == INT && $3.type == INT) $$.type = INT;
               else TypeCheckError("+");};
  ```

**AST 순회** *(p.48)*
```c
static void traverse( TreeNode * t,
        void (* preProc) (TreeNode *),
        void (* postProc) (TreeNode *) )
{ if (t != NULL)
  { preProc(t);
    { int i;
      for (i=0; i < MAXCHILDREN; i++)
          traverse(t->child[i],preProc,postProc);
    }
    postProc(t);
    traverse(t->sibling,preProc,postProc);
  }
}
```
- preProc → 자식들 재귀 → postProc → sibling 순회. type checking은 **post-processing 단계**에서 수행

**순회 중 type checking 주의점** *(p.49)*
- type 선언은 symbol table에 **새 identifier와 타입을 추가**
- class 정의도 symbol table에 추가: `class_defn : CLASS ID {decls} ;`
- **Forward reference**(`class A {B b;}`가 `class B {...}`보다 먼저 나옴)가 있으면, 합법적인 이름을 모으기 위해 AST를 **여러 번 순회(multiple passes)**해야 한다

**AST node별 type_inference 예** *(p.50~51, 61~62)*
- 예시 AST: `Add(Add(Num(1), Num(2)), Num(3))`
- `Num`: `val == NUMERIC`이면 `Int` 반환, 아니면 `TypeCheckError()`
- `Add`: `t1 = left.type; t2 = right.type; if (t1 == Int && t2 == Int) return Int; else TypeCheckError("+")`

### Type rule 명세: Inference Rule *(p.52~60)*
- 앞 강의에서 본 명세 방법: lexical analysis = regular expression, syntax analysis = CFG. type checking에서는 **논리적 inference rule(추론 규칙)**을 형식 명세로 사용 *(p.52)*
- Inference rule의 형태 *(p.53~54)*: **가설(hypotheses)이 참이면 결론(conclusion)이 참**
  - 표기: `Λ`는 "and", `⟹`는 "if-then", `x:T`는 "x는 타입 T를 가짐"
  - 예: `e1 : int Λ e2 : int ⟹ e1 + e2 : int` — 일반형 `hypothesis1 Λ hypothesis2 Λ … ⟹ conclusion`
- 관례적 표기 *(p.55)*: 가설들 `⊢ hypothesis1  ⊢ hypothesis2 …`을 분자에, `⊢ conclusion`을 분모에 쓰고 오른쪽에 **[Rule name]**. `⊢`는 "…가 증명 가능하다"는 뜻

**Soundness와 type judgement** *(p.56~57)*
- **Static semantics**: type judgement를 기술하는 형식 표기. `e : T`는 e가 타입 T의 **sound한 expression**. 어떤 T에 대해 `e : T`면 e는 **typable**
- 예: `2 : int`, `True : bool`, `2 * (3 + 4) : int`, `"Hello" : string`
- **Statement도 expression이 될 수 있다** *(p.57)*
  - `if (b) 2 else 3 : int` (if-else를 expression으로 쓰는 언어: Python `x = 2 if (b) else 3`), `x == 10 : bool`, `b = true, y = 2 : int`, `result = (a /= 2, b++);` 등
  - 값이 없는 statement는 특별한 **unit type(void / empty type)** — `S : void`는 "S는 결과 타입이 없는 sound statement"

**Sound inference rules** *(p.58)*
- `i is an integer literal ⊢ i : int` **[Int]**
- `⊢ e1 : int  ⊢ e2 : int ⟹ ⊢ e1 + e2 : int` **[Int Add]**
- 규칙이 **sound**하다 = `⊢ e : T`이면 e가 실제로 타입 T로 평가된다. sound한 규칙만 쓰지만 **더 좋은 규칙과 덜 좋은 규칙**이 있다 (예: `i is an integer literal ⊢ i : object`도 sound하지만 정보가 약함)

**Proof tree** *(p.59~60)*
- parse tree처럼 **proof tree**가 존재. 예: `1 is an integer literal ⊢ 1 : int [Int]`, `2 ... ⊢ 2 : int [Int]` → `⊢ 1 + 2 : int [Int Add]`
- **Type checking = `e : T`를 증명하는 과정**
  - proof tree는 **AST의 구조**를 따른다 — AST node 하나당 type rule 하나를 사용
  - AST를 **bottom-up(post-processing)** 으로 순회: 각 node e의 가설은 하위 expression의 타입 증명, 결론은 e의 타입

**더 많은 inference rule** *(p.63~64)*
- `s is a string literal ⊢ s : string` [String], `⊢ false : bool` [False], `⊢ new T : T` [New], `⊢ e : bool ⟹ ⊢ !e : bool` [Not]
- **If-then-else**: `⊢ e1 : bool  ⊢ e2 : T  ⊢ e3 : T ⟹ ⊢ if e1 then e2 else e3 : T`
- **If-then**: `⊢ e1 : bool  ⊢ e2 : T ⟹ ⊢ if e1 then e2 : void` — programmer가 if-then으로 값을 얻으려 하지 않도록 **권장하지 않아야** 한다

**Class Exercise: while** *(p.65~66)*
- 답: `⊢ e1 : Bool  ⊢ e2 : T ⟹ ⊢ while (e1) { e2 } : Void` [while]

**Class Exercise: proof tree** *(p.67~68)*
- CFG: `exp → true | false | if exp then exp else exp | 0 | succ exp | pred exp | iszero exp`
- 규칙: `⊢ 0 : int`, `⊢ true : bool`, `⊢ false : bool`, [if-then-else], `⊢ e1 : int ⟹ ⊢ succ e1 : int`(슬라이드에는 [succ]의 가설이 `e1: bool`로 인쇄되어 보이나 정답 proof tree는 int 가정으로 전개됨), `⊢ e1 : int ⟹ ⊢ pred e1 : int` [pred], `⊢ e1 : int ⟹ ⊢ iszero e1 : bool` [iszero]
- 증명할 식: (1) `if iszero 0 then 0 else pred 0 : int`, (2) `pred succ iszero pred 0 : int`
- 정답 proof tree: `0:int` → `iszero 0 : bool`, `0:int` → `pred 0 : int`, → (1) 완성. (2)는 `0 : int → pred 0 : int → iszero pred 0 : bool → succ iszero pred 0 : int → pred succ iszero pred 0 : int`

### Type Environment *(p.69~75)*
- **문제** *(p.69)*: 변수 참조 `x;`의 타입을 어떻게 정의할까? 참조만으로는 x에 타입을 줄 정보가 부족 (`⊢ x : ?` [Var]) → **규칙에 더 많은 정보를 제공**해야 한다
- **Type environment** *(p.70)*: **free variable**의 타입을 제공. **object identifier → type으로의 함수**
  - 변수가 expression 안에서 정의되지 않으면 그 expression에서 **free**: `x`는 free, `x+y`는 x와 y가 free, `int z = x`는 x만 free
  - 표기 **`O ⊢ e : T`**: 변수들이 O가 주는 타입을 가진다고 가정할 때 e가 타입 T임이 증명 가능. **O는 본질적으로 symbol table**
- 복습 *(p.71)*: 앞의 symbol table 예시를 다시 보여줌 (labels까지 포함)
- 예시 *(p.72)*: `int x; int y; … z = x + y;` → `O(x) = int`, `O(y) = int` → `O ⊢ x : int` [Var], `O ⊢ y : int` [Var] → `O ⊢ x + y : int` [Int Add]
- **선언이 있는 복잡한 예** *(p.73)*: `O[T/x]`는 선언이 있는 context. `O[T/x](x) = T`, `O[T/x](y) = O(y)` (x ≠ y). **symbol table의 entry를 수정하거나 추가**하는 것과 같다
  - `for (T1 i = 0;;) { exp }`: `O[T1/i] ⊢ exp : T2` ⟹ `O ⊢ for(i : T1) {exp : T2}`
- **Class attribute** *(p.74)*: `O_c`는 class 전체 scope. `O_c(x) = T` (class C의 모든 attribute `x:T`). `O_c(x1) = T1  O_c ⊢ exp : T1 ⟹ O_c ⊢ x1 = exp : T1`
- **Class method** *(p.75)*: 별도 scope **M**으로 함수를 기술. `M(C, f) = (T1, T2, …, Tn, Tn+1)` — class C의 method f가 `f(x1:T1, …, xn:Tn)`이고 반환 타입이 `Tn+1`
  - `O, M ⊢ e0 : T0, …, O, M ⊢ en : Tn` 그리고 `M(T0, f) = (T1, …, Tn, Tn+1)` ⟹ `O, M ⊢ e0.func(e1, …, en) : Tn+1`

### Subtyping *(p.76~79)*
- class 사이의 관계 *(p.76)*: `X ≤ X`, `X ≤ Y` (X가 Y를 상속), `X ≤ Y`이고 `Y ≤ Z`이면 `X ≤ Z`. 예: `float ≤ double`, `char ≤ int`
- **더 관대한(permissive) 규칙**: `O ⊢ y : T0`, `T0 ≤ T1`, `O[T1/x] ⊢ exp : T2` ⟹ `O ⊢ for(x : T1 = y) {exp : T2}` — 초기값 y의 타입 T0가 **선언 타입 T1의 subtype이면 허용**
- **Subtyping과 type conversion** *(p.77)*
  - B가 A의 subtype이면 A에 적용 가능한 **모든 함수를 B에도** 적용할 수 있다
  - **subtype → supertype은 암시적 변환 가능**: `char ≤ int ≤ float ≤ double`이므로 char→int, int→float, float→double
  - **supertype → subtype**으로 바꿀 때는 **명시적 변환(explicit conversion)** 필요
- **lub (least upper bound)** *(p.78)*
  - `if e0 then e1 else e2`에서 e1과 e2의 타입이 다르면, 둘을 포괄하는 **가장 작은 supertype**을 쓴다
  - `lub(X, Y) = Z`: ① `X ≤ Z`이고 `Y ≤ Z`, ② 임의의 `Z'`가 `X ≤ Z'`이고 `Y ≤ Z'`이면 `Z ≤ Z'`
  - 규칙: `O ⊢ e0 : bool  O ⊢ e1 : T1  O ⊢ e2 : T2 ⟹ O ⊢ if e0 then e1 else e2 : lub(T1, T2)`
- **Inheritance와 subtyping** *(p.79)*: subtyping을 가능케 하는 일반적 방법은 **상속**(overriding이 없다고 가정). 예: `class A`, `class B inherits A`, `class C inherits A`, `class D inherits C` → **`lub(B, D) = A`**

## 6. Static Scoping vs. Dynamic Scoping *(p.80~84)*

- (scope analysis에 대한 "또 다른 재미있는 주제") *(p.80)*
  - **Static scoping**: symbol table을 **정적으로** 만들고, 그 table로 변수가 **어디서 선언**되었는지 추론
  - **Dynamic scoping**: 변수의 scope가 **함수 호출에 따라 동적으로** 바뀜
- 질문 *(p.81)*: `int x = 50; int func2() { return x; } int func1() { int x = 10; int y = func2(); return y; } int main() { func1(); }` — **func1이 무엇을 반환하는가?**
- **Static scoping** *(p.82)*: 사용(usage)이 **컴파일 시간**에 symbol table로 결정됨. `func2`의 `x`는 선언 위치 기준으로 **Global의 `x = 50`**. → **50 반환**
- **Dynamic scoping** *(p.83)*: 사용이 **call stack(가장 가까운 선언)**에 기반. main → func1(x, y 선언) → func2 호출: func2에는 선언이 없고 `x`를 사용 → 호출 스택을 거슬러 올라가 **func1의 `x = 10`**을 찾음. → **10 반환**
- **Perl** *(p.84)*: **static과 dynamic을 모두 지원** (슬라이드에는 "static + dynamic typing"으로 적혀 있으나 내용은 scoping)
  - `local $x`: 변수가 **call stack에서 보임**(dynamic)
  - `my $x`: 변수가 **그 scope 안에서만** 쓰임(static)
  - 같은 코드에서 `func1`이 `local $x = 10`이면 func2가 10을, `my $x = 10`이면 50을 본다
