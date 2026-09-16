# Lecture 6: Subqueries

*Database Management Systems, 3rd ed. (Ramakrishnan & Gehrke)*

## 1. Subqueries란? *(슬라이드 p.6~7)*

> **Subquery**: 다른 쿼리 안에 들어있는 쿼리

- 보통 outer query의 일부를 단순화하거나 분리해내는 역할
- 사용 사례가 프로그래밍의 **helper method**와 비슷함

### 동기: "직군별 최고 연봉자는 누구인가?" *(p.8~9)*
GROUP BY/HAVING만으로는 "무엇이 최고 연봉인지"는 알 수 있어도 "누가" 그 연봉을 받는지 알아내려면 self-join이 필요해서 지저분해진다:
```sql
SELECT P1.Name, MAX(P2.Salary)
FROM Payroll AS P1, Payroll AS P2
WHERE P1.Job = P2.Job
GROUP BY P1.Name, P1.Salary, P2.Job
HAVING P1.Salary = MAX(P2.Salary);
```
- 한 번의 pass에서 **두 가지 연산(그룹별 최댓값 계산 + 그 최댓값을 가진 사람 찾기)**을 동시에 하고 있어서 읽기 어려움

### Subquery로 두 단계에 나누기 *(p.9~10)*
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P,
     (SELECT P1.Job AS Job, MAX(P1.Salary) AS MaxSalary
      FROM Payroll AS P1
      GROUP BY P1.Job) AS MP
WHERE P.Job = MP.Job AND P.Salary = MP.MaxSalary;
```
- 먼저 subquery로 **직군별 최댓값을 따로 계산**(1st pass)한 뒤, 그 결과를 Payroll과 join(2nd pass)해서 "누구"를 찾음 — 두 연산을 분리해서 훨씬 읽기 쉬움

## 2. Subquery 문법 규칙 *(슬라이드 p.11~14)*

- subquery가 **정확히 하나의 값**(한 tuple, 한 attribute)을 반환하면, **field가 들어갈 자리 어디에나** 쓸 수 있음
- 그렇지 않으면 subquery는 **"추가 테이블"**처럼 취급됨 — 이름과 컬럼명을 붙여줄 수 있음(`AS MP` 등)

### WITH 절 *(p.14)*
```sql
WITH MaxPaid AS
     (SELECT P1.Job AS Job, MAX(P1.Salary) AS MaxSalary
      FROM Payroll AS P1
      GROUP BY P1.Job)
SELECT P.Name, P.Salary
FROM Payroll AS P, MaxPaid AS MP
WHERE P.Job = MP.Job AND P.Salary = MP.MaxSalary;
```
- subquery를 FROM 앞에 먼저 정의해서 좀 더 "테이블처럼" 보이게 하는 문법
- **WITH는 그냥 syntactic sugar** — 위 예시의 FROM-subquery 버전과 완전히 동일한 쿼리

### Subquery가 들어갈 수 있는 위치 *(p.15)*
FROM, SELECT, WHERE/HAVING — **테이블을 쓸 수 있는 곳이면 어디든** 가능

## 3. Subqueries in FROM *(슬라이드 p.17~18)*

- subquery는 결과를 "캐싱"해서 나중에 join할 수 있는 **부분 문제(subproblem)**로 활용 가능
- "rows"와 "columns"를 가진 진짜 테이블처럼 동작하므로 쿼리가 더 자연스럽게 읽힘
- 이제 **Java를 짤 때처럼 helper method 감각으로 SQL을 짤 수 있음**

## 4. Subqueries in SELECT *(슬라이드 p.20~35)*

### 기본 규칙: 반드시 단일 값 반환 *(p.20)*
```sql
SELECT P.Name, (SELECT AVG(P1.Salary) FROM Payroll AS P1)
FROM Payroll AS P;
```

### Correlated Subquery (상관 서브쿼리) *(p.21~22)*
```sql
SELECT P.Name, (SELECT AVG(P1.Salary)
                FROM Payroll AS P1
                WHERE P.Job = P1.Job)
