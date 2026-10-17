# Lecture 8: Schema Design and Normalization — 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

정리 노트: `notes/lecture-08-design-normalization.md` (슬라이드 p.6~96)
오늘 목표: 테이블이 anomaly를 갖는지 FD로 판정하고, BCNF 분해 알고리즘으로 직접 쪼갤 수 있다.

## 0. 선수 개념 점검

- **Key**: 각 행을 식별하는 값. "유일하게 식별"만으로는 부족하고 **최소(minimal)** 조건이 붙는다 (4절).
- **Join**: 조건을 만족하는 행끼리 붙여 새 테이블을 만드는 연산. 보통 key로 연결.
- **부분집합 ⊆**: A의 모든 원소가 B에 있으면 `A ⊆ B` (같아도 됨). **진부분집합 ⊂**: 부분집합이면서 B와 같지 않은 것. `{a,b} ⊆ {a,b}`는 성립, `{a,b} ⊂ {a,b}`는 아님. key의 "최소"는 "진부분집합 중에 superkey가 없다"는 뜻.
- **함수**: x가 정해지면 y가 하나로 정해지는 관계. 오늘 배울 FD가 바로 이것.

## 1. Data Anomalies *(p.6~12)*

인턴이 직원 디렉토리를 한 테이블에 다 몰아 설계함:

| ID | Name | Car | Permit |
|---|---|---|---|
| 123 | Leslie | Charger | C15 |
| 567 | Magda | Civic | E18 |
| 567 | Magda | Ferrari | E18 |

**Data anomaly**: 서로 무관한 정보가 한 테이블에 섞여 있어서 생기는 중복, 갱신 불일치, 의도치 않은 삭제 문제.

- **Update Anomaly**: Magda의 permit을 C22로 바꾸려면 두 행을 모두 바꿔야 한다. 하나만 바꾸면 E18과 C22가 공존해 모순. 한 행만 갱신해 불일치가 생기거나, 매번 여러 행을 다 갱신해야 해서 느리다.
- **Deletion Anomaly**: SQL 삭제는 행 단위다. Leslie의 Charger 행을 `DELETE`하면 Leslie는 그 행 하나뿐이라 직원 정보 자체가 같이 사라진다. NULL로 채우는 방법도 있지만 NULL이 계속 쌓인다.
- **Redundancy Anomaly**: Magda의 ID/Name/Permit이 행마다 반복 저장되어 공간 낭비.

세 문제의 공통 원인은 Car와 상관없는 정보(Name, Permit)가 Car 옆에 같이 있다는 것.

**해결책**: 무관한 attribute를 분리. `(ID, Name, Permit)`과 `(ID, Car)`로 쪼갠다. 둘 다 ID를 가지고 있어 join으로 복원 가능. 분리 후 확인: Magda permit 변경은 1행, Leslie의 Charger를 지워도 Leslie 정보는 보존, Magda 이름은 1회만 저장.

**Informal Design Guidelines** *(p.12)*
- attribute의 의미(semantics)가 자명해야 함
- tuple 내 중복 정보를 피해야 함
- tuple 내 NULL을 피해야 함
- "spurious"(가짜) tuple이 생기지 않아야 함. 존재해선 안 되는 tuple은 애초에 만들 수 없게 해야 함.

## 2. Design Theory와 Functional Dependencies *(p.13~33)*

**Design Theory**: 데이터 anomaly를 찾아서 없애는 방법을 알려주는 형식 이론. 도구는 **FD**. "무관해 보이니까 쪼개자"라는 감을 엄밀하게 판정할 수 있게 해준다.

프로세스 *(p.15)*: ① `R(A1, A2, …)`에서 시작 → ② FD를 찾음 → ③ FD로 schema를 normalize.

**Functional Dependency**: 속성 집합 A가 속성 집합 B를 함수적으로 결정한다는 제약. A 값이 같은 두 tuple은 B 값도 반드시 같다. 표기 `A → B`.

