# Lecture 5: Aggregates

*Database Management Systems, 3rd ed. (Ramakrishnan & Gehrke)*

## 1. 지금까지: Joined Tables 위의 단순 쿼리 *(슬라이드 p.9)*

지금까지는 join된 테이블 위에서 **단순 쿼리**(행 단위 필터링)를 다뤘다. 이제는 **하나의 테이블을 요약(summarize)하는 복잡한 쿼리**를 다룬다.

## 2. SQL Aggregation Functions *(슬라이드 p.10~14)*

### 왜 필요한가 *(p.10)*

| 비즈니스 질문 | 연산 |
|---|---|
| "이 영화 얼마나 인기 있어?" | COUNT |
| "커피에 돈을 너무 많이 쓰나?" | SUM |
| "커피 평균 가격은?" | AVG(mean) |
| "반에서 누가 제일 높은 점수 받았어?" | MAX |
| "이 거리에서 제일 싼 음식은?" | MIN |

- 기본 5개 aggregation 함수: **COUNT, SUM, AVG, MAX, MIN**. 일부 DB는 stddev, var, checksum 등도 지원 *(p.11)*

### AGG(attr)의 동작 *(p.12)*
- `AGG(attr)`은 **NULL이 아닌 값들에 대해서만** 연산한다
- `AGG(DISTINCT attr)`로 중복 제거 후 연산도 가능
- **예외**: `COUNT(*)`는 NULL 필드와 상관없이 **모든 행**을 센다 (더 일반적으로 말하면, `*`는 특정 attribute가 아니라 "행 자체"처럼 동작)

### 예시 *(p.13~14)*
```sql
SELECT SUM(salary) FROM Payroll;
SELECT MAX(salary) FROM Payroll;
SELECT MIN(salary) FROM Payroll WHERE job='Researcher' OR job='Prof';
```
- salary가 NULL인 행(Riley)은 SUM/MAX/MIN 계산에서 자동으로 제외됨

```sql
SELECT COUNT(*) FROM Payroll;              -- 전체 행 수
SELECT COUNT(job) FROM Payroll;            -- job이 NULL이 아닌 행 수
SELECT COUNT(salary) FROM Payroll;         -- salary가 NULL이 아닌 행 수
SELECT COUNT(DISTINCT job) FROM Payroll;   -- job의 서로 다른 값 개수
```

## 3. GROUP BY *(슬라이드 p.16~29)*

### 문제 상황 *(p.16)*
"직군(Job)별 평균 salary"를 구하려면, Job 값마다 WHERE 조건을 바꿔 쿼리를 여러 번 날려야 했다:
```sql
SELECT AVG(Salary) FROM Payroll WHERE Job = 'TA';
SELECT AVG(Salary) FROM Payroll WHERE Job = 'Prof';
-- ... Job 종류마다 반복
```

### GROUP BY로 한 번에 *(p.17~20)*
```sql
SELECT Job, AVG(Salary)
FROM Payroll
GROUP BY Job;
```
- **Group-by는 matching column value 기준으로 데이터를 partition**한 뒤, 각 그룹에 aggregation을 적용
- **그룹 하나당 결과 행 하나**가 된다

**동작 순서(Order of Operations)** *(p.18~20)*:
1. 값 기준으로 tuple들을 그룹으로 묶는다 (Job='TA'인 것끼리, 'Prof'인 것끼리, ...)
2. 각 그룹에 aggregation을 적용한다

### Retained Fields (남는 필드) *(p.23~26)*
- **GROUP BY와 SELECT의 aggregation에 쓰인 필드만 남고, 나머지는 버려진다**
- 그룹화/집계에 안 쓰인 필드는 **SELECT절에 아예 쓸 수 없다**:
```sql
-- 잘못된 예 (에러): Name은 GROUP BY에도, aggregate에도 없음
SELECT Name, AVG(Salary)
FROM Payroll
GROUP BY Job;
```
- 이유: 한 그룹(예: Job='TA') 안에 Leslie, Frances처럼 서로 다른 Name이 여러 개 있을 수 있는데, 그중 어떤 Name을 대표로 골라야 할지 정할 수 없기 때문

### 여러 컬럼으로 GROUP BY *(p.27~28)*
```sql
SELECT Job, Name, AVG(Salary)
FROM Payroll
GROUP BY Job, Name;
```
- **(Job, Name) 조합이 같은 행끼리** 하나의 그룹이 됨 — 같은 Name이라도 Job이 다르면 별도 그룹, 같은 (Job,Name) 조합이 여러 행이면 하나로 합쳐짐

