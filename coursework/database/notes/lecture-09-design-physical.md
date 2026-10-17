# Lecture 9: Physical Design and Indices

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*Database Systems & its Applications — Physical Design and Indices*

슬라이드 쪽번호가 인쇄되어 있지 않거나 틀려 있어서, 아래 `p.N`은 PDF 파일의 페이지 순서(1부터 시작)를 가리킨다.
구성: **① Relations → Files (디스크, relation 표현, 쿼리 실행) → ② Index 사용 (생성, 다중 index, 다중 attribute index) → ③ Index 구현 (메모리 B+ tree, clustered vs unclustered, index 선택)**

## 0. 복습 Q와 Outline *(p.2~4)*

### 슬라이드 Q *(p.2)*
- 아래 table과 FD가 주어졌을 때, BCNF decomposition algorithm으로 다른 schema를 제안해보라 (답 없음, 8강 마지막 문제와 동일)
  - `Students(Fname, Lname, Initials, Major, PredictedGPA, ActualGPA)`
  1. `FName, LName → Initials`
  2. `Major → PredictedGPA`

### Database Design Process 복습 *(p.3)*
Conceptual Model → Relational Model + Schema + Constraints → Conceptual Schema + Normalization → **Physical Schema + Indexing (오늘)**

### Outline *(p.4, 10, 18, 25, 30, 34, 48, 56, 70)*
- **From Relations to Files**: Hard Reality of Hard Disks / Representing Relations / Querying a Relation / … quickly
- **Using Indices**: Using an Index / Multi* Indices
- **Implementing Indices**: In memory: B+-Trees / On disk: Clustered vs Unclustered / Using Indices (again)

---

## 1. 디스크의 현실 (Hard Reality of Hard Disks) *(p.5~9)*

### 디스크의 기계적 특성 *(p.5)*
- 회전 속도 (~7200RPM)
- Platter 수 (1~30개)
- Track 수 (≤ 10000)
- Track당 byte 수 (105MB)
- 구성 요소(슬라이드 그림): Spindle, Platters, Tracks, Cylinder, Sector, Disk head, Arm assembly, Arm movement

### 디스크 접근 특성 *(p.6)*
- **Disk latency** = 요청한 시점부터 데이터가 main memory에 올라올 때까지의 시간. 아래 둘이 하한
  - **Seek time** = head가 track에 도달하는 시간: **10ms ~ 40ms**
  - **Rotational latency** = platter가 회전하는 시간: **5ms**
- Bandwidth는 보통 **40~80MB/s**
- **Disk latency는 main memory보다 훨씬 높다**

### 디스크 구성 *(p.7)*
- 디스크는 **page 또는 block**이라는 덩어리로 조직됨
- **디스크에서 가까이 있는(같은 block의) 데이터는 함께 접근**됨 → block 하나를 통째로 main memory에 한 번에 load

### Jeff Dean의 "Numbers Everyone Should Know" (LADIS '09) *(p.8)*
슬라이드 표 (손글씨로 2025 update 표시가 일부 덧붙어 있음):

| 항목 | 시간 |
|---|---|
| L1 cache reference | 0.5 ns |
| Branch mispredict | 5 ns |
| L2 cache reference | 7 ns |
| Mutex lock/unlock | 100 ns (손글씨: 25) |
| Main memory reference | 100 ns |
| Compress 1K bytes with Zippy | 10,000 ns (손글씨: 300) |
| Send 2K bytes over 1 Gbps network | 20,000 ns (손글씨: 1,600) |
| Read 1 MB sequentially from memory | 250,000 ns |
| Round trip within same datacenter | 500,000 ns |
| Disk seek | 10,000,000 ns |
| Read 1 MB sequentially from network | 10,000,000 ns |
| Read 1 MB sequentially from disk | 30,000,000 ns (손글씨로 앞자리를 고친 흔적이 있으나 판독 불확실) |
| Send packet CA→Netherlands→CA | 150,000,000 ns |

