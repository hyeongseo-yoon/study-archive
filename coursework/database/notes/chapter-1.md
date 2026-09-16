# Chapter 1: Course Overview & The Relational Model

*Database Systems & its Applications, Hanyang University (Instructor: Cha Jaehyuk)*

> 이 자료는 슬라이드에 쪽번호가 인쇄되어 있지 않아서, 아래 `p.N`은 PDF 파일 자체의 페이지 순서(1부터 시작)를 가리킨다.

## 1. Course Overview *(p.2~10)*

### Course Objectives *(p.4)*
- Database management system의 기본 원리 이해
- 데이터베이스 애플리케이션을 작성할 수 있는 능력 갖추기

### Course Format *(p.5)*
- 강의(화·목): 온라인 / 요약&Q&A(화): 오프라인, 노트북 지참 필수
- 과제 5개 + 미니프로젝트 1개
- 시험 2회: 중간(10/20), 기말(12/10)

### Textbook *(p.6)*
- 주교재: *Database Management Systems*, 3rd ed. (Ramakrishnan & Gehrke)
- 참고: *Database Systems: The Complete Book*, 2nd ed.

### Grading *(p.7)*
Project 25% / Exams 60% / Quizzes 10% / In-class activities 5+?%

### Course Schedule 요약 *(p.8~9)*
- Week 1-4: Course Overview, Relational Model(chap.3), SQL(chap.5)
- Week 4-7: Database Design(chap.2), Overview(chap.1), Schema Refinement & Normal Forms(chap.19), Relational Algebra/Calculus(chap.4)
- Week 8: Midterm1, Database Application Development(chap.6)
- Week 9~17: Storing Data(chap.9) → Tree Indexing(chap.10) → Hash Indexing(chap.11) → Query Evaluation/External Sorting(chap.12,13) → Evaluating Relational Operators(chap.14) → Query Optimizer(chap.15) → Transactions(chap.16) → Concurrency Control(chap.17) → Crash Recovery(chap.18) → Final Exam

---

## 2. Databases & DBMS *(p.13~19)*

### Database란? *(p.14~16)*
**관련된 데이터를 저장하는 파일들의 모음(a collection of files storing related data)**.
예: Accounts database, Payroll database, HYU's student database, Amazon's products database, Airline reservation database.

### DBMS(Database Management System)란? *(p.17~19)*
> "다른 누군가가 작성해준, 대용량 데이터베이스를 효율적으로 관리하고 오랜 기간에 걸쳐 지속(persist)시킬 수 있게 해주는 커다란 프로그램"

**DBMS 예시**:
- 상용: Oracle, IBM DB2, Microsoft SQL Server, Vertica, Teradata
- 클라우드: Snowflake, Redshift, BigQuery, SQL Azure
- 오픈소스: MySQL(Sun/Oracle), PostgreSQL, DuckDB
- 오픈소스 라이브러리: **SQLite**

→ **DBMS는 Data Model이 필요하다.**

---

## 3. Data Models *(p.21~22)*

**Data Model** = 데이터의 수학적 정의(mathematical definition of data).

다양한 모델이 존재: Relational(이 수업에서 다룸), Semi-structured, Key-value pairs, Graph, OO(객체지향) 등.

---

## 4. The Relational Model *(p.23~45)*

### 역사 *(p.24~26)*
- E. F. Codd, *"A Relational Model of Data for Large Shared Data Banks"*, Communications of the ACM, 1970
- Codd는 이 공로로 **1981년 ACM Turing Award** 수상

### Relational Model의 3가지 원칙 *(p.27~28)*
1. 데이터는 **단순하고 flat한 relation**(테이블)에 저장된다
2. **set-at-a-time** 쿼리 언어로 조회한다 (한 번에 레코드 하나씩이 아니라 집합 단위로 처리)
3. **물리적 표현 방식을 규정하지 않는다** (논리적 모델과 물리적 저장을 분리)

### 예시 — Payroll 테이블 *(p.29~32)*
Payroll 부서가 직원의 ID, 이름, 직함, 급여를 저장하려 할 때:
```
Payroll (UserId, Name, Job, Salary)
```
- **Schema**: 데이터를 기술하는 것 (`Payroll (UserId, Name, Job, Salary)`)
- **Instance**: 실제 데이터

| UserID | Name | Job | Salary |
|---|---|---|---|
| 123 | Jack | TA | 50000 |
| 345 | Allison | TA | 60000 |
| 567 | Magda | Prof | 90000 |
| 789 | Dan | Prof | 100000 |

### Terminology(용어) *(p.33~36)*
- **Table / Relation** = 위 표 전체 (예: `Payroll`)
- **Rows / Tuples / Records** = 각 행(예: `123, Jack, TA, 50000`)
- **Columns / Attributes / Fields** = 각 열(예: `UserID`, `Name`, `Job`, `Salary`)

### Every Data Model has Three Parts *(p.37~40)*
1. **Instance**: 실제 데이터 (테이블의 행들)
2. **Schema**: 데이터의 타입(구조) — 컬럼 이름과 종류
3. **Query Language**: 데이터를 어떻게 가져올지 — 예:
   ```sql
   SELECT Name
   FROM Payroll
   WHERE Salary > 70000;
   ```

### Discussion of the Relational Model — 4가지 규칙 *(p.41~44)*
- **Set semantics**: 순서는 중요하지 않다(order doesn't matter)
- **Duplicates not allowed**: 완전히 동일한 두 행이 있으면 **set semantics 위반**
  - (일부 시스템은 중복을 허용하기도 하지만 나쁜 설계 — 이 경우 그 컬렉션은 **set이 아니라 bag**이라고 부름)
- **Attrs have types**: 각 attribute(컬럼)는 타입을 가짐 (예: `Salary`가 `INT`인데 `"banana"` 값이 들어가면 타입 위반)
- **Tables are flat**: 테이블 안에 **sub-table을 둘 수 없음** — 예: `Job` 컬럼 안에 `JobName/DaysPerWeek` 서브테이블을 넣는 것은 불가능. 모든 관계는 평평한(flat) 2차원 구조여야 함

### Recap *(p.43~45)*
Relational Model의 3원칙 재확인: (1) flat relation에 저장 — 이번 챕터에서 다룸, (2) set-at-a-time 쿼리 언어 — 다음 강의(**SQL**)에서 다룸, (3) 물리적 표현을 규정하지 않음

---

## 핵심 요약

- **DBMS**는 대용량 데이터를 효율적/지속적으로 관리해주는 소프트웨어이며, 동작을 위해 **Data Model**이 필요함
- **Relational Model**(Codd, 1970)은 데이터를 **flat relation(테이블)**에 저장하고, **set-at-a-time** 쿼리 언어로 접근하며, **물리적 저장 방식을 규정하지 않는** 3가지 원칙 위에 서 있음
- 모든 데이터 모델은 **Instance(실제 데이터) / Schema(타입) / Query Language(조회 방법)** 세 부분으로 구성됨
- Relational Model의 데이터는 **set semantics**(순서 무관, 중복 불허)를 따르고, 각 attribute는 **타입**을 가지며, 테이블은 **flat**해야 함(서브테이블 불허)
- Terminology: Table/Relation = Rows(Tuples/Records) × Columns(Attributes/Fields)
