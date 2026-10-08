# Lecture 2: SQL Basics — 수업노트

> 정리 노트: `notes/lecture-02-sql-basics.md` (슬라이드 p.6~88)
> 오늘 목표: 테이블을 만들고 키로 관계를 걸 수 있고, 기본 쿼리가 계산하는 결과(for-each semantics)를 설명할 수 있다.

## 0. 선수 개념 점검

- **Relational model 용어**: table = 표 전체 / row(tuple) = 표의 행 하나 / attribute(column) = 열 하나(성분 1개)
- **Set vs bag**: set은 같은 tuple이 있을 수 없다. bag(multiset)은 같은 tuple이 여러 번 있을 수 있다. 4번 섹션(DISTINCT)에서 다시 쓰인다.
- Declarative vs imperative, key, 테이블 간 관계 표현은 수업 중에 다뤘다.

## 1. SQL 개요 *(p.6~7)*

- **SQL(Structured Query Language)**: relational database 전용 언어. Java, Python, C++ 같은 범용 언어가 아니다.
- **Declarative, set-at-a-time**
  - **Declarative**: 원하는 결과가 *무엇(what)* 인지만 적는다. *어떻게(how)* 계산할지는 시스템(DBMS)이 정한다.
  - **Set-at-a-time**: 행 하나씩이 아니라 테이블(행의 집합) 전체를 대상으로 연산한다.
- C나 Java는 **imperative**다. "반복문 돌려서, 조건 맞으면, 저장해라"처럼 절차(how)를 직접 적는다. SQL은 "TA인 사람의 이름을 줘"처럼 결과만 적는다.
- **왜 이렇게 설계했나**: 계산 방법을 시스템에 맡기면 DBMS가 인덱스를 쓸지 전체를 훑을지 같은 최적화를 마음대로 할 수 있다. 사용자는 쿼리를 안 바꿔도 되고, 데이터가 커져도 성능이 알아서 좋아질 수 있다.
- 확인: SQL 쿼리는 *무엇을 원하는지*만 적는 일이고, 그 결과 시스템은 *찾는 방법을 알아서 최적화*할 자유를 얻는다.

## 2. Basic Query: SELECT-FROM-WHERE *(p.8~17)*

수업 내내 쓰는 **Payroll** 테이블:

| UserID | Name | Job | Salary |
|---|---|---|---|
| 123 | Jack | TA | 50000 |
| 345 | Allison | TA | 60000 |
| 567 | Magda | Prof | 90000 |
| 789 | Dan | Prof | 100000 |

**예제 1** *(p.8~9)*
```sql
SELECT *
FROM Payroll;
```
- `*`는 모든 컬럼. 테이블 전체(컬럼 4개, 행 4개)가 그대로 나온다.

**예제 2** *(p.10~17)*
```sql
SELECT P.Name, P.UserID
FROM Payroll AS P
WHERE P.Job = 'TA';
```
- 결과 컬럼: Name, UserID
- 결과 행: Jack/123, Allison/345
- **`P`는 alias(별칭)**: `Payroll AS P`는 "이 쿼리 안에서는 Payroll을 P라고 부르겠다"는 뜻이고 `P.Name`은 "P의 Name 컬럼". 지금은 테이블이 하나라 없어도 되지만 테이블이 여러 개 나오는 쿼리(join)에서는 사실상 필수.

**일반형**
```sql
SELECT 반환할 attribute들
FROM   대상 테이블(들)  [AS 별칭]
WHERE  필터 조건;
```
- **SELECT**: 결과에 남길 컬럼
- **FROM**: 데이터를 가져올 테이블
- **WHERE**: 조건에 맞는 행만 남기는 필터

## 3. Semantics: For-each Semantics *(p.18~31)*

예제 2 쿼리가 계산하는 결과를 일반 프로그래밍 언어 의사코드로 쓰면:

```python
for each row in Payroll:
    if (row.Job == 'TA'):
        output (row.Name, row.UserID)
```

| SQL | 의사코드 |
|---|---|
| `FROM Payroll` | `for each row in Payroll` (순회 대상) |
| `WHERE P.Job = 'TA'` | `if (row.Job == 'TA')` (필터) |
| `SELECT P.Name, P.UserID` | `output (row.Name, row.UserID)` (출력할 컬럼) |

- 이렇게 쿼리가 **무슨 결과를 내는지** 정의하는 방식이 **for-each semantics**. 쿼리 결과가 헷갈릴 때 이 루프를 머릿속으로 돌려보면 된다. join, subquery로 갈수록 계속 쓰인다.

