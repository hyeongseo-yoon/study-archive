# Lecture 10-11: Query Execution — Relational Algebra

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*Database Systems & its Applications — Relational Algebra*

> 슬라이드 쪽번호가 인쇄되어 있지 않거나 잘려 있어서, 아래 `p.N`은 PDF 파일의 페이지 순서(1부터 시작)를 가리킨다.
> 구성: **① Relational Algebra(RA) 개요와 연산자 → ② SQL을 RA로 변환 → ③ RA tree 변환 규칙(Tree Transformations)**

## 0. Outline *(p.2, 15, 52, 76, 91, 110, 116)*
- Relational Algebra: Introduction, Operators
- SQL to RA: Flat Queries, Subqueries, Subqueries in FROM, Subqueries in WHERE/HAVING
- Tree Transformations: Introduction and Caveats, Rules

## 1. Relational Algebra 개요 *(p.3~14)*

### 쿼리 실행의 큰 그림 *(p.3)*
- RDBMS 안에서 **SQL → Relational Algebra → (동치인 여러 Logical Plan) → Physical Plans → 최소 비용(Least Cost) Plan 선택 → Execution**
  - Logical plan은 조인 순서가 다른 여러 동치 트리로 확장되고, 각 join은 물리 알고리즘(`⋈_smj` sort-merge join, `⋈_hj` hash join, `⋈_nlj` nested-loop join 등)을 골라 physical plan이 된다

### SQL에서 RA로 *(p.4)*
- **SQL은 선언적(declarative)** 언어 — "어떻게(how)"가 아니라 "무엇을(what)" 가져올지를 말함. Java 프로그램 전체를 쓰는 것보다 SQL이 쓰기 쉽다
- 그러나 **컴퓨터는 명령형(imperative/procedural)** — "how"만 이해한다
- 따라서 **명령처럼 읽히면서도 쿼리의 본질적 연산을 담는 언어**가 필요 → **Relational Algebra**

### 역사 *(p.5~6)*
- RA에서 처음으로 **"how to get it"**을 표현하기 시작한다
- **Ted Codd**(IBM)가 발명/형식화: 물리적 세부사항을 모르는 채 테이블에 대한 명령형 프로그래밍을 기술할 필요를 인식. IBM은 처음에 그의 기법을 무시했고 **10년 뒤 그는 Turing Award**를 수상
- **Relational Algebra ≠ SQL**: IBM이 마침내 관계형 모델에 투자했을 때 Codd는 팀에 포함되지 않았다. 최초의 질의 언어 **SQL은 1974년 Donald Chamberlin과 Ray Boyce**가 설계, 첫 구현은 **Patricia Selinger**가 이끈 다른 팀 → 그래서 **SQL→RA 매핑은 어색한 부분이 있다**

### RA의 목적 *(p.7)*
- RA는 명령처럼 읽히지만 쿼리 연산을 이해한다. RDBMS는 쿼리를 처리할 때 **RA tree 또는 DAG**를 생성하고, 몇 가지 최적화 후 RA tree를 실행 명령으로 변환한다

### RA 기본 *(p.8~10)*
- SQL은 원하는 것을 말하고, RA는 **어떻게 얻을지**를 표현
- RA는 **set-at-a-time 대수(algebra)**: 연산자 모음. **입력: 하나 또는 두 개의 relation, 출력: 새 relation**
- RA는 이 연산자들을 **어떻게 조합할지**도 명시 → RA expression은 연산 수행 **순서**도 명시한다 = **query plan**
- 연산자는 그리스 문자(σ, π, δ …)로 표기. RA expression/query plan은 보통 **트리**로 표시하며 입력 relation의 **tuple이 트리를 따라 위로 흘러(flow up)** 가며 변형된다
- 인라인 표기 예 *(p.10)*: `σ_{maxSal>10}(γ_{P.Job, max(P.Salary)→maxSal}((Payroll P) ⋈_{P.UserID=R.UserID} (σ_{R.Car='Camry'}(Registry R))))` — 같은 식을 트리로도 그릴 수 있다

### 이 수업에서 다루는 RA 연산자 *(p.11~13)*
- **기본 연산자** *(p.11)*: **Join ⋈**, **Cartesian Product ×**, **Selection σ**("where clause"), **Projection π**("select clause"), **Union ∪**, **Intersection ∩**, **Difference −**
  - RA에는 **집합을 검사하는 연산자가 없다** — 멤버십 연산자 ∊도, 동등 연산자 =도 없음
