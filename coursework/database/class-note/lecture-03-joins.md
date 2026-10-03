# Lecture 3: Joins — 수업노트

> 정리 노트: `notes/lecture-03-joins.md` (슬라이드 p.5~59)
> 오늘 목표: 두 테이블을 join으로 묶는 쿼리를 쓰고, 그 결과가 어떻게 계산되는지(nested-loop semantics) 설명할 수 있다. 실제 DB가 왜 그 방식대로 돌리지 않는지도 말할 수 있다.

## 0. 선수 개념 점검

- 2강 내용(foreign key, declarative, alias, for-each semantics, set vs bag)은 이전 수업에서 다뤘기 때문에 점검 없이 바로 진행했다.

## 1. Recap: Foreign Key & SELECT-FROM-WHERE *(p.5~9)*

수업 내내 쓰는 두 테이블:

**Payroll**

| UserID | Name | Job | Salary |
|---|---|---|---|
| 123 | Leslie | TA | 50k |
| 345 | Frances | TA | 60k |
| 567 | Magda | Prof | 120k |
| 789 | Quinn | Prof | 100k |

**Registry**

| UserID | Car |
|---|---|
| 123 | Charger |
| 567 | Civic |
| 567 | Ferrari |

- **Foreign key**는 다른 테이블의 row를 유일하게 식별하는 attribute(들)다. Registry.UserID는 Payroll의 primary key(UserID) 값을 그대로 복사해서 담고 있다.
- **참조 방향이 중요하다.**
  - Registry.UserID → Payroll.UserID는 유효하다. Payroll의 UserID는 유일해서 Registry의 값 하나가 Payroll의 row 하나를 가리킬 수 있다.
  - 반대 방향(Payroll → Registry)은 무효다. Registry에는 567이 두 번 나와서 Payroll의 567이 어느 row를 가리키는지 정해지지 않는다.
  - 정리: FK는 **유일성이 보장된 쪽(key)을 가리켜야** 한다.
- SQL은 declarative라서 *what*만 쓰고 *how*는 시스템이 정한다. 이게 7번 섹션의 핵심 복선이다.

## 2. Joins 개요 *(p.11)*

- **Foreign key는 테이블 간 관계를 *describe*(기술)한다.** "이 컬럼은 저 테이블을 가리킨다"는 선언일 뿐이다.
- **Join은 그 관계를 *realize*(구현)해서** 실제로 두 테이블의 row를 결합한다.
- 항상 foreign key로만 join하는 건 아니다. join 조건은 자유롭게 줄 수 있다.
- Join에는 여러 종류(flavor)가 있다. 오늘은 inner join을 배우고, outer join은 4강에서 다룬다.

## 3. Inner Joins *(p.13)*

> Inner join은 SQL 쿼리의 "bread and butter"다. 흔히 그냥 "join"이라고 부른다. 두 relation을 **join predicate**(결합 조건)로 교집합(intersect)한다.

Payroll과 Registry를 **UserID가 같은 값끼리** 묶으면:

| Name | Job | Salary | Car |
|---|---|---|---|
| Leslie | TA | 50k | Charger |
| Magda | Prof | 120k | Civic |
| Magda | Prof | 120k | Ferrari |

포인트 세 가지:
1. **Frances(345)와 Quinn(789)은 결과에 없다.** 차 등록이 없어서 짝이 없다. inner join은 짝이 있는 것만 남긴다.
2. **Magda는 두 번 나온다.** Registry에 567이 두 row라 매치도 두 건이다. join은 1:1 매칭이 아니라 *조건을 만족하는 모든 조합*을 만든다.
3. 결과 컬럼은 두 테이블의 컬럼이 이어붙은 형태다. 위 표는 그중 일부만 골라 보여준 것이다.

**확인 문제**: Payroll에 `(999, Zoe, TA, 40k)`, Registry에 `(999, Tesla)`, `(999, Prius)`, `(999, Model3)`을 추가하고 UserID로 inner join하면 Zoe는 3번 나온다. 조건을 만족하는 모든 조합이 나오니까 Zoe(1) × 차(3) = 3 row다.