`A1..Am → B1..Bn`이 R에서 성립 ⟺ 모든 tuple t, t'에 대해 (t와 t'가 A1..Am 값이 모두 같으면 B1..Bn 값도 모두 같다).

용어 *(p.17~18)*
- 왼쪽은 **antecedent**(결정자, determinant), 오른쪽은 **consequent**. antecedent가 consequent를 **yields**한다고 말함.
- FD는 한 인스턴스에서 **holds**하거나 **does not hold**. 스키마의 **모든** 가능한 인스턴스에서 성립해야 R이 그 FD를 **satisfy**하고, 그때 FD는 R의 **constraint**.
- 경고: FD는 인과관계가 아니다. "A가 B를 일으킨다"가 아니라 "A 값이 정해지면 B 값이 하나로 정해진다".
- 실생활 예: `UserID → Name`, `ModelNumber → Capacity`, `FullName → Initials`.

### FD 확인하는 방법 *(p.22~27)*
FD가 깨지는지는 "A는 같은데 B는 다른 두 행이 있나?"를 찾으면 된다. 같은 테이블 R1, R2를 self-join해서 센다.

| ID | Name | Phone | Position |
|---|---|---|---|
| 111 | Amal | 1234 | Clerk |
| 222 | Kim | 9876 | Salesrep |
| 333 | Amal | 9876 | Salesrep |
| 444 | Luka | 1234 | Lawyer |

```sql
SELECT COUNT(*)
FROM R1, R2
WHERE R1.position = R2.position
  AND R1.phone <> R2.phone
-- answer: 0  → Position → Phone 성립 (반례 없음)
```

- `ID → Name, Phone, Position`: 성립 (ID가 key).
- `Phone → Position`: 성립 안 함. Phone `1234`가 Clerk와 Lawyer로 갈림.
- `Name → Phone`: 성립 안 함. Amal이 `1234`(행 111)와 `9876`(행 333)로 Phone이 다름. 확인 쿼리는 `WHERE R1.name = R2.name AND R1.phone <> R2.phone`.
- `Phone → Position` 쿼리 결과가 2인 이유: (Amal/Clerk, Luka/Lawyer) 쌍이 순서만 바꿔 두 번 세어짐. 슬라이드는 쌍이 중복되지 않게 `<>` 대신 `<`로 바꾼 버전(`R1.position < R2.position`, answer 1)도 보여줌 *(p.27)*.

### 함정: 인스턴스에서 성립 ≠ FD(제약) *(p.28)*
설계에서 중요한 건 지금 데이터에서 성립하냐가 아니라 **앞으로 어떤 데이터가 들어와도 성립해야 하냐**다. 이건 데이터가 아니라 **도메인 지식**으로 판단한다. 지금 `Position → Phone`이 성립해도, 현실에서 같은 직책이 같은 전화번호를 쓴다는 보장이 없으니 FD로 선언하면 안 된다.

| ID | Name | Job | Car |
|---|---|---|---|
| 123 | Leslie | TA | Civic |
| 345 | Frances | TA | NULL |
| 567 | Magda | Prof | Ferrari |
| 789 | Quinn | Prof | Picklemobile |

- `ID → Name`, `Name → Car`, `Name → Job`: 인스턴스에서는 이름이 전부 달라 셋 다 성립 (Frances의 Car가 NULL이어도 반례는 아님).
- 도메인으로는 `ID → Name`만 진짜 FD. 같은 이름의 사람이 여러 명일 수 있고, 한 사람이 차를 여러 대 가질 수 있어서 `Name → Car`, `Name → Job`은 선언하면 안 된다.

### Armstrong's Axioms *(p.29~33)*
FD 몇 개가 주어지면 거기서 논리적으로 따라 나오는 FD가 있다. 예: `rating → popularity`와 `city, popularity → rec?`이면 `city, rating → rec?`도 성립.

