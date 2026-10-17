# Lecture 6: Subqueries

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*Database Management Systems, 3rd ed. (Ramakrishnan & Gehrke)*

슬라이드 하단 쪽번호가 일부 잘려 있어 아래 새로 추가한 항목의 `p.N`은 PDF 페이지 순서 기준이다.

## 0. 도입: 복습 Q와 Developing/Debugging 팁 *(PDF p.2~5, p.20)*

### 슬라이드 Q *(p.2)*
- 직군별 최고 연봉을 가진 사람의 이름을 구하는 쿼리를 써보라 (답 없음). 슬라이드 문구: *"If you're having a hard time with SQL, write a Java program instead"*

| UserID | Name | Job | Salary |
|---|---|---|---|
| 123 | Leslie | TA | 50k |
| 345 | Frances | TA | 60k |
| 567 | Magda | Prof | 120k |
| 789 | Quinn | Prof | 100k |

기대 출력: (Frances, TA, 60k), (Magda, Prof, 120k) — 컬럼 `Name, Job, MAX(Salary)`

### Developing/Debugging SQL Tips *(p.4)*
1. **데이터 크기를 3가지로 나눠 쓴다**
   - **아주 작은 수동 생성 데이터셋**(5행? 20행?): 문법 확인, edge case(빈 결과, 주말, 차 없는 TA 등) 점검. 결과를 손으로 계산해 쿼리 출력과 비교 가능
   - **중간 크기 데이터셋**(100행? 500행?): 가급적 전체 데이터를 대표. 쿼리 하나에 10분/2시간 걸리지 않을 정도. 모든 결과 행을 계산하긴 어렵지만 검증은 가능
   - **전체 데이터셋**: 결과 검증이 어려움
2. `<your query> LIMIT n;`
3. `<your query>`를 `SELECT COUNT(*) FROM ( <your query> )`로 바꿔 본다
4. 이번 강의 주제가 이 3번의 서브쿼리 문법(*"Today's topic!"*)

### Development/Debugging 예시 코드 *(p.20)*
```sql
CREATE TABLE FlightsSmall (
    -- copy-n-paste from Flights    ← 동일한 테이블 생성
);
INSERT INTO FlightsSmall VALUES
    (…), (…), (…), … (…);           ← 수동 생성/선택한 행으로 채움

INSERT INTO FlightsMedium …         ← 또는 무작위 1000행으로 채움
    (SELECT * FROM Flights LIMIT 1000);

SELECT ... FROM FlightsSmall ...
SELECT ... FROM FlightsMedium ...   -- Work faster on HW3!
```
- 쿼리를 개발할 때(문법 오류 확인 등)는 작은 데이터셋을 쓰고, 만족하면 전체 데이터셋에서 테스트

## 1. Subqueries란? *(슬라이드 p.6~7)*

**Subquery**: 다른 쿼리 안에 들어있는 쿼리

- 보통 outer query의 일부를 단순화하거나 분리해내는 역할
- 사용 사례가 프로그래밍의 **helper method**와 비슷함

### 동기: "직군별 최고 연봉자는 누구인가?" *(p.8~9)*
직군별 최고 연봉(`Job, MAX(Salary)` = TA 60k, Prof 120k)은 이미 구할 수 있지만, **그 연봉을 받는 사람이 누구인가?** (PDF p.7) → 위 Payroll 테이블에서 `Name, Job, MAX(Salary)` = (Frances, TA, 60k), (Magda, Prof, 120k)가 원하는 결과.

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
- 슬라이드 그림(PDF p.9, p.16): 1st pass 결과 `MP(Job, MaxSal)` = (TA, 60k), (Prof, 120k)를 `Payroll(UserID, Name, Job, Salary)` = (123, Leslie, TA, 50k), (345, Frances, TA, 60k), (567, Magda, Prof, 120k), (789, Quinn, Prof, 100k)와 join(`+`)

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

