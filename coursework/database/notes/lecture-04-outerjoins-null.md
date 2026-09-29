# Lecture 4: Outer Joins and NULL

*Database Management Systems, 3rd ed. (Ramakrishnan & Gehrke)*

## 1. NULLs in SQL *(슬라이드 p.5)*

> **NULL**: missing, unknown, undefined, 또는 inapplicable을 의미하는 값

WHERE절 predicate 안에 NULL이 섞이면 어떻게 평가할지가 문제가 된다:
```sql
WHERE price < 1000
  AND (size = 10 OR color = 'red')
```

## 2. SQL의 Three-Valued Logic *(슬라이드 p.6~12)*

SQL predicate는 세 가지 값 중 하나로 평가된다:

| 값 | 숫자 |
|---|---|
| False | 0 |
| Unknown | 0.5 |
| True | 1 |

- `price < 1000`에서 price가 50이면 True, 2000이면 False, **NULL이면 Unknown** *(p.7)*
- `A op B`는 A, B가 둘 다 NULL이 아니면 True/False, 하나라도 NULL이면 **Unknown** *(p.8)*
  - `A AND B = min(A, B)`
  - `A OR B = max(A, B)`
  - `NOT A = 1 - A`
- **SQL은 조건이 True로 평가되는 튜플만 반환한다** (Unknown, False는 모두 걸러짐) *(p.8~12)*

### 예시로 보는 함정 *(p.9~12)*
```sql
SELECT * FROM Toys WHERE (price <= 100) OR (price > 100);
```
- 직관적으로는 항상 참일 것 같지만, price가 NULL인 행은 `(NULL<=100)=Unknown OR (NULL>100)=Unknown → max(0.5,0.5)=0.5(Unknown)`이 되어 **반환되지 않는다**
- 모든 행을 받으려면 `OR (price IS NULL)`을 명시적으로 추가해야 함

### Discussion *(p.13~16)*
- NULL과 3값 논리는 query optimizer에게 큰 골칫거리다: `A OR NOT(A) ≠ True`, aggregate 함수도 NULL을 특별 취급, outer join은 교환/결합법칙이 성립하지 않음 등
- 컬럼에 NULL이 절대 없다는 걸 안다면 `NOT NULL`로 선언해서 optimizer를 도와줄 수 있다:
```sql
CREATE TABLE Toys (
  Name VARCHAR(256) NOT NULL,
  Price INT NOT NULL,
  Size INT,           -- this may be null
  Color VARCHAR(256)  -- same here
);
```
- 그러면 `(price <= 100) OR (price > 100)` 같은 조건은 optimizer가 "항상 참"으로 보고 아예 제거할 수 있음

## 3. Outer Joins *(슬라이드 p.18~24)*

Inner join은 두 테이블에 **매칭되는 행이 있는 경우만** 결과에 포함시킨다 — 즉, 암묵적으로 두 인스턴스가 모두 not-null이라고 가정하는 것.

차를 안 가진 사람도 이름은 포함시키고 싶다면? *(p.18~19)*
```sql
SELECT P.Name, R.Car
FROM Payroll AS P
     LEFT OUTER JOIN Registry AS R
     ON P.UserID = R.UserID;
```
- 매칭되는 Registry 행이 없으면 **NULL**로 채워서라도 Payroll 쪽 행은 다 보존한다 — NULL이 여기서는 "차가 없음"의 placeholder 역할

의사코드로 보면 *(p.21)*:
```python
foreach row_p in Payroll:
    found = False
    foreach row_r in Registry:
        if row_p.userID == row_r.userID:
            output(row_p.name, row_r.car)
            found = True
    if not found:
        output(row_p.name, NULL)
```

### Outer Join의 종류 *(p.22)*
- **LEFT OUTER JOIN**: 왼쪽 테이블의 모든 행 보존
- **RIGHT OUTER JOIN**: 오른쪽 테이블의 모든 행 보존
- **FULL OUTER JOIN**: 양쪽 테이블의 모든 행 보존

### 마무리 생각 *(p.24)*
- Outer join은 inner join보다 최적화 여지가 적음 — 꼭 필요할 때만 사용
- LEFT OUTER JOIN이 유용한 전형적 상황: **one-to-many** 관계 (회사가 0개 이상의 제품을 만듦, 학생이 0개 이상의 수업을 들음, 고객이 0개 이상의 주문을 함)
- RIGHT/FULL OUTER JOIN을 써야 할 좋은 이유는 거의 없음 — SQLite는 아예 지원하지 않음

## 4. Self Joins *(슬라이드 p.26~38)*