## 4. Nested-Loop Semantics *(p.14~27)*

"모든 조합 중 조건 맞는 것"을 정확히 정의하는 방법이 **nested-loop semantics**다. 2강의 for-each semantics를 루프 두 겹으로 확장한 것이다.

```python
foreach row_p in Payroll:
    foreach row_r in Registry:
        if row_p.userID == row_r.userID:
            output(row_p.name, row_r.car)
```

손으로 따라가 보면:

| 바깥 루프 (Payroll) | 안쪽 루프가 훑는 Registry | 매치 | 출력 |
|---|---|---|---|
| 123 Leslie | 123, 567, 567 | 123 | (Leslie, Charger) |
| 345 Frances | 123, 567, 567 | 없음 | 없음 |
| 567 Magda | 123, 567, 567 | 567 두 개 | (Magda, Civic), (Magda, Ferrari) |
| 789 Quinn | 123, 567, 567 | 없음 | 없음 |

- 바깥 루프의 **row 하나마다 안쪽 루프가 처음부터 끝까지** 다시 돈다. 비교 횟수는 4 × 3 = 12번이다.
- 매치가 없으면 출력이 없다. Frances와 Quinn이 사라지는 이유다.
- 매치가 여러 개면 출력도 여러 번이다. Magda가 두 번 나오는 이유다.
- 결과는 (Leslie, Charger), (Magda, Civic), (Magda, Ferrari) 세 건이다.
- 앞의 확인 문제와 같은 원리다. Zoe가 바깥 루프에서 한 번 잡히면, 안쪽 루프에서 999가 세 번 매치되어 출력이 세 번 나온다.

**중요한 단서**: 이건 join이 *어떤 결과를 내야 하는지*를 정의하는 의미(semantics)일 뿐이다. DB가 실제로 이렇게 계산한다는 뜻이 아니다. (7번에서 다시 다룬다.)

**확인 문제**: `if`를 빼고 모든 조합을 출력하면 4 × 3 = **12행**이 된다. `if`는 모든 조합 중에서 **조건을 만족하는 것만 걸러내는 필터**다. 이 "일단 전부 이어붙인 조합을 만들고 → 조건으로 거른다"는 관점은 6번 멘탈 모델로 이어진다.

## 5. Inner Join 문법 *(p.28~29, p.35)*

같은 join을 SQL로 쓰는 방법이 두 가지 있다.

**Explicit(명시적) 문법** *(p.28)*
```sql
SELECT P.Name, R.Car
FROM Payroll AS P
     INNER JOIN Registry AS R
     ON P.UserID = R.UserID;
```
- join할 테이블은 `INNER JOIN`으로, 결합 조건은 `ON`으로 쓴다.
- `INNER JOIN`은 그냥 `JOIN`이라고 써도 같다.

**Implicit(암묵적) 문법** *(p.29)*
```sql
SELECT P.Name, R.Car
FROM Payroll AS P, Registry AS R
WHERE P.UserID = R.UserID;
```
- `FROM`에 테이블을 쉼표로 나열하고, 결합 조건을 `WHERE`에 쓴다.
- nested loop 코드와 거의 1:1로 대응된다. `FROM`의 두 테이블이 두 겹 루프이고, `WHERE`가 `if`다.

둘은 같은 결과를 낸다. 차이는 *결합 조건을 어디에 쓰느냐*(`ON` vs `WHERE`)뿐이다.

### 함정: implicit 문법과 연산자 우선순위 *(p.35)*

implicit 문법은 결합 조건과 필터 조건이 전부 `WHERE`에 섞여 들어간다.

```sql
-- (A) 괄호 있음 (의도한 대로)
WHERE P.UserID = R.UserID AND (R.Car = 'Civic' OR R.Car = 'Ferrari');

-- (B) 괄호 없음 (다른 의미가 됨!)
WHERE P.UserID = R.UserID AND R.Car = 'Civic' OR R.Car = 'Ferrari';
```

