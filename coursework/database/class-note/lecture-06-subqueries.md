# Lecture 6: Subqueries — 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

> 정리 노트: `notes/lecture-06-subqueries.md` (슬라이드 p.6~137)
> 오늘 목표: 서브쿼리를 FROM/SELECT/WHERE 어디에든 써서 쿼리를 쪼개고, "오직 ~만", "~가 없는" 같은 요구사항을 논리식으로 바꿔 `EXISTS/IN/ANY/ALL`로 쓸 수 있다. 어떤 문제에 서브쿼리가 꼭 필요한지 판단할 수 있다.

## 0. 선수 개념 점검

1. **GROUP BY와 SELECT**: `GROUP BY`를 쓰면 `SELECT`에는 group by에 쓰인 컬럼과 aggregate 식만 올 수 있다. `WHERE`는 group by **전**에 행을 거르고, `HAVING`은 **후**에 그룹을 거른다.
2. **COUNT(\*) vs COUNT(attr)**: `COUNT(*)`는 전체 행 수, `COUNT(attr)`는 NULL을 거르고 센다. 행이 0개거나 전부 NULL인 입력에서 `COUNT`는 **0**, `SUM/AVG/MAX/MIN`은 **NULL**이다. **`COUNT`만 빈 입력에 0**이고 6번 섹션에서 쓰인다.
3. **LEFT OUTER JOIN**: 매칭이 없는 왼쪽 행은 남고, 오른쪽 컬럼은 NULL로 채워진다.
4. **`= NULL`**: 조건식의 값이 **UNKNOWN(0.5)**이다. `WHERE`는 TRUE(1)만 통과시키므로 전부 걸러진다. NULL 확인은 `IS NULL`(TRUE=1)로 한다. SQL의 비교 연산자는 `=` 하나다(`==` 아님).
5. **Self-join과 alias**: 같은 테이블 두 개를 구분하려면 alias가 필수다.

## 1. Subquery란? *(p.6~10)*

> **Subquery**: 다른 쿼리 안에 들어있는 쿼리. 프로그래밍의 **helper method**와 비슷하다. outer query의 일부를 따로 떼어내 단순화한다.

### 동기: "직군별 최고 연봉자는 누구인가?"
`Payroll(UserID, Name, Job, Salary)`에서 self-join + GROUP BY/HAVING으로 풀면:
```sql
SELECT P1.Name, MAX(P2.Salary)
FROM Payroll AS P1, Payroll AS P2
WHERE P1.Job = P2.Job
GROUP BY P1.Name, P1.Salary, P2.Job
HAVING P1.Salary = MAX(P2.Salary);
```
`GROUP BY`만으로는 최고 연봉이 "얼마"인지는 알아도 "누가" 받는지는 모르기 때문에 self-join이 필요해져 지저분하다. 한 번에 **두 연산(① 직군별 최댓값 ② 그 값을 가진 사람 찾기)**을 하고 있어서 읽기 어렵다.

### Subquery로 두 단계에 나누기
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P,
     (SELECT P1.Job AS Job, MAX(P1.Salary) AS MaxSalary
      FROM Payroll AS P1
      GROUP BY P1.Job) AS MP