**함정: for-each는 결과의 정의일 뿐이다** *(p.29~31)*
- DBMS가 이 루프를 그대로 돌린다는 뜻이 아니다. 행이 1억 개고 TA가 두 명뿐이면 전부 훑는 건 낭비다.
- 실행 방법의 예 *(p.29~30)*
  1. Payroll 전체를 순회 (for-each 그대로)
  2. **Job index**에서 'TA'를 찾아 그 레코드만 읽기
  3. Job에 대한 **bit-map index**를 순회
- 세 방법은 **결과가 완전히 같고** 속도만 다르다.

**Index란**: 책 맨 뒤 "찾아보기"와 같다. `Job` 컬럼에 index를 만들어두면 "Job = 'TA'인 행의 저장 위치"를 바로 찾을 수 있어서 테이블 전체를 읽지 않고 해당 행만 읽는다.

시각화 (저장 위치 [1]~[4], 이어서 1억 행까지):
```
방법 1: 전체 순회
 [1] Job=TA? -> 맞음, 출력
 [2] Job=TA? -> 맞음, 출력
 [3] Job=TA? -> 아님
 [4] Job=TA? -> 아님
  ...
 [1억] Job=TA? -> 아님        => 1억 번 검사

방법 2: Job index
 Job index:  Prof -> [3],[4],...   TA -> [1],[2]
 index에서 'TA' 찾기 -> [1],[2]
 [1] 읽기 -> 출력, [2] 읽기 -> 출력   => 테이블에서는 2행만 읽음

방법 3: bit-map index (값마다 "행 순서대로 해당하면 1, 아니면 0")
         위치:  [1] [2] [3] [4] ...
 Job=TA   :     1   1   0   0  ...
 Job=Prof :     0   0   1   1  ...
 TA 비트열을 훑으며 1인 위치만 출력 (비트열은 다 훑지만 행 전체를 읽는 것보다 훨씬 가볍다)
```

**핵심**: for-each semantics는 **결과를 정의할 뿐 실행 계획을 강제하지 않는다.** SQL은 결과가 무엇이어야 하는지만 정의했으므로, 같은 결과만 나오면 DBMS는 어떤 방법을 써도 된다.

## 4. ORDER BY와 DISTINCT *(p.32~46)*

### ORDER BY *(p.33~43)*
```sql
SELECT * FROM Payroll ORDER BY Name;
```
- 기본은 **오름차순**. Name 순서는 Allison, Dan, Jack, Magda.
- 여러 컬럼: `ORDER BY Job, Name` → Job으로 먼저 정렬하고 같은 Job 안에서 Name으로 정렬. 컬럼 순서가 곧 **정렬 우선순위**.

`ORDER BY Job, Name` 결과 (Prof가 알파벳상 TA보다 앞):

| Job | Name |
|---|---|
| Prof | Dan |
| Prof | Magda |
| TA | Allison |
| TA | Jack |

- `ORDER BY Name, Job`은 Name을 먼저 정렬한다. 이 테이블은 Name이 전부 달라서 Job은 영향을 못 주고 Allison, Dan, Jack, Magda 순이 된다. 위 결과와 다르다.

### DISTINCT *(p.44~46)*
```sql
SELECT Job FROM Payroll;
```
→ `TA, TA, Prof, Prof` (행마다 하나씩 나오니 중복이 남는다) — **bag semantics**

```sql
SELECT DISTINCT Job FROM Payroll;
```
→ `TA, Prof` (중복 제거) — **set semantics**

- SQL의 기본은 set이 아니라 **bag**이다. 중복 제거는 `DISTINCT`를 직접 써야 한다.
- for-each 관점: 루프가 행마다 `output`을 한 번씩 실행하니 같은 Job이 나와도 그대로 출력돼 bag이 된다.
- `DISTINCT`를 붙이면 중복 행에 **접근하지 않는** 게 아니라, **접근은 다 하되 이미 출력한 값이면 출력만 건너뛴다.** 이미 나왔는지 알려면 그 행의 값을 봐야 하기 때문이다.
```python
seen = empty set
for each row in Payroll:
    if (row.Job not in seen):
        output (row.Job)
        seen.add(row.Job)
```
- 이건 의미를 보여주는 코드이고, 실제 DBMS는 정렬이나 해시 같은 더 빠른 방법으로 처리해도 된다 (3번 섹션과 같은 얘기).

## 5. Tables in SQL: CREATE / INSERT / DELETE *(p.47~59)*

