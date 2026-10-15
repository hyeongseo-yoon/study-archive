# Lecture 5: Aggregates — 수업노트

> 정리 노트: `notes/lecture-05-aggregates.md` (슬라이드 p.9~81)
> 오늘 목표: 테이블을 요약하는 쿼리(집계, 그룹핑)를 쓰고, SQL이 실제로 어떤 순서로 실행되는지 머릿속에서 그려서 결과를 예측할 수 있다.

## 0. 선수 개념 점검

- **`NULL = NULL`**: 결과는 **UNKNOWN(0.5)**이다. 참도 거짓도 아니라서 `WHERE`에서 걸러진다. NULL 확인은 `IS NULL`로 한다.
- **LEFT OUTER JOIN**: `A LEFT OUTER JOIN B`에서 B에 매칭되는 행이 없는 A의 행은 A 컬럼은 그대로, B 컬럼은 전부 NULL로 채워져서 나온다. 이 NULL 행이 8번 섹션에서 다시 나온다.
- **Implicit join**: `FROM A, B WHERE A.id = B.id`는 `INNER JOIN ... ON`과 동치다. 6번 섹션(FJWGHOS)에서 중요하다.
- **Alias**: `FROM Payroll AS p`. 편해서 쓰기도 하지만 **꼭 필요한 경우**가 있다. 같은 테이블을 두 번 쓰는 self-join, 두 테이블에 같은 이름의 컬럼이 있어서 `UserID`만 쓰면 모호할 때(오늘 쿼리의 `p.UserID`, `r.UserID`).
- **Primary Key**: 각 행을 유일하게 식별하는 컬럼이고, **NULL이 될 수 없다**. GROUP BY 컬럼을 고를 때 쓰인다.

## 1. 단순 쿼리에서 요약 쿼리로 *(p.9)*

지금까지는 행 하나하나를 보고 남길지 버릴지 정하는 쿼리였다. 오늘은 **여러 행을 모아서 값 하나로 요약**하는 쿼리를 배운다.

## 2. Aggregation 함수 *(p.10~14)*

수업에서 쓴 예제 테이블 `Payroll`(설명용으로 만든 것):

| UserID | Name    | Job  | Salary |
| ------ | ------- | ---- | ------ |
| 1      | Leslie  | TA   | 40000  |
| 2      | Frances | TA   | 50000  |
| 3      | Magda   | Prof | 100000 |
| 4      | Riley   | Prof | NULL   |
| 5      | Quinn   | NULL | 60000  |

### 예제
```sql
SELECT SUM(Salary) FROM Payroll;       -- 250000 (Riley의 NULL은 무시, 나머지 4개 합)
SELECT COUNT(*) FROM Payroll;          -- 5
SELECT COUNT(Salary) FROM Payroll;     -- 4
SELECT COUNT(Job) FROM Payroll;        -- 4
SELECT COUNT(DISTINCT Job) FROM Payroll;  -- 2 (TA, Prof. NULL은 무시)
```

### 규칙

| 형태            | 세는 대상                                |
| ------------- | ------------------------------------ |
| `COUNT(attr)` | 그 컬럼이 **NULL이 아닌 행**만 센다             |
| `COUNT(*)`    | 컬럼을 안 보고 **행 자체**를 센다. NULL 여부와 상관없다 |

- `SUM`, `AVG`, `MAX`, `MIN`도 `COUNT(attr)`처럼 **NULL이 아닌 값에만** 연산한다. `COUNT(*)`만 예외다. `*`는 특정 컬럼이 아니라 "행 하나"처럼 동작한다.

### 시그니처
```sql
AGG(attr)            -- AGG ∈ {COUNT, SUM, AVG, MAX, MIN}
AGG(DISTINCT attr)   -- 중복 제거 후 연산
COUNT(*)             -- 행 수
```
- **반환값**: 테이블 전체를 요약해서 **행 1개, 값 1개**.
- **연산할 값이 하나도 없을 때**(전부 NULL이거나 행이 0개): `COUNT`는 0, `SUM`/`AVG`/`MAX`/`MIN`은 NULL이다(슬라이드엔 없고 표준 SQL 동작).
- **이름 풀이**: AVG는 average(mean), `DISTINCT`는 "서로 다른 값만".
- 기본 5개 외에 일부 DB는 stddev, var, checksum 등도 지원한다 *(p.11)*.

