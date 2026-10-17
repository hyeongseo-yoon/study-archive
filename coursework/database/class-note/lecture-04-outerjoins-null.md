# Lecture 4: Outer Joins and NULL — 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

정리 노트: `notes/lecture-04-outerjoins-null.md` (슬라이드 p.5~44)
오늘 목표: NULL이 섞인 WHERE 조건이 왜 직관과 다르게 평가되는지 설명하고, outer join과 self-join으로 "짝 없는 행 보존"과 "같은 테이블 두 번 순회" 쿼리를 쓸 수 있다.


## 1. NULLs in SQL *(p.5)*

- **NULL**은 missing, unknown, undefined, inapplicable일 때 쓰는 특수 값이다. 0도 빈 문자열도 아니고 "값이 없거나 알 수 없다"는 표시다.
- 문제는 WHERE에 NULL이 섞이면 조건을 어떻게 평가하느냐다.

## 2. Three-Valued Logic *(p.6~16)*

### 규칙 *(p.6~8)*

SQL predicate는 True/False 둘이 아니라 세 값 중 하나로 평가된다.

| 값 | 숫자 |
|---|---|
| False | 0 |
| Unknown | 0.5 |
| True | 1 |

1. **NULL이 낀 비교는 Unknown이다.** `A op B`에서 A, B가 둘 다 NULL이 아니면 True/False, 하나라도 NULL이면 Unknown. (`price < 1000`에서 price가 50이면 True, 2000이면 False, NULL이면 Unknown.) NULL은 "모르는 값"이라 비교 판단의 근거가 없기 때문이다.
2. **논리 연산자는 숫자로 계산한다.** `A AND B = min(A, B)`, `A OR B = max(A, B)`, `NOT A = 1 - A`.
3. **WHERE는 True(=1)인 행만 통과시킨다.** False와 Unknown은 모두 걸러진다.

### 예시로 보는 함정 *(p.9~12)*

Toys 테이블: (Ball, 50), (Robot, 2000), (Kite, NULL)

```sql
SELECT * FROM Toys WHERE (price <= 100) OR (price > 100);
```

- 직관으로는 모든 행이 나올 것 같지만 **2행**(Ball, Robot)만 나온다.
- Kite: `NULL <= 100` → Unknown(0.5), `NULL > 100` → Unknown(0.5), `max(0.5, 0.5) = 0.5` → Unknown → 걸러진다.
- "NULL은 어디에도 안 속해서 걸러진다"는 직관은 결과는 맞지만, 정확한 이유는 **"Unknown이 True가 아니라서"**다.
- 그래서 `A OR NOT(A)`는 항상 True가 아니다. A가 Unknown이면 `max(0.5, 1 - 0.5) = 0.5`.
- 모든 행을 받으려면 `OR (price IS NULL)`을 명시해야 한다. NULL 판별은 `= NULL`이 아니라 `IS NULL`이다(`= NULL`도 Unknown).

### 점검 문제로 확인한 것
- `WHERE NOT (price > 100)`: Ball은 NOT(False) = 1 → 통과, Robot은 NOT(True) = 0, Kite는 NOT(Unknown) = 0.5 → 걸러짐. **결과 1행(Ball).**
- `WHERE price > 100 AND price IS NULL`: Kite는 `min(0.5, 1) = 0.5` → Unknown이라 걸러짐. **결과 0행**이며, 이유는 False가 아니라 Unknown이라서다.
- 핵심: **Unknown은 False처럼 걸러지지만, NOT을 씌워도 True가 되지 않는다.** (`NOT(Unknown) = Unknown`)

### Discussion *(p.13~16)*

- NULL과 3값 논리는 **query optimizer에게도 골칫거리**다: `A OR NOT(A) ≠ True`라서 논리적으로 당연한 단순화를 못 한다. aggregate 함수도 NULL을 특별 취급한다(5강). outer join은 교환/결합법칙이 성립하지 않아 실행 순서를 마음대로 바꿀 수 없다.
- 컬럼에 NULL이 절대 없다는 걸 안다면 **`NOT NULL`로 선언**해서 optimizer를 도울 수 있다.
```sql
CREATE TABLE Toys (
    Name  VARCHAR(256) NOT NULL,
    Price INT NOT NULL,
    Size  INT,            -- this may be null
    Color VARCHAR(256)    -- same here
);
```
- 그러면 `(price <= 100) OR (price > 100)` 같은 조건을 optimizer가 "항상 참"으로 보고 아예 제거할 수 있다.

## 3. Outer Joins *(p.18~24)*

**Payroll**(UserID, Name): 123 Leslie, 345 Frances, 567 Magda, 789 Quinn
**Registry**(UserID, Car): 123 Charger, 567 Civic, 567 Ferrari

- 상황: "모든 직원의 이름과 소유한 차를 보고 싶다. 차가 없는 직원도 이름은 나와야 한다." inner join은 Frances와 Quinn을 빠뜨린다.
- 해결: 짝이 없으면 **NULL로 채워서라도** 한쪽 행을 보존한다. NULL이 "차가 없음"의 placeholder 역할을 한다.

