# Lecture 2: SQL Basics

*Database Management Systems, 3rd ed. (Ramakrishnan & Gehrke)*

## 1. SQL 개요 *(슬라이드 p.6~7)*

- **SQL(Structured Query Language)**: relational database 전용 언어. Java/Python/C++ 같은 범용 언어가 아님
- **Declarative, set-at-a-time**: 원하는 데이터가 *무엇(what)*인지 기술하면, 시스템이 그걸 어떻게(*how*) 계산할지 알아서 결정

## 2. Basic Query: SELECT-FROM-WHERE *(슬라이드 p.8~17)*

Payroll 테이블 예시로 시작:

```sql
SELECT *
FROM Payroll;
```

- 컬럼(UserID, Name, Job, Salary) 전체와 모든 행을 그대로 반환

조건을 걸고 원하는 컬럼만 뽑는 예시:

```sql
SELECT P.Name, P.UserID
FROM Payroll AS P
WHERE P.Job = 'TA';
```

- **SELECT**: 반환할 attribute들 지정
- **FROM**: 대상 테이블(들) 지정. `Payroll AS P`처럼 alias(별칭)를 줄 수 있음
- **WHERE**: 필터 조건
- 결과: Job이 'TA'인 행만 남기고 Name, UserID 두 컬럼만 반환 (Jack/123, Allison/345)

## 3. Semantics: For-each Semantics *(슬라이드 p.18~31)*

SQL 쿼리가 정확히 무엇을 계산하는지 정의하는 방법 — **for-each semantics**로 이해하면 된다:

```python
for each row in Payroll:
    if (row.Job == 'TA'):
        output (row.Name, row.UserID)
```

- 이게 **for-each semantics**: SQL이 계산하는 *결과가 무엇인지(what)*를 정의하는 방식
- 실제 실행 방법(*how*)은 시스템이 결정 — 예를 들면: *(p.29~30)*
  - Payroll 전체를 순회(for-each semantics 그대로)
  - 또는: Job 인덱스에서 'TA'를 찾아 그 레코드만 읽기
  - 또는: Job에 대한 bit-map index를 순회
  - → **for-each semantics는 결과를 정의할 뿐, 실행 계획을 강제하지 않는다**

## 4. ORDER BY와 DISTINCT *(슬라이드 p.32~46)*

### ORDER BY *(p.33~43)*
```sql
SELECT * FROM Payroll ORDER BY Name;
```
- 지정한 컬럼 기준으로 정렬해서 반환 (기본 오름차순)
- 여러 컬럼 지정 가능: `ORDER BY Job, Name` — Job으로 먼저 정렬하고, 같은 Job 안에서 Name으로 정렬
- `ORDER BY Job, Name`과 `ORDER BY Name, Job`은 결과가 다름 (정렬 우선순위가 다르므로)

### DISTINCT *(p.44~46)*
```sql
SELECT Job FROM Payroll;
```
- 결과: TA, TA, Prof, Prof (중복 포함) — **bag semantics**

```sql
SELECT DISTINCT Job FROM Payroll;
```
- 결과: TA, Prof (중복 제거) — **set semantics**

## 5. Tables in SQL: 생성/삽입/삭제 *(슬라이드 p.47~59)*

### CREATE TABLE *(p.48~49)*
```sql
CREATE TABLE Payroll (
  UserID INT,
  Name TEXT,
  Job TEXT,
  Salary INT);
```
- 테이블/컬럼명은 대소문자 구분 안 함(case-insensitive)이지만 가독성을 위해 관례를 지키는 게 좋음
- **데이터 타입**: 각 attribute는 타입을 가짐 — 문자열(CHAR(20), VARCHAR(50), TEXT), 숫자(INT, SMALLINT, FLOAT), MONEY, DATETIME 등. 벤더마다 고유 타입도 많음
- 이 타입은 **statically enforced**(정적으로 강제)됨 — 단, SQLite는 예외

### INSERT *(p.50~52)*
```sql
INSERT INTO Payroll VALUES (123,'Jack','TA',50000);
INSERT INTO Payroll VALUES (345,'Allison','TA',60000);
```
- 삽입된 tuple은 **persistent**(컴퓨터를 꺼도 유지됨)
- 여러 행을 한 번에 넣는 동치 문법:
```sql
INSERT INTO Payroll VALUES
  (123,'Jack','TA',50000),
  (345,'Allison','TA',60000),
  (999,'Zack','Prof',90000);
```

### DELETE *(p.53~58)*
```sql
DELETE FROM Payroll WHERE UserID=789;
```
- 조건에 맞는 행(들)을 삭제. `WHERE Job='Prof'`처럼 여러 행이 걸리면 다 삭제됨
```sql
DELETE FROM Payroll;
```
- WHERE 없이 쓰면 테이블의 **모든 행**을 삭제 (테이블 자체는 남음)

