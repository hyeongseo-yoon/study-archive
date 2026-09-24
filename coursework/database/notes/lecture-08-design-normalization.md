# Lecture 8: Schema Design and Normalization

*Database Management Systems, 3rd ed. (Ramakrishnan & Gehrke)*

## 1. Data Anomalies *(슬라이드 p.6~12)*

### 예시: 잘못된 설계 *(p.6)*
인턴에게 직원 이름/ID/차량/주차허가를 담는 employee directory 설계를 시켰더니, 아래처럼 한 테이블에 다 몰아넣은 설계를 제안함:

| ID | Name | Car | Permit |
|---|---|---|---|
| 123 | Leslie | Charger | C15 |
| 567 | Magda | Civic | E18 |
| 567 | Magda | Ferrari | E18 |

이 설계의 문제(**data anomalies**)를 살펴봄.

### Redundancy Anomaly *(p.7)*
Redundant row = 불필요한 데이터 — Magda의 permit·name·ID가 반복 저장되어 공간을 낭비함

### Update Anomaly *(p.8)*
Redundant row = 느린 업데이트 또는 데이터 불일치 — Magda의 주차허가를 C22로 바꾸려면 **두 개의 row를 모두 갱신**해야 함(하나만 바꾸면 데이터가 모순됨)

### Deletion Anomaly *(p.9)*
관련 없는 컬럼들이 한 테이블에 있으면 삭제 의미가 불분명해짐 — Leslie의 차량 정보를 지우면 Leslie라는 사람 자체가 통째로 사라져버릴 수 있음

### 해결책: 무관한 attribute 분리 *(p.10~11)*
서로 무관한 attribute/column을 분리하면 redundancy, 불일치 업데이트, 불분명한 삭제를 모두 방지할 수 있음 — 위 테이블을 `(ID,Name,Permit)`와 `(ID,Car)`로 분리

### Informal Design Guidelines *(p.12)*
- attribute의 의미(semantics)가 자명해야 함
- tuple 내 중복 정보를 피해야 함
- tuple 내 NULL 값을 피해야 함
- "spurious"(가짜) tuple의 생성을 허용하지 말아야 함 — 존재해서는 안 되는 tuple은 애초에 허용하지 않음

---

## 2. Design Theory와 Functional Dependencies *(슬라이드 p.13~24)*

### Design Theory란 *(p.13)*
데이터 anomaly를 식별하고 제거하는 방법을 알려주는 formalism. **Functional Dependency(FD)**를 사용 — 테이블을 분리해야 한다는 직관을 엄밀하게 설명할 수 있게 해줌

### 프로세스 개요 *(p.15)*
인턴의 설계에서 ID는 key가 아니었지만, 그럼에도 Name과 ParkingLot을 결정(determine)하고 있었음. 일반적 절차:
1. relational schema `R(A1, A2, A3, …)`에서 시작
2. 그 schema의 **functional dependency(FD)**를 찾음
3. FD를 이용해 schema를 **normalize**함

### Functional Dependency 정의 *(p.16)*
> **Functional Dependency** `A1,…,Am → B1,…,Bn`이 relation R에서 성립하려면: `∀t,t' ∈ R, (t.A1=t'.A1 ∧ … ∧ t.Am=t'.Am → t.B1=t'.B1 ∧ … ∧ t.Bn=t'.Bn)`

- 비형식적으로는 "일부 attribute가 다른 attribute를 결정한다"는 의미
- 실생활 예: `FullName → Initials`, `ModelNumber → Capacity`, `UserID → Name`
- **경고: dependency는 causation(인과관계)을 의미하지 않는다**

### FD 용어 *(p.17~18)*
FD `A1,…,Am → B1,…,Bn`에서:
- `A1,…,Am`을 **antecedent**(선행자) 또는 **determinant**(결정자)라 부름
- `B1,…,Bn`을 **consequent**(후행자)라 부름
- antecedent가 consequent를 **yields**(산출)한다고 말함
- FD는 R의 **하나의 인스턴스**에 대해 **holds**(성립)하거나 **does not hold**(성립하지 않음)
- R의 **모든** 인스턴스에서 어떤 FD가 참이면, R이 그 FD를 **satisfies**(만족)한다고 함
- R이 어떤 FD를 만족하면, 그 FD는 R에 대한 **constraint**(제약)임

### FD 직관 — 예시로 확인하기 *(p.19~21)*
`R(A,B,C,D,E,F)`에서 `AC → DF`가 성립하는지 확인하려면: A,C 값이 일치하는 두 tuple을 찾았을 때, 그 두 tuple이 D,F 값도 반드시 일치해야 함

### Example: FDs that Hold *(p.22~27)*
아래 테이블에서 여러 FD의 성립 여부를 SQL 쿼리로 검증:

