# Lecture 9: Physical Design and Indices — 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

정리 노트: `notes/lecture-09-design-physical.md` (슬라이드 p.2~78, 쪽번호는 PDF 페이지 순서 기준)
오늘 목표: 쿼리와 workload를 보고 **어떤 index를 어떤 속성 순서로, clustered로 할지 unclustered로 할지** 근거를 들어 고를 수 있다.

## 0. 선수 개념 점검

1. **디스크 vs 메모리**: 디스크는 head를 움직이는 기계적 동작이 있어 느리다.
2. **Index**: 찾고자 하는 내용을 빠르게 찾게 해주는 구조 (책의 찾아보기와 비슷). 이진탐색처럼 log n 시간.
3. **Equality vs Range**: equality는 값 **하나**를 찾는 것, range는 값의 **구간**을 찾는 것. 오늘 내내 중요한 차이.
4. **Primary key**: 테이블의 행을 식별하는 유일한 값. DBMS는 PK에 보통 index를 자동으로 만든다.
5. 참고: 실제 DB의 index는 BST보다 **B+ tree**를 주로 쓴다 (5번 섹션).

## 1. 디스크의 현실 *(p.5~9)*

**Disk latency**: 데이터를 요청한 시점부터 그 데이터가 main memory에 올라올 때까지 걸리는 시간.

### 디스크가 느린 이유 *(p.5~6)*
디스크는 회전하는 원판(platter)에 head가 붙은 arm이 움직이며 읽는 기계 장치다. latency는 두 부분으로 나뉜다.

| 구성 | 뜻 | 대략 시간 |
|---|---|---|
| **Seek time** | arm이 움직여 head가 원하는 track에 도달하는 시간 | 10~40ms |
| **Rotational latency** | 원하는 sector가 head 밑으로 돌아오기를 기다리는 시간 | 약 5ms |

- 이 둘이 latency의 하한이다. 데이터가 어디에 있든 최소한 이만큼은 걸린다.
- head가 자리를 잡고 나면 연속된 데이터를 읽는 속도(bandwidth)는 40~80MB/s로 꽤 빠르다.
- 그래서 **처음 찾아가는 비용은 비싸고, 찾아간 뒤 쭉 읽는 건 싸다.** 오늘 내용 대부분이 이 성질에서 나온다.

### 규모 감각 *(p.8, Jeff Dean 표)*
- Main memory reference: 100ns, Disk seek: 10,000,000ns(10ms). seek 한 번이 메모리 참조의 약 **10만 배**.
- 그래서 DB 성능 최적화는 사실상 **디스크 접근 횟수를 줄이는 싸움**이다.
- 손글씨 메모: SSD random read(4~8KB)는 약 100,000ns. HDD보다 훨씬 빠르지만 메모리보단 여전히 1000배 느리다.
- 슬라이드의 비유: L1 cache = 모니터에 붙인 sticky note, L2 cache = 룸메이트를 소리쳐 부르기, main memory = 교과서 넘겨보기. 단계마다 한 칸 멀어질 때 한 자릿수 이상 느려지고, 디스크 seek는 비유 범위를 넘어선다.

### Page/Block *(p.7)*
- 디스크는 byte 단위가 아니라 **page(또는 block)** 덩어리 단위로 조직된다.
- 한 block 안의 데이터는 통째로 한 번에 main memory로 올라온다. record 하나만 필요해도 그 block 전체를 읽는다.
- **왜 합리적인가**: 비싼 건 찾아가는 비용(seek + rotation)이고 읽는 비용은 싸다. block 단위로 크게 읽어 비싼 비용을 여러 record가 나눠 부담하게 하는 것. 가까이 있는 데이터는 곧 같이 필요해질 가능성이 높다.

### Caching/Buffering *(p.9)*
- 읽어온 block은 main memory의 **cache**에 저장한다.
- 같은 block의 다른 원소를 다시 접근하면 디스크에 안 가고 메모리에서 읽는다.
- **목표**: 디스크 접근, 특히 random 접근을 최소화.

## 2. Relation의 표현 *(p.11~17)*

**Physical data independence**: 논리적인 relation(table)은 그대로인데, 그걸 디스크에 어떻게 저장할지는 여러 방식 중에서 고를 수 있다는 성질.

### Row-store vs Column-store *(p.11)*
`FLIGHT(fid, date, carrier, origin, dest, price)` 예:

| 방식 | 저장 단위 | 모양 |
|---|---|---|
| **Row-store** | 한 row의 attribute들을 함께 저장 | `[3224, 2010/01/03, DL, SEA, NYC, $1544]` 그 다음 row |
| **Column-store** | attribute별로 따로 저장 | fid만 모은 파일, date만 모은 파일, … price만 모은 파일 |

- row-store에서 row는 정렬돼 있을 수도, 아닐 수도 있다. relation이 충분히 크면 파일이 여러 개 필요할 수도 있다.
- 이 수업은 주로 row-store를 전제로 한다.

### Heap File vs Sequential File *(p.12~16)*

| 종류 | 정의 | 예 |
|---|---|---|
| **Heap File** | record가 정렬되지 않은 채 저장된 파일 | `flight12 flight88 flight37 … flight1` |
| **Sequential File** | record가 어떤 기준(보통 primary key)으로 정렬돼 저장된 파일 | `flight1 flight2 flight3 … flight37` |

- `fid = 3224` 하나를 찾을 때: heap은 나올 때까지 계속 꺼내 봐야 하고, sequential은 이진탐색이 가능하다.
- 다만 sequential이어도 이진탐색은 block을 건너뛰며 읽으니 random 접근이 log(block 수)번 생긴다. 그래도 heap의 전체 훑기보다는 훨씬 낫다.

### DBMS의 목표 *(p.17)*
1. table 파일을 디스크의 **연속된 chunk**에 저장하려 한다. 한 번의 head 접근으로 필요한 데이터를 연속으로 가져올 수 있고, 순차 읽기가 random 읽기보다 빠르기 때문.
2. table 데이터를 메모리로 불필요하게 복사하는 걸 최소화한다. 한 번에 block 하나 분량을 load하고 그 block을 완전히 활용해 같은 block을 다시 fetch하지 않게 한다.

## 3. Relation 질의하기 *(p.19~24)*

**Full table scan**: 조건에 맞는 row를 찾으려고 파일의 모든 record를 처음부터 끝까지 읽는 방식.

```sql
SELECT *
FROM Flights
WHERE date = '2010/01/03';
```
- Flights가 `date` 기준으로 정렬돼 있지 않으면 이진탐색도 못 하고 파일 전체를 읽어야 한다. 슬라이드도 "그건 좀 느리다…"로 끝난다.

### 슬라이드 Q (p.24): full table scan이 느린 진짜 이유
- 파일이 디스크에 연속으로 놓여 있으면 head 이동은 처음 한 번 정도이고 이후는 순차 읽기다. 그래서 "seek이 계속 늘어나서"는 정확한 이유가 아니다.
- 진짜 이유: 조건에 맞는 row가 몇 개 안 돼도 **모든 block을 디스크에서 메모리로 읽어와야** 한다. table이 클수록 읽는 block 수에 비례해 시간이 늘고, 메모리보다 클 수도 있다.
- 즉 문제는 CPU 비교 횟수가 아니라 **불필요한 디스크 I/O의 양**이다. "big-O linear search"라고만 답하면 부족하다.

## 4. Index 사용하기 *(p.26~47)*

### 정의와 생성 *(p.26~29)*
**Index**: 특정 attribute(들)의 값으로 row에 **직접 접근**할 수 있게 해주는 **별도의 파일**. 원래 relation의 저장 방식은 바꾸지 않는다.

```sql
CREATE INDEX myIndex ON Flights(date)
```
- data file은 그대로 두고, 옆에 `date` 값으로 정렬된 index file을 만든다. 각 항목은 data file의 해당 record를 가리킨다.
- 조직 방식: **B+ tree**(가장 흔함), Hash table, Bit-map, R-tree 등.

### 알아둘 점 *(p.31)*
- table에 index는 **0개 이상** 만들 수 있다. PK(`fid`)에는 DBMS가 보통 자동으로 만든다.
- `CREATE INDEX`는 한 번만 실행하고, 만들고 저장하는 데 시간이 걸린다.
- 이후 SQL 쿼리는 빨라질 수도, 느려질 수도, 그대로일 수도 있다.

### Index Impacts *(p.32~33)*
```sql
CREATE INDEX keyindex ON Flights(fid);
CREATE INDEX myIndex1 ON Flights(date);
CREATE INDEX myIndex2 ON Flights(origin);
```

