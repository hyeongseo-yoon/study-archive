# Lecture 2: SQL Basics — 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

정리 노트: `notes/lecture-02-sql-basics.md` (슬라이드 p.6~88)
오늘 목표: 테이블을 만들고 키로 관계를 걸 수 있고, 기본 쿼리가 계산하는 결과(for-each semantics)를 설명할 수 있다.

## 0. 선수 개념

- **table** = 표 전체 / **row(tuple)** = 행 하나 / **attribute(column)** = 열 하나
- **set**: 같은 tuple 중복 불가 / **bag(multiset)**: 중복 가능 (4번 DISTINCT에서 사용)
- declarative vs imperative, key, 테이블 간 관계 표현은 수업 중에 다룸

## 1. SQL 개요 *(p.6~7)*

- **SQL**: relational database 전용 언어. **declarative**(무엇을 원하는지만 적고, 계산 방법은 DBMS가 결정), **set-at-a-time**(행 하나씩이 아니라 테이블 전체 대상).
- C/Java는 **imperative**("반복문 돌려서, 조건 맞으면, 저장해라"처럼 how를 직접 적음). SQL은 "TA인 사람의 이름을 줘"처럼 결과만 적는다.
- 계산 방법을 DBMS에 맡기기 때문에 DBMS가 최적화(인덱스 사용 등)를 자유롭게 할 수 있고, 사용자는 쿼리를 안 바꿔도 데이터가 커질 때 성능이 알아서 좋아질 수 있다.

## 2. Basic Query: SELECT-FROM-WHERE *(p.8~17)*

**Payroll** 테이블 (수업 내내 사용):

| UserID | Name    | Job  | Salary |
| ------ | ------- | ---- | ------ |
| 123    | Jack    | TA   | 50000  |
| 345    | Allison | TA   | 60000  |
| 567    | Magda   | Prof | 90000  |
| 789    | Dan     | Prof | 100000 |

```sql
SELECT P.Name, P.UserID
FROM Payroll AS P
WHERE P.Job = 'TA';
```
- 결과: Jack/123, Allison/345
- `*` = 모든 컬럼 (`SELECT * FROM Payroll;` → 테이블 전체가 그대로 나옴)
- `AS P` = alias(별칭). "이 쿼리 안에서 Payroll을 P라고 부르겠다"는 뜻이고 `P.Name`은 "P의 Name 컬럼". 테이블이 하나면 없어도 되지만 join처럼 테이블이 여러 개일 때는 사실상 필수.
- SELECT: 결과에 남길 컬럼 / FROM: 데이터를 가져올 테이블 / WHERE: 조건에 맞는 행만 남기는 필터

```sql
SELECT 반환할 attribute들
FROM   대상 테이블(들) [AS 별칭]
WHERE  필터 조건;
```

## 3. For-each Semantics *(p.18~31)*

쿼리의 결과를 의사코드로 정의하는 방식:

```python
for each row in Payroll:            # FROM
    if (row.Job == 'TA'):           # WHERE
        output (row.Name, row.UserID)   # SELECT
```

- 쿼리 결과가 헷갈릴 때 이 루프를 머릿속으로 돌려보면 된다. join, subquery로 갈수록 계속 쓰인다.

**함정: for-each는 결과의 정의일 뿐이다** *(p.29~31)*
- DBMS가 이 루프를 그대로 돌린다는 뜻이 아니다. 행이 1억 개고 TA가 두 명뿐이면 전부 훑는 건 낭비다.
- 실행 방법의 예 *(p.29~30)*
  1. Payroll 전체를 순회 (for-each 그대로)
  2. **Job index**에서 'TA'를 찾아 그 레코드만 읽기
  3. Job에 대한 **bit-map index**를 순회 (값마다 "행 순서대로 해당하면 1, 아니면 0"인 비트열을 훑으며 1인 위치만 출력)
- 세 방법은 **결과가 완전히 같고** 속도만 다르다.
- **Index**: 책 뒤의 "찾아보기"처럼, 특정 컬럼 값으로 행 위치를 바로 찾게 해주는 구조.
- **핵심**: for-each semantics는 결과를 정의할 뿐 실행 계획을 강제하지 않는다. 같은 결과만 나오면 DBMS는 어떤 방법을 써도 된다.