### 의사코드 *(p.21)*
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
- 포인트: "다를 때"가 아니라 **"Registry를 다 돌았는데 한 번도 매칭이 안 됐을 때"** NULL을 출력한다. Magda도 다른 row와는 UserID가 다르므로, "한 번이라도 매칭됐는지"를 기억하는 `found`가 필요하다.

### SQL 문법 *(p.18~19)*
```sql
SELECT P.Name, R.Car
FROM Payroll AS P
     LEFT OUTER JOIN Registry AS R
     ON P.UserID = R.UserID;
```
구조: `FROM 왼쪽테이블 LEFT OUTER JOIN 오른쪽테이블 ON 조건`

| Name | Car |
|---|---|
| Leslie | Charger |
| Frances | NULL |
| Magda | Civic |
| Magda | Ferrari |
| Quinn | NULL |

### 종류 *(p.22)*

| 종류 | 보존하는 쪽 |
|---|---|
| LEFT OUTER JOIN | 왼쪽 테이블의 모든 행 |
| RIGHT OUTER JOIN | 오른쪽 테이블의 모든 행 |
| FULL OUTER JOIN | 양쪽 테이블의 모든 행 |

### 마무리 생각 *(p.24)*
- Outer join은 inner join보다 **최적화 여지가 적다**(교환/결합법칙 불성립). 꼭 필요할 때만 쓴다.
- LEFT OUTER JOIN이 잘 맞는 상황은 **one-to-many 관계**다: 회사 → 0개 이상의 제품, 학생 → 0개 이상의 수업, 고객 → 0개 이상의 주문.
- RIGHT/FULL을 써야 할 좋은 이유는 거의 없고, SQLite는 아예 지원하지 않는다.

```sql
SELECT P.Name, R.Car
FROM Payroll AS P LEFT OUTER JOIN Registry AS R ON P.UserID = R.UserID
WHERE R.Car <> 'Civic';
```
- 결과는 **(Leslie, Charger), (Magda, Ferrari)** 2행이다. WHERE는 **행 단위**로 평가되므로 Magda의 Civic 행만 빠지고 Ferrari 행은 남는다. Frances와 Quinn은 `NULL <> 'Civic'`이 Unknown이라 걸러진다.
- 실무 포인트: LEFT OUTER JOIN으로 짝 없는 행을 살려도, **오른쪽 테이블 컬럼에 WHERE 조건을 걸면 NULL 행이 Unknown으로 걸러져서 outer join의 의미가 사라진다.**

## 4. Self Joins *(p.26~38)*

SQL 쿼리의 FROM절에는 같은 relation이 여러 번 등장할 수 있다. 이를 **self-join**이라 하고, 구분을 위해 alias가 필수다.

### 왜 필요한가? *(p.27~31)*

"Civic과 Ferrari를 **둘 다** 가진 사람"을 찾으려는 쿼리:
```sql
SELECT P.Name, R.Car
FROM Payroll AS P, Registry AS R
WHERE P.UserID = R.UserID
  AND R.Car = 'Civic'
  AND R.Car = 'Ferrari';
```
- 항상 **빈 결과**다. for-each semantics에서 한 번의 순회로 잡은 row 하나의 Car는 'Civic'이면서 동시에 'Ferrari'일 수 없다. 조건이 항상 모순이다.
- "반복문 안에 카운터 변수를 두자"는 절차적 발상이다. SQL은 declarative라서 변수도 루프도 직접 쓰지 않는다. 대신 **같은 테이블을 처음부터 다시 한 번 돌 수 있게** 한다. 바깥 루프에서 Magda-Civic 행을 잡은 채로 안쪽 루프에서 Registry를 또 돌면 Magda-Ferrari를 만날 수 있다. 이를 FROM절에 같은 테이블을 두 번 쓰는 것으로 표현한다.

### Self-Join = All-Pairs *(p.32~35)*
```sql
SELECT * FROM Registry AS R1, Registry AS R2;
```
R1의 모든 행과 R2의 모든 행의 **모든 조합(all-pairs)**. Registry가 3행이면 3 x 3 = 9행이고, 자기 자신과 짝지어진 것도 포함된다.

| R1.UserID | R1.Car  | R2.UserID | R2.Car  |
| --------- | ------- | --------- | ------- |
| 123       | Charger | 123       | Charger |
| 123       | Charger | 567       | Civic   |
| 123       | Charger | 567       | Ferrari |
| 567       | Civic   | 123       | Charger |
| 567       | Civic   | 567       | Civic   |
| 567       | Civic   | 567       | Ferrari |
| 567       | Ferrari | 123       | Charger |
| 567       | Ferrari | 567       | Civic   |
| 567       | Ferrari | 567       | Ferrari |

- 원하는 행은 6번째(Civic, Ferrari)와 8번째(Ferrari, Civic).
- `R1.UserID = R2.UserID`: **같은 사람** 소유의 쌍만 남긴다. 없으면 다른 사람끼리도 짝지어진다.
- `R1.Car <> R2.Car`: 자기 자신과의 쌍(5행, 9행 등)을 제거한다.
- 한계: 6행과 8행은 같은 쌍의 순서만 바뀐 것이고, "Civic과 Ferrari"를 지정하지도 않는다(Civic과 Charger를 가진 사람도 통과).