### 비즈니스 질문과 연산 *(p.10)*

| 비즈니스 질문                | 연산        |
| ---------------------- | --------- |
| "이 영화 얼마나 인기 있어?"      | COUNT     |
| "커피에 돈을 너무 많이 쓰나?"     | SUM       |
| "커피 평균 가격은?"           | AVG(mean) |
| "반에서 누가 제일 높은 점수 받았어?" | MAX       |
| "이 거리에서 제일 싼 음식은?"     | MIN       |

## 3. GROUP BY *(p.16~29)*

### 문제 상황 *(p.16)*
직군별 평균 월급을 구하려면 Job 값마다 쿼리를 따로 날려야 한다.
```sql
SELECT AVG(Salary) FROM Payroll WHERE Job = 'TA';
SELECT AVG(Salary) FROM Payroll WHERE Job = 'Prof';
-- 직군이 100개면 쿼리 100개...
```

### GROUP BY로 한 번에 *(p.17~20)*
```sql
SELECT Job, AVG(Salary)
FROM Payroll
GROUP BY Job;
```
- Job 값이 같은 행끼리 **partition**하고, 각 그룹에 aggregate를 적용한다.
- **그룹 하나당 결과 행 하나.** 결과 행 수는 원본 행 수가 아니라 **서로 다른 Job 값의 개수**다.
- 동작 순서: ① 값 기준으로 그룹을 묶는다 → ② 각 그룹에 aggregate를 적용한다.

결과(우리 테이블):

| Job  | AVG(Salary)              |
| ---- | ------------------------ |
| TA   | 45000                    |
| Prof | 100000 (Riley의 NULL은 무시) |
| NULL | 60000                    |

- **GROUP BY는 NULL끼리를 같은 값으로 취급해서 하나의 그룹으로 묶는다.** 그래서 Quinn(Job = NULL)은 빠지지 않고 자기만의 그룹이 된다. `NULL = NULL`이 UNKNOWN인 것과 다른 예외 규칙이다.

### Retained Fields: 남는 필드 *(p.23~26)*
```sql
-- 에러!
SELECT Name, AVG(Salary)
FROM Payroll
GROUP BY Job;
```
- TA 그룹의 결과 행은 하나인데, `Name` 칸에 Leslie와 Frances 중 뭘 넣을지 정할 수 없어서 에러다.
- **규칙**: GROUP BY 이후에 남는 건 **GROUP BY에 쓴 컬럼**과 **aggregate 결과**뿐이다. 나머지 컬럼은 버려지고 SELECT에도 쓸 수 없다.

### 여러 컬럼으로 GROUP BY *(p.27~28)*
```sql
SELECT Job, Name, AVG(Salary)
FROM Payroll
GROUP BY Job, Name;
```
- **(Job, Name) 조합이 같은 행끼리** 한 그룹이다. Name이 같아도 Job이 다르면 다른 그룹, 조합이 같은 행이 여러 개면 하나로 합쳐진다.
- 우리 테이블에서는 5행 모두 조합이 달라서 **그룹 5개 = 결과 5행**이다.

### 여러 aggregate 동시에 *(p.29)*
```sql
SELECT Job, MIN(Salary), MAX(Salary)
FROM Payroll
GROUP BY Job;
```
- 한 GROUP BY에 aggregate를 여러 개 붙여도 된다. 그룹마다 각각 계산해서 한 행에 나란히 나온다.

## 4. HAVING *(p.31~32)*

"평균 월급이 55000보다 큰 직군만"을 WHERE로 쓰면 에러다.
```sql
SELECT Job, AVG(Salary)
FROM Payroll
WHERE AVG(Salary) > 55000   -- 에러
GROUP BY Job;
```
- WHERE는 행을 하나씩 보는 필터라서, 여러 행을 모아야 나오는 `AVG(Salary)`를 그 자리에서 쓸 수 없다.
- 그룹이 만들어지고 집계가 끝난 뒤에 거르는 것이 **HAVING**이다.