| 쿼리 | 결과 | 이유 |
|---|---|---|
| `WHERE fid = 1234` | 빨라짐 | `fid` index 사용 |
| `WHERE date < '2000/01/01'` | 빨라짐 | range라도 `date` index로 구간 시작점을 바로 찾음. 매칭 row가 table의 큰 비율이면 이득이 줄어듦(6번 섹션) |
| `WHERE dest = 'NYC'` | 같음 | `dest`에 index가 없어 full scan |
| `INSERT INTO Flights VALUES (...)` | **느려짐** | index는 data file과 별개의 파일이라 row 하나를 넣으면 index 3개에도 새 항목을 각각 넣어야 함 |

- DELETE, UPDATE도 마찬가지. 그래서 index는 공짜가 아니고 **읽기는 빨라지는 대신 쓰기는 느려지는 trade-off**다. 7번 섹션의 핵심.

### Multiple Indices *(p.35~37)*
```sql
SELECT *
FROM Flights
WHERE date = '2010/01/03'
  AND origin = 'SEA';
```
- 시스템은 **두 index를 동시에 쓸 수 없다.** `Flights(date)`와 `Flights(origin)` 중 하나를 골라야 한다.
  - Option 1: `date` index로 `2010/01/03`의 flight를 가져온 다음, 각각 `origin = 'SEA'`인지 검사
  - Option 2: `origin` index로 `'SEA'` 출발 flight를 가져온 다음, 각각 `date = '2010/01/03'`인지 검사
- 한쪽 조건은 index로 거르고 나머지는 가져온 row를 하나씩 확인한다.

### Multi-Attribute Index *(p.38~40)*
**Multi-attribute index**: 여러 attribute의 값을 **이어 붙인(concatenation) 값**을 key로 삼는 index.

```sql
CREATE INDEX myIndex12 ON Flights(date, origin);
```
- 위 쿼리는 이 index 하나로 해결된다. 고를 필요 없이 `(date, origin)` index를 쓰고, 보통 가장 효율적이다.
- 두 index를 따로 만들어 합치는 게 아니라, 처음부터 두 속성을 이어 붙인 값으로 index 하나를 만드는 것.
- 세 속성이면 `Flights(date, origin, dest)`처럼 date + origin + dest를 이어 붙여 넣는다.

구조는 **사전 순 정렬**과 같다 *(p.40)*:
```
2000/01/01
   "SEA"
      "SF", "NY"
   "NY"
      "SF", "SEA"
2000/01/02
   ...
```
먼저 `date`로 정렬, 같은 date 안에서 `origin`으로, 같은 origin 안에서 `dest`로 정렬.

### 속성 순서가 중요한 이유 *(p.41~47)*
index가 `(date, origin)` 하나뿐일 때:

- `WHERE date = '2010/01/03'` → **사용 가능.** 단 `origin`이 안 정해졌으니 date 구간 전체를 읽는 range처럼 동작해서 equality 둘 다일 때보다 효율이 떨어진다 *(p.43)*.
- `WHERE origin = 'SEA'` → **쓸모없음** *(p.45)*.

**전화번호부 비유**: "성 → 이름" 순 전화번호부에서 "김씨 전부"는 김 구간만 펼치면 되지만, "이름이 영희인 사람 전부"는 모든 성 구간을 뒤져야 한다. `(date, origin)`에서 `origin = 'SEA'` 항목은 각 date 구간마다 흩어져 있어 구간 하나로 모이지 않는다.

**규칙**: index는 **앞쪽부터 이어지는 속성(prefix)에 equality 조건**이 있을 때 쓸모 있다.

```sql
CREATE INDEX myIndex3 ON Flights(date, origin, dest);
```

| 쿼리 조건 | index 사용 |
|---|---|
| `date AND origin AND dest` | 가능 (가장 효율적) |
| `date AND origin` | 가능 (index에 대한 range) |
| `date` | 가능 (index에 대한 range) |
| `origin AND dest` | 불가 (date prefix가 없음) |
| `origin` | 불가 |
| `dest` | 불가 |