- **확장 연산자** *(p.12)*: **Grouping & Aggregation γ**, **Sort τ**, **Duplicate Elimination δ**, **Rename ρ**
- **기타** *(p.13)*: **Right Outer Join ⟖**, **Left Outer Join ⟕**, **Full Outer Join ⟗**

### Sets vs Bags *(p.14)*
- **Set**: {a,b,c} 처럼 중복 없음. **Bag**: {a,a,b,c} 처럼 **중복 허용**
- RA는 두 가지 버전: **Set semantics = 표준 RA**, **Bag semantics = 확장 RA**
- **DB 시스템은 bag semantics를 구현한다** (슬라이드는 "Why?"라고 묻기만 하고 답은 적지 않음. 아래는 정리하는 쪽의 해석: SQL 테이블/결과가 중복 행을 허용하고, 중복 제거는 비용이 들기 때문)

## 2. RA 연산자 상세 *(p.16~51)*

### Projection π ≡ SELECT *(p.16~18)*
- **단항(unary)** 연산자. 지정되지 않은 column을 제거
- 예: `π_{A,B}(R)`은 R의 A, B attribute를 반환. **출력 relation의 스키마가 다르다** (R(A,B,C) → S(A,B))
- **set 또는 bag semantics** 모두 가능: `π_A(T)`를 bag으로 하면 중복이 남고(1, 1, 2), set이면 중복이 제거(1, 2)된다 *(p.18)*

### Selection σ ≡ WHERE *(p.19~20)*
- **단항** 연산자. 주어진 **predicate**로 입력 tuple을 걸러냄
- 예: `σ_{A<6}(R)`은 A<6인 모든 tuple 반환. **출력 스키마는 입력과 동일**

### Union ∪ / Intersection ∩ *(p.21)*
- `∪` ≡ UNION, `∩` ≡ INTERSECT
- **이항(binary)** 연산자, **두 입력의 스키마가 같아야** 한다. set 또는 bag semantics 모두 가능