### 슬라이드 Q *(PDF p.18~19)*
- **p.18**: 사람마다 **2017년 이전에 만들어진 차를 몇 대 모는지** 구하는 SQL을 써보라. **Frances와 Quinn도 출력에 포함**하고 **FROM 절에 subquery를 사용**. 힌트 1: `COALESCE(c, val)`은 c가 NULL이면 val을 반환 (답 없음)
- **p.19**: 이산수학의 1차 논리를 떠올려보라 — **이중 부정 + De Morgan 법칙**을 써서 `∀x < 7`과 동치인 명제를 찾아라. 옆 사람과 확인 (답 없음. 아래 Ex.5의 변환이 같은 패턴: `∀x<7 ≡ ¬¬∀x<7 ≡ ¬∃x. x≥7`)

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
- 슬라이드는 이 쿼리가 Frances에 대해 무엇을 하는지, 아래 두 쿼리 중 어느 것과 동치인지 물음 *(PDF p.37, 39)*:
```sql
-- (a) inner join
SELECT P.Name, COUNT(R.Car)
FROM Payroll AS P, Registry AS R
WHERE P.UserID = R.UserID
GROUP BY P.Name, P.UserID

-- (b) left outer join
SELECT P.Name, COUNT(R.Car)
FROM Payroll AS P
LEFT OUTER JOIN Registry AS R
    ON P.UserID = R.UserID
GROUP BY P.Name, P.UserID
```
  - 답: **(b)와 동치**. 슬라이드는 Frances(UserID 345)에 대해 subquery가 `SELECT COUNT(R.Car) FROM Registry AS R WHERE 345 = R.UserID` → **0**을 낸다고 보여줌 *(p.38)*, "Subquery will return 0 when there are no matching rows" *(p.39)*
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
- 슬라이드의 추가 질문 *(p.42)*: 이 쿼리를 **decorrelated 쿼리로 다시 쓸 수 있는가?** (답 없음)

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

- `IN`/`NOT IN`, `ANY`/`ALL`은 subquery 결과가 **정확히 한 컬럼**일 때만 정의됨 *(PDF p.47, SQL-Specific Notes)*

### Quantifier 논의 *(PDF p.71)*
- SQL(과 모든 관계형 질의 언어)은 **존재 한정사 ∃**를 자연스럽게 지원 — 매칭 record를 확인하는 **join**을 쓰면 됨. **`EXISTS`, `IN`, `ANY`는 사실상 join의 변형**
- **전칭 한정사 ∀**: SQL의 `ALL`은 매우 간결하지만 **∀가 표현할 수 있는 모든 것을 표현하지는 못한다** — 예: `P s.t. ∀( isEven(R.year) ∧ R.userid = P.userid )`
- 보통 **De Morgan 법칙으로 ∀를 ∃로 변환**: `NOT EXISTS`, `NOT IN`

## 8. Example로 보는 EXISTS/IN/ANY/ALL *(슬라이드 p.72~96)*

공통 예시 데이터 *(PDF p.48 이후 모든 예제)*:

| UserID | Name | Job | Salary |
|---|---|---|---|
| 123 | Leslie | TA | 50k |
| 345 | Frances | TA | 60k |
| 567 | Magda | Prof | 120k |
| 789 | Quinn | Prof | 100k |

| UserID | Car | Year |
|---|---|---|
| 123 | Charger | 2009 |
| 567 | Civic | 2016 |
| 567 | Ferrari | 2000 |
| 789 | Picklemobile | 2018 |

슬라이드는 쿼리를 **조각별로 쌓아 올리며** 만든다 (예: Ex.1은 `SELECT * FROM Registry AS R WHERE P.UserID = R.UserID` → `NOT EXISTS (…)` → 전체 쿼리 순서, *PDF p.50~52*).

### Ex.1~2: "차를 몰지 않는 사람" *(p.72~85)*
논리식: `P s.t. ∅ = {cars P drives}` — **결과: (Frances, 60k)**

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
- "drive **a** car before 2016" → **존재(∃)** 명제: `∃(R.year<2016 ∧ R.userid=P.userid)` → `2016 > ANY (subq)` *(PDF p.61~66)*
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE 2016 > ANY (SELECT R.Year
                  FROM Registry AS R
                  WHERE P.UserID = R.UserID)