- 손글씨 메모: system call 약 500ns, context switch 10,000ns, **SSD random read (4~8KB) 약 100,000ns**
- 비유(슬라이드 왼쪽): **L1 cache reference = 모니터에 붙인 sticky note**, **L2 cache reference = 룸메이트를 소리쳐 부르기**, **Main memory reference = 교과서 넘겨보기** (디스크 seek는 화살표만 표시되고 비유 없음)

### Caching/Buffering *(p.9)*
- block 전체를 읽어서 main memory의 **cache**라는 영역에 저장
- 같은 block의 원소를 다시 접근할 때는 디스크로 가지 않고 main memory에서 읽음

---

## 2. Relation의 표현 (Representing Relations) *(p.11~17)*

### 많은 표현 방식 *(p.11)*
**Physical data independence** = 선택 가능한 저장 방식이 많다는 뜻
- **Row-store**: 한 row의 attribute들이 함께 저장됨. row는 정렬되어 있을 수도, 아닐 수도 있음. relation이 "충분히 크면" 여러 파일이 필요할 수 있음
- **Column-store**: 모든 fid가 든 파일 하나, 모든 date가 든 파일 하나, … 모든 price가 든 파일 하나

### Relation을 파일로 저장 *(p.12~15)*
- relation 전체를 **하나의 (관련된) 파일(들)**에 저장
- 예: `FLIGHT(fid, date, carrier, origin, dest, price)` — 파일은 `flight1 flight2 flight3 … flight37 …`처럼 record들이 이어진 형태
- 한 record 예시: `3224 | 2010/01/03 | DL | SEA | NYC | $1544` (fid, date, airline, origin, dest, price 순)

### Heap File vs Sequential File *(p.16)*
- **Heap File**: 파일이 **정렬되어 있지 않음** — 예: `flight12 flight88 flight37 … flight1 …`
- **Sequential File**: 파일이 **어떤 기준으로 정렬됨**, 보통 primary key — 예: `flight1 flight2 flight3 … flight37 …`

### 목표 *(p.17)*
- DBMS는 table 파일을 디스크의 **연속된 chunk**에 저장하려 한다 — **순차 읽기가 임의(random) 읽기보다 빠르기 때문**
- DBMS는 table 데이터를 메모리로 **불필요하게 복사하는 것을 최소화**하려 한다
  - 한 번에 block 하나 분량의 table을 load
  - memory block을 "완전히 활용"해서 디스크에서 다시 fetch하지 않도록

---

## 3. Relation 질의하기 (Querying a Relation) *(p.19~24)*

### Full table scan *(p.19~23)*
```sql
SELECT *
FROM Flights
WHERE date = '2010/01/03';
```
- 슬라이드의 질문: "이 쿼리를 어떻게 실행할 수 있을까?" → "음, **파일의 모든 record를 읽어야** 한다…" → "그건 좀 느리다…"
- 파일(`flight1 flight2 flight3 … flight37 …`)을 처음부터 끝까지 훑는 그림이 애니메이션으로 진행됨

### 슬라이드 Q *(p.24)*
- 이 **full table scan**이 매칭되는 row를 찾는 데 느린 이유는? (**"big-O linear search"라고만 답하는 것은 불충분**하다고 명시, 답 없음)

---

## 4. Index 사용하기 *(p.26~47)*

### Index란 *(p.26~27)*
- **Index**: attribute(들)을 기준으로 row에 **직접 접근**할 수 있게 해주는 **별도의 파일**
  - **원래 relation의 표현을 바꾸지 않는다!**
- index 파일의 조직 방식: **B+ tree (가장 흔함, B-tree의 약간 변형)**, Hash table, Bit-map, R-tree, 기타(DBMS에 따라 다름)

### Index 생성 *(p.28~29)*
```sql
CREATE INDEX myIndex ON Flights(date)
```
- 슬라이드 그림: Data file(`flight1, flight2, … flight999, flight1000, …`) 옆에 date 값(`2000/01/01`, `2000/01/02`, `2000/01/03`, …, `2010/01/03`, …)으로 정렬된 Index file이 생기고, 각 항목이 data file의 record를 가리킴