## 4. ORDER BY와 DISTINCT *(p.32~46)*

**ORDER BY** *(p.33~43)*
```sql
SELECT * FROM Payroll ORDER BY Job, Name;
```
- 기본은 **오름차순**. 여러 컬럼이면 앞 컬럼이 **정렬 우선순위**가 높다 (Job 먼저, 같은 Job 안에서 Name).
- 결과: (Prof, Dan), (Prof, Magda), (TA, Allison), (TA, Jack)  (Prof가 알파벳상 TA보다 앞)
- `ORDER BY Name, Job`은 Name을 먼저 정렬한다. 이 테이블은 Name이 전부 달라 Job은 영향이 없고 Allison, Dan, Jack, Magda 순이 된다.

**DISTINCT** *(p.44~46)*
```sql
SELECT Job FROM Payroll;            -- TA, TA, Prof, Prof  (bag)
SELECT DISTINCT Job FROM Payroll;   -- TA, Prof            (set)
```
- SQL의 기본은 set이 아니라 **bag semantics**. 중복 제거는 `DISTINCT`를 직접 써야 한다.
- for-each 관점: 루프가 행마다 `output`을 한 번씩 실행하니 같은 Job이 나와도 그대로 출력돼 bag이 된다.
- `DISTINCT`는 중복 행에 접근하지 않는 게 아니라, **접근은 다 하되 이미 출력한 값이면 출력만 건너뛴다.**
```python
seen = empty set
for each row in Payroll:
    if (row.Job not in seen):
        output (row.Job)
        seen.add(row.Job)
```
- 이건 의미를 보여주는 코드이고, 실제 DBMS는 정렬이나 해시 같은 더 빠른 방법으로 처리해도 된다.

## 5. CREATE / INSERT / DELETE *(p.47~59)*

**CREATE TABLE** *(p.48~49)*
```sql
CREATE TABLE Payroll (
  UserID INT,
  Name TEXT,
  Job TEXT,
  Salary INT);
```
- 스키마(컬럼 이름 + 타입)만 만들고 **행은 0개**.
- 이름은 대소문자 구분 안 함(그래도 관례를 지키는 게 가독성에 좋음). 타입 예: `CHAR(20)`, `VARCHAR(50)`, `TEXT`, `INT`, `SMALLINT`, `FLOAT`, `MONEY`, `DATETIME`.
- 타입은 statically enforced (SQLite는 예외).

**INSERT** *(p.50~52)*
```sql
INSERT INTO Payroll VALUES (123,'Jack','TA',50000);

INSERT INTO Payroll VALUES      -- 여러 행 한 번에
  (345,'Allison','TA',60000),
  (999,'Zack','Prof',90000);
```
- 값은 컬럼 선언 순서대로, 문자열은 작은따옴표. 넣은 tuple은 **persistent**.

**DELETE** *(p.53~58)*
```sql
DELETE FROM Payroll WHERE Job = 'TA';   -- 조건에 맞는 행 삭제
DELETE FROM Payroll;                    -- WHERE 없으면 모든 행 삭제 (테이블은 남음)
```

**DROP TABLE** *(p.59)*
```sql
DROP TABLE Payroll;     -- 테이블 자체 삭제
```
- 대량 삽입은 `INSERT` 반복 대신 `COPY` 권장.

## 6. Keys (Primary Key) *(p.60~75)*

**Key**: 하나의 row를 **유일하게** 식별하는 attribute(들) *(p.61~63)*

- Salary가 지금 데이터에서 전부 달라도 **우연히** 유일한 것일 뿐 key가 아니다. **어떤 데이터가 들어와도 유일**해야 하고, 데이터는 현실에서 오므로 key는 현실 규칙을 반영해야 한다 *(p.64~65)*.

```sql
CREATE TABLE Payroll (
  UserID INT PRIMARY KEY,
  Name TEXT, Job TEXT, Salary INT);
```
- 컬럼 목록 끝에 `PRIMARY KEY (UserID)`로 써도 같음 *(p.66~68)*.
- 선언하면 같은 key 값의 행을 두 번 못 넣게 DBMS가 막는다 (중복 INSERT는 제약 위반 에러). PRIMARY KEY가 없으면 완전히 같은 행이 두 개 들어가는데, 이게 **bag semantics**다. key는 중복을 막는 장치이기도 하다.