- 그래서 `(origin, date)` index는 `(date, origin)`과 **중복이 아니다.** 앞에 오는 속성이 달라서 도울 수 있는 쿼리가 다르다.
- 예시 확인: index가 `(date, origin, dest)` 하나일 때
  - `date AND dest` → 쓸 수 있지만 **date 부분만** 효과. 중간의 `origin`이 비어 있어 `dest`는 index로 못 좁히고 date 구간을 가져온 뒤 하나씩 확인한다. prefix가 끊기지 않고 이어진 데까지만 index가 일한다.
  - `origin AND dest` → 쓸모없음
  - `date AND origin` → 쓸 수 있음

## 5. Index 구현: 메모리 구조와 B+ Tree *(p.49~55)*

### 메모리 안의 index *(p.49~50)*
- index 파일을 디스크에서 읽는 것보다 더 빠른 방법은 **index를 메모리에 두는 것**.
- 메모리 안의 index 구조: B+ Tree(Clustered/Unclustered), Hash Index, R Tree, Radix Tree, Bloom Filter, LSMT 등. 이 수업은 B+ tree를 다룬다.

### B+ Tree *(p.51~52)*
**B+ tree**: 디스크 parameter(block 크기 등)에 맞춰 구성한 n-ary search tree로, index된 attribute 값은 트리에 두고 실제 record는 data file을 가리키는 index 구조.

- **index된 attribute는 모두 트리 안(= 메모리)**에 있다.
- **그 외 attribute는 모두 디스크**의 data file에 있다.
- leaf가 data file의 record를 가리킨다.
- 이진 트리가 아니라 노드 하나가 여러 갈래(n-ary)를 가져서 트리 높이가 낮다.

### Index-only 쿼리 *(p.53~54)*
```sql
CREATE INDEX idx12 ON Flights(date, origin);   -- (A)
CREATE INDEX idx1  ON Flights(date);           -- (B)

SELECT date, COUNT(DISTINCT origin)
FROM Flights
WHERE date LIKE '2010/01/%'
GROUP BY date;
```
두 index 모두 메모리에 들어간다고 가정. 정답은 **(A) `idx12`**.

- 쿼리가 필요로 하는 값은 `date`와 `origin`.
- (A): 메모리 index에서 `2010/01/%` 구간을 찾고, 그 항목에 `date`와 `origin`이 둘 다 있다. 날짜별 origin 종류 수를 세면 끝. data file을 안 읽으므로 **디스크 접근 0번**.
- (B): index에 `origin`이 없다. 매칭된 row마다 디스크의 data file로 가서 `origin`을 읽어야 한다. 한 달치 flight면 디스크 접근이 매우 많다.
- **핵심**: 쿼리가 필요로 하는 값이 index 안에 다 있으면 디스크에 안 가도 된다. 이런 경우를 index-only 쿼리라고 부른다(수업 중 붙인 용어, 슬라이드 용어는 아님).
- 확인: index가 `(date)` 하나뿐이어도 쿼리가 `SELECT date ... WHERE date LIKE '2010/01/%'`처럼 `date`만 필요하면 디스크에 안 가도 된다.
- **슬라이드 오타 의심**: p.54 정답 칸에 "idx1이 메모리에 들어가면 디스크에 갈 필요가 없다"고 적혀 있고 `idx1` 줄이 회색으로 흐려져 있다. 위 논리상 `idx12`를 `idx1`로 잘못 쓴 것으로 보인다(슬라이드가 그렇게 말한 건 아니고 해석). 정답은 `idx12`로 기억.

## 6. Clustered vs Unclustered Index *(p.57~69)*

### Selection vs Range scan *(p.57)*

| 종류 | 만족하는 tuple 수 | 예 | 성능 목표 |
|---|---|---|---|
| **Selection** | 적음 | attribute = 40 | sequential scan(full scan)을 이기기 |
| **Range scan** | 많음 | attribute가 (40-85] | 불필요한 disk I/O 최소화 |

range scan의 전형적인 트리 구현: 조건을 만족하는 첫 tuple을 찾고, 그 뒤 tuple들을 쭉 메모리로 load.

### Clustered Index *(p.58~61)*
**Clustered index**: data file의 tuple들이 디스크에서 **index key와 같은 순서로 정렬돼 있는** index.