WHERE P.Job = MP.Job AND P.Salary = MP.MaxSalary;
```
1st pass: subquery가 직군별 최댓값 테이블 `MP`를 만들고, 2nd pass: `MP`를 `Payroll`과 join해 "누구"를 찾는다.

### 예제 테이블과 MP 결과
| UserID | Name | Job | Salary |
|---|---|---|---|
| 1 | Leslie | TA | 40000 |
| 2 | Frances | TA | 50000 |
| 3 | Magda | Prof | 100000 |
| 4 | Riley | Prof | NULL |
| 5 | Quinn | NULL | 60000 |

`MP`:
| Job | MaxSalary |
|---|---|
| TA | 50000 |
| Prof | 100000 |
| NULL | 60000 |

- Prof 그룹은 Riley의 NULL이 무시돼 100000이다.
- **`GROUP BY`는 NULL끼리를 같은 그룹으로 묶는다**(`=` 비교와 규칙이 다름). 그래서 `(NULL, 60000)` 행이 생긴다.
- 최종 결과에서 **Quinn은 나오지 않는다**. `WHERE P.Job = MP.Job`에서 `NULL = NULL`이 UNKNOWN(0.5)이라 걸러지기 때문이다.

## 2. Subquery 문법 규칙, WITH *(p.11~15)*

- subquery가 **정확히 하나의 값(1 tuple, 1 attribute)**을 반환하면 → **값(field) 자리 어디에나** 쓸 수 있다.
- 그 외(여러 행/여러 컬럼)면 → **"추가 테이블"**처럼 취급된다. 테이블 이름(`AS MP`), 컬럼 이름(`AS MaxSalary`)을 붙일 수 있다.

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
- subquery를 `FROM` **앞에 먼저 정의**해서 더 "테이블처럼" 보이게 하는 문법이다.
- **WITH는 syntactic sugar**다. FROM-subquery 버전과 의미가 완전히 같다. 성능이 좋아지는 게 아니라 가독성용이다. helper method를 먼저 정의해두고 쓰는 느낌이다.

### 위치 *(p.15)*
`FROM`, `SELECT`, `WHERE/HAVING`. 테이블이나 값을 쓸 수 있는 곳이면 어디든 가능하다.

## 3. Subqueries in FROM *(p.17~18)*

- 방금 본 `MP`가 FROM 안의 subquery다.
- 결과를 "캐싱해서 나중에 join할 수 있는 **부분 문제(subproblem)**"로 쓴다.
- 진짜 테이블처럼 rows/columns를 가져 쿼리가 자연스럽게 읽힌다. Java 짤 때처럼 **helper method 감각**으로 SQL을 짤 수 있다.

### 확인 문제: 값 자리 vs 테이블 자리
```sql
-- (A) 맞는 쿼리
SELECT P.Name, (SELECT MAX(P1.Salary) FROM Payroll AS P1)
FROM Payroll AS P;

-- (B) 틀린 쿼리
SELECT P.Name, (SELECT P1.Job, MAX(P1.Salary) FROM Payroll AS P1 GROUP BY P1.Job)
FROM Payroll AS P;
```
- **(A)**: `GROUP BY`가 없어 전체를 요약한 **1행 × 1컬럼**이다. 값 하나라서 `SELECT` 목록에 들어갈 수 있다. 모든 행에 같은 값(상수)이 붙는 건 outer row와 무관하게 한 번 계산된 값이기 때문이다.
- **(B)**: `GROUP BY P1.Job`으로 TA, Prof, NULL의 **3행**, `Job`과 `MAX`의 **2컬럼** → **3행 × 2컬럼**이라 값 자리에 못 쓴다. 이런 결과는 `FROM`(테이블 자리)에 써야 한다.

| subquery 결과 | 쓸 수 있는 자리 |
|---|---|
| 1행 × 1컬럼 (값 하나) | `SELECT` 목록, `WHERE` 비교식 등 **값 자리** |
| 여러 행 / 여러 컬럼 | **테이블 자리**(`FROM`), 이름 붙이기 |

헷갈리기 쉬운 점: `SELECT` 안에 있다고 "컬럼 자리"가 아니다. `SELECT` 목록의 각 항목은 **값을 내는 식(expression)**이고(`SELECT Name, 5, Salary * 2, 'hello'`처럼 상수·계산식도 가능), 값 하나짜리 subquery도 그런 식 중 하나다.

## 4. Subqueries in SELECT, Correlated Subquery *(p.20~35)*

### 기본 규칙: 반드시 단일 값 반환 *(p.20)*
```sql
SELECT P.Name, (SELECT AVG(P1.Salary) FROM Payroll AS P1)
FROM Payroll AS P;
```
모든 행에 전체 평균이 똑같이 붙는다.

### Correlated Subquery *(p.21~22)*
각 사람 옆에 **그 사람 직군의 평균 연봉**을 붙이려면:
```sql
SELECT P.Name, (SELECT AVG(P1.Salary)
                FROM Payroll AS P1
                WHERE P.Job = P1.Job)