```sql
SELECT Job, MAX(Salary)
FROM Payroll
GROUP BY Job
HAVING AVG(Salary) > 55000;
```

|            | 필터링 대상      | 시점         |
| ---------- | ----------- | ---------- |
| **WHERE**  | 개별 행(tuple) | 그룹화 **이전** |
| **HAVING** | 그룹          | 집계 **이후**  |

- HAVING은 이미 계산된 그룹 결과를 걸러내는 후처리다. 그룹을 나누는 방식이나 집계에 쓰인 원본 행은 바꾸지 못한다.
- 위 쿼리의 결과(판단은 AVG로, 출력은 MAX):

| Job  | AVG    | 통과? | 출력           |
| ---- | ------ | --- | ------------ |
| TA   | 45000  | 탈락  |              |
| Prof | 100000 | 통과  | MAX = 100000 |
| NULL | 60000  | 통과  | MAX = 60000  |

## 5. WHERE vs HAVING *(p.34~42)*

우리 테이블로 직접 비교:
```sql
-- Query 1
SELECT Job, AVG(Salary) FROM Payroll
WHERE Salary > 45000
GROUP BY Job;

-- Query 2
SELECT Job, AVG(Salary) FROM Payroll
GROUP BY Job
HAVING AVG(Salary) > 45000;
```

**Query 1** (WHERE → 행을 먼저 거름): 통과하는 행은 Frances 50000, Magda 100000, Quinn 60000. Leslie 40000은 탈락, Riley의 `NULL > 45000`은 UNKNOWN이라 탈락.

| Job  | AVG    |
| ---- | ------ |
| TA   | 50000  |
| Prof | 100000 |
| NULL | 60000  |

**Query 2** (HAVING → 그룹을 먼저 만들고 거름): TA의 평균은 Leslie까지 포함해 `45000`이고, `45000 > 45000`은 거짓이라 TA 그룹이 통째로 탈락.

| Job  | AVG    |
| ---- | ------ |
| Prof | 100000 |
| NULL | 60000  |

- TA 그룹이 Query 1에선 평균 50000으로 살아남고 Query 2에선 사라졌다. **WHERE는 그룹의 재료를 바꾸고, HAVING은 완성된 그룹을 버린다.** 서로 대체할 수 없다.

## 6. Query Mental Model: FJWGHOS *(p.43~58)*

SQL은 쓰는 순서와 실행되는 순서가 다르다. 개념적 실행 순서:

```
FROM → JOIN → WHERE → GROUP BY → HAVING → ORDER BY → SELECT
```

| 단계              | 하는 일                                                                        |
| --------------- | --------------------------------------------------------------------------- |
| **FROM / JOIN** | 필터링 **전에** 모든 테이블을 결합해서 composite tuple을 만든다. implicit join도 JOIN 단계에서 처리된다 |
| **WHERE**       | 만들어진 tuple을 걸러낸다. 여기서 걸러진 tuple이 속했을 그룹은 아예 형성되지 않는다                        |
| **GROUP BY**    | 남은 tuple을 그룹으로 묶고 aggregate를 계산한다. 그룹핑 키와 집계값만 남는다                          |
| **HAVING**      | 집계값 기준으로 그룹을 거른다                                                            |
| **ORDER BY**    | 결과를 정렬한다                                                                    |
| **SELECT**      | 컬럼을 고르거나 변형한다(예: `UPPER(Name)`). 필요 없는 컬럼을 버린다                              |

### 순서로 설명되는 에러
```sql
SELECT Salary * 2 AS double_pay
FROM Payroll
WHERE double_pay > 100000;   -- 에러
```
- `double_pay` alias는 SELECT 단계에서 만들어지는데 WHERE는 그보다 먼저 실행되므로, WHERE 시점에는 그 이름이 존재하지 않는다.

> **오해 주의**: `FROM A, B WHERE A.id = B.id`를 보면 join이 WHERE에서 일어나는 것처럼 보이지만, **JOIN은 항상 WHERE보다 먼저**다. implicit join도 결국 join이다.

## 7. Aggregates + Joins *(p.60~71)*

테이블: `Payroll(UserID, Name, Job, Salary)` (UserID가 PK), `Registry(UserID, Car, Year)`.