```sql
CREATE CLUSTERED INDEX DateIndex ON Flights(date)
```
- RDBMS가 Flights 자체를 `date` 순으로 정렬해 저장한다.
- data file 자체가 index key 순서로 정렬돼야 하는데 파일은 한 번에 **한 가지 기준으로만** 정렬할 수 있으므로, **table당 보통 하나만** 둘 수 있다.
- Selection: key를 찾아 tuple을 가져온다.
- Range scan: 첫 key를 찾은 뒤 이어지는 tuple들이 디스크에서도 이어져 있어 순차로 쭉 읽으면 된다. 같은 block을 재사용할 수 있다.

### Unclustered Index *(p.62~65)*
**Unclustered index**: data file이 index 순서로 정렬돼 있지 않아서, index 항목이 tuple을 복사하지 않고 **포인터로 가리키는** index.

```sql
CREATE UNCLUSTERED INDEX DateIndex ON Flights(date)
```
- 바탕 data file은 Heap File이고 index 순서는 디스크 순서와 다르다.
- **table당 몇 개든** 만들 수 있다.
- Selection은 clustered와 비슷하다.
- Range scan은 key를 찾은 뒤 포인터를 따라가는데 tuple들이 디스크에 흩어져 있다. cache가 가득 차면 같은 block을 다시 load해야 할 수도 있다.

### 그림으로 감 잡기
한 block에 tuple 5개, 범위에 해당하는 tuple이 key 순서로 10개라면
- Clustered: 10개가 연속이라 block 2개만 읽으면 된다.
- Unclustered: 10개가 흩어져 있으면 최악엔 block 10번. 같은 block을 여러 번 불러올 수도 있다.

### 언제 index가 오히려 손해일까 *(p.66~69)*
**Sequential scan**: table 전체를 block 순서대로 한 번 읽는 것. 한 block에 tuple이 5개 들어간다고 가정(`t1~t5`가 block 1, `t6~t10`이 block 2, …).

- clustered index가 있으면 그에 대한 range scan은 full scan보다 **엄격히 낫거나 같다.** 필요한 구간만 읽으니까.
- **unclustered index**는 다르다. 범위에 해당하는 tuple이 table 곳곳에 흩어져 있으면 포인터를 하나씩 따라가며 같은 block을 여러 번 load/unload하게 된다. 그러느니 table 전체를 한 번 쭉 순차로 읽는 게 더 빠를 수 있다.
- 매칭되는 tuple이 **많으면(range가 넓으면)** unclustered index는 full scan보다 느려질 수 있다. 슬라이드 마지막 질문("몇 개 record부터 많은 거냐")이 이 얘기이고 정확한 기준은 슬라이드도 답을 주지 않았다.
- 확인: `date` 위 unclustered index가 있을 때
  - `WHERE date = '2010/01/03'` (하루치, 10년 데이터 중 극소수): index가 이득.
  - `WHERE date > '2001/01/01'` (전체의 90%): 거의 모든 block을 어차피 읽어야 하고 tuple마다 random 접근이 생기므로, block 수만큼 한 번씩 순차로 읽는 full scan이 I/O가 더 적을 수 있다.

### 정리 *(p.68~69)*
- clustered index가 있으면 range 쿼리는 항상 full scan보다 낫지만, **clustered는 하나뿐**이다.
- 기본적으로 clustered index는 **primary key**에 걸린다.
- 이를 바꿀 땐 보통 **multi-attribute clustered index**를 고른다:
```sql
CREATE CLUSTERED INDEX cover ON Flights(date, dest, origin, price)
```
  - 파일이 (date, dest, origin, price) 순으로 정렬된다.
  - 쿼리가 필요로 하는 attribute를 index에 다 넣어 두면 디스크에 안 가도 되는 경우도 만들 수 있다.

## 7. Index Selection Problem *(p.71~78)*

### 문제 *(p.71~72)*
**Index selection problem**: 예상되는 query와 update의 조합이 주어졌을 때 어떤 index를 만들지 고르는 문제.

- index를 만들면 일부 SELECT는 빨라지지만 **모든 INSERT/DELETE/UPDATE는 느려진다.**
- 런타임에 RDBMS가 알아서 고르기는 어렵다. 일부 시스템에는 index를 자동 선택하는 **auto tuner**가 있다.
- workload가 미리 알려져 있는 경우가 많으므로(예: Tableau 같은 데이터 시각화의 축 범위 쿼리) 개발자와 DBA가 예상 workload에 맞춰 직접 고른다.