### Discussion *(p.31)*
- table에 index를 **0개 이상** 만들 수 있다
  - `Flights(fid)` 위의 index — fid가 PK이므로 DBMS가 아마 자동으로 만든다
  - `Flights(date)`, `Flights(origin)`, …
- `CREATE INDEX`는 **한 번만** 실행 — 만들고 저장하는 데 시간이 걸릴 수 있음
- 이후 SQL 쿼리는 **더 빨라질 수도, 느려질 수도, 같을 수도** 있다

### Index Impacts *(p.32)*
```sql
-- FLIGHT(fid, date, carrier, origin, dest, price)
CREATE INDEX keyindex ON Flights(fid);   -- probs done by DBMS
CREATE INDEX myIndex1 ON Flights(date);
CREATE INDEX myIndex2 ON Flights(origin);
```
- 질문: 이 index들이 우리 homework의 성능을 어떻게 바꿀까?

### 슬라이드 Q *(p.33)*
위 세 index를 만들었을 때 다음 쿼리가 **더 빠를지, 느릴지, 같을지** (답 없음):
```sql
SELECT * FROM Flights WHERE fid = 1234;
SELECT * FROM Flights WHERE date < '2000/01/01';
SELECT * FROM Flights WHERE dest = 'NYC';
INSERT INTO Flights
VALUES (3243, '2022/04/20','DL','SEA','NYC',159);
```

### Multiple Indices *(p.35~37)*
```sql
CREATE INDEX keyindex ON Flights(fid);   -- probs done by DBMS
CREATE INDEX myIndex1 ON Flights(date);
CREATE INDEX myIndex2 ON Flights(origin)

SELECT *
FROM Flights
WHERE date = '2010/01/03'
  AND origin = 'SEA';
```
- **두 index를 동시에 쓸 수 없다!** 시스템은 `Flights(date)`와 `Flights(origin)` 중 **하나를 선택**해야 함
- **Option 1**: `Flights(date)` index 사용 — `2010/01/03`의 모든 flight를 효율적으로 가져온 뒤, 각각이 `origin = 'SEA'`인지 검사
- **Option 2**: `Flights(origin)` index 사용 — `'SEA'`에서 출발하는 모든 flight를 효율적으로 가져온 뒤, 각각이 `date = '2010/01/03'`인지 검사

### Multi-Attribute Indices *(p.38~40)*
```sql
CREATE INDEX keyindex ON Flights(fid);   -- probs done by DBMS
CREATE INDEX myIndex1 ON Flights(date);
CREATE INDEX myIndex2 ON Flights(origin);
CREATE INDEX myIndex12 ON Flights(date, origin);

SELECT *
FROM Flights
WHERE date = '2010/01/03'
  AND origin = 'SEA';
```
- 이제는 **고를 필요 없다!** 시스템이 `Flights(date, origin)` index를 쓰고, 이게 **아마 모든 선택지 중 가장 효율적**
- **Multi-attribute index는 attribute들을 이어 붙인(concatenation) 값에 대한 index일 뿐이다** *(p.39)*
```sql
CREATE INDEX myIndex3 ON Flights(date, origin, dest);
```
  - date + origin + dest를 이어 붙여서 index 자료구조에 insert
- 슬라이드 그림 *(p.40)*: index file이 `date` 값별로 나뉘고, 각 date 아래에서 `origin`("SEA", "NY", …)별로, 그 아래에서 `dest`("SF", "NY", "SEA", …)별로 정렬된 구조 (예: 2000/01/01 → "SEA" → "SF", "NY" / "NY" → "SF", "SEA" …)