**문제**: 2017년 이전에 만들어진 차를 각 사람이 몇 대씩 갖고 있는가? (이름과 대수를 보여줘)
- "몇 대" → Aggregate(COUNT), "각 사람" → GROUP BY, 이름은 Payroll에 있고 차는 Registry에 있으니 Join.

FJWGHOS 순서대로 단계별로 완성:

```sql
-- 1. FROM/JOIN: 두 테이블 결합 (alias로 UserID 구분)
SELECT ...
FROM Payroll AS p, Registry AS r
WHERE p.UserID = r.UserID;
```
- 이 WHERE는 문법상 WHERE지만 하는 일은 JOIN 조건이다.

```sql
-- 2. WHERE: 2017년 이전 조건 추가
FROM Payroll AS p, Registry AS r
WHERE p.UserID = r.UserID
  AND r.Year < 2017;
```

```sql
-- 3. GROUP BY: 사람별로 묶고 COUNT
SELECT p.UserID, COUNT(*) AS cnt
FROM Payroll AS p, Registry AS r
WHERE p.UserID = r.UserID
  AND r.Year < 2017
GROUP BY p.UserID;
```
- PK인 `UserID`로 묶으면 사람 한 명이 정확히 한 그룹이 된다.

```sql
-- 4. SELECT: 이름을 보여주려면 GROUP BY에도 Name을 넣어야 함
SELECT p.Name, COUNT(*) AS cnt
FROM Payroll AS p, Registry AS r
WHERE p.UserID = r.UserID
  AND r.Year < 2017
GROUP BY p.UserID, p.Name;
```
- `UserID`가 PK라서 `Name`을 같이 묶어도 그룹 수는 변하지 않는다. `Name`을 붙인 건 SELECT에 쓰기 위해서다.
- 결과: **Leslie 1대, Magda 2대.**

## 8. 빈 그룹(Empty Groups) 문제 *(p.75~81)*

위 결과엔 **Frances(차 없음)와 Quinn(2018년식 차만 있음)이 없다.** 0대라고 나와야 하는 사람들이 통째로 사라졌고, 두 사람이 사라진 **단계가 서로 다르다.**

### Case 1: Frances는 JOIN 단계에서 사라짐 *(p.76~80)*
- Frances는 Registry에 매칭되는 행이 없어서 inner join이 버린다. FROM/JOIN 단계에서 이미 사라졌으니 이후 단계는 볼 수 없다.
- 해결은 **LEFT OUTER JOIN**으로 Payroll의 행을 전부 살리는 것:
```sql
SELECT p.Name, COUNT(*) AS cnt
FROM Payroll AS p
     LEFT OUTER JOIN Registry AS r
     ON p.UserID = r.UserID
GROUP BY p.UserID, p.Name;
```
- **하지만 아직 틀리다.** Frances가 `(Frances, NULL, NULL, NULL)` 한 행으로 들어오는데 `COUNT(*)`는 행 자체를 세므로 이 NULL 행도 1로 센다. Frances가 "차 1대"가 된다.
- 수정: **`COUNT(r.UserID)`**
```sql
SELECT p.Name, COUNT(r.UserID) AS cnt
FROM Payroll AS p
     LEFT OUTER JOIN Registry AS r
     ON p.UserID = r.UserID
GROUP BY p.UserID, p.Name;
```
- `COUNT(컬럼)`은 NULL을 세지 않으므로 outer join이 채운 NULL placeholder가 카운트되지 않는다. Frances는 정확히 0이 된다.
- (정리 노트의 p.81 쿼리엔 `GROUP BY`가 빠져 있다. 위가 올바른 형태.)

### Case 2: Quinn은 WHERE 단계에서 사라짐 *(p.81)*
- Quinn은 매칭되는 행(Picklemobile, 2018)이 있어서 JOIN은 통과한다. 그런데 `r.Year < 2017` 조건에 걸려서 **WHERE에서 탈락**한다.
- WHERE는 그룹화 **이전**에 동작하므로, 거기서 걸러진 행의 그룹은 **형성될 기회조차 없다.** count가 0인 그룹은 만들어지지 못한다.
- outer join만으론 해결이 안 된다. 이 강의에서는 "punt"하고 넘어가며, 해법은 다음 강의(subquery)에서 나온다.