### 여러 Aggregation 함께 쓰기 *(p.29)*
```sql
SELECT Job, MIN(Salary), MAX(Salary)
FROM Payroll
GROUP BY Job;
```
- 한 GROUP BY에 여러 aggregate 함수를 동시에 적용 가능

## 4. HAVING *(슬라이드 p.31~32)*

- 가끔은 **그룹 자체를 통째로** 걸러내고 싶을 때가 있다 (예: `MIN(Salary) > 80000`인 그룹만 원함)
- 이건 WHERE절로 표현할 수 없다 — **WHERE는 한 번에 한 개의 개별 레코드만 검사**하기 때문
- 대신 **HAVING** 절을 사용:
```sql
SELECT Job, MAX(Salary)
FROM Payroll
GROUP BY Job
HAVING AVG(Salary) > 55000;
```
- **WHERE는 tuple(개별 행)을 필터링**, **HAVING은 group(집계된 그룹)을 필터링**
- HAVING은 partitioning 자체나, 집계에 쓰인 원본 행들을 바꾸지 못한다 — 이미 계산된 그룹 결과에 대한 후처리 필터일 뿐

## 5. WHERE vs HAVING: 다른 쿼리다! *(슬라이드 p.34~42)*

다음 두 쿼리는 **같은 결과가 아니다**:
```sql
-- Query 1
SELECT Job, AVG(Salary)
FROM Payroll
WHERE Salary > 50k
GROUP BY Job;

-- Query 2
SELECT Job, AVG(Salary)
FROM Payroll
GROUP BY Job
HAVING AVG(Salary) > 50k;
```
- **Query 1**: `Salary > 50k`인 **행만 먼저 걸러낸 뒤** 그 남은 행들로 그룹 평균을 계산 → TA 그룹의 평균이 필터링된 행들만으로 계산됨(예: 60k)
- **Query 2**: **모든 행으로** 먼저 그룹 평균을 계산한 뒤(TA=45k, Prof=110k), 그 평균값이 50k보다 큰 그룹만 남김 → TA는 탈락
- **다른 출력, 다른 실행 순서(execution)** — WHERE는 그룹화 *이전* 단계, HAVING은 그룹화 *이후* 단계에서 동작하기 때문

## 6. Query Mental Model: FJWGHOS *(슬라이드 p.43~58)*

SQL 쿼리의 각 절이 실제로 실행되는(개념적) 순서:

```
Tables/Relations
      ↓
FROM
      ↓
JOIN
      ↓
WHERE
      ↓
GROUP BY
      ↓
HAVING
      ↓
ORDER BY
      ↓
SELECT
```

이 순서를 머리글자로 **FJWGHOS**라고 부른다 (SQL 문법상 쓰는 순서 SELECT-FROM-...-ORDER BY와는 다르다는 점에 주의).

### 각 단계 설명 *(p.45~58)*
- **FROM/JOIN**: 모든 테이블을 join해서 "composite tuple"들을 만든다 — **어떤 필터링도 하기 전에** 먼저 전부 결합 (implicit `FROM A,B WHERE ...`도 JOIN 단계로 취급됨 — implicit join도 join이다!)
- **WHERE**: 방금 만들어진 composite tuple들을 걸러낸다. **그룹화 이전에** 필터링이 일어나므로, 여기서 걸러진 tuple이 속했던 그룹은 애초에 만들어지지도 않는다
- **GROUP BY**: 남은 tuple들을 그룹으로 묶고, 각 그룹에 aggregate들을 계산한다. 그룹핑 키와 집계값만 남고 나머지 attribute는 버려진다
- **HAVING**: 집계된 그룹들을 그 집계값 기준으로 걸러낸다
- **ORDER BY**: 남은 결과를 정렬한다
- **SELECT**: 남은 결과의 컬럼을 변환/선택한다 (예: `UPPER(Name)`처럼 컬럼 값 변형, 필요없는 컬럼 버리기)

> **오해 주의**: implicit 문법(`FROM A, B WHERE ...`)을 보면 join이 WHERE 단계에서 일어나는 것처럼 보이지만, 실제로는 **JOIN은 항상 WHERE보다 먼저** 일어난다. Implicit join도 결국 join이다.

## 7. Aggregates + Joins 함께 쓰기 *(슬라이드 p.60~71)*

**문제**: "2017년 이전에 만들어진 차를 각 사람이 몇 대씩 갖고 있는가?"
- "How many"(Aggregate: COUNT + 아마 GROUP BY) + "each person"(Join: 두 테이블의 attribute 결합) *(p.62)*

단계별로 FJWGHOS를 따라가며 쿼리를 완성:

```sql
-- 1. FROM/JOIN: 두 테이블 결합
SELECT ...
FROM Payroll AS p, Registry AS r
WHERE p.UserID = r.UserID;
```

