# Lecture 1: Introduction & The Relational Model

*Database Management Systems, 3rd ed. (Ramakrishnan & Gehrke)*

## 1. Database와 DBMS *(슬라이드 p.12~18)*

### Database란? *(p.12~14)*
- **database**: a collection of files storing related data
- 예시: Accounts database, Payroll database, HYU's student database, Amazon's products database, Airline reservation database

### DBMS란? *(p.15~18)*
- **DBMS(Database Management System)**: "A big program written by someone else that allows us to manage efficiently a large database and allows it to persist over long periods of time"
- 예시 *(p.17)*:
  - 전통 상용: Oracle, IBM DB2, Microsoft SQL Server, Vertica, Teradata
  - 클라우드: Snowflake, Redshift, BigQuery, SQL Azure
  - 오픈소스: MySQL(Sun/Oracle), PostgreSQL, DuckDB
  - 오픈소스 라이브러리: **SQLite**
- DBMS가 동작하려면 **Data Model**이 필요하다 *(p.18)*

## 2. Data Model 개요 *(슬라이드 p.19~21)*

- **Data Model** = mathematical definition of data
- 종류: Relational, Semi-structured, Key-value pairs, Graph, OO 등 *(p.20)*
- 이 수업에서 다루는 건 **Relational** 모델 *(p.21)*

## 3. Relational Model의 배경 *(슬라이드 p.22~23)*

- E. F. Codd, *"A Relational Model of Data for Large Shared Data Banks"* (Communications of the ACM, 1970) *(p.22)*
- Codd는 이 공로로 1981년 **ACM Turing Award** 수상 *(p.23)*

## 4. Relational Model의 특징 *(슬라이드 p.24~25)*

- **Data is stored in simple, flat relations** — 이 수업은 여기부터 시작 *(p.24~25)*
- **Is retrieved via a set-at-a-time query language**
- **No prescription for the physical representation** — 데이터가 물리적으로 어떻게 저장되는지는 모델이 규정하지 않음

## 5. Relational Model 예시와 용어 *(슬라이드 p.26~32)*

Payroll 부서가 직원의 ID, 이름, 직함, 급여를 저장해야 하는 상황 *(p.26)*:

```
Payroll (UserId, Name, Job, Salary)
```
- 이 부분(구조 정의)이 **schema** — 데이터를 기술하는 것 *(p.27)*

| UserID | Name | Job | Salary |
|---|---|---|---|
| 123 | Jack | TA | 50000 |
| 345 | Allison | TA | 60000 |
| 567 | Magda | Prof | 90000 |
| 789 | Dan | Prof | 100000 |

위 실제 데이터가 **instance** — 실제 데이터 그 자체 *(p.28)*

### 용어 정리 *(p.29~32)*
- **Table / Relation**: Payroll 같은 표 전체
- **Rows / Tuples / Records**: 표의 각 행
- **Columns / Attributes / Fields**: UserID, Name, Job, Salary 같은 열

## 6. Data Model의 세 요소 *(슬라이드 p.33~36)*

모든 data model은 다음 세 부분으로 구성된다:
- **Instance**: 실제 데이터 *(p.34)*
- **Schema**: 데이터의 타입(구조) *(p.35)*
- **Query Language**: 데이터를 어떻게 가져올지 *(p.36)*

```sql
SELECT Name
FROM Payroll
WHERE Salary > 70000;
```

## 7. Relational Model 세부 논의 *(슬라이드 p.37~42)*

- **Set semantics**: 순서(order)는 의미 없음 *(p.38)*
- **Duplicates not allowed**: 완전히 같은 행이 두 개 있으면 안 됨 — 허용하는 시스템도 있지만 안 좋은 설계. 중복을 허용하면 그 컬렉션은 set이 아니라 **bag**이라고 부름 *(p.39~40)*
- **Attrs have types**: 각 attribute(컬럼)는 타입을 가짐 — 예를 들어 Salary가 INT 타입인데 문자열("banana")이 들어가면 위반 *(p.41)*
- **Tables are flat**: 서브테이블(중첩 테이블)은 허용되지 않음 — 예를 들어 Job 컬럼 안에 JobName/DaysPerWeek 표를 또 넣는 건 불가 *(p.42)*

## Lecture 1 핵심 요약 *(슬라이드 p.43~45)*

- Relational Model의 세 가지 특징: flat relation에 데이터 저장 / set-at-a-time query language로 조회 / 물리적 표현은 규정하지 않음
- Schema(타입) vs Instance(실제 데이터) 구분
- Table/Relation, Row/Tuple/Record, Column/Attribute/Field 용어
- Set semantics(순서 무관, 중복 불허)와 attribute type, flat 구조라는 제약

다음 시간은 이 모델을 실제로 다루는 언어인 **SQL**로 이어진다.