FROM Payroll AS P;
```
- **"Correlated"** = subquery 안에서 **outer 테이블(P)을 참조**한다는 뜻
- **의미(semantics)**: correlated subquery는 **outer 쪽의 매 tuple마다 처음부터 다시 계산**된다
- subquery가 helper method라면, correlated subquery는 **"parameterized" helper method** — outer row의 값을 파라미터로 받아 매번 재계산

### 예시로 보는 실행 흐름 *(p.23~29)*
outer 쿼리가 Payroll의 각 행(P)을 순회할 때마다, 그 행의 Job 값으로 필터링된 subquery(Payroll AS P1)를 새로 실행해서 AVG(Salary)를 계산:
- P=Leslie(TA) → subquery가 TA인 행들(Leslie, Frances)만 평균 → 55k
- P=Frances(TA) → 마찬가지로 55k
- P=Magda(Prof) → Prof인 행들(Magda, Quinn) 평균 → 110k
- P=Quinn(Prof) → 110k

결과에 `AS AvgSal`로 alias도 붙일 수 있음 — **subquery의 출력에도 별칭 부여 가능**

## 5. Correlated Subquery의 성능 *(슬라이드 p.37~39)*

- 좋은 optimizer는 correlated subquery를 **decorrelate**(비상관화)해서 join 형태로 재작성한다:
```sql
-- 원래(correlated)
SELECT P.Name, (SELECT AVG(P1.Salary) FROM Payroll AS P1 WHERE P.Job = P1.Job)
FROM Payroll AS P;

-- decorrelate된 형태(join+group by)
SELECT P1.Name, AVG(P2.Salary)
FROM Payroll AS P1, Payroll AS P2
WHERE P1.Job = P2.Job
GROUP BY P1.Name;
```
- **단순한 SQL 엔진은 correlated subquery를 nested loop처럼 직접 실행**해서 비효율적일 수 있음 — outer row 개수만큼 subquery를 매번 재실행하므로
- 현대적 엔진은 자동으로 decorrelate하지만, 성능이 걱정되고 optimizer를 확신할 수 없다면 correlated subquery를 피하는 게 안전

## 6. 빈 그룹(Empty Groups) 문제, 다시 *(슬라이드 p.32~36, p.65~66)*

이전 강의(outer join)에서 겪었던 "차 없는 사람의 대수를 0으로 세고 싶다" 문제를 correlated subquery로 우아하게 해결 가능:
```sql
SELECT P.Name, (SELECT COUNT(R.Car)
                FROM Registry AS R
                WHERE P.UserID = R.UserID) AS NumCars
FROM Payroll AS P;
```
- Frances처럼 매칭되는 Registry 행이 없으면, 내부 subquery가 **빈 결과셋에 대해 COUNT를 계산 → 자동으로 0**을 반환 (COUNT는 애초에 빈 입력에도 0을 내는 aggregate이므로)
- 이는 `LEFT OUTER JOIN` + `GROUP BY` 조합과 동등한 효과를 **더 직관적으로** 얻는 방법 — subquery의 join이 사실상 "outer join"처럼 동작하는 셈
- 이걸 활용하면 이전 강의의 "2017년 이전 차 개수" 문제도 우아하게 풀린다:
```sql
SELECT P.Name, (SELECT COUNT(R.Car)
                FROM Registry AS R
                WHERE P.UserID = R.UserID
                  AND R.Year < 2017) AS NumOldCars