**Armstrong's Axioms**: 주어진 FD들로부터 함의되는 모든 FD를 도출할 수 있는 세 가지 추론 규칙 (1970년대 도입, 지금도 널리 사용).
- **Reflexivity (trivial FD)**: `B ⊆ A`이면 `A → B`. 예: `{name,job} → {name}`.
- **Augmentation**: `A → B`이면 어떤 C를 붙여도 `AC → BC`. 예: `{ID}→{name}`이면 `{ID,job}→{name,job}`.
- **Transitivity**: `A → B`, `B → C`이면 `A → C`. 예: `{ID}→{name}`, `{name}→{initials}`이면 `{ID}→{initials}`.

부차 규칙 *(p.32)*
- **Pseudo Transitivity**: `A → BC`이고 `C → D`이면 `A → BD`
- **Extensivity**: `A → B`이면 `A → AB`

할 수 있는 것/없는 것 *(p.33)*: `{name}→{initials}`만 알 때
- `{name, hair color}→{initials}`는 가능 (Augmentation. antecedent에 속성을 더하는 건 항상 안전. 우변에서 initials만 취하는 건 reflexivity로 정당화).
- `{name}→{initials, hair color}`는 불가능. consequent에 새 속성을 넣으려면 그 속성을 결정하는 FD(`name → hair color`)가 따로 주어져야 한다. axiom만으로는 없던 속성을 우변에 만들 수 없다.

## 3. Closures *(p.35~41)*

axiom을 하나씩 적용해 FD를 도출하는 건 번거롭고 다 찾았는지도 알기 어렵다.

**Closure**: 속성 집합 X가 결정하는 모든 속성의 집합. `X⁺`로 표기.

예: `Name → Initials`, `ID → Name`이 주어지면
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
FD를 하나씩 보면서 좌변이 전부 지금의 X 안에 있는 FD의 우변을 X에 추가하고, 더 안 커질 때까지 반복. tl;dr: transitivity를 반복 적용.

### 예시 *(p.39)*
FD: `id → name`, `rating → popularity`, `name, rating → rec?`

`{id, rating}` → (`id→name`) `{id, rating, name}` → (`rating→popularity`) `{id, rating, name, popularity}` → (`name,rating→rec?`) `{id, rating, name, popularity, rec?}`. 전체 속성과 같으므로 `{id, rating}`은 key.

### 점검 *(p.40)*
FD: `Name, SignatureDrink → Calories`, `Name → Price`
- `{Name}⁺ = {Name, Price}` (SignatureDrink가 없어서 첫 FD는 못 씀)
- `{Name, SignatureDrink}⁺ = {Name, SignatureDrink, Price, Calories}` (전체)

### Closure로 FD 검사하기 *(p.41)*
`A → B`가 성립하는지는 **`B ⊆ A⁺`인지**만 보면 된다. axiom을 반복 적용하는 것과 동치인데 훨씬 간단. 예: `Price ∈ {Name, SignatureDrink}⁺`이므로 `{Name, SignatureDrink} → Price` 성립.

## 4. Formal Definition of Keys *(p.43~51)*

- **Superkey**: R의 모든 속성을 결정하는 속성 집합. `X⁺ = R의 모든 속성`.
- **Key**: **minimal** superkey. 어떤 진부분집합도 superkey가 아님.
- **Candidate key**: key가 여러 개일 때 그 각각.

**minimal의 의미**: 더 뺄 수 있는 속성이 없다. 예: `R(ID, Name, Phone)`, `ID → Name, Phone`
- `{ID}⁺ = 전체` → superkey. 뺄 게 없으니 minimal, key.
- `{ID, Name}`도 superkey지만 Name을 빼도 `{ID}`가 여전히 superkey이므로 minimal이 아님. superkey지만 key는 아님.