### 교훈
outer join 뒤에 개수를 셀 땐 `COUNT(*)`가 아니라 **join된 쪽의 컬럼**을 세야 NULL placeholder가 안 세어진다.

### 한 줄 확인
`COUNT(r.UserID)`로 바꾸면 Frances가 0이 되는 이유: outer join 때문에 `(Frances, NULL, NULL, NULL)` 한 행이 생기는데, `COUNT(r.UserID)`는 `r.UserID`가 NULL인 행을 세지 않아서 0이 된다. `COUNT(*)`는 그 NULL 행도 행이니까 1로 센다.

## Lecture 5 핵심 요약

- 5대 aggregation 함수(COUNT/SUM/AVG/MAX/MIN)는 기본적으로 **NULL을 무시**하지만, `COUNT(*)`만은 예외로 행 자체를 센다.
- **GROUP BY**: 값 기준으로 그룹을 나눈 뒤 각 그룹에 집계를 적용한다. 그룹 하나가 결과 행 하나다. NULL끼리는 한 그룹이 된다. GROUP BY나 aggregate에 없는 컬럼은 SELECT에 쓸 수 없다.
- **HAVING**은 그룹(집계 이후)을 필터링, **WHERE**는 개별 행(집계 이전)을 필터링한다. 서로 다른 단계에서 동작하므로 결과가 다를 수 있다.
- **FJWGHOS**: FROM → JOIN → WHERE → GROUP BY → HAVING → ORDER BY → SELECT가 SQL의 개념적 실행 순서다. SELECT의 alias를 WHERE에서 못 쓰는 것도 이 순서 때문이다.
- Join + Aggregate를 함께 쓸 때 **outer join으로 빈 그룹을 살리고, `COUNT(컬럼)`으로 NULL placeholder를 세지 않게** 주의해야 정확한 0을 얻는다. WHERE에서 탈락한 그룹은 outer join으로도 못 살린다(→ 6강 subquery).

---

## 별첨: FJWGHOS 외우는 법

글자만 외우면 금방 잊어버린다. **이유로 순서를 복원하는 게** 더 오래간다.

### 논리로 복원하기
순서는 "재료 → 가공 → 출력" 흐름이다.

1. **FROM / JOIN**: 재료부터 모아야 한다. 테이블을 먼저 결합한다.
2. **WHERE**: 행 단위로 거르려면 그룹을 만들기 전이어야 한다.
3. **GROUP BY**: 남은 행을 묶는다.
4. **HAVING**: 그룹을 걸러내려면 그룹이 이미 있어야 한다. 그래서 GROUP BY 다음이다.
5. **ORDER BY**: 결과를 정렬한다.
6. **SELECT**: 마지막에 보여줄 컬럼을 고르고 변형한다.

각 단계가 앞 단계의 결과물을 입력으로 받는다고 생각하면 순서가 하나로 정해진다. WHERE에서 집계를 못 쓰는 것, SELECT alias를 WHERE에서 못 쓰는 것도 같은 논리에서 나온다.

### 외울 때 쓸 수 있는 방법
- **문장 만들기**: **F**rom **J**oin **W**here **G**roup **H**aving **O**rder **S**elect를 "**F**ine, **J**ust **W**ait, **G**uys, **H**e's **O**ut **S**oon" 같은 식으로 아무 문장이나 만든다(예시일 뿐, 본인이 웃기다고 느끼는 걸 써야 오래 간다).
- **시험 전략**: 쿼리 문제가 나오면 순서를 종이에 먼저 써놓고, 각 단계에서 테이블이 어떻게 변하는지 손으로 따라간다. 수업 때 한 TA/Prof 계산처럼.

### 주의할 점
슬라이드 모델은 ORDER BY가 SELECT 앞에 있다. 그런데 **실제 SQL 표준의 논리 순서는 SELECT 다음이 ORDER BY**다. SELECT에서 만든 alias를 ORDER BY에서 쓸 수 있는 게 그 증거다. 이 수업 시험은 슬라이드 기준으로 답하는 게 안전하다. 중요한 건 **WHERE → GROUP BY → HAVING** 순서와 **JOIN이 맨 앞**이라는 점이다.