FROM Payroll AS P;
```

## 7. Subqueries in WHERE/HAVING *(슬라이드 p.68~70)*

WHERE/HAVING에서 subquery를 쓰면 그 결과로 **행을 필터링**할 수 있다. SQL 연산자와 1차 논리(first-order logic) 대응:

| SQL | 논리 표기 |
|---|---|
| `EXISTS (subq)` | ∅ ≠ {subq} |
| `NOT EXISTS (subq)` | ∅ = {subq} |
| `attribute IN (subq)` | e ∈ {subq} |
| `attribute NOT IN (subq)` | e ∉ {subq} |
| `val > ANY (subq)` | ∃e. val > e |
| `val > ALL (subq)` | ∀e. val > e |

- `IN`/`NOT IN`, `ANY`/`ALL`은 subquery 결과가 **정확히 한 컬럼**일 때만 정의됨

## 8. Example로 보는 EXISTS/IN/ANY/ALL *(슬라이드 p.72~96)*

### Ex.1~2: "차를 몰지 않는 사람" *(p.72~85)*
논리식: `P s.t. ∅ = {cars P drives}`

```sql
-- NOT EXISTS 버전
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE NOT EXISTS (SELECT * FROM Registry AS R WHERE P.UserID = R.UserID);
```
- 위는 correlated query. 논리식을 `P ∉ {people who drive}`로 바꿔 쓰면 **decorrelate**된 버전이 나온다:
```sql
-- NOT IN 버전 (decorrelated)
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE P.UserId NOT IN (SELECT UserID FROM Registry);
```
- **같은 문제를 서로 다른 논리식으로 표현하면, 서로 다른 (하지만 동치인) 쿼리가 나온다** — 밑바탕의 propositional logic을 분석하는 게 decorrelation의 핵심 도구

### Ex.3~4: "2016년 이전 차를 모는 사람" vs "오직 2016년 이전 차만 모는 사람" *(p.87~94)*
- "drive **a** car before 2016" → **존재(∃)** 명제: `∃(R.year<2016 ∧ R.userid=P.userid)` → `2016 > ANY (subq)`
- "**only** drive cars before 2016" → **전칭(∀)** 명제: `∀(R.year<2016 ∧ R.userid=P.userid)` → `2016 > ALL (subq)`
  - 이 둘은 결과가 다르다! Magda는 Civic(2016)과 Ferrari(2000)를 둘 다 갖고 있어서 "drive a car before 2016"에는 해당(ANY)하지만 "only drive cars before 2016"에는 해당하지 않음(ALL 조건 위반)

### Ex.5: ALL을 EXISTS로 재작성(De Morgan) *(p.95~99)*
```
P s.t. ∀ R.year < 2016
     ≡ P s.t. ¬¬(∀ R.year < 2016)
     ≡ P s.t. ¬∃R. ¬(year < 2016)     (드모르간: ¬∀x.φ ≡ ∃x.¬φ)
     ≡ P s.t. ¬∃R. year ≥ 2016
```
→ SQL로:
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE NOT EXISTS (SELECT * FROM Registry AS R
                   WHERE P.UserID = R.UserID AND R.Year >= 2016);
```
- (단, `R.year`가 NULL이 아니라고 가정한 변환)

### Ex.6: SQL에 없는 연산자(isEven) 표현하기 *(p.101~106)*
"오직 짝수 연도에 만들어진 차만 모는 사람" → `∀ isEven(R.year)`. SQL엔 `isEven()`이 없으므로, 드모르간으로 `¬∃ isOdd(R.year)`로 바꾸고 `isOdd(x)`는 `MOD(x,2)=1`로 표현:
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE NOT EXISTS (SELECT * FROM Registry AS R
                   WHERE P.UserID = R.UserID AND MOD(R.Year, 2) = 1);