### 속성 순서가 중요한가? *(p.41~45)*
- 슬라이드 Q: 속성 선언 순서가 중요한가? 즉, 아래가 중복(redundant)인가?
```sql
CREATE INDEX myIndex21 ON Flights(origin, date);
```
- 이제 **`(date, origin)` index만 있다고 가정**하고:
```sql
SELECT *
FROM Flights
WHERE date = '2010/01/03';
```
  - **그래도 index를 쓸 수 있다** *(p.43)*. 단 origin이 지정되지 않았으므로 **range query처럼** 쓰이고 equality predicate보다 효율이 떨어짐
```sql
SELECT *
FROM Flights
WHERE origin = 'SEA';
```
  - **Index가 쓸모없다** *(p.45)*

### 규칙 정리 *(p.46~47)*
```sql
CREATE INDEX myIndex3 ON Flights(date, origin, dest);
```
- **attribute들의 앞부분(prefix)에 대한 equality predicate**일 때 유용:
  - `date='…' AND origin='…' AND dest='…'`
  - `date='…' AND origin='…'` ← 이 둘은 index에 대한 **range query**
  - `date='…'` ←
- **하지만 아래는 불가** — date prefix가 없으므로 **index가 전부 쓸모없다**:
  - `origin='…' AND dest='…'`
  - `origin='…'`
  - `dest='…'`

---

## 5. Index 구현: 메모리 구조와 B+ Tree *(p.49~55)*

### 메모리 안의 구조 *(p.49)*
- index 파일보다 더 빠른 것? → **메모리에 있는 index!** (그림: index file이 data file 옆이 아니라 in-memory 구조로 올라감)

### In-memory Index Structures *(p.50)*
B+ Tree Index (**Clustered / Unclustered**), Hash Index, R Tree, Radix Tree, Bloom Filter, Hilbert Curves, Learned Index, LSMT, …

### In-memory Indices: B+ Trees *(p.51~52)*
- 이 수업에서의 B+ tree:
  - **n-ary search tree**
  - 구성(configuration)은 **디스크 parameter**에 기반
  - **index된 attribute는 모두 search tree 안에(따라서 메모리에!)** 있다
  - **그 외 attribute는 모두 디스크에** 있다
- 슬라이드 그림: 루트 `50, 40, 30, 20` 아래로 `80, 20, 18, 15, 10` 같은 키 값이 내려가고, leaf가 data file(`flight1 … flight1001`)의 record를 가리킴

### 슬라이드 Q *(p.53)*
- 두 후보 index 중 아래 쿼리가 더 빠른 쪽은? (**두 index 모두 메모리에 들어간다고 가정**, 답은 다음 슬라이드)
```sql
CREATE INDEX idx12 ON Flights(date, origin);
CREATE INDEX idx1 ON Flights(date);

SELECT date, COUNT(DISTINCT origin)
FROM Flights
WHERE date LIKE '2010/01/%'
GROUP BY date;
```

### Memory-only Queries *(p.54)*
- 슬라이드 문구는 "`idx1`이 메모리에 완전히 들어가면 디스크에 전혀 갈 필요가 없다"이지만, 같은 슬라이드에서 `CREATE INDEX idx1 ON Flights(date)`는 **회색으로 흐리게(제외 표시)** 되어 있고 `idx12 ON Flights(date, origin)`만 선명하게 남아 있다 — 쿼리가 `date`와 `origin`을 모두 쓰므로 **`idx12`가 답**이고 슬라이드의 `idx1`은 오타로 보인다
- **쿼리에 필요한 attribute(date, origin)가 모두 이미 메모리(index 안)에 있다** → data file을 읽을 필요가 없어 디스크 접근이 없음 *(슬라이드: "All the attributes we need for this query are already in memory")*

### 슬라이드 Q: 어떤 index를 만들 것인가 *(p.55)*
아래 query load에서 (있다면) 어떤 index를 만들겠는가? (답 없음)
```sql
-- 시간당 1회
SELECT *
FROM Flights
WHERE date = ?;

-- 분당 1회
SELECT origin
FROM Flights
WHERE date = ?;

-- 초당 여러 번
SELECT *
FROM Flights f1, Flights f2
WHERE f1.date = ?
  AND f2.date = ?
  AND f1.dest = f2.origin
```

---