### Difference − ≡ EXCEPT *(p.22)*
- 기호 `−` 또는 `\`. 이항 연산자이지만 **방향이 중요**(R − S ≠ S − R). 두 입력의 스키마가 같아야 함

### Grouping γ ≡ GROUP BY *(p.23)*
- 표기 `γ_{attributes, aggregates}`. **단항** 연산자이며 **스키마와 cardinality가 모두 변할 수 있다**
- grouped attribute를 먼저, 그 다음 aggregate를 명시. **aggregate를 계산할 수 있는 유일한 연산**
- 예: `γ_{A, max(B)→mB}(R(A,B,C))` → S(A, mB) ≈ `SELECT A, MAX(B) AS mB FROM T GROUP BY A`

### Sorting τ ≡ ORDER BY *(p.24)*
- **단항**. **스키마와 cardinality는 변하지 않는다**. column 기준으로 정렬 (기본 오름차순, SQL과 동일). 예: `τ_{A,B}(R)`

### Deduplication δ ≡ UNIQUE/DISTINCT *(p.25)*
- **단항**. 중복 tuple 제거. cardinality는 바뀔 수 있지만 **스키마는 그대로**
- **모든 attribute로 grouping하는 것과 같다** → 단지 syntactic sugar

### 연습 문제 *(p.26)*
- `SELECT MAX(UserID) FROM Payroll UNION SELECT MAX(UserID) FROM Registry`의 RA tree 그리기 (정답 없음)

### Joins 개요 *(p.27~28)*
- 모든 join은 **이항 연산자**이고 **bag semantics**
- **Inner joins**: Equijoin(⋈=), Cross product(×), Theta-join(⋈_θ), Natural join(⋈), Semi-join(⋉)
- **Outer join 변형**: Left, Right, Full (⟕, ⟖, ⟗)

### Equijoin ⋈= *(p.29~31)*
- `⋈_{attr1=attr2}`: **명시적으로 지정한 동등 조건**. **두 입력은 서로소(disjoint)인 attribute**를 가져야 한다
- 공통 column을 포함해 "중복된" column까지 **모든 column을 반환**
- 예: `R(A,B) ⋈_{R.A=S.C} S(C,D) → T(A,B,C,D)`; `R ⋈_{B=C} S`는 B=C인 tuple 쌍만 결합 *(p.30)*
- **같은 이름의 attribute가 있으면 relation 이름을 접두**: `R(A,B) ⋈_{R.B=S.B} S(B,C) → T(R.A, R.B, S.B, S.C)` *(p.31)*

### Cross Product × *(p.32~33)*
- Cross Product 또는 Cartesian Product. 두 입력은 서로소인 attribute. `R(A,B) × S(C,D) → T(A,B,C,D)`. 모든 tuple 쌍의 조합(|R|×|S|개) *(p.33)*

### Joins 논의 *(p.34)*
- **equijoin은 논리적으로 cross product 뒤에 selection**: `R ⋈_{B=C} S = σ_{B=C}(R × S)`
- 그러나 **DB 시스템은 equijoin을 이렇게 계산하지 않는다** — equijoin 전용 구현을 둔다

### 연습 문제 *(p.35)*
- `SELECT date, COUNT(origin) AS c FROM Flights WHERE date LIKE '2010/01/%' GROUP BY date ORDER BY date;`의 RA tree. 힌트: **WHERE = σ, SELECT = π, 모든 aggregate = γ**

### Theta-Join ⋈_θ *(p.36~38)*
- **임의의 predicate**를 쓰는 이항 연산. 두 입력은 서로소인 attribute. **equijoin도 동등 predicate를 쓰는 theta-join**
- 예: `R(A,B) ⋈_{B≤C} S(C,D) → T(A,B,C,D)` — B ≤ C를 만족하는 모든 쌍 *(p.38)*

### Natural Join ⋈ *(p.39~42)*
- **파라미터 없는** 이항 연산. **같은 이름의 모든 attribute에 대한 equijoin**을 수행하고, **공통 attribute는 한 벌만 반환**
- 예: `R(A,B) ⋈ S(B,C) → T(A,B,C)` — B=B로 join하며 B는 하나만 유지 *(p.40)*
- 예제 *(p.41)*: `AnonymizedPatient(Age, Zip, Diagnosis) ⋈ Voters(Name, Age, Zip)` → (Age, Zip, Diagnosis, Name) — 익명화된 의료 데이터와 유권자 명부를 Age·Zip으로 결합하면 개인이 재식별될 수 있다
- **직관에 어긋나는 함정(Gotcha)** *(p.42)*: 피연산자의 **모든 column이 일치**하거나 **일치하는 column이 전혀 없으면** 특수 동작
  - 모든 column이 일치 → **교집합 R ∩ S**
  - 일치하는 column 없음 → **cartesian product R × S**

### Semi-join ⋉ *(p.43~45)*
- 이항 연산자. **오른쪽과 join되는 왼쪽 tuple**을 반환. **스키마는 왼쪽(원본) 테이블과 동일**
- 여러 개 매치되어도 **한 tuple만** 반환. 두 번째 테이블의 tuple로 첫 번째 테이블을 **"필터링"**한다 (σ는 단일 predicate로 필터링하는 것과 대비)
- `R(A,B) ⋉ S(B,C) → T(A,B)`. **T는 항상 R의 부분집합** *(p.45)*

### Outer Joins ⟕, ⟖, ⟗ *(p.46~48)*
- 이항 연산자. **left / right / full outer join**. 앞에서 본 **모든 join의 변형** (left outer equijoin, right outer equijoin, full outer equijoin, left outer theta-join …)
- 예: `R(A,B) ⟕ S(B,C) → T(A,B,C)` — 매칭되지 않는 왼쪽 tuple은 **NULL**로 채워 유지(예: `(2, b)` → `(2, b, NULL)`) *(p.48)*

### Joins 논의: 왜 join이 많은가 *(p.49~51)*
- 이유 **정규화(Normalization)**: 이상(anomaly)을 없애기 위해 relation을 정규화하고, 나중에 원래 데이터셋을 복원하려고 **join**을 수행
- **가장 흔한 join은 equijoin과 natural join**. 일부 시스템은 이 둘만 지원

## 3. SQL → RA 변환 *(p.53~109)*

### Query Plan *(p.53)*
- query plan = RA로 쓴 expression(보통 트리). DBMS는 SQL 쿼리를 대응하는 query plan으로 변환하며, plan은 **연산자의 순서**를 지정. **tuple은 plan을 따라 위로 흘러가며** 변형된다

### Tuples Flow Up 예제 *(p.54~58)*
- `SELECT AVG(P.Salary) FROM Payroll AS P, Registry AS R WHERE P.UserID = R.UserID;`
- plan(아래→위): `Payroll P`, `Registry R` → `⋈_{P.UserID=R.UserID}` → `γ_{AVG P.Salary}` → `π_{AVG P.Salary}`

### 변환 순서 *(p.59)*
- 이 순서를 외우는 약어 **FJWGHOS**: **F**rom → **J**oin → **W**here → **G**roup by → **H**aving → **O**rder by → **S**elect
- 대응: FROM = Tables/Relations(⋈), WHERE = σ, GROUP BY = γ, HAVING = σ, ORDER BY = τ, SELECT = π (아래에서 위로 쌓는다)

### 예제: SQL → RA *(p.60~74)*
```sql
CREATE TABLE Payroll (UserID INT PRIMARY KEY, Name VARCHAR(100), Job VARCHAR(100), Salary INT);
CREATE TABLE Registry (UserID INT REFERENCES Payroll, Car VARCHAR(100));
```
"차를 여러 대 모는 TA를 찾고 모는 차 수로 정렬":
```sql
SELECT DISTINCT P.Name
FROM Payroll AS P, Registry AS R
WHERE P.UserID = R.UserID AND P.Job = 'TA'
GROUP BY P.UserID, P.Name
HAVING COUNT(*) > 1
ORDER BY COUNT(*)
```
1. **FROM/JOIN** *(p.61)*: `⋈_{P.UserID=R.UserID}(Payroll P, Registry R)`
2. **WHERE** *(p.62)*: `σ_{P.Job='TA'}`을 join 위에 얹는다. 조건이 늘면(예: `AND P.Salary > 20000`) 하나의 σ에 `∧`로 묶는다 *(p.63)*
3. **GROUP BY** *(p.64)*: `γ_{P.UserID, P.Name, count(*)→cnt}`
4. **HAVING** *(p.65~66)*: `σ_{cnt>1}` — **WHERE와 HAVING 둘 다 σ가 된다**
5. **ORDER BY** *(p.67)*: `τ_{cnt}`
6. **SELECT** *(p.68)*: `π_{P.Name}`
7. **DISTINCT** *(p.69)*: `δ`를 맨 위에 추가
- **이 쿼리는 틀렸다(INCORRECT!)** *(p.70)*: SQLite는 받아들이지만 다른 엔진은 거부한다 (슬라이드는 "why?"라고만 묻는다. 바로 다음 슬라이드들의 설명으로 보면 원인은 SELECT에 없는 `COUNT(*)`로 ORDER BY 하면서 DISTINCT를 쓰는 것)
- *(p.71)* **deduplication이 정렬 순서를 바꿀 수 있다**: π로 `cnt`가 사라진 뒤 δ가 중복을 제거하면 정렬 순서가 보장되지 않는다
- *(p.72)* **DISTINCT를 쓰면 ORDER BY 식도 SELECT 절에 포함**해야 한다 — 아니면 출력이 잘못 정렬됨
- *(p.73~74)* 고친 쿼리: `SELECT DISTINCT P.Name, COUNT(*) …` → `π_{P.Name, cnt}`, 그 위에 `δ`, 그 위에 `τ_{cnt}` 로 정렬 순서가 유지된다

### 연습 문제 *(p.75)*
- `SELECT P.UserID, COUNT(*) FROM Payroll AS P, Registry AS R WHERE P.UserID = R.UserID GROUP BY P.UserID`를 RA로 (정답 없음)

### Subquery를 RA로 *(p.77)*
- RA는 대수이므로 **subquery(또는 sub-RA)가 없다**. set-at-a-time(relation in, relation out)
- SQL에 subquery가 있으면 DBMS는 ① subquery를 **decorrelate**, ② subquery를 RA로 번역, ③ outer query를 RA로 번역한다

### FROM 절 Subquery → RA *(p.78~90)*
```sql
WITH Driver AS
  (SELECT P1.UserID AS UserID, R1.Car AS Car
   FROM Payroll AS P1, Registry AS R1
   WHERE P1.UserId = R1.UserID)