FROM Payroll AS P;
```
- subquery 안에서 **바깥 테이블 `P`를 참조** → **Correlated Subquery(상관 서브쿼리)**.
- 의미(semantics): outer의 **매 tuple마다 subquery를 처음부터 다시 계산**한다. subquery가 helper method라면 correlated subquery는 **파라미터를 받는 helper method**이고, outer row의 값이 파라미터다.

### 실행 흐름 *(p.23~29)*
- P = Leslie(TA) → TA인 행들(Leslie 40k, Frances 50k) 평균 → **45k**
- P = Frances(TA) → **45k**
- P = Magda(Prof) → Prof 행들(Magda 100k, Riley NULL), NULL은 무시 → **100k**
- P = Riley(Prof) → **100k**
- P = Quinn(NULL) → `P.Job = P1.Job`이 `NULL = NULL`(UNKNOWN)이라 전부 걸러져 **행 0개의 AVG → NULL**

결과에 `AS AvgSal` 같은 alias도 붙일 수 있다. subquery 출력에도 별칭을 줄 수 있다.

## 5. Correlated Subquery의 성능 *(p.37~39)*

- 그대로 실행하면 outer row가 N개일 때 subquery를 N번 돌리는 **nested loop**가 되어 비효율적일 수 있다.
- 좋은 optimizer는 **decorrelate**(join 형태로 재작성)한다:
```sql
-- 원래 (correlated)
SELECT P.Name, (SELECT AVG(P1.Salary) FROM Payroll AS P1 WHERE P.Job = P1.Job)
FROM Payroll AS P;

-- decorrelate된 형태 (join + group by)
SELECT P1.Name, AVG(P2.Salary)
FROM Payroll AS P1, Payroll AS P2
WHERE P1.Job = P2.Job
GROUP BY P1.Name;
```
- 단순한 엔진은 nested loop로 직접 실행해 느릴 수 있고, 현대적 엔진은 자동으로 decorrelate한다. optimizer를 확신할 수 없으면 correlated subquery를 피하는 게 안전하다.

### 두 쿼리는 항상 같은가? → 아니다
- 원래(correlated): Quinn 행이 **나오고** 평균은 NULL이다(outer row는 그대로 순회).
- decorrelate(inner join): `NULL = NULL`이 UNKNOWN이라 Quinn이 join에서 매칭 상대가 없어 **결과에서 통째로 사라진다**.
- 슬라이드의 decorrelate 예시는 **매칭이 항상 있다고 가정**할 때만 동치다. 엄밀히는 `LEFT OUTER JOIN`이 필요하다. `GROUP BY P1.Name`은 이름이 유일하다는 가정도 깔려 있다.

## 6. 빈 그룹(Empty Groups) 문제, 다시 *(p.32~36, p.65~66)*

4강 문제: "차가 없는 사람도 포함해 사람별 차 대수를 세고 싶다(없으면 0)". `LEFT OUTER JOIN + GROUP BY`로 풀었던 것을 correlated subquery로:
```sql
SELECT P.Name, (SELECT COUNT(R.Car)
                FROM Registry AS R
                WHERE P.UserID = R.UserID) AS NumCars
FROM Payroll AS P;
```
- outer는 `Payroll`의 **모든 행**을 순회하므로 사람이 빠지지 않는다.
- Frances처럼 매칭이 없으면 subquery는 빈 결과셋에 `COUNT` → **0**. (`SUM`/`MAX`였다면 **NULL**이 나온다. 빈 입력에 0을 내는 건 `COUNT`뿐.)
- `LEFT OUTER JOIN + GROUP BY`와 같은 효과를 더 직관적으로 얻는다.

### 응용: 2017년 이전에 등록된 차의 개수
```sql
SELECT P.Name, (SELECT COUNT(R.Car)
                FROM Registry AS R
                WHERE P.UserID = R.UserID
                  AND R.Year < 2017) AS NumOldCars