### CREATE TABLE *(p.48~49)*
```sql
CREATE TABLE Payroll (
  UserID INT,
  Name TEXT,
  Job TEXT,
  Salary INT);
```
- `INT`, `TEXT`는 각 attribute의 **데이터 타입**.
- `CREATE TABLE`은 **테이블의 틀(스키마)만** 만든다. 컬럼 이름과 타입만 정해지고 **행은 0개**(빈 표).
- 테이블/컬럼 이름은 대소문자 구분 안 함(case-insensitive). 그래도 가독성 때문에 관례를 지키는 게 좋다.
- 타입 종류: 문자열(`CHAR(20)`, `VARCHAR(50)`, `TEXT`), 숫자(`INT`, `SMALLINT`, `FLOAT`), `MONEY`, `DATETIME` 등. 벤더마다 고유 타입도 많다.
- 타입은 **statically enforced**: 컬럼이 INT면 문자열을 못 넣게 막는다. 단 **SQLite는 예외**.

### INSERT *(p.50~52)*
```sql
INSERT INTO Payroll VALUES (123,'Jack','TA',50000);
INSERT INTO Payroll VALUES (345,'Allison','TA',60000);
```
- `INSERT INTO 테이블명 VALUES (값들...)`. 값은 컬럼 선언 순서대로, 문자열은 작은따옴표로 감싼다.
- 넣은 tuple은 **persistent**: 컴퓨터를 꺼도 남는다.
- 여러 행을 한 번에 넣는 동치 문법:
```sql
INSERT INTO Payroll VALUES
  (123,'Jack','TA',50000),
  (345,'Allison','TA',60000),
  (999,'Zack','Prof',90000);
```

### DELETE *(p.53~58)*
(Jack, Allison, Zack 세 행이 있다고 가정)
```sql
DELETE FROM Payroll WHERE Job = 'TA';
```
- 조건에 맞는 행들 삭제. Jack, Allison이 지워지고 Zack만 남는다.
```sql
DELETE FROM Payroll;
```
- WHERE가 없으면 조건이 항상 참이라 **모든 행**이 삭제된다. **테이블 자체는 남고** 컬럼 구조만 있는 빈 테이블이 된다.

### DROP TABLE과 정리 *(p.59)*
```sql
DROP TABLE Payroll;
```
- 테이블 자체를 삭제. 과제에서는 자주 쓰지만 실무 앱에서는 조심해야 한다.
- INSERT한 tuple은 persistent, 대량 삽입은 `INSERT`를 반복하지 말고 `COPY`를 권장.

## 6. Keys (Primary Key) *(p.60~75)*

**도입 질문**: "Magda 행만 지워라"처럼 WHERE에 넣으면 항상 한 행만 걸리는 컬럼이 있나?
- UserID는 값이 고유하므로 가능. Name, Job, Salary는 겹칠 수 있어서 불가.
- Salary는 지금 데이터에서 전부 달라도 **우연히** 유일한 것일 뿐이다. 같은 임금이 들어올 수 있으면 key가 아니다. **지금 데이터에서 우연히 유일한 것**과 **어떤 데이터가 들어와도 유일해야 하는 것**은 다르다. 데이터는 현실에서 오므로 키는 현실 규칙을 반영해야 한다 *(p.64~65)*.

> **Key**: 하나의 row를 **유일하게** 식별하는 attribute(들) *(p.61~63)*

```sql
CREATE TABLE Payroll (
  UserID INT PRIMARY KEY,
  Name TEXT, Job TEXT, Salary INT);
```
- 컬럼 목록 끝에 따로 `PRIMARY KEY (UserID)`로 써도 같은 뜻 *(p.66~68)*.
- 선언하면 DBMS가 **같은 UserID를 가진 행을 두 번 못 넣게** 막는다.

### 복합 키 *(p.69~74)*

| Name | Job | Salary |
|---|---|---|
| Alice | TA | 20000 |
| Alice | Prof | 200000 |
| Bob | Prof | 200000 |

- Name 하나만으로도(Alice 반복), Job 하나만으로도(Prof 반복) key가 안 된다.
- **(Name, Job) 조합은 유일**하다. 컬럼을 추가하지 않아도 key가 있다. "한 사람이 같은 직업을 두 번 갖지 않는다"는 현실 규칙이 있으면 이 조합은 어떤 행이든 하나만 가리킨다. 이것이 **복합 키(composite key)**.
```sql
CREATE TABLE Payroll (
  Name TEXT,
  Job TEXT,
  Salary INT,
  PRIMARY KEY (Name, Job));
```
- 복합 키는 인라인 방식으로는 못 쓰고 반드시 **컬럼 목록 끝에 `PRIMARY KEY (col1, col2)`로 따로** 선언한다. 키가 여러 컬럼이라 한 컬럼에 속하게 쓸 수 없어서다.