## 6. Clustered vs Unclustered Index *(p.57~69)*

### Scans vs Selections *(p.57)*
- **Selection**은 비교적 **적은 수의 tuple**이 만족 — 예: attribute = 40인 tuple. 성능 목표는 보통 **sequential scan(full table scan)을 이기는 것**
- **Range scan**은 **많은 tuple**이 만족 — 예: attribute가 (40-85]인 tuple. index를 쓸 때의 목표는 **불필요한 disk I/O 최소화**
  - 전형적인 tree 기반 구현: **조건을 만족하는 첫 tuple을 찾고, 그다음 tuple들을 메모리로 load**

### Clustered Index *(p.58~61)*
- main data file(tuple 자체를 저장)은 정렬되어 있을 수도, 아닐 수도 있음
- data가 정렬된 attribute(들)에 index를 만들 수 있음 → **clustered index**
```sql
CREATE CLUSTERED INDEX DateIndex ON Flights(date)
```
  - RDBMS가 Flights를 date attribute로 sort함
- **Clustered index**: tuple이 디스크에서 **index의 key 순서와 같은 순서**로 정렬되어 있는 index *(p.59)*
  - **table당 보통 clustered index는 하나만** 둔다
  - 슬라이드 그림: Sequential Data File(`flight1 … flight1001`)과 date key(`2000/01/01 … 2009/12/31, 2010/01/01, 2010/01/02, 2010/01/03 … 2010/12/31, 2011/01/01 …`)의 순서가 같음
- **Selection** *(p.60)*: 조건에 맞는 index key를 찾아서 해당 tuple을 가져옴 — 예: key 55에 대응하는 tuple 찾기
- **Range scan** *(p.61)*: 조건에 맞는 index key를 찾은 뒤 **이어지는 tuple들을 메모리로 load** — 예: date "2010/xx/xx"인 tuple들. **디스크에서 tuple을 load할 때 block을 재사용할 수 있다**

### Unclustered Index *(p.62~65)*
- **Unclustered index**: 데이터를 정렬된 순서로 저장하지 않음 — 구현이 tuple을 복사하는 대신 **포인터를 저장**해서 "재사용"할 수 있음
```sql
CREATE UNCLUSTERED INDEX DateIndex ON Flights(date)
```
- 바탕 data file은 **Heap Data File** *(p.63)*. unclustered index의 순서는 디스크상의 순서와 다름
  - **table당 unclustered index는 몇 개든** 만들 수 있다
- **Selection** *(p.64)*: clustered와 같이 key를 찾아 해당 tuple 가져옴 (예: key 55)
- **Range scan** *(p.65)*: key를 찾은 뒤 이어지는 tuple을 메모리로 load — 예: date "2010/xx/xx". 단 **cache가 너무 차면 block을 다시 load해야 할 수 있다…**

### Sequential Table Scan *(p.66)*
- 한 disk block이 **5개 tuple**을 담는다고 가정
- key 범위 `[2010/01/01, 2010/01/03)`의 tuple들을 찾으려면 **table 전체를 scan해야 할 수도** 있다 (key는 tuple의 field 중 하나)
  - 슬라이드 그림: `t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 t11 t12 t13 ...` (5개씩 한 block)
- **clustered index가 있으면 그에 대한 range scan이 full table scan보다 엄격히 낫다** … 하지만 …

### Unclustered Index Range Scan *(p.67)*
- **unclustered index scan보다 sequential scan이 나은 경우는?**
  - key 범위 `(2010/01/01, 2010/01/03]`의 tuple을 찾을 때, **같은 data file block을 여러 번 load/unload하는 것보다 table 전체를 한 번 scan하는 편이 더 빠를 수 있다**
- 슬라이드 Q: **sequential scan이 clustered index scan보다 나을 때는?** (답 없음)

### Discussion *(p.68~69)*
- index가 clustered이면 **range query는 항상** 전체 table scan보다 효율적
  - 하지만 **clustered index는 하나만** 만들 수 있다!