### 최종 쿼리 *(p.37~38)*
```sql
SELECT P.Name, R1.Car, R2.Car
FROM Registry AS R1, Registry AS R2, Payroll AS P
WHERE R1.UserID = P.UserID
  AND R2.UserID = P.UserID
  AND R1.Car = 'Civic'
  AND R2.Car = 'Ferrari';
```
1. `FROM`: Registry를 두 번 순회하고 Payroll도 둔다. 세 테이블의 모든 조합(triple)이 만들어진다.
2. `R1.UserID = P.UserID AND R2.UserID = P.UserID`: R1과 R2가 **둘 다 같은 P(같은 사람)**에 연결된다. R1.UserID = R2.UserID도 자동 성립하고, P를 거치므로 이름도 얻는다.
3. `R1.Car = 'Civic' AND R2.Car = 'Ferrari'`: R1과 R2 **각각에 한 값씩** 지정한다. 원래 쿼리는 한 R에 두 값을 요구해서 실패했지만, 이제는 서로 다른 두 R이 한 값씩 맡는다. Civic ≠ Ferrari라서 `<>`가 불필요하고, 순서가 고정되어 중복(8행)도 생기지 않는다.

| Name  | R1.Car | R2.Car  |
| ----- | ------ | ------- |
| Magda | Civic  | Ferrari |

Self-join은 "테이블 데이터를 다시 한 번 순회"하는 수단이다. 같은 테이블로 all-pairs(또는 triple, quadruple...)를 만든 뒤 원하는 조합만 필터링한다. "한 행에 값 두 개를 나란히 놓고 비교해야 할 때" 쓰는 패턴이다. 세 대를 비교하려면 R3까지 세 번 쓰면 된다. all-pairs를 만든 뒤 거르므로 데이터가 크면 비싸서, join 조건을 꼭 걸어야 한다.

## 5. Set/Bag 연산 *(p.40~44)*

- **Relational model은 set semantics**가 기본이다. 한 relation 안에 중복 레코드는 원래 없어야 한다.
- SQL은 중간 결과를 계산하는 과정에서 중복이 자주 생기고, 이 중복이 aggregate 계산 등에서 의미가 있어서 **기본적으로 bag semantics**를 가정한다.

| set 연산      | 의미         | bag 연산          | 의미                   |
| ----------- | ---------- | --------------- | -------------------- |
| `UNION`     | 합집합(중복 제거) | `UNION ALL`     | 중복 유지, count를 **덧셈** |
| `INTERSECT` | 교집합        | `INTERSECT ALL` | count의 **min**       |
| `EXCEPT`    | 차집합        | `EXCEPT ALL`    | count의 **max(0, 차)** |

```sql
(SELECT * FROM T1)
UNION
(SELECT * FROM T2);

(SELECT name, color FROM T1)
EXCEPT ALL
(SELECT name, color FROM T2);
```
- "set semantics"는 "중복 없음", "bag semantics"는 "중복 있음"을 뜻하는 용어로 계속 쓰인다.

### 예시
T1에 (Ball, red)가 3번, T2에 2번일 때: `UNION` → 1번, `UNION ALL` → 3 + 2 = 5번, `INTERSECT ALL` → min(3, 2) = 2번, `T1 EXCEPT ALL T2` → max(0, 3 - 2) = 1번, `T2 EXCEPT ALL T1` → max(0, 2 - 3) = 0번.

### 점검 문제로 확인한 것
T1에 (Kite, blue) 2번, T2에 4번일 때: `UNION ALL` → 6, `INTERSECT ALL` → 2, `T1 EXCEPT ALL T2` → 0, `T2 EXCEPT ALL T1` → 2. 개별 원소의 개수로 세면 쉽게 풀린다.

## Lecture 4 핵심 요약

- SQL은 NULL 때문에 3값 논리(True/False/Unknown)로 동작하며, WHERE절은 **True인 것만** 반환한다. `NOT(Unknown)`도 Unknown이라 직관과 어긋나는 경우가 많다.
- **LEFT/RIGHT/FULL OUTER JOIN**: 매칭 안 되는 쪽을 NULL로 채워서라도 원본 행을 보존한다. 실무에서는 거의 LEFT OUTER JOIN만 쓰고, 오른쪽 테이블 컬럼에 WHERE를 걸면 효과가 사라질 수 있다.
- **Self-join**: 같은 테이블을 여러 번 FROM에 등장시켜 "다시 순회"한다. all-pairs를 만든 뒤 조건으로 필터링하는 패턴이다.
- SQL의 집합 연산(UNION/INTERSECT/EXCEPT)과 그 bag 버전(...ALL)의 차이.

---

## 체크리스트
1. NULLs in SQL
2. Three-Valued Logic (+ 함정 예시, Discussion)
3. Outer Joins
4. Self Joins
5. Set/Bag 연산