| ID | Name | Phone | Position |
|---|---|---|---|
| 111 | Amal | 1234 | Clerk |
| 222 | Kim | 9876 | Salesrep |
| 333 | Amal | 9876 | Salesrep |
| 444 | Luka | 1234 | Lawyer |

- `ID → Name, Phone, Position` ✅ (ID가 PK이므로 당연히 성립)
- `Position → Phone` ✅ — 검증 쿼리: `SELECT COUNT(*) FROM R1,R2 WHERE R1.position=R2.position AND R1.Phone<>R2.Phone` → 결과 0(위반 없음)이면 FD가 성립함
- `Phone → Position` ❌ — 검증 쿼리 결과 1(같은 Phone `1234`를 가진 Amal은 Clerk, Luka는 Lawyer로 Position이 다름) → **FD가 깨짐**

### Reasoning about FDs — Armstrong's Axioms *(p.29~33)*
일부 FD는 다른 FD를 논리적으로 함의(imply)함 — 예: `rating → popularity`와 `city, popularity → rec?`이 성립하면 `city, rating → rec?`도 성립함(직접 확인 가능하지만, 일반적 알고리즘이 필요)

**Armstrong's Axioms** (1970년대 도입, 지금도 널리 사용됨) *(p.31)*:
- **Reflexivity (Trivial FD)**: `B ⊆ A`이면 `A → B` — 예: `{name} ⊆ {name,job}`이므로 `{name,job} → {name}`
- **Augmentation**: `A → B`이면 모든 `C`에 대해 `AC → BC` — 예: `{ID}→{name}`이므로 `{ID,job}→{name,job}`
- **Transitivity**: `A → B`이고 `B → C`이면 `A → C` — 예: `{ID}→{name}`이고 `{name}→{initials}`이므로 `{ID}→{initials}`

**부차적 규칙(Secondary Rules)** *(p.32)*:
- **Pseudo Transitivity**: `A → BC`이고 `C → D`이면 `A → BD`
- **Extensivity**: `A → B`이면 `A → AB`

**Armstrong's Axioms만으로 할 수 있는 것/없는 것** *(p.33)*:
- `{name}→{initials}`만 알고 있을 때 `{name, hair color}→{initials}`로 만드는 것은 **가능**(antecedent에 attribute를 추가하는 건 consequent의 attribute를 제거하지 않으므로 문제없음)
- 반대로 `{name}→{initials, hair color}`로 만드는 것은 **불가능**(axiom만으로는 antecedent에 도입하지 않은 attribute를 consequent에 도입할 방법이 없음)

---

## 3. Closures *(슬라이드 p.35~41)*

### Closure 정의 *(p.35~37)*
> 집합 `{A1,…,Am}`의 **Closure**(표기: `{A1,…,Am}⁺`)는, `A1,…,Am → B`가 성립하는 모든 attribute `B`의 집합이다. Closure는 **한 attribute 집합이 결정하는 모든 것**을 찾아냄

- 예: `Name → Initials`, `ID → Name`이 주어지면
  - `Name⁺ = {Name, Initials}`
  - `ID⁺ = {ID, Name, Initials}`
  - `Initials⁺ = {Initials}`

### Closure Algorithm *(p.38)*
```
Input: X = {A1, …, Am}
Output: X⁺

Repeat until X does not change:
    if B1,…,Bn → C is a FD and B1,…,Bn ∈ X
    then X ← X ∪ C
Return X
```
- tl;dr: transitivity를 반복 적용
- 절차: (1) 우변에 추가할 attribute `C`를 찾는다 → (2) 추가한다 → (3) 갱신된 FD 목록을 다시 살펴 더 추가할 `C`를 찾는다

### 예시: Closure 구하기 *(p.39)*
`id → name`, `rating → popularity`, `name, rating → rec?`이 주어졌을 때:
`{id, rating}⁺ = {id, rating} → {id, rating, name} → {id, rating, name, popularity} → {id, rating, name, popularity, rec?}`
전체 attribute 집합과 일치하면, **`{id, rating}`은 key**

### Closure로 FD 성립 여부 검사하기 *(p.41)*
`A → B`가 성립하는지 확인하려면, 단순히 **`B ⊆ A⁺`인지만 확인**하면 됨 — Armstrong's Axioms를 반복 적용하는 것보다 훨씬 간단하고 이와 동치인 테스트

---

## 4. Formal Definition of Keys *(슬라이드 p.43~51)*

### Superkey, Key, Candidate Key *(p.43~45)*
- **Superkey**: relation R의 attribute 집합 `{A1,…,An}`이 superkey라는 것은, R의 모든 attribute `B`에 대해 `A1,…,An → B`가 성립함을 뜻함. 즉 `{A1,…,An}⁺ = R의 모든 attribute`
- **Key**: **minimal**(최소) superkey — key의 어떤 진부분집합(subset)도 superkey가 아님
- **Candidate Key**: relation이 여러 key를 가질 때, 그 각각의 key를 candidate key라 부름