### 정리 *(p.75)*
- Key = row를 유일하게 식별하는 attribute(들)
- 후보가 여러 개일 수 있는데 SQL은 그중 **하나를 primary key로 정하게** 강제
- 모든 테이블에 primary key를 두는 게 좋은 습관 (예외도 있음)
- 테이블 간 관계는 **foreign key**로 표현 (다음 절)

**확인**: `(Name, Job)`이 PK인 테이블에 `(Alice, TA, 99999)`를 한 번 더 INSERT하면 DBMS가 **에러로 거부**한다(제약 위반). PRIMARY KEY 선언이 없으면 그냥 들어가서 완전히 같은 행이 두 개 생기는데, 이게 **bag semantics**다. 키는 중복을 막아주는 장치이기도 하다.

## 7. Foreign Keys *(p.76~87)*

**Payroll**

| UserID | Name | Job | Salary |
|---|---|---|---|
| 123 | Jack | TA | 50000 |
| 345 | Allison | TA | 60000 |
| 567 | Magda | Prof | 90000 |
| 789 | Dan | Prof | 100000 |

**Regist** (누가 어떤 차를 등록했는지)

| UserID | Car |
|---|---|
| 123 | Charger |
| 567 | Civic |
| 567 | Pinto |

- `(567, Civic)`의 주인은 UserID로 두 표를 대조하면 Magda임을 알 수 있다.

> **Foreign Key**: 다른 테이블의 한 row를 **유일하게 식별하는** attribute(들). 그 테이블을 "reference"한다. *(p.78~80)*

- **방향이 중요**하다 *(p.81~83)*
  - `Regist.UserID → Payroll.UserID`는 유효. Payroll에서 UserID가 유일하다.
  - `Payroll.UserID → Regist.UserID`는 불가. Regist에서 567이 두 번 나와서 "한 행"을 못 가리킨다.
  - **FK는 반드시 유일한 attribute(거의 항상 primary key)를 참조해야 한다.**
- FK 컬럼 자체는 유일하지 않아도 된다(Regist에서 567이 두 번). 유일해야 하는 건 **참조 대상(Payroll.UserID)** 쪽이다.
- `(999, Tesla)`처럼 Payroll에 없는 사람을 참조하는 행은 FK를 선언하면 DBMS가 삽입을 막아준다. (참조 무결성이라고 부른다. 슬라이드에는 없는 용어.)
- Payroll에서 UserID=567 행을 DELETE하면 Regist의 567 행이 가리킬 대상이 사라져 **dangling reference**가 생긴다. 실제 DBMS는 그 DELETE를 거부하거나 Regist 행도 같이 지우는 식으로 처리하는데, 이 강의에서는 다루지 않았다.
- FK는 탐색을 빠르게 하는 장치가 아니다. **테이블 간 관계를 표현하고 잘못된 참조를 막는** 장치다. for-each semantics와 직접 관련은 없고, 이 관계를 이용해 두 테이블을 합쳐 읽는 게 다음 강의의 **join**이다.

```sql
CREATE TABLE Payroll (
  UserID INT PRIMARY KEY,
  Name TEXT, Job TEXT, Salary INT);

CREATE TABLE Regist (
  UserID INT REFERENCES Payroll(UserID),
  Car TEXT);
```
- `REFERENCES 테이블(컬럼)`: 그 테이블의 그 컬럼을 참조한다고 선언. 참조 대상이 그 테이블의 primary key면 `REFERENCES Payroll`로 줄여 쓸 수 있다 *(p.85~86)*.
- 복합 키를 참조하는 FK는 별도 줄로 선언 *(p.87)*:
```sql
CREATE TABLE Regist (
  Name TEXT,
  Job TEXT,
  Car TEXT,
  FOREIGN KEY (Name, Job) REFERENCES Payroll);
```

**PK vs FK**: PK는 자기 테이블에서 행을 유일하게 식별한다. FK는 다른 테이블의 유일한 키를 가리키는 attribute다.

## 8. 핵심 요약 *(p.88)*

- SELECT-FROM-WHERE 기본 쿼리
- DISTINCT, ORDER BY
- Semantics: for-each로 SQL이 계산하는 **결과**를 정의 (실행 방법은 강제하지 않음)
- CREATE TABLE, KEY(primary key), FOREIGN KEY

다음 시간은 SQL을 계속 다룬다.