FROM Payroll AS P;
```
`LEFT OUTER JOIN`에서 `WHERE R.Year < 2017`을 바깥에 쓰면 NULL로 채워진 행이 걸러져 차 없는 사람이 사라지는 함정(조건을 `ON`에 넣어야 함)이 있었는데, subquery 버전은 구조적으로 그 문제가 없다.

## 7. Subqueries in WHERE/HAVING *(p.68~70)*

`WHERE/HAVING`에 쓰면 결과로 **행을 필터링**한다. SQL 연산자와 1차 논리의 대응:

| SQL | 논리 표기 | 읽는 법 |
|---|---|---|
| `EXISTS (subq)` | ∅ ≠ {subq} | 결과가 하나라도 있다 |
| `NOT EXISTS (subq)` | ∅ = {subq} | 결과가 하나도 없다 |
| `attr IN (subq)` | e ∈ {subq} | 결과 집합에 포함된다 |
| `attr NOT IN (subq)` | e ∉ {subq} | 결과 집합에 포함되지 않는다 |
| `val > ANY (subq)` | ∃e. val > e | 결과 중 **하나라도** 만족 (존재) |
| `val > ALL (subq)` | ∀e. val > e | 결과 **전부** 만족 (전칭) |

- `IN/NOT IN`, `ANY/ALL`은 subquery 결과가 **정확히 한 컬럼**일 때만 쓸 수 있다. `EXISTS`는 컬럼 수와 무관하므로 보통 `SELECT *`를 쓴다.

### ANY/ALL의 빈 집합 처리 (확인 문제)
- `5 > ANY {3, 7}` → TRUE (5 > 3 성립), `5 > ALL {3, 7}` → FALSE (5 > 7 깨짐)
- 빈 집합: `∃e. φ(e)`는 만족하는 원소를 못 찾으니 **FALSE**. `∀e. φ(e)`는 **반례(φ를 깨뜨리는 원소)가 하나도 없다**는 뜻이라 빈 집합엔 반례가 없어 **TRUE** (vacuous truth, 공허한 참).
- 정리: `val > ANY (빈 집합)` = FALSE, `val > ALL (빈 집합)` = TRUE.

## 8. EXISTS/IN/ANY/ALL 예제 *(p.72~106)*

문제를 풀 때 **먼저 논리식으로 쓰고 SQL로 옮긴다.** 테이블: `Payroll(UserID, Name, Job, Salary)`, `Registry(UserID, Car, Year)`.

### Ex.1~2: "차를 몰지 않는 사람" *(p.72~85)*
논리식: `P s.t. ∅ = {P가 모는 차들}`
```sql
-- NOT EXISTS 버전 (correlated)
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE NOT EXISTS (SELECT * FROM Registry AS R WHERE P.UserID = R.UserID);
```
같은 문제를 `P ∉ {차를 모는 사람들}`로 쓰면 decorrelated 버전이 나온다:
```sql
-- NOT IN 버전 (decorrelated)
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE P.UserID NOT IN (SELECT UserID FROM Registry);
```
같은 문제를 다른 논리식으로 표현하면 **서로 다른 (동치인) 쿼리**가 나오고, 논리를 바꿔 쓰는 게 decorrelation의 핵심 도구다.

### 함정: NOT IN과 NULL
`Registry.UserID`에 NULL이 하나라도 있으면 `3 NOT IN (1, 2, NULL)`은:
```
3 <> 1  AND  3 <> 2  AND  3 <> NULL
 TRUE   AND   TRUE   AND  UNKNOWN(0.5)   →  UNKNOWN