의도는 "Civic이나 Ferrari를 가진 사람의 이름과 차"이다.

**연산자 우선순위: AND가 OR보다 먼저 묶인다.** 산수에서 `×`가 `+`보다 먼저 계산되는 것과 같다. (`2 + 3 * 4`는 `2 + (3 * 4)`.) SQL에서는 `AND`가 곱셈, `OR`이 덧셈 역할이다.

```sql
A AND B OR C   →   (A AND B) OR C
```

`OR`는 양쪽 중 한쪽만 참이어도 전체가 참이다.

**(B)의 실제 해석**
```sql
WHERE (P.UserID = R.UserID AND R.Car = 'Civic') OR R.Car = 'Ferrari';
```
- 왼쪽 덩어리는 의도대로 "Civic을 가진 사람과 짝지은 row"다.
- 오른쪽 `R.Car = 'Ferrari'`는 **join 조건과 상관없이** 단독으로 참이 될 수 있다.

**끼어드는 row**: nested loop로 보면 Registry의 `(567, Ferrari)`가 안쪽 루프에 나올 때 `R.Car = 'Ferrari'`가 참이므로, **바깥 루프의 Payroll row가 누구든** 조건을 통과한다.

| Name | Car |
|---|---|
| Leslie | Ferrari |
| Frances | Ferrari |
| Magda | Ferrari |
| Quinn | Ferrari |

Leslie, Frances, Quinn은 Ferrari를 가진 적이 없는데도 소유자로 나온다. join이 깨지고 Payroll 4명 × Ferrari 조합이 전부 튀어나온 것이다. (A)는 괄호 덕분에 `join 조건 AND (Civic 또는 Ferrari)`로 묶여 `(Magda, Civic)`, `(Magda, Ferrari)`만 나온다.

**정리**
- implicit 문법은 join 조건과 필터가 `WHERE`에 섞여서 이런 실수가 나기 쉽다.
- explicit 문법은 join 조건이 `ON`에 따로 있어서, `WHERE`에 `OR`를 써도 join 조건이 깨지지 않는다.
- implicit을 쓰면 `AND`/`OR`가 섞일 때 **괄호를 꼭 명시**해야 한다.

## 6. SQL 쿼리는 여러 "phase"를 가진다 *(p.30, p.36)*

- Join은 마치 **임시 테이블(temporary table)**을 만드는 것처럼 동작한다. 두 테이블을 UserID로 묶은 중간 결과가 하나 생긴다.
- 그 임시 테이블에 **WHERE 필터를 추가로 적용**할 수 있다. 그래서 쿼리는 "join으로 중간 결과 만들기 → WHERE로 거르기 → SELECT로 컬럼 고르기"처럼 단계(phase)를 가진다.
- **멘탈 모델**: SQL을 **composite tuple의 컬렉션을 만드는 과정**으로 생각해도 된다. 두 테이블의 tuple을 이어붙인(concatenate) 조합들을 만들고, 조건을 만족하는 것만 골라낸다. 앞에서 본 12행짜리 "전부 이어붙인 조합"에서 `if`로 거르는 관점과 같다.

**예제**: "Civic을 가진 사람의 이름과 연봉"
```sql
SELECT P.Name, P.Salary
FROM Payroll AS P
     INNER JOIN Registry AS R
     ON P.UserID = R.UserID
WHERE R.Car = 'Civic';
```
- **join 조건은 `ON`**, **필터 조건은 `WHERE`**에 쓴다.
- phase 순서:
  1. **FROM + JOIN + ON**: UserID로 묶어 임시 테이블을 만든다. `(Leslie, Charger)`, `(Magda, Civic)`, `(Magda, Ferrari)` 같은 composite tuple들이 생긴다.
  2. **WHERE**: `Car = 'Civic'`인 것만 남긴다. `(Magda, Civic)` 하나가 남는다.
  3. **SELECT**: `Name`, `Salary`만 고른다. 결과는 `(Magda, 120k)`.