**복합 키(composite key)** *(p.69~74)*: 여러 attribute의 **조합**이 유일한 key.

| Name  | Job  | Salary |
| ----- | ---- | ------ |
| Alice | TA   | 20000  |
| Alice | Prof | 200000 |
| Bob   | Prof | 200000 |

- Name 하나만으로도(Alice 반복), Job 하나만으로도(Prof 반복) key가 안 된다. **(Name, Job) 조합은 유일**하다 ("한 사람이 같은 직업을 두 번 갖지 않는다"는 현실 규칙).
```sql
CREATE TABLE Payroll (
  Name TEXT,
  Job TEXT,
  Salary INT,
  PRIMARY KEY (Name, Job));
```
- 복합 키는 인라인 방식으로 못 쓰고 반드시 컬럼 목록 끝에 `PRIMARY KEY (col1, col2)`로 따로 선언한다 (키가 여러 컬럼이라 한 컬럼에 속하게 쓸 수 없어서).

**정리** *(p.75)*: 후보 key가 여럿이어도 SQL은 그중 하나를 **primary key**로 정하게 한다. 모든 테이블에 primary key를 두는 게 좋은 습관. 테이블 간 관계는 **foreign key**로 표현.

## 7. Foreign Keys *(p.76~87)*

**Regist** (누가 어떤 차를 등록했는지)

| UserID | Car     |
| ------ | ------- |
| 123    | Charger |
| 567    | Civic   |
| 567    | Pinto   |

**Foreign Key**: 다른 테이블의 한 row를 **유일하게 식별하는** attribute(들). 그 테이블을 "reference"한다. *(p.78~80)*

- 예: `(567, Civic)`의 주인은 UserID로 Payroll과 대조하면 Magda임을 알 수 있다.
- **방향이 중요** *(p.81~83)*
  - `Regist.UserID → Payroll.UserID`는 가능. Payroll에서 UserID가 유일하다.
  - `Payroll.UserID → Regist.UserID`는 불가. Regist에서 567이 두 번 나와서 "한 행"을 못 가리킨다.
  - **FK는 반드시 유일한 attribute(거의 항상 primary key)를 참조해야 한다.**
- FK 컬럼 자체는 중복돼도 된다(Regist에서 567이 두 번). 유일해야 하는 건 **참조 대상** 쪽.
- `(999, Tesla)`처럼 Payroll에 없는 사람을 참조하는 행은 FK를 선언하면 DBMS가 삽입을 막아준다 (참조 무결성. 슬라이드에는 없는 용어).
- Payroll에서 UserID=567 행을 DELETE하면 Regist의 567 행이 가리킬 대상이 사라져 **dangling reference**가 생긴다. 실제 DBMS는 그 DELETE를 거부하거나 Regist 행도 같이 지우는 식으로 처리하는데, 이 강의에서는 다루지 않았다.
- FK는 탐색을 빠르게 하는 장치가 아니라 **테이블 간 관계를 표현하고 잘못된 참조를 막는** 장치다. for-each semantics와 직접 관련은 없고, 이 관계를 이용해 두 테이블을 합쳐 읽는 게 다음 강의의 **join**.

```sql
CREATE TABLE Regist (
  UserID INT REFERENCES Payroll(UserID),
  Car TEXT);
```
- 참조 대상이 primary key면 `REFERENCES Payroll`로 줄여 쓸 수 있다 *(p.85~86)*.
- 복합 키 참조는 별도 줄로 *(p.87)*:
```sql
FOREIGN KEY (Name, Job) REFERENCES Payroll
```

**PK vs FK**: PK는 자기 테이블에서 행을 유일하게 식별, FK는 다른 테이블의 유일한 키를 가리킨다.

## 8. 핵심 요약 *(p.88)*

- SELECT-FROM-WHERE 기본 쿼리
- DISTINCT, ORDER BY
- Semantics: for-each는 **결과**를 정의 (실행 방법은 강제하지 않음)
- CREATE TABLE, primary key, foreign key