- 기본적으로 clustered index는 **primary key**에 건다
- 이를 override할 수 있는데, 그럴 땐 보통 **multi-attribute clustered index**를 선택:
```sql
CREATE CLUSTERED INDEX cover ON Flights(date,dest,origin,price)
```
  - index 파일이 (date, dest, origin, price) 순으로 정렬됨

---

## 7. Index Selection Problem *(p.71~78)*

### 문제 정의 *(p.71)*
- 애플리케이션마다 SQL query와 update의 조합이 다르다. 개발자로서 **어떤 index를 만들어야 하나?**
  - 일부 SELECT-FROM-WHERE 쿼리는 빨라짐
  - **모든 INSERT/DELETE/UPDATE는 느려짐**
- 런타임에 **RDBMS는 어떤 index를 골라야 하나?** 알기 어렵다! 일부 시스템은 index를 자동 선택하는 **auto tuner**가 있다

### RDBMS 돕기 *(p.72)*
- application workload는 **미리 알려져 있는 경우가 많다**
  - Flights 애플리케이션: 검색 방식이 origin city와 …?
  - 데이터 시각화 소프트웨어(예: Tableau): 2D plot — 그래프 축 범위에 대한 query
- 개발자와 RDBMS 관리자가 **예상 query workload에 맞는 index를 함께 만든다**

### 예제: Users 테이블 *(p.73~76)*
슬라이드 Q: `Users`에 어떤 index를 만들 수 있는가?
```sql
CREATE TABLE Users (
    id INT PRIMARY KEY,
    age INT,
    score INT);
```
```sql
-- Expecting 1000 exec/day
SELECT *
FROM Users, Assets
WHERE Users.id = Assets.uid

-- Expecting 1000 exec/day
SELECT *
FROM Users
WHERE Users.score > 95

-- Expecting 10 exec/day
SELECT *
FROM Users
WHERE Users.age > 21
```
슬라이드의 답:
- `Users.id = Assets.uid` *(p.74)*: **ID는 unique하고 아마 selection**이므로 **unclustered index**면 충분
- `Users.score > 95` *(p.75)*: 이 range query는 **score에 대한 clustered index**의 혜택을 받는다
- `Users.age > 21` *(p.75)*: 이 range query는 **age에 대한 clustered index**의 혜택을 받는다 — 하지만 **clustered index는 하나만** 존재할 수 있다!
- 결론 *(p.76)*: **고려할 것이 많다!** 추가 정보가 없다면 좋은 기본값은 **더 자주 쓰일 index에 clustering을 적용**하는 것 (여기서는 1000 exec/day인 score)

### Understanding Your Indices *(p.77~78)*
- 내부 구현을 모르면 특정 predicate에서 index가 어떻게 동작할지 알 수 없다. 일반적으로 **equality predicate(=)가 더 빠르다**고 가정할 수 있음
- 실무에서는 **실제 index 자료구조를 알아야** 한다
- 예 *(p.78)*:
  - **Hash table은 range predicate(<, >)를 구현할 수 없다**
  - **B+ tree는 range predicate를 구현할 수 있다.** 하지만!!! "hardware layer cake" 때문에 **많은 tuple을 순차적으로 읽는 것이 임의 순서로 읽는 것보다 훨씬 효율적**이고, **unclustered B+ tree index에 대한 range query는 본질적으로 임의 순서**다
  - … 그럼 "많다"는 것은 **몇 개의 record**부터인가? (슬라이드는 질문으로 끝남)

---

## 수업에서 다룬 섹션

1. 디스크의 현실 (Hard Reality of Hard Disks)
2. Relation의 표현 (Row-store/Column-store, Heap vs Sequential File)
3. Relation 질의하기 (Full table scan)
4. Index 사용하기 (생성, Multiple Indices, Multi-Attribute Indices, 속성 순서와 prefix 규칙)
5. Index 구현: 메모리 구조와 B+ Tree (index-only 쿼리 포함)
6. Clustered vs Unclustered Index
7. Index Selection Problem