```
  - 슬라이드가 subquery를 `SELECT R.Year FROM Registry AS R WHERE P.UserID = R.UserID` → `ANY (…)` → `2016 > ANY (…)` 순서로 쌓음. **결과: (Leslie, 50k), (Magda, 120k)** — Magda는 차 중 하나(Ferrari 2000)만 맞지만 출력에 포함
- **슬라이드 Q** *(p.67)*: "**only** drive cars made before 2016"의 명제 `P s.t. ???`를 써보라 (직전 문제는 `∃R.year<2016`로 번역됐음을 상기). 기대 결과는 Leslie 50k만 (*"Only 1 of Magda's cars match, so she is excluded"*)
- "**only** drive cars before 2016" → **전칭(∀)** 명제: `∀(R.year<2016 ∧ R.userid=P.userid)` → `2016 > ALL (subq)` *(p.68~70)*
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE 2016 > ALL (SELECT R.Year
                  FROM Registry AS R
                  WHERE P.UserID = R.UserID)
```
  - **결과: (Leslie, 50k)**. 슬라이드 주석: 한정사(quantifier)만 빼면 Ex.3과 명제가 동일해서 쿼리 개발 과정은 생략
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
- (단, `R.year`가 NULL이 아니라고 가정한 변환 — 슬라이드 주석 *"We are assuming that year cannot be NULL"*)
- 슬라이드는 이 시점에서 join 조건을 명제에서 생략하겠다고 선언함 (*"Henceforth, I'll elide the join from the proposition"*, p.73) — 명제를 `P s.t. ∀R.year<2016`처럼 줄여 씀
- **같은 명제의 두 SQL 표현이 동치임** *(PDF p.80)*: `2016 > ALL (SELECT R.Year …)` ≡ `NOT EXISTS (SELECT * … AND R.Year >= 2016)`. 결과는 둘 다 (Leslie, 50k)
- **슬라이드 Discussion** *(p.81)*: 차 year가 NULL인 차가 있다고 하자. 명제 `P s.t. ∀R.year < 2017`과 `P s.t. ¬∃R.year ≥ 2017` 중 그 사람이 결과에 포함되는 것은? (답 없음 — 본문 9절에서 둘이 동치가 아니라고 정리)

### Ex.6: SQL에 없는 연산자(isEven) 표현하기 *(p.101~106)*
"오직 짝수 연도에 만들어진 차만 모는 사람" → `∀ isEven(R.year)`. SQL엔 `isEven()`이 없으므로, 드모르간으로 `¬∃ isOdd(R.year)`로 바꾸고 `isOdd(x)`는 `MOD(x,2)=1`로 표현:
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P
WHERE NOT EXISTS (SELECT * FROM Registry AS R
                   WHERE P.UserID = R.UserID AND MOD(R.Year, 2) = 1);