- 다만 이건 의미(semantics)상의 순서이고, 실제 실행 순서는 다를 수 있다. (7번)

## 7. Joins 구현: 복잡도와 최적화 *(p.38~45)*

### 문제: nested loop는 너무 비싸다 *(p.38~41)*

- relation이 2개이면 루프가 두 겹이라 비교가 n × n = n²번이다.
- **k개의 relation**(각 크기 n)을 join하면 루프가 k겹이라 복잡도가 **O(nᵏ)**이다. 테이블 10개, 행 1000개씩이면 1000¹⁰이라 사실상 계산이 불가능하다.
- 그런데 **실제 DB는 nested loop로 계산하지 않는다.** nested loop는 결과가 *무엇이어야 하는지*를 정의하는 의미일 뿐이고, 같은 결과만 나오면 어떻게 계산하든 상관없다.

### 가능한 최적화 *(p.42~44)*

1. **루프 순서를 바꿔도 결과는 같다.** `foreach` 루프의 순서는 결과 집합에 영향을 주지 않아서, 시스템이 더 유리한 순서로 자유롭게 바꿀 수 있다.
2. **필터를 미리 적용해서 순회할 데이터를 줄일 수 있다.** 예를 들어 `R.Car = 'Ferrari'` 조건을 먼저 걸어 Registry를 한 행으로 줄여놓고 join하면 안쪽 루프가 훨씬 가벼워진다.
3. **index를 써서 조건에 맞는 행만 바로 찾을 수 있다.** 모든 행을 훑지 않고 키로 바로 찾아간다. (index는 이후 강의에서 다룬다.)

### 왜 필터를 앞으로 당겨도 결과가 같은가

`R.Car = 'Ferrari'` 필터가 붙은 join을 nested loop로 쓰면:

```python
foreach row_p in Payroll:
    foreach row_r in Registry:
        if row_p.userID == row_r.userID and row_r.Car == 'Ferrari':
            output(row_p.name, row_r.car)
```

`if`의 두 조건을 따로 보면:
- `row_p.userID == row_r.userID`는 **p와 r을 둘 다 봐야** 판단할 수 있다.
- `row_r.Car == 'Ferrari'`는 **r만 보면** 판단할 수 있다. p가 누구인지는 상관없다.

`AND`는 둘 다 참이어야 통과하므로, r만 보는 조건은 *r이 안쪽 루프에 들어오기 전에* 미리 검사해도 결과가 같다.

```python
ferraris = [r for r in Registry if r.Car == 'Ferrari']   # 먼저 거른다

foreach row_p in Payroll:
    foreach row_r in ferraris:                           # 안쪽 루프가 짧아졌다
        if row_p.userID == row_r.userID:
            output(row_p.name, row_r.car)
```

- `userID` 비교 횟수: 첫 번째 코드는 4 × 3 = **12번**, 두 번째 코드는 4 × 1 = **4번**.
- Ferrari가 아닌 r은 어떤 p와 만나도 `if`에서 어차피 탈락한다. 이런 r을 미리 치워도 최종 결과는 안 변하고 쓸데없는 비교만 줄어든다.

> 한 테이블의 row만 보고 판단할 수 있는 필터는 join 전에 미리 적용해도 결과가 같다. 그래서 optimizer가 앞으로 당겨 쓸 수 있다.

- 반대로 `P.UserID = R.UserID`처럼 **두 테이블을 같이 봐야 하는 조건**은 미리 적용할 수 없다. 그게 join 조건 자체이기 때문이다.
- "WHERE가 join 뒤에 적용된다"는 건 **결과가 그렇게 계산된 것과 같아야 한다**는 의미(semantics)이지, 실제로 그 순서로 실행한다는 뜻이 아니다. 결과만 같으면 optimizer가 순서를 마음대로 바꿔도 된다.

### Physical Data Independence *(p.45)*