### 예제 *(p.73~76)*
```sql
CREATE TABLE Users (id INT PRIMARY KEY, age INT, score INT);
```

| 쿼리 | 빈도 |
|---|---|
| `SELECT * FROM Users, Assets WHERE Users.id = Assets.uid` | 1000회/일 |
| `SELECT * FROM Users WHERE Users.score > 95` | 1000회/일 |
| `SELECT * FROM Users WHERE Users.age > 21` | 10회/일 |

슬라이드의 답:
- `id = uid`: id는 unique라서 한 row씩 찾는 selection. **unclustered index**면 충분.
- `score > 95`: range라서 **score의 clustered index**가 도움이 된다.
- `age > 21`: 이것도 range라서 **age의 clustered index**가 도움이 되지만 clustered는 하나뿐.
- 결론: 추가 정보가 없으면 **더 자주 쓰이는 쪽에 clustering**을 주는 게 좋은 기본값. 여기선 1000회/일인 `score`.
- 확인: 빈도가 뒤바뀌어 `age > 21`이 1000회/일이면 `age`에 건다. "반복 접근"이라서라기보다 **range 쿼리이면서 자주 도는 쪽**이 clustered의 혜택을 가장 많이 받기 때문.

### 내 index가 어떻게 동작하는지 알아야 한다 *(p.77~78)*
- 일반적으로 equality predicate(=)가 더 빠르다고 가정할 수 있지만, 실무에서는 실제 index 자료구조를 알아야 한다.
- **Hash table index**는 range 조건(`<`, `>`)을 구현할 수 없다.
- **B+ tree**는 range를 구현할 수 있다. 하지만 "hardware layer cake" 때문에 많은 tuple을 순차로 읽는 게 임의 순서로 읽는 것보다 훨씬 효율적이고, **unclustered B+ tree의 range scan은 본질적으로 random 접근**이다.
- 슬라이드 마지막 질문 "몇 개의 record부터 많다고 하느냐"는 답이 주어지지 않았다.

### 슬라이드 Q (p.55): workload에 맞는 index 고르기 (수업 중 내가 설명한 분석, 슬라이드에는 답 없음)
```sql
-- 시간당 1회
SELECT * FROM Flights WHERE date = ?;
-- 분당 1회
SELECT origin FROM Flights WHERE date = ?;
-- 초당 여러 번
SELECT * FROM Flights f1, Flights f2
WHERE f1.date = ? AND f2.date = ? AND f1.dest = f2.origin
```
**답: `date`에 clustered index 하나.**
```sql
CREATE CLUSTERED INDEX DateIndex ON Flights(date);
```
1. 세 쿼리가 전부 `date = ?`로 시작하므로 `date` index 하나로 셋을 다 도울 수 있다.
2. 하루치 flight는 row가 많이 달려 있어(`SELECT *`) selection이라기보다 작은 range scan에 가깝다. unclustered면 흩어져서 random 접근이 많고, clustered면 같은 날짜 row가 연속이라 block 몇 개만 순차로 읽으면 된다.
3. 가장 자주 도는 쿼리는 3번(초당 여러 번)이고 `f1.date`, `f2.date`로 하루치를 가져오는 부분이 핵심이라 clustered `date`가 가장 큰 효과를 준다. 1, 2번은 덤.
4. clustered는 하나뿐이므로 가장 자주 쓰이는 접근 경로에 주라는 기본값과 맞는다.
5. INSERT/UPDATE가 느려지는 비용도 index 하나로 최소화된다.

변형:
- 2번은 `(date, origin)`이 있으면 index-only가 되지만 분당 1회라 빈도가 낮고, `date` clustered로 하루치가 연속이라 이미 충분히 싸다. INSERT 비용 대비 이득이 작아 보인다.
- 3번의 join 때문에 `(date, origin)`이나 `(date, dest)` 같은 multi-attribute clustered를 생각해볼 수 있지만, 효과는 DBMS의 join 실행 방식에 달려 있어 `date` clustered가 안전한 기본값.

## 슬라이드 Q 중 이번 수업에서 다루지 않은 것
- p.2: 8강 마지막의 BCNF decomposition 문제 (`Students(Fname, Lname, Initials, Major, PredictedGPA, ActualGPA)`, FD: `FName, LName → Initials`, `Major → PredictedGPA`). 8강 복습이라 넘어감.