```
- **De Morgan's Laws(∀↔∃ 변환)를 쓰면 SQL이 직접 지원하지 않는 연산도 표현 가능**해진다 — 문제를 풀리게 만드는 사례
- 변환 과정 *(PDF p.83~87)*: `∀ isEven(R.year)` ≡ `¬¬(∀ isEven(R.year))` ≡ `¬∃ ¬isEven(R.year)` ≡ `¬∃ isOdd(R.year)`. 앞서 `P s.t. ∀R.year<2016`을 `2016 > ALL (…)`로 쓴 것처럼 하려 해도 SQL엔 `isEven()` 연산자가 없다(p.85)
- **결과: (Frances, 60k), (Magda, 120k), (Quinn, 100k)** — 슬라이드 질문: **차가 없는 Frances를 "짝수 연도에 만든 차를 모는 사람"에 포함시켜야 하는가?** (p.84)

### 세 묶음 정리 *(PDF p.88)*
6개 예제에서 **4개 문제**를 풀었고, 밑바탕의 명제 논리를 살펴본 덕분에:
- 한 문제를 **decorrelate** (Ex.1 → 2)
- 다른 문제를 **추론하기 쉽게** 만듦 (Ex.4 → 5)
- 한 문제를 **풀 수 있게** 만듦 (Ex.6)

## 9. Subquery 관련 주의점 *(슬라이드 p.108~112)*

- **Edge case를 항상 생각할 것**: zero matches(매칭 0개), NULL 값
  - `∀R.year < 2017`과 `¬∃R.year ≥ 2017`은 논리적으로 동치이지만, **차의 year가 NULL인 경우엔 다르게 동작**할 수 있음(3값 논리 때문)
  - "차가 없는 사람(Frances)"을 "짝수 연도 차만 모는 사람"에 포함시킬지는 애매한 설계 판단 — 명확한 정답이 없고 요구사항에 따라 다름
- **Subquery가 항상 먼저 계산되어 저장되는 게 아니다** — optimizer가 전체 쿼리와 함께 최적화하므로 실제 실행은 훨씬 효율적일 수 있음
- 따라서 **subquery는 가독성을 위해 쓰는 것이지, 성능을 위해 쓰는 게 아니다** — 성능은 optimizer의 책임(physical data independence)
  - 슬라이드는 "optimizer가 전체 쿼리와 함께 최적화하면 훨씬 효율적일 수 있다 (**why?**)"라고 묻고 답은 적지 않음 *(PDF p.92)*
- **슬라이드 Q** *(PDF p.94)*: 모든 직원의 `userid, name, salary`와 **직군별 최고 연봉**을 출력하는 쿼리를 써보라. **correlated subquery**로 가능한가? **decorrelated subquery**로? **subquery 없이**도 가능한가? (답 없음)

| UserID | Name | Job | Salary | Per-Job Max Salary |
|---|---|---|---|---|
| 123 | Leslie | TA | 50k | 60k |
| 345 | Frances | TA | 60k | 60k |
| 567 | Magda | Prof | 120k | 120k |
| 789 | Quinn | Prof | 100k | 120k |

## 10. Monotonicity(단조성) *(슬라이드 p.116~130)*

**Monotonic 쿼리 q**: 데이터 인스턴스 I, J에 대해 `I ⊆ J → q(I) ⊆ q(J)`
즉, **입력 테이블에 행을 더 추가해도 재실행했을 때 이전 결과가 사라지지 않는다**

(수학의 단조증가함수 `x≤y → f(x)≤f(y)`와 같은 개념 — eˣ, x³, arctan(x)는 단조증가, sin(x)·e⁻ˣ·tan(x)는 아님)

슬라이드 정의 원문 *(PDF p.96)*: 임의의 superset에 대해 그 superset 위의 쿼리 결과는 I 위의 결과를 **최소한 포함**해야 한다. 즉 **입력 테이블에 tuple을 더 추가해도 q를 다시 실행했을 때 출력 tuple이 지워지지 않는다**.

### 예시로 판별하기 *(p.121~130)*
- **Ex#1 (단순 INNER JOIN)** *(PDF p.98~100)*: "모든 직원과 그들의 차를 반환" → **Monotone**. Payroll이나 Registry에 tuple을 추가해도 이전 결과를 "제거"할 수 없음
```sql
SELECT P.Name, P.Car
FROM Payroll AS P, Registry AS R
WHERE P.UserID = R.UserID
```
  - 기존 결과: (Leslie, Charger), (Magda, Civic), (Magda, Ferrari), (Quinn, Picklemobile)
  - Registry에 `(345, Tesla, 2022)`를 추가하면 → 기존 결과 **⊂** 기존 + (Frances, Tesla): 새 행만 늘어남
  - Payroll에 `(012, Tumaini, TA, 25k)`를 추가하면 → Registry에 매칭이 없으므로 결과 **= 동일**
  - (참고: 슬라이드 쿼리의 `P.Car`는 Payroll에 없는 컬럼이라 `R.Car`의 오타로 보인다)
- **Ex#2 (subquery로 최고 연봉자 찾기)** *(p.101)*: **Not Monotone** — 더 높은 연봉의 새 행을 추가하면 기존 최고 연봉자가 결과에서 **사라짐**
```sql
SELECT P.Name
FROM Payroll AS P
WHERE P.Salary = (SELECT MAX(Salary)
                  FROM Payroll)