```
AND는 값 중 최솟값을 취하므로 UNKNOWN이고 `WHERE`에서 걸러진다. **모든 사람이 걸러져 결과가 통째로 빈다.** 반면 `NOT EXISTS` 버전은 NULL 행이 그냥 매칭에서 빠질 뿐 다른 사람의 판정에 영향이 없다.

| 상황 | NOT EXISTS | NOT IN |
|---|---|---|
| `Registry.UserID`에 NULL 없음 | 차 없는 사람 | 차 없는 사람 (동일) |
| `Registry.UserID`에 NULL 있음 | 차 없는 사람 | **빈 결과** (함정) |

NULL 가능성이 있는 컬럼에 `NOT IN`은 위험하고 `NOT EXISTS`가 더 안전하다.

### Ex.3~4: "2016년 이전 차를 모는 사람" vs "오직 2016년 이전 차만 모는 사람" *(p.87~94)*

| 요구사항 | 논리 | SQL |
|---|---|---|
| drive **a** car before 2016 | ∃ (존재) | `2016 > ANY (subq)` |
| **only** drive cars before 2016 | ∀ (전칭) | `2016 > ALL (subq)` |
```sql
-- 존재
SELECT P.Name, P.Salary FROM Payroll AS P
WHERE 2016 > ANY (SELECT R.Year FROM Registry AS R WHERE P.UserID = R.UserID);

-- 전칭
SELECT P.Name, P.Salary FROM Payroll AS P
WHERE 2016 > ALL (SELECT R.Year FROM Registry AS R WHERE P.UserID = R.UserID);
```
Magda가 Civic(2016)과 Ferrari(2000)를 갖고 있으면 subquery 결과는 `{2016, 2000}`: ANY는 `2016 > 2000`이 성립해 포함, ALL은 `2016 > 2016`이 깨져 제외.

차가 한 대도 없는 **Frances**는 ALL 쿼리에서 빈 집합에 대해 TRUE이므로 **결과에 나온다**. "오직 옛날 차만 모는 사람"으로 부르는 게 자연스러운가는 명확한 정답이 없는 설계 판단이라, 요구사항에서 차 없는 사람을 포함할지 명시해야 하고, 빼려면 조건을 하나 더 붙여야 한다.

### Ex.5: ALL을 EXISTS로 재작성 (De Morgan) *(p.95~99)*
```
P s.t. ∀R. year < 2016
  ≡ P s.t. ¬¬(∀R. year < 2016)      (이중 부정)
  ≡ P s.t. ¬∃R. ¬(year < 2016)      (드모르간: ¬∀x.φ ≡ ∃x.¬φ)
  ≡ P s.t. ¬∃R. year ≥ 2016
```
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE NOT EXISTS (SELECT * FROM Registry AS R
                   WHERE P.UserID = R.UserID AND R.Year >= 2016);
```
단, `R.Year`가 NULL이 아니라는 가정에서의 변환이다.

### Ex.6: SQL에 없는 연산자 표현하기 *(p.101~106)*
"오직 **짝수 연도**에 만들어진 차만 모는 사람" → `∀ isEven(R.year)`. SQL엔 `isEven()`이 없으므로 `¬∃ isOdd(R.year)`로 바꾸고 `isOdd(x)`를 `MOD(x, 2) = 1`로 쓴다.
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE NOT EXISTS (SELECT * FROM Registry AS R
                   WHERE P.UserID = R.UserID AND MOD(R.Year, 2) = 1);