**key 확인 순서**: ① closure를 구해 전체 속성이면 superkey ② 속성을 하나씩 뺀 부분집합도 superkey인지 확인. 하나라도 superkey면 minimal이 아님. 전부 아니면 key.

예시 *(p.46~48)*
- `R(A,B,C)`, `A→B, B→C, C→A`: A, B, C 각각이 key.
- `R(A,B,C)`, `AB→C, AC→B`: AB, AC 각각이 key.

SQL에서는 candidate key 중 하나를 `PRIMARY KEY`로, 나머지는 `UNIQUE`로 선언 *(p.49)*.

### 설계에서 key가 왜 중요한가 *(p.50)*
`A → B`에서
- A가 **superkey**: 괜찮음. A가 행을 하나로 특정하니 B가 반복될 일이 없음.
- A가 **superkey가 아님**: redundancy의 신호. 같은 A 값의 행이 여럿일 수 있고 그때마다 B가 반복됨. B를 다른 테이블로 빼야 함.

### 점검
`R(A,B,C,D)`, FD: `A→B`, `B→C`, `C→D`
- `{A}⁺`: `{A}` → `{A,B}` → `{A,B,C}` → `{A,B,C,D}` = 전체. superkey.
- `{A,B}`: closure가 전체라 superkey지만, 진부분집합 `{A}`가 이미 superkey라 minimal이 아님. key는 아님.
- `{B}⁺ = {B,C,D}`, `{C}`, `{D}`도 A가 없어서 superkey 아님. 따라서 key는 `{A}` 하나.

## 5. Normalization 개요와 BCNF *(p.53~63)*

### 정규형 종류 *(p.53~54)*
- **1NF**: Flat (모든 값이 atomic)
- **2NF**: partial FD 없음 (지금은 obsolete)
- **3NF**: 모든 FD를 보존하지만 일부 anomaly는 허용
- **BCNF**: transitive FD 없음. 단 FD를 잃을 수 있음. **이 강의는 BCNF만 다룸**
- **4NF**: multi-valued dependency를 고려
- **5NF**: join dependency를 고려 (다루기 어려움)

### 정의 *(p.55~56)*
**1NF**: 모든 attribute 값이 atomic. multivalued 값이나 nested relation은 허용되지 않음. 이를 데이터가 "flat"하다고 표현.

**BCNF (Boyce-Codd Normal Form)**: relation R이 BCNF라는 것은, 모든 non-trivial FD `X → C`에 대해 `X`가 superkey라는 뜻. (non-trivial: 우변이 좌변의 부분집합이 아닌 FD.) 동치인 표현: 모든 `X`에 대해 `X⁺ = X`이거나 `X⁺ = A`(A는 R의 모든 속성). 4절의 "antecedent가 superkey가 아닌 FD는 redundancy의 신호"가 그대로 정의가 된 것.

### 왜 BCNF인가 *(p.60)*
앞서 본 3가지 anomaly(redundancy/update/deletion)는 relation이 **BCNF이면 없고, BCNF가 아니면 있다**.

### BCNF와 SQL: 사람들 *(p.58~59)*
- "Boyce-Codd"는 **Edgar F. Codd**(relational model 창시자, IBM)와 **Raymond Boyce**(초기 기여자, IBM)에서 유래.
- Codd는 1970년 relational model을 창안. 이후 IBM이 본격 투자하며 꾸린 팀에는 (아이러니하게도) Codd가 포함되지 않았고, 첫 query language SQL은 1974년 **Donald Chamberlin과 Ray Boyce**가 설계 (구현은 System R과 Patricia Selinger).
- Boyce와 Codd는 이후 협업하여 BCNF를 고안.