```sql
-- 2. WHERE: 조건 추가 (2017년 이전)
SELECT ...
FROM Payroll AS p, Registry AS r
WHERE p.UserID = r.UserID
  AND r.Year < 2017;
```

```sql
-- 3. GROUP BY: 사람별로 묶기 (PK인 UserID로 그룹화)
SELECT p.UserID, COUNT(*) AS cnt
FROM Payroll AS p, Registry AS r
WHERE p.UserID = r.UserID
  AND r.Year < 2017
GROUP BY p.UserID;
```

```sql
-- 4. SELECT: UserID 대신 Name을 보여주고 싶다면, GROUP BY에도 추가해야 함
SELECT p.Name, COUNT(*) AS cnt
FROM Payroll AS p, Registry AS r
WHERE p.UserID = r.UserID
  AND r.Year < 2017
GROUP BY p.UserID, p.Name;
```
- 결과: Leslie(1), Magda(2) — TADA!

## 8. 빈 그룹(Empty Groups) 문제 *(슬라이드 p.75~81)*

위 쿼리 결과를 보면 **Frances(차 없음)와 Quinn(2018년식 차만 있음)의 그룹이 아예 안 보인다** — 원래 "0대"라고 나와야 할 사람들이 결과에서 통째로 빠져버림.

### 원인
- **WHERE는 그룹화 이전에 동작**하므로, WHERE에서 걸러진 tuple이 속한 그룹은 애초에 형성조차 되지 않는다 — 즉 count=0인 그룹은 만들어질 기회조차 없다

### Case #1: JOIN 자체 때문에 사라지는 경우 (Frances) *(p.76~80)*
- Frances는 Registry에 매칭되는 행이 아예 없어서 **inner join 단계에서부터** 사라짐
- 해결: **LEFT OUTER JOIN**으로 Payroll의 모든 행을 보존:
```sql
SELECT p.Name, COUNT(*) AS cnt
FROM Payroll AS p
     LEFT OUTER JOIN Registry AS r
     ON p.UserID = r.UserID
GROUP BY p.UserID, p.Name;
```
- 하지만 이것만으로는 **아직 틀림!** — Frances의 매칭 안 된 행이 `(Frances, NULL, NULL, NULL)`로 들어오는데, `COUNT(*)`는 **행 자체**를 세기 때문에 이 NULL 행도 1로 세어져 Frances가 "차 1대"로 잘못 나온다

### Case #2: WHERE 조건 때문에 사라지는 경우 (Quinn) *(p.81)*
- Quinn은 매칭되는 행(Picklemobile, 2018)이 있지만 `r.Year < 2017` 조건에 걸려서 사라짐 — outer join만으로는 해결 안 됨(그 자체로 별도 subquery 등이 필요, 이 강의에서는 "punt"하고 넘어감)

### 올바른 수정: COUNT(*)  대신 COUNT(r.UserID) *(p.81)*
```sql
SELECT p.Name, COUNT(r.UserID) AS cnt
FROM Payroll AS p
     LEFT OUTER JOIN Registry AS r
     ON p.UserID = r.UserID;
```
- `COUNT(r.UserID)`는 **NULL을 세지 않으므로**, 차가 없어서 outer join이 채워넣은 NULL 행은 카운트되지 않음 → Frances는 정확히 0으로 계산됨
- 교훈: outer join 뒤에 개수를 셀 때는 `COUNT(*)`가 아니라 **join된 쪽의 특정 컬럼**을 세야 NULL placeholder 행이 잘못 카운트되는 걸 막을 수 있다

## Lecture 5 핵심 요약

- 5대 aggregation 함수(COUNT/SUM/AVG/MAX/MIN)는 기본적으로 **NULL을 무시**하지만, `COUNT(*)`만은 예외 — 행 자체를 센다
- **GROUP BY**: 값 기준으로 그룹을 나눈 뒤 각 그룹에 집계 적용. GROUP BY나 aggregate에 없는 컬럼은 SELECT에 쓸 수 없다
- **HAVING**은 그룹(집계 이후)을 필터링, **WHERE**는 개별 행(집계 이전)을 필터링 — 서로 다른 단계에서 동작하므로 결과와 실행 모두 다를 수 있다
- **FJWGHOS**: FROM → JOIN → WHERE → GROUP BY → HAVING → ORDER BY → SELECT가 SQL의 실제(개념적) 실행 순서
- Join + Aggregate를 함께 쓸 때, **outer join으로 빈 그룹을 살리고, `COUNT(컬럼)`으로 NULL placeholder를 세지 않게** 주의해야 정확한 "0" 결과를 얻을 수 있다
