# Lecture 3: Joins

*Database Management Systems, 3rd ed. (Ramakrishnan & Gehrke)*

## 1. Recap: Foreign Key & SELECT-FROM-WHERE *(슬라이드 p.5~9)*

- **Foreign Key**: 다른 테이블의 row를 유일하게 식별하는 attribute(들) — Registry.UserID는 Payroll의 primary key 값을 그대로 복사해서 담고 있는 것 *(p.5)*
- 참조 방향이 중요 — Registry.UserID(FK) → Payroll.UserID(PK)는 유효하지만, 반대 방향(Payroll→Registry)은 Registry 쪽에 중복값(예: 567이 두 번)이 있으면 무효 *(p.6~7)*
- SQL은 declarative — *what*을 원하는지만 쓰면 시스템이 *how*를 결정 *(p.8~9)*

## 2. Joins 개요 *(슬라이드 p.11)*

- **Foreign key**는 테이블 간 관계를 *describe*(기술)한다
- **Join**은 그 관계를 실제로 *realize*(구현)해서 테이블들을 결합한다
- 항상 foreign key로 결합하는 건 아니고, join 조건은 다양하게 줄 수 있음
- Join에는 여러 종류(flavor)가 있음

## 3. Inner Joins *(슬라이드 p.13)*

> Inner join은 SQL 쿼리의 "bread and butter" — 흔히 그냥 "join"이라고도 부름. 두 relation을 **join predicate**로 교집합(intersect)한다

| Payroll |||| Registry ||
|---|---|---|---|---|---|
| UserID | Name | Job | Salary | UserID | Car |
| 123 | Leslie | TA | 50k | 123 | Charger |
| 345 | Frances | TA | 60k | 567 | Civic |
| 567 | Magda | Prof | 120k | 567 | Ferrari |
| 789 | Quinn | Prof | 100k | | |

두 테이블을 UserID가 같은 값끼리 묶으면:

| Name | Job | Salary | Car |
|---|---|---|---|
| Leslie | TA | 50k | Charger |
| Magda | Prof | 120k | Civic |
| Magda | Prof | 120k | Ferrari |

## 4. Nested-Loop Semantics *(슬라이드 p.14~27)*

Join도 결국 for-each semantics의 확장인 **nested-loop**로 이해할 수 있다:

```python
foreach row_p in Payroll:
    foreach row_r in Registry:
        if row_p.userID == row_r.userID:
            output(row_p.name, row_r.car)
```

- Payroll의 각 행에 대해 Registry의 모든 행을 순회하며 userID가 일치하는 조합만 출력
- 123(Leslie)↔123(Charger) 매치 → 1건, 567(Magda)↔567(Civic), 567(Magda)↔567(Ferrari) 매치 → 2건, 345/789는 매치 없음
- 결과: (Leslie, Charger), (Magda, Civic), (Magda, Ferrari)

## 5. Inner Join 문법 *(슬라이드 p.28~29, p.35)*

**Explicit(명시적) 문법**:
```sql
SELECT P.Name, R.Car
FROM Payroll AS P
     INNER JOIN Registry AS R
     ON P.UserID = R.UserID;
```
- `INNER JOIN`은 그냥 `JOIN`으로 줄여 써도 동일

**Implicit(암묵적) 문법**:
```sql
SELECT P.Name, R.Car
FROM Payroll AS P, Registry AS R
WHERE P.UserID = R.UserID;
```

- **주의**: implicit 문법에서 WHERE에 다른 조건까지 AND/OR로 섞으면 **연산자 우선순위(operator precedence)** 때문에 명시적 괄호 없이는 explicit 버전과 다른 결과가 나올 수 있음:
```sql
-- 괄호 있음(의도한 대로 동작)
WHERE P.UserID = R.UserID AND (R.Car = 'Civic' OR R.Car = 'Ferrari');
-- 괄호 없음(다른 의미가 됨!)
WHERE P.UserID = R.UserID AND R.Car = 'Civic' OR R.Car = 'Ferrari';
```

## 6. SQL 쿼리는 여러 "phase"를 가진다 *(슬라이드 p.30, p.36)*

- Join은 마치 **임시 테이블(temporary table)**을 만드는 것처럼 동작한다
- 그 임시 테이블에 대해 WHERE 필터를 추가로 적용할 수 있음
- **멘탈 모델**: SQL을 "composite tuple"들의 컬렉션을 만드는 과정으로 생각해도 됨 — 두 테이블의 튜플을 이어붙인(concatenate) 것들의 집합을 만든 다음, 조건을 만족하는 것만 골라내는 것