```
- **슬라이드 Q** *(p.102)*: 아래 쿼리는 monotone인가? 단조성(또는 아님)을 보여줄 행을 하나 추가해보라 (답은 다음 슬라이드: **No**)
```sql
SELECT P.Job, COUNT(*)
FROM Payroll AS P
GROUP BY P.Job
```
  - 기존 결과: (TA, 2), (Prof, 2)
- **GROUP BY COUNT(*)**: 새 행을 추가해 그룹의 count가 바뀌면(예: TA count가 2→3), 이전 결과 행 `(TA, 2)`는 사라지고 `(TA, 3)`으로 대체됨 → **Not Monotone** (aggregate는 일반적으로 새 tuple에 민감함)
  - 새 행 `(100, Riley, Researcher, 80k)`을 추가하면 결과가 (TA,2), (Prof,2), **(Researcher,1)**로 **기존 결과 ⊆ 새 결과** *(p.103)* — 이 케이스만 보면 monotone처럼 보임
  - 새 행 `(200, Tumaini, TA, 25k)`를 추가하면 결과가 (TA, **3**), (Prof, 2)로 바뀌어 **(TA, 2)가 사라짐** (슬라이드: *"Our old row with Count=2 is gone!"*) *(p.104)* → 하나라도 이런 케이스가 있으면 전체 쿼리는 not monotone
  - 슬라이드 요약: *"Aggregates are generally sensitive to any new tuples!"* *(p.105)*
- **Ex#3 (NOT EXISTS로 차 없는 사람 찾기)** *(p.106~109)*: **Not Monotone** — 새 차량 행을 추가하면 그 사람이 "차 없는 사람" 목록에서 **빠짐**
```sql
SELECT P.Name
FROM Payroll AS P
WHERE NOT EXISTS (SELECT *
                  FROM Registry AS R
                  WHERE P.UserID = R.UserID)
```
  - 기존 결과: (Frances)
  - Payroll에 `(200, Tumaini, TA, 25k)`를 추가하면 → 결과 (Frances) ⊆ (Frances, Tumaini): 이 경우엔 오히려 늘어남 *(p.108)*
  - Registry에 `(345, Tesla, 2022)`를 추가하면 → **Frances가 결과에서 사라짐** *(p.109)* → not monotone

## 11. 유용한 정리(Theorem) *(슬라이드 p.132~136)*

**정리**: Q가 subquery와 aggregate가 없는 SELECT-FROM-WHERE 쿼리라면, Q는 **항상 monotone**이다 *(PDF p.111)*
```sql
SELECT a1, a2, …, ak
FROM R1 AS x1, R2 AS x2, …, Rn AS xn
WHERE conditions
```
**증명에 쓰는 nested-loop semantics** *(PDF p.112~115)*:
```
for x1 in R1 do
    for x2 in R2 do
        …
            for xn in Rn do
                if Conditions
                    output (a1,…,ak)
```
- R2에 새 tuple을 insert하면 → x2가 tuple 하나를 더 순회할 뿐 → **기존 출력 결과는 하나도 잃지 않는다**

**증명(스케치)**: nested-loop semantics로 보면, 새 tuple이 어떤 relation Rᵢ에 추가돼도 그 relation을 순회하는 for-loop이 **한 번 더 도는 것**뿐이다. 기존에 조건을 만족해 출력되던 (a₁,...,aₖ) 조합은 여전히 그대로 출력되고, 새 tuple로 인해 만족되는 조합이 있으면 결과에 *추가*만 될 뿐 — 어떤 기존 출력도 사라지지 않는다.

### 정리의 대우(역이용) *(p.137)*

어떤 쿼리가 **not monotone**이라면, 그 쿼리는 subquery/aggregate 없는 단순 SFW로 표현할 수 없다

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

---

## 수업에서 다룬 섹션

1. Subquery란? + 동기 (직군별 최고 연봉자)
2. Subquery 문법 규칙, WITH 절
3. Subqueries in FROM
4. Subqueries in SELECT, Correlated Subquery
5. Correlated Subquery의 성능, decorrelate
6. 빈 그룹(Empty Groups) 문제, 다시
7. Subqueries in WHERE/HAVING
8. EXISTS/IN/ANY/ALL 예제 (Ex.1~6)
9. Subquery 관련 주의점
10. Monotonicity
11. 유용한 정리(Theorem)와 그 대우