### 예시 *(p.46~48)*
- `R(A,B,C)`에서 `A→B, B→C, C→A`이면: **A, B, C 각각이 key** (순환적으로 서로를 결정)
- `R(A,B,C)`에서 `AB→C, AC→B`이면: **AB, AC 각각이 key**

### SQL에서의 키 *(p.49)*
relation이 여러 key(candidate key)를 가질 수 있는데, `CREATE TABLE` 시 그중 하나를 **PRIMARY KEY**로 지정하고, 나머지는 **UNIQUE**로 선언할 수 있음

### Design에서 키의 유용성 *(p.50)*
- Antecedent가 superkey가 아닌 FD는 **redundancy(중복)의 힌트**임 — 구체적으로는, 그 FD의 consequent를 다른 relation으로 뽑아낼(extract) 수 있음
- 재구성하면: `A`가 superkey이면 `A → B`는 괜찮음(문제없음) / `A`가 superkey가 아니면 `B`를 R에서 제거(다른 테이블로 옮김)해야 함

---

## 5. Normalization 개요와 BCNF *(슬라이드 p.53~63)*

### 다양한 Normal Form *(p.53~54)*
- **1NF**: Flat(모든 값이 atomic)
- **2NF**: partial FD 없음 (지금은 obsolete)
- **3NF**: 모든 FD를 보존(preserve)하지만 일부 anomaly는 허용
- **BCNF**: transitive FD 없음, 단 FD를 잃을(lose) 수 있음 — **이 강의는 BCNF만 다룸**
- **4NF**: multi-valued dependency를 고려
- **5NF**: join dependency를 고려(다루기 어려움)

### 1NF, BCNF 정의 *(p.55~56)*
> **1NF**: relation R이 First Normal Form이라는 것은 모든 attribute 값이 **atomic**함을 뜻함 — attribute 값은 multivalued일 수 없고, nested relation은 허용되지 않음. 이를 데이터가 "**flat**"하다고 표현
>
> **BCNF (Boyce-Codd Normal Form)**: relation R이 BCNF라는 것은, 모든 **non-trivial functional dependency `X → C`에 대해 `X`가 superkey**임을 뜻함. 동치인 표현: 모든 `X`에 대해 `X⁺ = X`이거나 `X⁺ = A`(A는 R의 모든 attribute)

### BCNF와 SQL: 사람들 *(p.58~59)*
- "Boyce-Codd"라는 이름은 **Edgar F. Codd**(relational data model의 창시자, IBM)와 **Raymond Boyce**(relational data model의 초기 기여자, IBM)에서 유래
- Codd는 1970년 relational model을 창안. 이후 IBM이 본격 투자하며 꾸린 팀에는 (아이러니하게도) Codd가 포함되지 않았고, 첫 query language SQL은 1974년 **Donald Chamberlin과 Ray Boyce**가 설계함(실제 구현은 System R과 Patricia Selinger가 담당)
- Boyce와 Codd는 이후 협업하여 BCNF를 고안함

### 왜 BCNF인가 *(p.60)*
- 앞서 본 3가지 anomaly(redundancy/update/deletion)를 상기
- relation이 **BCNF이면 이 anomaly들이 없음**
- **BCNF가 아니면 이 anomaly들이 있음**

### Example: BCNF 검사 *(p.61~63)*
`(ID, Name, Car, ParkingLot)` 테이블, FD: `ID → Name, ParkingLot`

- **버전 1 (정의 1 적용)**: FD의 antecedent가 ID인데, ID는 superkey가 아님(Car를 결정하지 못함) → **BCNF 아님**
- **버전 2 (정의 2 적용)**: 가능한 attribute 부분집합을 순회하다가 `{ID}`를 발견 — `ID⁺ = {ID, Name, ParkingLot}`인데 이는 전체 attribute 집합이 아님(Car가 빠짐) → **BCNF 아님**

---

## 6. BCNF Decomposition Algorithm *(슬라이드 p.65~88)*

### Anomaly 제거 원리 *(p.65~67)*
BCNF relation은 세 가지 data anomaly가 없음을 다시 확인. relation이 BCNF가 아니면, BCNF가 될 때까지 **decompose(분해)**를 반복 적용함

### Decomposing Schema — 일반 원리 *(p.68)*
Decomposition은 schema를 더 작은 부분들로 나누는 것. 이 강의에서 decomposition은 다음을 의미함:
```
R(A1,…,An, B1,…,Bm, C1,…,Ck)
  ↓
R1(A1,…,An, B1,…,Bm)
R2(A1,…,An, C1,…,Ck)
```
데이터를 다시 join할 수 있도록 **공통 attribute(A1,…,An)를 양쪽에 유지**함

