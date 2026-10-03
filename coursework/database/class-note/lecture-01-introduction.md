# Lecture 1 수업노트: Introduction & The Relational Model


**이번 수업 목표**: Relational Model이 뭔지, DB/DBMS/schema/instance 같은 핵심 용어를 자기 말로 설명할 수 있게 되는 것.

## 0. 선수 지식 체크 결과
- DB vs DBMS 구분: 감 잡지 못함 → 수업에서 설명
- 표(테이블)로 데이터를 저장한다는 것: 엑셀 스프레드시트와 비슷하다고 이해함
- 스키마(schema): 들어본 적 없음 → 수업에서 설명
- SQL: 모름 → 수업에서 대략 소개

## 1. Course Overview (보충)
- **수업 형식**: 강의는 화·목, 강의는 온라인. 요약 & Q&A는 화요일 오프라인이며 노트북 지참 필수.
- **과제**: 과제 5개 + 미니프로젝트 1개.
- **시험**: 중간고사 10/20, 기말고사 12/10.
- **교재**: 주교재는 *Database Management Systems*, 3rd ed. (Ramakrishnan & Gehrke). 참고로 *Database Systems: The Complete Book*, 2nd ed.도 있음.
- **성적 비율**: Project 25% / Exams 60% / Quizzes 10% / In-class activities 5+?%.
- **주차별 흐름**: Week 1~4 Overview, Relational Model(chap.3), SQL(chap.5) → Week 4~7 DB 설계(chap.2), 개요(chap.1), 스키마 정제와 정규형(chap.19), 관계 대수/관계 해석(chap.4) → Week 8 중간고사, 애플리케이션 개발(chap.6) → Week 9~17 저장(chap.9) → Tree Index(chap.10) → Hash Index(chap.11) → 외부 정렬과 질의 평가(chap.12, 13) → 관계 연산자 평가(chap.14) → 질의 최적화(chap.15) → 트랜잭션(chap.16) → 동시성 제어(chap.17) → 장애 복구(chap.18) → 기말고사.

## 2. Database와 DBMS
- **Database**: 관련된 데이터를 모아둔 파일들의 집합. 예: 계좌 정보, 학생 정보, 상품 정보, 항공 예약 정보.
- **DBMS (Database Management System)**: 데이터베이스를 효율적으로 관리하고, 오랫동안 안정적으로 유지해주는 프로그램.
- **핵심 구분**: database는 "데이터 그 자체", DBMS는 "그 데이터를 다루는 소프트웨어".
- 비유: 문서 파일들이 database라면, 그 파일을 열고 저장하고 관리해주는 워드 프로그램이 DBMS와 비슷한 관계.
- 예시 DBMS: Oracle, IBM DB2, MS SQL Server, Snowflake, BigQuery, MySQL, PostgreSQL, DuckDB, SQLite(오픈소스 라이브러리).
- DBMS가 동작하려면 **Data Model**이 필요하다.

**확인 문제 풀이**: "MySQL"은 DBMS, "우리 학교 학생 정보 데이터"는 DB.

## 3. Data Model 개요
- **Data Model** = 데이터를 수학적으로 정의한 것. "데이터를 어떤 형태로 표현할 것인가"에 대한 약속.
- 종류: Relational(관계형), Semi-structured(반정형, 예: JSON/XML), Key-value, Graph, Object-Oriented 등.
- 이 수업의 주제는 **Relational Model**, 즉 표(테이블) 형태로 데이터를 표현하는 모델.
- 한 DBMS가 여러 Data Model을 지원할 수도 있다(예: MySQL의 JSON 컬럼). 다만 이 수업은 Relational Model 하나에 집중한다.

**정리 확인**: DB(데이터 집합) / DBMS(데이터를 효율적으로 다루는 소프트웨어 시스템) / Data Model(데이터를 표현하는 방법)의 관계.

## 4. Relational Model의 배경
- E. F. Codd가 1970년 논문 *"A Relational Model of Data for Large Shared Data Banks"*(Communications of the ACM)에서 제안.
- 이 공로로 Codd는 1981년 ACM Turing Award 수상.