## 7. Joins 구현: 복잡도와 최적화 *(슬라이드 p.38~45)*

- k개의 relation(각 크기 n)을 nested loop semantics로 그대로 계산하면 복잡도는 **O(nᵏ)** — 매우 비쌈
- 하지만 **실제 DB는 nested loop로 계산하지 않는다**
- 가능한 최적화 *(p.42~44)*:
  - `foreach` 루프의 순서는 결과에 영향을 주지 않음 → 시스템이 자유롭게 순서를 바꿀 수 있음
  - 필터 조건(predicate)을 미리 적용해서 순회할 데이터를 줄일 수 있음 (예: `r.Car = 'Ferrari'` 조건을 먼저 걸기)
  - 모든 행을 순회하지 않고 **index**를 이용해 조건에 맞는 행만 바로 찾을 수도 있음 (index는 이후 강의에서 다룸)
- 이처럼 SQL은 declarative하기 때문에, **query optimizer**가 최적의 실행 계획을 알아서 선택함 — 이를 **Physical Data Independence**라고 부름 *(p.45)*

## 8. ORDER BY / DISTINCT 복습 *(슬라이드 p.47~48)*

```sql
SELECT Name, UserID
FROM Payroll
WHERE Job = 'TA'
ORDER BY Salary, Name;
```
- 기본 정렬은 오름차순(ascending). 여러 컬럼을 주면 앞 컬럼 우선으로 정렬

```sql
SELECT DISTINCT Job
FROM Payroll
WHERE Salary > 70000;
```
- 중복 제거

## 9. 테이블/키 생성 복습 *(슬라이드 p.50~59)*

### CREATE TABLE과 데이터 타입 *(p.50~52)*
```sql
CREATE TABLE Payroll (
  UserID INT,
  Name VARCHAR(100),
  Job VARCHAR(100),
  Salary INT
);
```
- 타입은 statically & strictly enforced. 실전에서 자주 쓰는 조합: 문자열은 `VARCHAR(N)`, 숫자는 `INT`/`FLOAT`, 날짜는 `DATETIME`(SQLite는 `VARCHAR(N)`로 대체)

### Primary Key *(p.53~54)*
```sql
CREATE TABLE Payroll (
  UserID INT PRIMARY KEY,
  Name VARCHAR(100), Job VARCHAR(100), Salary INT
);
```
- 또는 `PRIMARY KEY (UserId)`를 컬럼 목록 끝에 별도로 명시

### Aggregate(복합) Key *(p.55~57)*
> Key = 하나 이상의 attribute가 **in aggregate**(합쳐서) row를 유일하게 식별하는 것

```sql
CREATE TABLE Payroll (
  UserID INT,
  Name VARCHAR(100),
  Job VARCHAR(100),
  Salary INT,
  PRIMARY KEY (Name, Job)
);
```

### Foreign Key *(p.58~59)*
```sql
CREATE TABLE Registry (
  UserID INT REFERENCES Payroll,
  Car VARCHAR(100)
);
-- 또는 명시적으로
CREATE TABLE Registry (
  UserID INT,
  Car VARCHAR(100),
  FOREIGN KEY (UserID) REFERENCES Payroll
);
```
- 복합 키를 참조하는 복합 foreign key도 같은 방식으로 선언:
```sql
CREATE TABLE Registry (
  Name VARCHAR(100),
  Job VARCHAR(100),
  Car VARCHAR(50),
  FOREIGN KEY (Name, Job) REFERENCES Payroll
);
```

## Lecture 3 핵심 요약

- **Inner Join**: 두 테이블을 join predicate로 교집합. `INNER JOIN ... ON`(explicit) / `FROM A, B WHERE ...`(implicit) 두 문법이 동치지만, implicit에서는 연산자 우선순위를 조심해야 함
- Join의 의미는 **nested-loop semantics**로 정의되지만, 실제 실행은 **query optimizer**가 훨씬 효율적인 방법(순서 변경, 조기 필터링, 인덱스)으로 처리 — 이것이 **Physical Data Independence**
- ORDER BY/DISTINCT, CREATE TABLE의 데이터 타입, (복합) Primary Key/Foreign Key 선언 문법 복습

---

## 체크리스트
1. Recap: Foreign Key & SELECT-FROM-WHERE
2. Joins 개요
3. Inner Joins
4. Nested-Loop Semantics
5. Inner Join 문법 (explicit / implicit)
6. SQL 쿼리는 여러 "phase"를 가진다
7. Joins 구현: 복잡도와 최적화
8. ORDER BY / DISTINCT 복습
9. 테이블/키 생성 복습