SELECT P.Name, D.Car
FROM Payroll AS P, Driver AS D
WHERE P.UserID = D.UserID
```
- 먼저 `Driver`를 `π_{P1.UserID, R1.Car}(Payroll P1 ⋈ Registry R1)`로 *(p.79)*, 바깥 쿼리는 `π_{P.Name, D.Car}(Payroll P ⋈_{P.UserID=D.UserID} Driver D)` *(p.80)*
- **`Driver`를 정의로 치환** (일반 대수처럼) → `π_{P.Name, R1.Car}(Payroll P ⋈_{P.UserID=P1.UserID} π_{P1.UserID,R1.Car}(Payroll P1 ⋈_{P1.UserID=R1.UserID} Registry R1))` *(p.81)*
- 최적화 (**`Payroll.UserID`가 key라고 가정**) *(p.82~89)*:
  - **마지막 projection만 의미 있다** *(p.83)* → 안쪽 π 제거 *(p.84)*
  - **inner join 순서는 상관없다** *(p.85~87)*
  - **key에 대한 self join은 tuple별 정보를 중복할 뿐**이다 *(p.88)* → 제거 가능
  - 결과: `π_{P1.Name, R1.Car}(Payroll P1 ⋈_{P1.UserID=R1.UserID} Registry R1)` — **매우 단순하고 효율적인 plan** *(p.89)*
- 두 plan은 **동치(Equivalent)**: 단, Payroll.UserID가 key일 때 *(p.90)*

### WHERE/HAVING 절 Subquery → RA *(p.92~109)*
- **RA는 correlated query를 표현할 수 없다** (tuple은 위로만 흐른다!) → RA로 번역하기 전에 **decorrelate** 해야 한다 *(p.92)*
- 보통 outer query가 subquery의 **scalar 결과**(단일 tuple·단일 attribute)를 outer query의 값과 비교. decorrelate한 뒤에는 **`IN`이나 `=`를 join으로 변환**해야 한다 — RA에는 "집합을 검사하는" 연산자가 없기 때문 *(p.93)*

**Example 1: 이미 decorrelated** *(p.94~97)*
```sql
SELECT P.Name FROM Payroll AS P
WHERE P.Salary = (SELECT MAX(P1.Salary) FROM Payroll AS P1)
```
- subquery → `γ_{max P1.salary → m}(Payroll P1)`, 바깥은 `π_{P.Name}(Payroll P ⋈_{P.Salary=m} γ…)`. **이 subquery는 join과 동치** (슬라이드의 질문 "why?" — 정리하는 쪽의 해석: subquery 결과가 단일 값 m이라 `P.Salary = m` join이 같은 필터 역할을 하기 때문)

**Example 2: decorrelation 필요** *(p.98~100)* — "직무별 최고 연봉자"
```sql
SELECT P.Name, P.Job FROM Payroll AS P
WHERE P.Salary = (SELECT MAX(P1.Salary) FROM Payroll AS P1 WHERE P.Job = P1.Job)
```
- `P.Job = P1.Job` 때문에 correlated → **FROM 절의 GROUP BY subquery로 decorrelate**:
  ```sql
  SELECT P.Name, P.Job
  FROM Payroll AS P,
       (SELECT P1.Job AS Job, MAX(P1.Salary) AS MaxSalary FROM Payroll AS P1 GROUP BY P1.Job) AS MP
  WHERE P.Job = MP.Job AND P.Salary = MP.MaxSalary;
  ```
- RA: `π_{P.Name, P.Job}(Payroll P ⋈_{P.Job=MP.Job & P.Salary=MP.MaxSalary} γ_{P1.Job, max P1.salary→MaxSalary}(Payroll P1))`

**Example 3: NOT EXISTS** *(p.101~109)*
```sql
SELECT P.Name, P.Salary FROM Payroll AS P
WHERE NOT EXISTS (SELECT * FROM Registry AS R WHERE R.UserID = P.UserID)
```
- ① `NOT IN`으로 바꿈: `WHERE P.UserID NOT IN (SELECT UserID FROM Registry)` *(p.102)* — decorrelated지만 아직 RA로 표현 불가 *(p.103)*
- ② `NOT IN`을 **set difference(EXCEPT)에 대한 join**으로 바꿈 *(p.104~105)*:
  ```sql
  SELECT P.Name, P.Salary FROM Payroll AS P,
    (SELECT UserID FROM Payroll EXCEPT SELECT UserID FROM Registry) AS E
  WHERE P.UserID = E.UserID
  ```
- ③ RA: `π_{Name,Salary}(Payroll P1 ⋈_{P1.UserID=E.UserID} (π_{UserID}(Payroll P) − π_{UserID}(Registry)))` *(p.106~109)* — 원래의 NOT EXISTS 쿼리와 동치

## 4. Tree Transformations *(p.111~131)*

### 개요와 주의점 *(p.111)*
- 앞에서 원래 RA tree를 **의미는 같지만 구조가 다른 tree**로 변환했다. 그때 쓴 "규칙"이 보편적으로 보였지만 **일부는 문맥에 의존**한다

### 반례: key가 아닐 때 *(p.112~115)*
- 앞의 self join 제거 최적화는 **`Payroll.UserID`가 key가 아니면 틀리다**
- 예: Payroll에 UserID 123이 둘(Leslie, Tian)이고 Registry에 123의 Charger가 있으면, 원래 tree의 결과에는 (Leslie, Charger), (Tian, Charger)가 **각각 두 번씩 중복**되어 나오지만, 수정된 tree는 중복 없이 나온다. 두 결과가 **같지 않다(≠)** *(결과 표의 정확한 행 수는 슬라이드 그림 참고)*
- 결론 *(p.115)*: **relation R을 어떤 attribute로 self-join한 결과가 R 자체와 같아지는 것은 그 attribute가 key일 때뿐**이다

### 변환 규칙 *(p.117~129)*
| 규칙 | 내용 |
|---|---|
| **WHERE 멱등성** *(p.117)* | `σ_c(σ_c(R)) = σ_c(R)` (예: `abs(N) = abs(abs(N))`) |
| **SELECT 멱등성** *(p.118)* | `π_A(π_{A,B}(R)) = π_A(R)`. 이후 열 집합 `{A,B,C} − …` 으로 설명 |
| **WHERE-AND 교환성** *(p.119)* | `σ_{c AND d} = σ_c(σ_d) = σ_d(σ_c)` (덧셈/곱셈 C+D = D+C, C·D = D·C 처럼) |
| **WHERE-OR: 중복 주의** *(p.120)* | `σ_{c OR d} = σ_c ∪_set σ_d` — **set union**이어야 한다 (bag union이면 두 조건을 모두 만족하는 tuple이 중복) |
| **SELECT-WHERE 조건부 교환** *(p.121)* | `π_A(σ_c(R)) = σ_c(π_A(R))` — **c가 A의 attribute만 참조할 때**. 선택을 아래로 **"push down"** |
| **WHERE-HAVING 조건부 교환** *(p.122)* | `σ_{c(G)}(γ_{G,f(A)}(R)) = γ_{G,f(A)}(σ_{c(G)}(R))` — **c가 grouping attribute G만 참조할 때** push down |
| **WHERE-JOIN 분배** *(p.123)* | `σ_c(R × S) = σ_c(R) × S` (c가 한쪽에만 걸릴 때) — 분배법칙 |
| **WHERE-UNION/… 분배** *(p.124)* | `σ_c(A ∪ B) = σ_c(A) ∪ σ_c(B)`, ∩와 `\`(difference)도 마찬가지 (X(Y+Z) = XY+XZ 처럼) |
| **JOIN-UNION/… 분배** *(p.125)* | `(1 ∪ 2) × 3 = (1 × 3) ∪ (2 × 3)`. INTERSECT, EXCEPT도 동일 |
| **(LEFT) OUTER JOIN 분해** *(p.126)* | `A ⟕ B = (A ⋈ B) ∪ π_{attrs of A, NULL→attrs of B}(A \ π_{attrs of A}(A ⋈ B))` — inner join 결과에 **매칭 실패한 A의 tuple을 NULL로 채워 합집합** |
| **CROSS PRODUCT 순서** *(p.127)* | **교환적 + 결합적** → 어떤 부분 트리 순서도 가능(Any subtree order works!) |

### INNER JOIN 순서 *(p.128~129)*
- `σ_c(⋈_d ⋈_e …)`로 쓴 join tree는 **cross product + 한 개의 σ_{c∧d∧e}**로 풀 수 있다 (cross product는 결합적·교환적이라 **마음대로 섞을 수 있다**)
- 그 다음 **filter를 다시 아래로 밀어(push down) inner join 논리를 복구**한다 (`σ_d`, `σ_e`를 각 cross product 바로 위로)

### The Join Ordering Problem *(p.130)*
- inner join은 교환적·결합적. **join은 RDBMS가 하는 가장 비싼 연산**인 경우가 많다
- **최적 join 순서는 쿼리 성능에 결정적**이며 **NP-Hard 문제** → RDBMS는 **휴리스틱과 차선 알고리즘**을 자주 사용

### Final Discussion *(p.131)*
- **RA는 SQL과 기계어 사이의 중간 언어**. RDBMS는 RA expression에 최적화를 수행. 모든 데이터 관리 시스템이 이런 최적화를 구현할 만큼 발전한 것은 아니다
- 최적화된 plan이 정해지면: **대부분의 엔진은 plan을 해석(interpret)**하고, **더 새로운 엔진은 plan을 기계어로 컴파일**한 뒤 실행한다