```
드모르간 법칙(∀↔∃ 변환)을 쓰면 SQL이 직접 지원하지 않는 연산도 표현할 수 있다.

### 확인 문제: "오직 2016년 이후 차만 모는 사람"
```
∀R. year > 2016  ≡  ¬∃R. ¬(year > 2016)  ≡  ¬∃R. year ≤ 2016
```
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE NOT EXISTS (SELECT * FROM Registry AS R
                   WHERE P.UserID = R.UserID AND R.Year <= 2016);
```
규칙: `∀ 조건` → `NOT EXISTS (조건의 부정)`. 부등호를 정확히 뒤집어야 하고(`>` ↔ `≤`, `<` ↔ `≥`) 경계값(`=`)을 어느 쪽에 넣는지 틀리기 쉽다. 이 쿼리도 차가 없는 Frances는 포함되고, `Year`가 NULL이면 `NULL <= 2016`이 UNKNOWN이라 반례로 안 잡혀 결과에 남는다.

## 9. Subquery 관련 주의점 *(p.108~112)*

1. **Edge case를 항상 생각**: zero matches, NULL. `∀R.year < 2017`과 `¬∃R.year ≥ 2017`은 논리적으로 동치지만 `year`가 NULL이면 3값 논리 때문에 다르게 동작할 수 있다. 차 없는 사람(Frances)을 포함할지는 요구사항에 따른 설계 판단이다.
2. **Subquery가 항상 먼저 계산·저장되는 게 아니다**: optimizer가 전체 쿼리와 함께 최적화한다.
3. **Subquery는 가독성을 위한 것이지 성능을 위한 게 아니다**: 성능은 optimizer의 책임(physical data independence).

### 확인 문제: NULL 연식의 차
"2017년 이후 등록된 차가 하나도 없는 사람"을 `NOT EXISTS ... R.Year >= 2017`로 쓰면, `Year`가 NULL인 차를 가진 사람은 **포함된다**(`NULL >= 2017`이 UNKNOWN이라 반례로 안 잡혀 subquery가 비므로). 연식을 모르는 차가 2017년 이후일 수 있는데 "없다"고 단정하는 것이므로 요구사항에 안 맞을 수 있다. NULL을 어떻게 취급할지는 사람이 정해야 하고, NULL도 반례로 취급하려면 subquery 조건에 `OR R.Year IS NULL`을 넣는다.

## 10. Monotonicity *(p.116~130)*

> **Monotonic 쿼리 q**: 데이터 인스턴스 I, J에 대해 `I ⊆ J → q(I) ⊆ q(J)`. 입력에 행을 더 추가해도 이전 결과가 사라지지 않는다.

수학의 단조증가함수(`x ≤ y → f(x) ≤ f(y)`)와 같은 개념이다. eˣ, x³, arctan(x)는 단조증가, sin(x), e⁻ˣ, tan(x)는 아니다.

- **Ex#1 단순 INNER JOIN → Monotone**: 새 행(Tesla)을 추가해도 기존 결과가 유지되고 새 조합만 추가된다.
- **Ex#2 subquery로 최고 연봉자 찾기 → Not Monotone**: 더 높은 연봉의 새 행을 추가하면 기존 최고 연봉자가 결과에서 사라진다.
- **GROUP BY COUNT(\*) → Not Monotone**: 그룹의 count가 바뀌면(TA 2→3) `(TA, 2)`가 사라지고 `(TA, 3)`으로 대체된다. 완전히 새로운 그룹(Researcher) 추가만 보면 monotone처럼 보이지만, 값이 바뀌는 케이스가 하나라도 있으면 전체 쿼리는 not monotone이다.
- **Ex#3 NOT EXISTS로 차 없는 사람 찾기 → Not Monotone**: 새 차량 행을 추가하면 그 사람이 결과에서 빠진다.

### 확인 문제
```sql
-- (a) Monotone: 단순 SFW. 새 행은 결과에 추가될 뿐.
SELECT P.Name FROM Payroll AS P WHERE P.Salary > 50000;

-- (b) Not Monotone: ALL(∀)이라 TA 중 더 높은 연봉자를 추가하면 기존 통과자가 탈락.
SELECT P.Name FROM Payroll AS P
WHERE P.Salary > ALL (SELECT P1.Salary FROM Payroll AS P1 WHERE P1.Job = 'TA');

-- (c) Monotone: subquery가 있어도 EXISTS(양의 존재)라 새 행은 매칭을 늘릴 뿐.
SELECT P.Name FROM Payroll AS P
WHERE EXISTS (SELECT * FROM Registry AS R WHERE R.UserID = P.UserID);
```
**"subquery가 있다 = not monotone"이 아니다.** not monotone을 만드는 건 `NOT EXISTS`, `NOT IN`, `ALL`, aggregate처럼 **부정(¬)이나 전칭(∀)이 들어간 것**이다.