### 예시: FD를 이용한 Schema 분해 *(p.69~71)*
`(ID,Name,Car,ParkingLot)`, `ID → Name, ParkingLot`을 분해:
- **왼쪽 테이블**: antecedent(ID) + 그 closure(Name, ParkingLot) + 이 컬럼들에 관련된 FD들 → `R1(ID, Name, ParkingLot)`
- **오른쪽 테이블**: antecedent(ID) + 그 외 나머지 모든 컬럼 + 이 컬럼들에 관련된 FD들 → `R2(ID, Car)`
- 왼쪽 테이블에서는 ID가 superkey지만, **오른쪽 테이블에서도 ID가 superkey인지는 별도로 확인해야 함**(자동으로 보장되지 않음)

### BCNF Decomposition Algorithm (의사코드) *(p.73~76)*
```
Normalize(R):
    A ← R의 모든 attribute 집합
    find X s.t. X⁺ ≠ X and X⁺ ≠ A
    if X is not found
        "R is in BCNF"
    else
        decompose R into R1(X⁺) and R2((A - X⁺) ∪ X)
        Normalize(R1)
        Normalize(R2)
```
- `if X is not found`: R이 이미 BCNF인지 판정하는 부분
- `R1`에서는 `X → X⁺`가 성립하므로 X가 (R1 기준) superkey가 됨
- `R2`에서는 `X⁺ = X`가 성립함(즉 X 이상으로 더 결정하는 게 없음)
- **재귀 호출**하는 이유: R1과 R2가 여전히 BCNF가 아닐 수 있어 추가 분해가 필요할 수 있음

### 예시: Restaurant 테이블 전체 BCNF 분해 *(p.77~88)*
`Restaurant(id, name, rating, popularity, rec?)`, FD 3개: `id → name, rating` / `rating → popularity` / `popularity → rec?`

1. **1단계**: `rating⁺ = {rating, popularity, rec?}`인데 이는 전체 attribute가 아님(id, name 누락) → BCNF 위반 → `rating`을 기준으로 분해:
   - `R1(rating, popularity, rec?)` — FD: `rating→popularity`, `popularity→rec?`
   - `R2(rating, id, name)` — FD: `id→name, rating`
2. **R2 검사**: `id⁺`가 R2의 전체 컬럼 집합과 같음(id가 R2에서 superkey) → **R2는 BCNF**
3. **R1 검사**: `popularity⁺ = {popularity, rec?}`인데 R1의 전체 컬럼(rating 포함)과 다름 → 여전히 BCNF 위반 → `popularity`를 기준으로 다시 분해:
   - `R3(popularity, rec?)` — FD: `popularity→rec?`
   - `R4(rating, popularity)` — FD: `rating→popularity`
4. **R3, R4 검사**: 각각의 FD에서 antecedent가 자기 relation 내 전체 attribute를 결정 → 둘 다 **BCNF**
5. **최종 결과**: `R2(id, name, rating)`, `R3(popularity, rec?)`, `R4(rating, popularity)` — 이 세 relation이 normalize된 최종 schema이며, **더 이상 anomaly가 없음**

---

## 7. Discussion — BCNF의 한계와 3NF *(슬라이드 p.94~96)*

### BCNF vs 3NF 비교 *(p.94)*
- **Data anomaly**: 실무에서 심각한 문제이므로 반드시 피해야 함
- **BCNF**: anomaly 제거를 **보장**하고, 알고리즘이 간단하고 우아함. 하지만 **일부 FD를 잃을(lose) 수 있음** — 예: A와 B가 서로 다른 테이블로 쪼개지면 `AB → C`라는 FD 자체가 소실될 수 있음
- **3NF (Third Normal Form)**: 모든 FD를 보존하지만, 여전히 일부 data anomaly가 남을 수 있음. 정의는 비교적 간단하지만 normalization 알고리즘 자체는 복잡하고 지저분함

### 예시: BCNF가 FD를 잃는 경우 *(p.95~96)*
`Location(city, state, zipcode)`, FD: `zipcode → state`, `city, state → zipcode`

- `zipcode`의 closure가 전체 attribute가 아니므로(city 누락) BCNF 위반 → BCNF 알고리즘으로 분해하면: `L1(zipcode, state)`, `L2(zipcode, city)`
- **문제**: 분해 과정에서 **`city, state → zipcode`라는 FD 자체가 사라짐**(두 결과 테이블 어디에서도 이 FD를 표현할 수 없게 됨)
- **3NF**는 이런 FD 손실을 막기 위해 일부 anomaly를 허용하는 대신 모든 FD를 보존함 — 정의는 상대적으로 단순하지만, normalization 알고리즘은 복잡하고 비효율적임