- SQL은 declarative라서 *how*를 쿼리에 박아두지 않았다. 그래서 **query optimizer**가 최적의 실행 계획을 알아서 고른다.
- 이 덕분에 사용자는 쿼리를 그대로 두고도, DB 내부의 저장 방식이나 실행 방식이 바뀌어도 영향을 받지 않는다. 이를 **Physical Data Independence**라고 부른다.
- 1강에서 declarative의 이유로 "계산 방법을 시스템에 맡기면 최적화할 자유가 생긴다"고 했는데, 그 약속이 join에서 실제로 실현되는 지점이다.

## 8. ORDER BY / DISTINCT 복습 *(p.47~48)*

```sql
SELECT Name, UserID
FROM Payroll
WHERE Job = 'TA'
ORDER BY Salary, Name;
```
- `ORDER BY`는 결과를 정렬한다. **기본은 오름차순(ascending)**이다.
- 컬럼을 여러 개 주면 **앞 컬럼이 우선**이다. 여기서는 Salary로 먼저 정렬하고, Salary가 같은 row끼리만 Name으로 정렬한다.
- 정렬 기준인 Salary가 SELECT 목록에 없어도 된다.

```sql
SELECT DISTINCT Job
FROM Payroll
WHERE Salary > 70000;
```
- `DISTINCT`는 결과의 **중복 row를 제거**한다. SQL 결과는 기본이 bag이라, DISTINCT를 써야 set이 된다.
- Salary가 70000을 넘는 사람은 Magda(Prof), Quinn(Prof)이다. DISTINCT가 없으면 `Prof`가 두 번, 있으면 한 번만 나온다.

## 9. 테이블/키 생성 복습 *(p.50~59)*

### CREATE TABLE과 데이터 타입 *(p.50~52)*
```sql
CREATE TABLE Payroll (
    UserID INT,
    Name VARCHAR(100),
    Job VARCHAR(100),
    Salary INT
);
```
- 타입은 statically & strictly enforced다. 자주 쓰는 조합은 문자열 `VARCHAR(N)`, 숫자 `INT`/`FLOAT`, 날짜 `DATETIME`이다. SQLite는 날짜를 `VARCHAR(N)`로 대체한다.

### Primary Key *(p.53~54)*
```sql
CREATE TABLE Payroll (
    UserID INT PRIMARY KEY,
    Name VARCHAR(100), Job VARCHAR(100), Salary INT
);
```
- 컬럼 목록 끝에 `PRIMARY KEY (UserId)`로 따로 써도 된다.

### Aggregate(복합) Key *(p.55~57)*
> Key = 하나 이상의 attribute가 **in aggregate**(합쳐서) row를 유일하게 식별하는 것

```sql
CREATE TABLE Payroll (
    UserID INT, Name VARCHAR(100), Job VARCHAR(100), Salary INT,
    PRIMARY KEY (Name, Job)
);
```
- Name 단독이나 Job 단독으로는 중복될 수 있어도, **(Name, Job) 조합**이 유일하면 키가 된다.

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
- `REFERENCES Payroll`은 Payroll의 primary key를 참조한다는 뜻이다.
- 복합 키를 참조하면 복합 foreign key로 선언한다.
```sql
CREATE TABLE Registry (
    Name VARCHAR(100), Job VARCHAR(100), Car VARCHAR(50),
    FOREIGN KEY (Name, Job) REFERENCES Payroll
);
```

## Lecture 3 핵심 요약

- **Inner Join**: 두 테이블을 join predicate로 교집합한다. `INNER JOIN ... ON`(explicit) / `FROM A, B WHERE ...`(implicit) 두 문법이 동치지만, implicit에서는 AND가 OR보다 먼저 묶이는 연산자 우선순위를 조심해야 한다.
- Join의 의미는 **nested-loop semantics**로 정의되지만, 실제 실행은 **query optimizer**가 훨씬 효율적인 방법(순서 변경, 조기 필터링, 인덱스)으로 처리한다. 이것이 **Physical Data Independence**다.
- ORDER BY/DISTINCT, CREATE TABLE의 데이터 타입, (복합) Primary Key/Foreign Key 선언 문법을 복습했다.

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