- SQL 쿼리의 FROM절에는 같은 relation이 여러 번 등장할 수 있다 — 이를 **self-join**이라 부른다
```sql
FROM Registry AS R1, Registry AS R2, Payroll AS P
```

### 왜 필요한가? *(p.27~31)*
"Civic *과* Ferrari를 둘 다 소유한 사람"을 찾고 싶다고 하자. 다음 쿼리는 작동하지 않는다:
```sql
SELECT P.Name, R.Car
FROM Payroll AS P, Registry AS R
WHERE P.UserID = R.UserID
  AND R.Car = 'Civic'
  AND R.Car = 'Ferrari';  -- 하나의 R 행이 두 값을 동시에 가질 수 없음
```
- 결과는 항상 공집합 — SQL의 for-each(per-row) semantics 때문에, 한 번의 순회에서 한 row의 Car 컬럼이 'Civic'이면서 동시에 'Ferrari'일 수는 없다
- 필요한 건 한 사람이 소유한 자동차 두 대를 **한 행에 나란히** 놓는 것 — 그러려면 Registry를 두 번 "다시 순회"해야 하고, 이게 self-join이 필요한 이유

### Self-Join = All-Pairs *(p.32~35)*
```sql
SELECT * FROM Registry AS R1, Registry AS R2;
```
- 이 자체로는 R1×R2의 **모든 조합(cartesian product, all-pairs)**을 만든다 (자기 자신과의 조합 포함)
- 여기에 조건을 걸어 필터링:
  - `WHERE R1.UserID = R2.UserID`: 같은 사람이 소유한 차량 쌍만 남김 (단, (Civic,Civic)처럼 자기 자신과 짝지어진 중복 포함)
  - `AND R1.Car <> R2.Car`: 서로 다른 두 차량 쌍만 남겨 중복 제거

### 최종 쿼리 *(p.37~38)*
```sql
SELECT P.Name, R1.Car, R2.Car
FROM Registry AS R1, Registry AS R2, Payroll AS P
WHERE R1.UserID = P.UserID
  AND R2.UserID = P.UserID
  AND R1.Car = 'Civic'
  AND R2.Car = 'Ferrari';
```
- 결과: Magda(UserID 567) — Civic과 Ferrari를 둘 다 소유

> Self-join은 결국 "테이블 데이터를 다시 한 번 순회"하는 수단이다. Self-join으로 모든 pair(또는 triple, quadruple...)를 만든 뒤, 원하는 조합만 필터링하는 식으로 쓴다.

## 5. Set/Bag 연산 *(슬라이드 p.40~44)*

- **Relational model은 set semantics**가 기본 — 하나의 relation 안에 중복 레코드는 원래 말이 안 됨
- 하지만 SQL이 중간 결과를 계산하는 과정에서는 중복이 자주 생기고, 이 중복이 (aggregate 계산 등에서) 중요한 의미를 가질 수 있음 → **SQL은 보통 bag semantics를 가정**

| 집합 연산 | 의미 | | 대응하는 bag 연산 | 의미 |
|---|---|---|---|---|
| `UNION` | 합집합(중복 제거) | | `UNION ALL` | bag 합집합(중복 유지, count 덧셈) |
| `INTERSECT` | 교집합 | | `INTERSECT ALL` | bag 교집합(count의 min) |
| `EXCEPT` | 차집합 | | `EXCEPT ALL` | bag 차집합(count의 max(0, 차)) |

```sql
(SELECT * FROM T1)
UNION
(SELECT * FROM T2);

(SELECT name, color FROM T1)
EXCEPT ALL
(SELECT name, color FROM T2);
```
- "set semantics"라고 하면 "중복 없음", "bag semantics"라고 하면 "중복 있음"을 의미하는 용어로 계속 쓰인다

## Lecture 4 핵심 요약

- SQL은 NULL 때문에 3값 논리(True/False/Unknown)로 동작하며, WHERE절은 **True인 것만** 반환 — 직관과 어긋나는 경우가 많으니 주의
- **LEFT/RIGHT/FULL OUTER JOIN**: 매칭 안 되는 쪽을 NULL로 채워서라도 원본 행을 보존. 실무에서는 거의 LEFT OUTER JOIN만 사용
- **Self-join**: 같은 테이블을 여러 번 FROM에 등장시켜 "다시 순회" — all-pairs를 만든 뒤 조건으로 필터링하는 패턴
- SQL의 집합 연산(UNION/INTERSECT/EXCEPT)과 그 bag 버전(...ALL)의 차이