## 5. Relational Model의 특징
1. **Data is stored in simple, flat relations**: 데이터를 단순하고 평평한 관계(=테이블)로 저장.
2. **Is retrieved via a set-at-a-time query language**: 한 줄씩이 아니라 집합 단위로 조회하는 쿼리 언어(SQL)로 가져온다.
3. **No prescription for the physical representation**: 디스크에 실제로 어떻게 저장할지(파일 구조, 인덱스 등)는 모델이 규정하지 않는다.

**확인 문제 풀이**: MySQL과 PostgreSQL은 둘 다 Relational Model을 쓰지만, 디스크 저장 방식은 달라도 된다. 모델은 논리적 모습만 정하고 물리적 저장은 구현체가 정한다.

## 6. Relational Model 예시와 용어
예시 부서: Payroll(급여). 직원의 ID, 이름, 직함, 급여를 저장한다.

```
Payroll (UserId, Name, Job, Salary)
```
- 이 구조 정의가 **schema**. 데이터를 기술하는 구조.

| UserID | Name | Job | Salary |
|---|---|---|---|
| 123 | Jack | TA | 50000 |
| 345 | Allison | TA | 60000 |
| 567 | Magda | Prof | 90000 |
| 789 | Dan | Prof | 100000 |

- 위처럼 실제로 채워진 데이터가 **instance**. 실제 데이터 그 자체.

**용어 정리**
- Table / Relation: Payroll 같은 표 전체
- Rows / Tuples / Records: 표의 각 행
- Columns / Attributes / Fields: UserID, Name, Job, Salary 같은 열

**확인 문제 풀이**
- 행을 추가하면 instance가 바뀐 것.
- 컬럼을 추가하면 데이터를 기술하는 구조가 바뀐 것이므로 schema가 바뀐 것.

## 7. Data Model의 세 요소
모든 Data Model은 다음 세 부분으로 구성된다.
- **Instance**: 실제 데이터
- **Schema**: 데이터의 타입(구조)
- **Query Language**: 데이터를 어떻게 가져올지에 대한 언어

예시:
```sql
SELECT Name
FROM Payroll
WHERE Salary > 70000;
```
- 이 문장은 "Payroll 테이블에서 Salary가 70000보다 큰 사람들의 Name을 가져와"라는 뜻.
- **Query**: 그 언어로 쓴 구체적인 요청 한 문장. 위의 `SELECT ...` 문장 하나가 query.
- **Query Language**: 그 요청들을 작성하는 언어(문법 체계) 자체. Relational Model에서는 SQL.
- 구분: SQL = Query Language(언어), `SELECT ...` 한 문장 = Query(요청).

**Payroll 예시에 대입**
- Instance = 위 표에 채워진 실제 데이터 값들
- Schema = `Payroll (UserId, Name, Job, Salary)` 컬럼 구성 정의
- Query = `SELECT Name FROM Payroll WHERE Salary > 70000;` 같은 문장 하나
- SQL 문법 자체는 2강에서 본격적으로 다룬다.

## 8. Relational Model 세부 논의
1. **Set semantics**: 행의 순서는 의미가 없다.
2. **Duplicates not allowed**: 모든 값이 똑같은 행이 두 개 있으면 안 된다. 허용하는 시스템도 있지만 좋은 설계는 아니다. 중복을 허용한 컬렉션은 set이 아니라 **bag**이라고 부른다.
3. **Attrs have types**: 각 컬럼은 타입을 가진다. 예: Salary가 INT인데 "banana"가 들어가면 위반.
4. **Tables are flat**: 테이블 안에 또 다른 테이블(중첩 테이블)을 넣을 수 없다. 예: Job 컬럼 안에 JobName/DaysPerWeek 표를 넣는 것은 불가.

**확인 문제 풀이**: 완전히 같은 행이 두 번 들어간 표는 2번(Duplicates not allowed) 위반이며, 이 컬렉션은 bag이라고 부른다.

## 9. 수업 마무리 요약
- Relational Model의 세 가지 특징: flat relation 저장 / set-at-a-time 쿼리 언어로 조회 / 물리적 표현은 규정하지 않음.
- Schema(구조) vs Instance(실제 데이터) 구분.
- DB / DBMS / Data Model의 관계.
- Query(요청 한 문장) vs Query Language(SQL 자체) 구분.
- Set semantics, 중복 불허(bag), attribute type, flat 구조의 제약.
- 다음 시간: 이 모델을 다루는 언어인 SQL(2강).