## 11. 유용한 정리 *(p.132~137)*

> **정리**: Q가 subquery와 aggregate가 없는 SELECT-FROM-WHERE 쿼리라면, Q는 **항상 monotone**이다.

**증명 스케치** (nested-loop 의미):
```
for each tuple t1 in R1:
  for each tuple t2 in R2:
    ...
      if (조건 만족) output(a1, ..., ak)
```
어떤 relation에 새 tuple이 추가돼도 그 relation을 도는 for-loop이 한 번 더 돌 뿐이다. 기존에 출력되던 조합은 그대로이고, 새 tuple로 만족되는 조합은 결과에 *추가*만 되므로 기존 출력이 사라질 수 없다.

### 대우 *(p.137)*
> 어떤 쿼리가 **not monotone**이면, subquery/aggregate 없는 단순 SFW로 표현할 수 없다.

즉 "오직 ~만", "~가 없는" 같은 not monotone 요구사항은 반드시 **aggregate**, **`NOT EXISTS`**(∅ =), **`NOT IN`**(∉), **`ALL`**(∀) 중 하나가 필요하다. 문제 구조에 부정(¬)이나 전칭(∀)이 숨어 있으면 not monotone이라는 신호다.

⚠️ 정리는 **한 방향**만 성립한다. "SFW → monotone"은 참이지만 "monotone이면 SFW로 쓸 수 있다"는 아니다(위 (c)처럼 subquery가 있는데 monotone인 쿼리가 있음).

### 마무리 문제: "2017년 이후 등록된 차가 하나도 없는 사람"을 단순 SFW로 못 쓰는 이유
이 쿼리는 not monotone이다. 어떤 사람에게 2017년 이후 차 행을 **새로 추가**하면 이전 결과에 있던 그 사람이 **사라진다**. 단순 SFW(+join)는 항상 monotone이므로 정리의 대우에 의해 표현할 수 없고, `NOT EXISTS`/`NOT IN`/`ALL` 같은 부정·전칭 구조가 필요하다.

## Lecture 6 핵심 요약

- Subquery는 쿼리를 helper method처럼 분리해 가독성을 높이는 도구다. FROM/SELECT/WHERE/HAVING 어디든 쓴다. **값 하나(1×1)는 값 자리, 그 외는 테이블 자리**.
- **Correlated subquery**는 outer row마다 재계산되는 "파라미터화된" subquery다. 빈 그룹 문제를 우아하게 풀지만(`COUNT`만 빈 입력에 0), decorrelate된 join 버전과는 NULL/무매칭 행에서 다를 수 있다.
- `EXISTS/IN/ANY/ALL`은 ∃/∈/∃/∀에 대응한다. `ALL`은 빈 집합에서 TRUE, `ANY`는 FALSE. 문제를 논리식으로 쓰고 **드모르간**으로 변환하면 decorrelate하거나 SQL이 지원 안 하는 연산까지 표현할 수 있다.
- **`NOT IN`은 NULL이 섞이면 결과가 통째로 빈다.** 안전한 건 `NOT EXISTS`다. edge case(zero matches, NULL)는 요구사항에 따라 사람이 결정한다.
- **Monotonicity**: 데이터 추가가 기존 결과를 지우지 않는 성질. 순수 SFW는 항상 monotone → not monotone한 요구사항은 aggregate나 `NOT EXISTS`/`NOT IN`/`ALL`이 필요하다.