### 정리 *(p.59)*
- **CREATE TABLE**: 테이블은 persistent, 다양한 옵션/확장 존재
- **DROP TABLE**: 테이블 전체를 삭제. 과제에서는 자주 쓰지만 실무 앱에서는 조심해서 써야 함
- **INSERT**: tuple은 persistent, 대량 삽입은 `COPY` 사용 권장
- **DELETE**: 한 개/여러 개/전체 행 삭제 가능

## 6. Keys (Primary Key) *(슬라이드 p.60~75)*

> **Key**: 하나의 row를 **유일하게** 식별하는 attribute(들)

- 예: Job(TA/Prof 반복) → 키 아님. UserID(값이 고유) → 키의 좋은 후보 *(p.61~63)*
- Salary처럼 얼핏 고유해 보여도, 우연히 같은 값(두 사람이 같은 salary)이 나올 수 있으면 키가 아님 — **데이터는 현실 세계에서 오므로, 모델도 그 현실을 반영해야 한다** *(p.64~65)*

```sql
CREATE TABLE Payroll (
  UserID INT PRIMARY KEY,
  Name TEXT, Job TEXT, Salary INT);
```
- 또는 컬럼 목록 끝에 따로 `PRIMARY KEY (UserId)`로도 선언 가능 *(p.66~68)*

### 복합 키(key of more than one attribute) *(p.69~74)*
Name, Job 각각은 고유하지 않지만 (Name, Job) 조합은 고유한 경우:

| Name | Job | Salary |
|---|---|---|
| Alice | TA | 20000 |
| Alice | Prof | 200000 |
| Bob | Prof | 200000 |

```sql
CREATE TABLE Payroll (
  Name TEXT,
  Job TEXT,
  Salary INT,
  PRIMARY KEY (Name, Job));
```
- 복합 키는 반드시 `PRIMARY KEY (col1, col2)` 형태로 따로 선언해야 함(컬럼에 인라인으로 못 붙임)

### 정리 *(p.75)*
- Key = row를 유일하게 식별하는 attribute(들)
- 후보가 여러 개일 수 있음 → SQL은 그중 하나를 **primary key**로 정하도록 강제
- 좋은 습관: 모든 테이블에 primary key를 두는 것 (예외도 있음)
- 테이블 간 관계는 **foreign key**로 표현 (다음 절)

## 7. Foreign Keys *(슬라이드 p.76~87)*

데이터베이스는 여러 테이블을 가질 수 있는데, 테이블 간 관계는 어떻게 표현할까? *(p.76~77)*

| Payroll |||| Regist ||
|---|---|---|---|---|---|
| UserID | Name | Job | Salary | UserID | Car |
| 123 | Jack | TA | 50000 | 123 | Charger |
| 345 | Allison | TA | 60000 | 567 | Civic |
| 567 | Magda | Prof | 90000 | 567 | Pinto |
| 789 | Dan | Prof | 100000 | | |

> **Foreign Key**: 다른 테이블(another table)의 한 row를 유일하게 식별하는 attribute(들) — 그 테이블을 "reference"한다 *(p.78~80)*

- 방향이 중요함: Regist.UserID → Payroll.UserID는 유효(Payroll에서 UserID가 유일) *(p.81)*
- 반대로 Payroll.UserID → Regist.UserID는 불가 — Regist 테이블에서는 567이 두 번 나와 유일하지 않음 *(p.82)*
- **Foreign key는 반드시 유일한 attribute(거의 항상 primary key)를 참조해야 한다** *(p.83)*

```sql
CREATE TABLE Payroll (
  UserID INT PRIMARY KEY,
  Name TEXT, Job TEXT, Salary INT);

CREATE TABLE Regist (
  UserID INT REFERENCES Payroll(UserID),
  Car TEXT);
```
- Payroll 쪽 참조 대상 컬럼이 곧 그 테이블의 키 이름과 같다면 `REFERENCES Payroll`로 줄여 쓸 수도 있음 *(p.85~86)*
- 복합 키를 참조하는 foreign key는 별도 줄로 선언 *(p.87)*:
```sql
CREATE TABLE Regist (
  Name TEXT,
  Job TEXT,
  Car TEXT,
  FOREIGN KEY (Name, Job) REFERENCES Payroll);
```

## Lecture 2 핵심 요약 *(슬라이드 p.88)*

- SELECT-FROM-WHERE 기본 쿼리
- DISTINCT, ORDER BY
- Semantics: for-each로 SQL이 계산하는 결과를 정의
- CREATE TABLE, KEY(primary key), FOREIGN KEY

다음 시간은 SQL을 계속 다룬다.

---

## 체크리스트
1. SQL 개요
2. Basic Query: SELECT-FROM-WHERE
3. Semantics: For-each Semantics
4. ORDER BY와 DISTINCT
5. Tables in SQL: CREATE / INSERT / DELETE
6. Keys (Primary Key)
7. Foreign Keys
8. 핵심 요약