```
- **De Morgan's Laws(∀↔∃ 변환)를 쓰면 SQL이 직접 지원하지 않는 연산도 표현 가능**해진다 — 문제를 풀리게 만드는 사례

## 9. Subquery 관련 주의점 *(슬라이드 p.108~112)*

- **Edge case를 항상 생각할 것**: zero matches(매칭 0개), NULL 값
  - `∀R.year < 2017`과 `¬∃R.year ≥ 2017`은 논리적으로 동치이지만, **차의 year가 NULL인 경우엔 다르게 동작**할 수 있음(3값 논리 때문)
  - "차가 없는 사람(Frances)"을 "짝수 연도 차만 모는 사람"에 포함시킬지는 애매한 설계 판단 — 명확한 정답이 없고 요구사항에 따라 다름
- **Subquery가 항상 먼저 계산되어 저장되는 게 아니다** — optimizer가 전체 쿼리와 함께 최적화하므로 실제 실행은 훨씬 효율적일 수 있음
- 따라서 **subquery는 가독성을 위해 쓰는 것이지, 성능을 위해 쓰는 게 아니다** — 성능은 optimizer의 책임(physical data independence)

## 10. Monotonicity(단조성) *(슬라이드 p.116~130)*

> **Monotonic 쿼리 q**: 데이터 인스턴스 I, J에 대해 `I ⊆ J → q(I) ⊆ q(J)`
> 즉, **입력 테이블에 행을 더 추가해도 재실행했을 때 이전 결과가 사라지지 않는다**

(수학의 단조증가함수 `x≤y → f(x)≤f(y)`와 같은 개념 — eˣ, x³, arctan(x)는 단조증가, sin(x)·e⁻ˣ·tan(x)는 아님)

### 예시로 판별하기 *(p.121~130)*
- **Ex#1 (단순 INNER JOIN)**: 새 행(Tesla)을 추가해도 기존 결과가 유지되고 새 조합만 추가됨 → **Monotone** (SFW 쿼리는 새 데이터가 결과를 지울 수 없음)
- **Ex#2 (subquery로 최고 연봉자 찾기)**: 더 높은 연봉의 새 행을 추가하면 기존 최고 연봉자가 결과에서 **사라짐** → **Not Monotone**
- **GROUP BY COUNT(*)**: 새 행을 추가해 그룹의 count가 바뀌면(예: TA count가 2→3), 이전 결과 행 `(TA, 2)`는 사라지고 `(TA, 3)`으로 대체됨 → **Not Monotone** (aggregate는 일반적으로 새 tuple에 민감함)
  - 단, 완전히 새로운 그룹(Researcher)이 추가되는 경우는 기존 그룹 결과에 영향 없음 → 그 케이스만 보면 monotone처럼 보이지만, 값이 바뀌는 케이스가 하나라도 있으면 전체 쿼리는 not monotone
- **Ex#3 (NOT EXISTS로 차 없는 사람 찾기)**: 새 차량 행을 추가하면 그 사람이 "차 없는 사람" 목록에서 **빠짐** → **Not Monotone**

## 11. 유용한 정리(Theorem) *(슬라이드 p.132~136)*

> **정리**: Q가 subquery와 aggregate가 없는 SELECT-FROM-WHERE 쿼리라면, Q는 **항상 monotone**이다

**증명(스케치)**: nested-loop semantics로 보면, 새 tuple이 어떤 relation Rᵢ에 추가돼도 그 relation을 순회하는 for-loop이 **한 번 더 도는 것**뿐이다. 기존에 조건을 만족해 출력되던 (a₁,...,aₖ) 조합은 여전히 그대로 출력되고, 새 tuple로 인해 만족되는 조합이 있으면 결과에 *추가*만 될 뿐 — 어떤 기존 출력도 사라지지 않는다.

### 정리의 대우(역이용) *(p.137)*
> 어떤 쿼리가 **not monotone**이라면, 그 쿼리는 subquery/aggregate 없는 단순 SFW로 표현할 수 없다

즉, "monotone이 아닌" 요구사항(예: "오직 ~만", "~하는 사람이 없는")을 표현하려면 반드시:
- **aggregate**를 쓰거나
- **`NOT EXISTS`**(∅ =)를 쓰거나
- **`NOT IN`**(∉)을 쓰거나
- **`ALL`**(∀)을 쓰는 subquery가 필요하다

이 정리는 "왜 이 문제엔 subquery가 꼭 필요한가"를 판단하는 실전 기준이 된다 — 문제의 논리 구조에 부정(¬)이나 전칭(∀)이 숨어 있으면, 그건 monotone하지 않다는 신호이고 subquery/aggregate가 필요하다는 뜻이다.

## Lecture 6 핵심 요약

- Subquery는 쿼리를 helper-method처럼 분리해서 가독성을 높이는 도구. FROM/SELECT/WHERE/HAVING 어디든 위치 가능
- **Correlated subquery**는 outer row마다 재계산되는 "파라미터화된" subquery. Outer join+empty group 문제를 우아하게 해결 가능
- WHERE/HAVING의 `EXISTS/IN/ANY/ALL`은 1차 논리의 `∃`/`∈`/`∃`/`∀`에 대응 — 문제를 논리식으로 먼저 쓰고 De Morgan 법칙으로 변환하면 decorrelate하거나 SQL이 지원 안 하는 연산까지 표현 가능
- **Monotonicity**: 데이터 추가가 기존 결과를 절대 지우지 않는 성질. subquery/aggregate 없는 순수 SFW 쿼리는 항상 monotone → **not monotone한 요구사항은 반드시 aggregate나 NOT EXISTS/NOT IN/ALL이 필요**하다는 실전 판단 기준