### BCNF 검사 예시 *(p.61~63)*
`R(ID, Name, Car, ParkingLot)`, FD: `ID → Name, ParkingLot`
- `ID⁺ = {ID, Name, ParkingLot}`. 전체에서 Car가 빠졌으므로 ID는 superkey가 아님 → **BCNF 아님**.
- 검사 방법: **주어진 FD의 좌변마다 closure를 구해 전체 속성인지 본다.**
- 흔한 실수: `ID → Car`를 근거로 드는 것. 주어진 FD가 아니고 성립하지도 않는다 (한 사람이 차를 여러 대 가질 수 있음). 없는 FD를 근거로 쓰면 안 된다.
- 이 R은 1절의 인턴 설계(Car와 Name이 섞임)와 같은 구조.

## 6. BCNF Decomposition Algorithm *(p.65~93)*

BCNF가 아닌 relation은 BCNF가 될 때까지 **decompose**를 반복한다. 분해의 모양 *(p.68)*:

```
R(A1..An, B1..Bm, C1..Ck)
  ↓
R1(A1..An, B1..Bm)
R2(A1..An, C1..Ck)
```
**공통 속성 A를 양쪽에 둬서** 나중에 join으로 원래 데이터를 복원할 수 있게 한다.

예 *(p.69~71)*: `(ID, Name, Car, ParkingLot)`, `ID → Name, ParkingLot` → `R1(ID, Name, ParkingLot)` (ID와 그 closure), `R2(ID, Car)` (ID와 나머지). 분해 후 각 테이블에서 ID가 superkey인지 별도로 확인해야 한다 (자동 보장 아님).

### 알고리즘 *(p.73~76)*
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
- `X⁺ ≠ X`: X가 뭔가를 결정함(non-trivial). `X⁺ ≠ A`: 그런데 전부는 아님(superkey 아님). 둘 다 만족하는 X가 BCNF 위반의 증거.
- R1은 `X → X⁺`가 성립해 X가 R1의 superkey가 됨. R2는 `X⁺ = X`(X 이상으로 더 결정하는 게 없음).
- R1, R2도 아직 BCNF가 아닐 수 있어 **재귀 호출**.
- 분해는 **FD가 시키는 만큼만** 한다. FD로 보증되지 않는 속성끼리는 함부로 쪼개지 않는다.

### 점검 *(p.72)*
`Restaurant(id, name, rating, popularity, rec?)`을 `id → name, rating` 하나로 분해 (`X = {id}`):
- `R1 = X⁺ = (id, name, rating)`
- `R2 = (A − X⁺) ∪ X = {popularity, rec?} ∪ {id} = (id, popularity, rec?)` — **하나의 테이블**. `(id, popularity)`와 `(id, rec?)`로 또 쪼개면 안 된다 (popularity와 rec?가 무관하다는 FD가 없음).

### 전체 예시 *(p.77~88)*
FD: ① `id → name, rating` ② `rating → popularity` ③ `popularity → rec?`

1. `rating⁺ = {rating, popularity, rec?}`. 전체가 아니고 rating보다 큼 → 위반. `X = rating`으로 분해:
   - `R1(rating, popularity, rec?)`
   - `R2(rating, id, name)`
2. R2: R2 안에서 `id⁺ = {id, name, rating}` = R2 전체 → **BCNF**.
3. R1: `popularity⁺ = {popularity, rec?}` ≠ R1 전체(rating 포함) → 위반. `X = popularity`로 다시 분해:
   - `R3(popularity, rec?)`
   - `R4(rating, popularity)`
4. R3, R4: 각자 FD의 좌변이 자기 relation 전체를 결정 → 둘 다 **BCNF**.
5. 최종: `R2(id, name, rating)`, `R3(popularity, rec?)`, `R4(rating, popularity)`. 더 이상 anomaly 없음 *(p.89)*.

분해 후 데이터 *(p.89)*:

| R2: id | name | rating |
|---|---|---|
| 1 | Mee Sum Pastry | 3 |
| 2 | Café on the Ave | 4 |
| 3 | Guanaco's Tacos | 4 |
| 4 | Aladdin Gyro-Cery | 5 |

| R3: popularity | rec? |
|---|---|
| Respectable | N |
| Poppin | Y |

| R4: rating | popularity |
|---|---|
| 3 | Respectable |
| 4 | Poppin |
| 5 | Poppin |

(중간 단계 R1(rating, popularity, rec?)의 데이터는 (3, Respectable, N), (4, Poppin, Y), (5, Poppin, Y).)

분해 후에는 FD의 좌변이 자기 테이블의 superkey인지 **매번 그 relation 안에서 closure를 다시 계산해** 확인해야 한다.

### 연습 1 *(p.90~91)*
`Employees(ID, Name, Car, ParkingLot, Job, Salary)`
1. `ID → Name, Job, Salary`
2. `ID → Car`
3. `Car → ParkingLot`

- `ID⁺` = 전체 (Name, Job, Salary, Car가 나오고 Car에서 ParkingLot) → ID는 superkey, ID가 좌변인 FD는 문제없음.
- `Car⁺ = {Car, ParkingLot}`: 전체 아니고 Car보다 큼 → `X = Car`가 위반. Car는 행을 특정하지 못해 ParkingLot이 반복 저장됨.
- `R1 = (Car, ParkingLot)`, `R2 = {ID, Name, Job, Salary} ∪ {Car} = (ID, Name, Car, Job, Salary)`.
- R1: `Car → ParkingLot`, Car가 R1 전체를 결정 → BCNF. R2: `ID⁺` = R2 전체 → BCNF.
- 최종: `(Car, ParkingLot)`, `(ID, Name, Car, Job, Salary)`.

### 연습 2 *(p.92~93)*
`Students(FName, LName, Initials, Major, PredictedGPA, ActualGPA)`, `FName, LName → Initials`, `Major → PredictedGPA`
- `{FName, LName}⁺ = {FName, LName, Initials}` → 위반. 분해: `(FName, LName, Initials)`, `(FName, LName, Major, PredictedGPA, ActualGPA)`.
- 두 번째에서 `Major⁺ = {Major, PredictedGPA}` → 또 위반. 분해: `(Major, PredictedGPA)`, `(FName, LName, Major, ActualGPA)`.
- 최종: `(FName, LName, Initials)`, `(Major, PredictedGPA)`, `(FName, LName, Major, ActualGPA)`. `Major`를 먼저 잡아도 결과는 같은 모양.

## 7. Discussion — BCNF의 한계와 3NF *(p.94~96)*

**BCNF와 3NF**: BCNF는 anomaly 제거를 보장하지만 일부 FD를 잃을 수 있고, 3NF는 모든 FD를 보존하지만 일부 anomaly를 허용하는 정규형. **트레이드오프**다.

- **Data anomaly**: 실무에서 심각한 문제이므로 반드시 피해야 함.
- **BCNF**: anomaly 제거 보장, 알고리즘이 간단하고 우아함. 하지만 FD를 잃을 수 있음. A와 B가 서로 다른 테이블로 쪼개지면 `AB → C`가 소실될 수 있음.
- **3NF**: 모든 FD를 보존하지만 일부 anomaly가 남을 수 있음. 정의는 간단하지만 normalization 알고리즘이 복잡하고 지저분함.

### BCNF가 FD를 잃는 예 *(p.95~96)*
`Location(city, state, zipcode)`, FD: `zipcode → state`, `city, state → zipcode`
- `zipcode⁺ = {zipcode, state}`는 전체가 아니므로 BCNF 위반. BCNF로 분해하면 `L1(zipcode, state)`, `L2(zipcode, city)`.
- 문제: `city, state → zipcode`를 L1, L2 어디서도 표현할 수 없다. city와 state가 서로 다른 테이블로 갈라졌기 때문. FD가 사라짐.
- 3NF는 이런 FD 손실을 막으려고 일부 anomaly를 허용한다.
- 이 강의에서는 BCNF만 다루고 3NF는 "이런 게 있다"는 정도로만 알면 된다.
