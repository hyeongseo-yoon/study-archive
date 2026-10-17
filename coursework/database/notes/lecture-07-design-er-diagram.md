# Lecture 7: Conceptual Design and ER Diagrams

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*Database Management Systems, 3rd ed. (Ramakrishnan & Gehrke)*

## 1. Database Design 개요 *(슬라이드 p.4~10)*

### Relational Model 복습 *(p.4)*
- Relational model은 데이터를 **어떻게 조직할 수 있는지**의 메커니즘만 규정하고, **어떻게 조직해야 하는지**는 규정하지 않음(physical data independence)
- 지금까지는 relation 이름과 attribute가 이미 주어진 상태에서 query하는 법만 배움 — 이제부터 몇 강의에 걸쳐 **relation과 attribute 자체를 어떻게 설계할지**를 다룸

### Database Design이란 *(p.6)*
- **Database Design**(= Logical Design = Relational Schema Design): **무엇을 저장해야 하는지**와 **데이터 간 상호관계**를 고려해 데이터를 조직하는 것
- Arbitrary Data → (조직화) → Database로 가는 과정

### The Database Design Process (4단계) *(p.8~10)*
1. **Conceptual Model** (이번 강의): entity/relationship 다이어그램으로 표현
2. **Relational Model + Schema + Constraints** (이번 강의): 테이블 구조로 변환
3. **Conceptual Schema + Normalization** (다음 강의)
4. **Physical Schema + Indexing** (추후 강의)

---

## 2. ER Diagram 소개 *(슬라이드 p.12~16)*

### Running Example *(p.12~13)*
Product(이름, 가격 등)를 저장하려는 애플리케이션 예시: 어느 회사가 만드는지(Company: name/ceo/address), 어느 사용자가 사는지(Person: name/address/ssn) 정보를 함께 저장

### 왜 ER Diagram인가 *(p.14)*
- 애플리케이션의 설계를 **개념화(conceptualize)**하고 **소통(communicate)**하기 위해 ER diagram 사용
- ER diagram은 **rigorous**(코드로 깔끔히 매핑 가능)하고 **standardized**(아이디어를 전달하고 피드백을 구할 수 있음)함
- 다양한 "방언(dialect)"이 존재 — 이 강의는 교재 스타일(직사각형/다이아몬드/타원)을 사용

### ER Diagram의 구성 요소 (Building Blocks) *(p.15)*
| 요소 | 도형 |
|---|---|
| Entity set | 직사각형 |
| Attribute | 타원 |
| Relationship | 다이아몬드 |
| Subclass | 삼각형("is a") |
| Weak Entity | 이중 테두리 직사각형 + 이중 테두리 다이아몬드 |

---

## 3. Entity Sets and Attributes *(슬라이드 p.17~18)*

- **Entity set**은 **class**와 유사(데이터에 대한 서술), **Attribute**는 class의 **field**와 유사, **Entity**는 특정 **object**(구체적인 한 row)와 유사
- **Underline**된 attribute는 그 attribute가 primary key의 일부임을 나타냄
- 모든 entity set은 primary key(또는 그로부터 유도된 key)를 가져야 함
- SQL 변환: entity set은 그대로 `CREATE TABLE`로, attribute는 column으로, underline된 attribute는 `PRIMARY KEY`로 매핑됨 *(p.18)*
  - 예: `Person`(name, address, ssn — ssn에 underline)
```sql
CREATE TABLE Person (
    ssn INT PRIMARY KEY,
    name VARCHAR(…),
    address VARCHAR(…));
```

---

## 4. Relationships *(슬라이드 p.19~36)*

### 정의 *(p.19~20)*
**Relationship**: A, B가 entity set이면, relationship R은 **A × B의 부분집합(subset)**
- 슬라이드 예: `Product —makes— Company`, `Person —buys— Product`, `Company —employs— Person` *(p.21~23)*
- `makes` relationship을 SQL로 옮기면 *(p.21)*:
```sql
CREATE TABLE Makes
    (pname VARCHAR(100) REFERENCES Product,
     cname VARCHAR(100) REFERENCES Company);
```

### Relationship Attributes *(p.24)*
Relationship 자체도 attribute를 가질 수 있음 — 예: `makes`(Product-Company) relationship에 `quantity`를 붙일 수 있음

### Relationship Multiplicity *(p.25~30)*
세 종류: **One-to-one**, **Many-to-one**, **Many-to-many** (다이아몬드 양 끝의 화살표 유무로 표시 — 화살표(→)는 "많아야 하나"를, 실선(—)은 제약 없음을 뜻함)

- **One-to-one**: 양쪽 다 화살표 — 양쪽 entity 모두에 `UNIQUE REFERENCES`를 걸어 표현 가능 *(p.26)*
- **Many-to-many**: 양쪽 다 실선 — 양쪽에 `UNIQUE`를 걸 수 없고, 반드시 **두 attribute의 조합을 PRIMARY KEY**로 삼아야 함(단독 UNIQUE로는 다대다를 표현 못 함) *(p.27)*
- **Many-to-one**: 화살표가 "1쪽으로 제약되는(constrained to one)" entity를 향함 — 예: 각 Product가 정확히 1개 Company에 의해 만들어짐을 표현하려면 화살표가 Company를 향함 *(p.28~29)*
- 표현 원칙: **화살표가 가리키는 쪽(TO)이 "많아야 하나(at most one)"로 제약되는 entity** *(p.29)*
- 슬라이드 예 (Product: Beyblade, Trolls … / Company: Hasbro, Nyform …) *(p.25~31)*: 양쪽이 모두 화살표인 one-to-one은 "회사가 제품을 하나만 만든다"는 뜻이라 말이 안 됨(*"companies usually make many products"*, p.30). 화살표를 Company 쪽에만 두면 **각 product는 한 company에만 만들어짐** (p.31)
- **One-to-one SQL** *(p.26)*: 양쪽 FK에 `UNIQUE`
```sql
CREATE TABLE Company (
    name VARCHAR(100) PRIMARY KEY,
    ...);
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    ...);
CREATE TABLE Makes (
    cname VARCHAR(100)
        UNIQUE REFERENCES Company,
    pname VARCHAR(100)
        UNIQUE REFERENCES Product,
    ...);
```
- **Many-to-many SQL** *(p.27)*: 두 컬럼 조합을 PK로
```sql
CREATE TABLE Makes (
    cname VARCHAR(100)
        REFERENCES Company,
    pname VARCHAR(100)
        REFERENCES Product,
    PRIMARY KEY (cname, pname),
    ...);
```
  - 슬라이드에서는 one-to-one 코드에서 `UNIQUE`에 X 표시(삭제)를 하고 빨간색 `PRIMARY KEY (cname, pname)`을 추가해 보여줌

### Relationships in SQL — 별도 관계 테이블 vs. 마이그레이션 *(p.31~35)*
- 기본적으로는 relationship마다 별도의 relationship table을 만들 수 있음(각 참여 entity를 참조하는 FK들의 조합) *(p.31)*
- **하지만 One-to-one, Many-to-one 관계는 relationship table이 불필요(redundant)** — "많아야 하나"로 제약된 쪽(child table)에 상대방을 참조하는 FK와 relationship attribute를 직접 옮겨(migrate) 넣을 수 있음 *(p.33~34)*
  - 예: `Product`가 항상 정확히 하나의 `Company`에 만들어진다면, `Product` 테이블에 `cname REFERENCES Company`와 `mfr_location`(relationship attribute)을 직접 추가하면 됨
- **슬라이드 Q** *(p.33)*: "`Makes`의 CREATE TABLE문을 써보라. 그런데 `Makes` 테이블이 꼭 필요한가? 다른 표현 방법은?" (Product → Company many-to-one 다이어그램, `CREATE TABLE Makes ( . . . );`는 빈칸)
- **방법 1: 관계 테이블 유지 (many-to-one)** *(p.35)*: `pname`에만 `UNIQUE` (product 하나는 한 행에만 등장 → 한 company에서만 만들어짐), `cname`은 그냥 FK
```sql
CREATE TABLE Makes (
    cname VARCHAR(100)
        REFERENCES Company,
    pname VARCHAR(100)
        UNIQUE REFERENCES Product,
    ...);
```
- **방법 2: Product에 FK를 직접 저장 — `Makes` 테이블 불필요** *(p.36)*
```sql
CREATE TABLE Company (
    name VARCHAR(100) PRIMARY KEY,
    ...);
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100)
        REFERENCES Company
    ...);
```
  - Company.cname을 Product 안에 reference로 직접 저장. 단 **회사가 만드는 제품이 0개면 Product 행이 없다**(슬라이드 주석)
- **relationship attribute까지 migrate** *(p.37~38)*: `mfr_location`도 `Product`로 옮김
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100)
        REFERENCES Company,
    mfr_location VARCHAR(100)
    ...);
```
- **Many-to-many 관계는 여전히 관계 테이블(foreign key 조합)이 필요** *(p.37)*
- **Required(필수) 관계 표현**: rounded arrow(둥근 화살표)는 "정확히 하나(exactly one)"를, 일반 화살표는 "많아야 하나(at most one)"를 의미 — SQL에서는 보통 `NOT NULL`로 강제 *(p.39)*
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100) NOT NULL
        REFERENCES Company
    ...);
```
  - 슬라이드 Q: 두 종류의 relationship(exactly one vs at most one)을 구분하고 싶은 경우는 언제인가?
    - **답**: 상대편 없이도 그 entity가 현실에서 존재할 수 있는지에 따라 갈린다.
    - **exactly one(필수)**: 상대편 없이는 존재 의미가 없을 때. 예: 모든 Product는 반드시 제조사 Company가 있다 → `cname NOT NULL REFERENCES Company`
    - **at most one(선택)**: 상대편이 없을 수 있을 때. 예: Person —has— Passport(여권이 없는 사람도 있음), Student —enrolledIn— University(휴학·미등록 상태 허용) → FK가 NULL 가능
    - 구분이 중요한 이유: 필수 관계를 일반 화살표로 그리면 NOT NULL이 빠져 "소속 없는 행"이 조용히 저장되고, 선택 관계를 필수로 그리면 정상적인 데이터(여권 없는 사람)의 입력이 막힌다.
- **한계**: "각 회사는 최대 20개 제품만 만든다"처럼 ER diagram으로는 표현 가능하지만 **기본 SQL로는 표현 불가능한 제약**도 있음(예: `<=20` 같은 개수 제약) *(p.36)*

---

## 5. Multi-Way Relationships *(슬라이드 p.41~50)*

### 개념 *(p.41~42)*
- 대부분의 relationship은 두 entity set 사이의 binary relationship이지만, 가끔 **multi-way relationship**이 필요함 — 예: `Purchasing`(product+buyer+company), `Wedding Ceremony`(partner1+partner2+venue)
- Relation의 정의가 일반화됨: A, B, C가 집합이면 relationship R은 **A × B × C의 부분집합**

### Example #1: 기본 표현 *(p.43~44)*
- `Purchase(cname, pname, bname)` 테이블을 만들고 세 FK를 모두 포함하는 **composite primary key**로 지정
- 또는 애초에 PK를 두지 않는 선택지도 동등하게 가능(제약이 느슨해짐)
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    ...);
CREATE TABLE Company (
    name VARCHAR(100) PRIMARY KEY,
    ...);
CREATE TABLE Buyer (
    id INT PRIMARY KEY,
    ...);
CREATE TABLE Purchase (
    cname VARCHAR(100) REFERENCES Company,
    pname VARCHAR(100) REFERENCES Product,
    bname INT REFERENCES Buyer,
    PRIMARY KEY (cname, pname, bname),
    ...);
```
- 예시 데이터 *(p.44)*: `Purchase(bname, pname, cname)` = (Frances, Soap, Dial), (Quinn, Soap, Dial)

### Example #2: 추가 제약 표현하기 *(p.45~48)*
- "한 구매자는 항상 같은 회사의 같은 제품만 구매한다"는 제약을 표현하려면?
- **잘못된 접근**: `purchase` 관계를 binary(`Buyer→Company`)로 단순화하는 것만으로는 부족(그것만으로는 대응관계가 안 잡힘)
- **올바른 접근**: `PRIMARY KEY (bname, pname)`로 지정하면, (buyer, product) 조합마다 정확히 하나의 company만 허용되어 원하는 제약이 강제됨 — 이제 PK가 없으면 표현 불가능했던 제약을 표현할 수 있게 됨
- 슬라이드 진행 *(p.45~47)*: 질문 "한 buyer가 특정 product를 항상 같은 company에서 사려면?" → 아래 `Purchase`에서 두 번째 행(Frances, Soap, **Dove**)을 **막고 싶음**. 슬라이드에서 "That's it?!?!" 라고 묻고 PK만 바꾸면 된다고 보여줌 *(p.46~47)*

| bname | pname | cname |
|---|---|---|
| Frances | Soap | Dial |
| Frances | Soap | Dove ← 금지 |
| Quinn | Soap | Dial |

```sql
CREATE TABLE Purchase (
    cname VARCHAR(100) REFERENCES Company,
    pname VARCHAR(100) REFERENCES Product,
    bname INT REFERENCES Buyer,
    PRIMARY KEY (bname, pname),
    ...);
```
- 슬라이드 주석: 이제는 **PK가 반드시 있어야** 이 더 제한적인 설계를 표현할 수 있다 *(p.47)*

### PK 선택이 인코딩하는 의미 *(p.48~50)*
- `PRIMARY KEY (bname, pname)`는 **"각 (buyer, product) 쌍은 하나의 company에서만 옴"**을 의미
- 만약 `PRIMARY KEY (bname, cname)`를 선택했다면 **"각 (buyer, company) 쌍은 하나의 product에서만 옴"**을 의미하게 되어, 같은 buyer-company 쌍으로 다른 product를 구매하는 행(row)은 금지됨 — 즉 **어떤 attribute 조합을 PK로 선택하느냐가 실제로 어떤 비즈니스 제약을 강제하는지를 결정**함
- 예시 *(p.48~49)*: `PRIMARY KEY (bname, cname)`이면 (Frances, Soap, Dial)이 있을 때 **(Frances, Shampoo, Dial)** 은 같은 (buyer, company) 쌍에 다른 product이므로 금지됨. (Frances, Soap, Dove)는 (bname, pname) 기준 제약이므로 이 설계에서도 여전히 금지(`Still disallowed`)

**슬라이드 Q** *(p.50)*: 아래 표에서 chips 구매 두 행(Frances/Chips/Tim's Cascade, Quinn/Chips/Tim's Cascade)이 이 ER diagram에서 허용되는가? (답 없음)

| bname | pname | cname |
|---|---|---|
| Frances | Soap | Dial |
| Quinn | Soap | Dove |
| Frances | Chips | Tim's Cascade |
| Quinn | Chips | Tim's Cascade |

---

## 6. Subclassing *(슬라이드 p.51~60)*

### 개념 *(p.52~53)*
- Entity set은 다른 entity set의 **subclass**가 될 수 있음(`isA` 삼각형으로 표시) — 예: `Product`의 subclass로 `Toy`(age 속성 추가), `Candy`(chocolateType 속성 추가)
- Subclass는 superclass의 **모든 attribute, key, relationship을 암묵적으로 상속**함

### SQL로 표현하기 *(p.54~60)*
- 이 강의에서는 (DBMS 자체의 inheritance 지원 대신) **relation + key + foreign key**로 상속을 표현
- `Toy`, `Candy` 테이블은 각각 `Product`를 참조하는 FK(`pname`)를 가짐 — subclass의 instance는 Product의 특정 instance를 참조
- **FK를 PK로도 겸하게 하면**(`pname REFERENCES Product PRIMARY KEY`), 한 Product가 여러 subclass entity를 갖는 것을 방지할 수 있음(한 product가 동시에 Toy이면서 여러 개의 서로 다른 Toy row로 나타나는 것을 막음)
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    price INTEGER);
CREATE TABLE Toy (
    pname REFERENCES Product PRIMARY KEY,
    ...);
CREATE TABLE Candy (
    pname REFERENCES Product PRIMARY KEY,
    ...);
```
- 예시 데이터 *(p.55~60)*

| Product.name | price |
|---|---|
| Lego | 99 |
| M&M | 5 |

| Toy.pname | age |
|---|---|
| Lego | 8 |

| Candy.pname | chocType |
|---|---|
| M&M | milk |
| M&M | dark (FK만 있을 때; PK로 지정하면 이 두 번째 행이 막힘) |

- 참고 *(p.61)*: 일부 DBMS는 inheritance를 지원하지만 "core SQL"에서는 FK로 표현

---

## 7. Weak Entity Sets *(슬라이드 p.61~65)*

### 슬라이드 Q *(p.62)*
- 네 학번(예: 23xxxxx)이 너를 유일하게 식별하는가? PK로 쓸 수 있는가? / 네 전화번호가 유일하게 식별하는가? (답 없음 — key 선택이 항상 자명하지 않다는 질문)

### 정의 *(p.63~64)*
- **Weak entity set**의 key는 **다른 entity set의 key를 포함**함 — 즉 subclass도 일종의 weak entity라고 볼 수 있음
- 예: `Team`(sport, tname)이 `University`(size, uname)와 `affiliation` 관계를 가질 때, `tname`만으로는 팀을 유일하게 식별할 수 없음(같은 이름의 팀이 여러 대학에 있을 수 있음) → **Team의 key는 (tname, uname) 조합**
- Weak entity set과, 그것이 의존하는 relationship은 **이중 테두리(double outline)**로 표시

### SQL 표현 *(p.65)*
```sql
CREATE TABLE University(
    name VARCHAR(64) PRIMARY KEY,
    size INTEGER);
CREATE TABLE Team(
    tname VARCHAR(64),
    uname VARCHAR(64) REFERENCES University,
    sport VARCHAR(64),
    PRIMARY KEY (tname, uname));
```

---

## 8. Union Types *(슬라이드 p.66~73)*

### 문제 상황 *(p.67~68)*
- 두 entity set의 **합집합(union)**을 참조하고 싶을 때가 있음 — 어떤 entity set이 ES1 **xor** ES2와 relationship을 가지는 경우
- 예: 회사가 Windows 노트북과 Mac 노트북을 모두 보유하고, 각 Employee는 둘 중 **하나만** 지급받음

### 잘못된 설계 *(p.69~71)*
- `Employee`가 `Windows`와 `Mac` 각각에 대해 별도의 관계(`ownsW`, `ownsM`)를 가지도록 설계하면, **한 Employee가 두 노트북(Windows 하나 + Mac 하나)을 동시에 소유하는 것을 막지 못함** — xor 의미를 강제하지 못하는 결함

### 올바른 설계 *(p.72~73)*
- `Windows`와 `Mac`을 공통 superclass `Laptop`의 subclass로 만들고, `Employee`가 (Windows/Mac이 아니라) **`Laptop`과 직접 `owns` 관계**를 가지도록 설계
- 이렇게 하면 union 의미가 **부모 class(Laptop)에 대한 relationship**을 통해 자연스럽게 구현됨 — 한 Employee는 하나의 Laptop(그 밑의 Windows든 Mac이든 하나)만 소유 가능
- 더 개선: 공통 attribute(예: `id`)를 subclass가 아니라 `Laptop`(부모)에 직접 두면 더 깔끔해짐

---

## 9. Integrity Constraints *(슬라이드 p.74~85)*

### Attribute-level / Tuple-level 제약 *(p.75~76)*
- `CHECK (condition)`: DBMS가 항상 조건이 참이도록 강제
  - **Attribute constraint**: 단일 attribute에 부여 — 예: `age INT CHECK (age > 12 AND age < 120)`
  - **Tuple constraint**: 여러 attribute를 함께 조건으로 사용 — 예: `CHECK (email IS NOT NULL OR phone IS NOT NULL)`
```sql
CREATE TABLE User (
    uid INT PRIMARY KEY,
    firstName VARCHAR(32),
    lastName VARCHAR(32),
    age INT CHECK (age > 12 AND age < 120),   -- Attribute constraint
    email VARCHAR(64),
    phone VARCHAR(32),
    CHECK (email IS NOT NULL OR phone IS NOT NULL)   -- Tuple constraint
);
```
- 적용 가능 범위: 단일 attribute / 단일 tuple *(p.75)*
- DBMS가 쉽게 검사할 수 있음(실제 데이터베이스에서 얼마나 유용한지는 논쟁의 여지가 있다고 언급) *(p.76)*

### Global Assertions *(p.77)*
```sql
CREATE ASSERTION myAssert CHECK (
    NOT EXISTS (
      SELECT Product.name FROM Product, Purchase
      WHERE Product.name = Purchase.prodName
      GROUP BY Product.name HAVING COUNT(*) > 200)
);
```
- DBMS가 검사하기에 **비용이 크고(expensive)**, 실무에서는 **거의 쓰이지 않음** — 대신 trigger를 쓰지만 trigger도 자체적인 문제가 있음

### Referential Constraints (참조 무결성) *(p.78~85)*
- Foreign key는 그 FK를 포함하는 relation에 제약을 둠 — 참조 대상 relation의 row가 update/delete될 때 이 제약을 어떻게 유지할지 결정해야 함 *(p.78)*
```sql
CREATE TABLE Payroll (
    UserID INT PRIMARY KEY,
    Name VARCHAR(100),
    Job VARCHAR(100),
    Salary INT);
CREATE TABLE Registry (
    UserID INT REFERENCES Payroll,
    Car VARCHAR(100));
```
- 질문: 두 relation에 걸친 이 제약을 어떻게 유지하는가?
- `ON UPDATE`/`ON DELETE`로 선언하며 4가지 옵션: *(p.79)*
  - **NO ACTION** (기본값): 에러를 발생시킴
  - **CASCADE**: 참조하는(referencer) row도 함께 update/delete
  - **SET NULL**: 참조하는 row의 FK 필드를 NULL로 설정
  - **SET DEFAULT**: 참조하는 row의 FK 필드를 (테이블 생성 시 지정된) 기본값으로 설정
  - `SET DEFAULT`는 테이블 생성 시 default 값이 지정돼 있어야 함 *(p.79)*:
```sql
CREATE TABLE Table (
    id INT DEFAULT 42 REFERENCES OtherTable,
    ...
);
```
- **예시로 본 각 옵션의 동작** *(p.80~85)*:
  - **Example 1 — `ON UPDATE CASCADE`** *(p.80~81)*: `Company.name`을 `'lmao'`로 UPDATE하면, `Product.cname`을 참조하던 row들도 함께 `'lmao'`로 자동 갱신됨
```sql
CREATE TABLE Company (
    name VARCHAR(100) PRIMARY KEY);
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100)
        REFERENCES Company
        ON UPDATE CASCADE);

UPDATE Company
SET name = 'lmao'
WHERE name = 'Hasbro';
```

| Company.name | | Product.name | cname |
|---|---|---|---|
| Hasbro → **lmao** | | Beyblade | Hasbro → **lmao** |
| Nyform | | Troll | Hasbro → **lmao** |

  - 슬라이드 설명: Company의 update가 참조하던 row들도 함께 update함 *(p.81)*  - **Example 2 — `ON DELETE SET NULL`** *(p.82~83)*: `Company`에서 해당 row를 DELETE하면, 참조하던 `Product.cname`이 `NULL`로 설정됨
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100)
        REFERENCES Company
        ON UPDATE CASCADE
        ON DELETE SET NULL);

DELETE FROM Company
WHERE name = 'lmao';
```

| 실행 전 Company | 실행 전 Product (name, cname) | 실행 후 Company | 실행 후 Product |
|---|---|---|---|
| lmao, Nyform | Beyblade/lmao, Troll/lmao | Nyform | Beyblade/NULL, Troll/NULL |

  - 슬라이드 설명: Company에서의 삭제가 참조하던 row들의 값을 NULL로 바꿈 *(p.83)*
  - **Example 3 — `ON DELETE NO ACTION`** *(p.84~85)*: 슬라이드 예시에서는 DELETE가 그대로 진행되어 참조하던 `Product.cname`이 존재하지 않는 값을 가진 채로 **"고아(orphaned)"** row로 남는 결과가 나타남
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100)
        REFERENCES Company
        ON DELETE NO ACTION);

DELETE FROM Company
WHERE name = 'lmao';
```

| 실행 전 Company | 실행 전 Product | 실행 후 Company | 실행 후 Product |
|---|---|---|---|
| lmao, Nyform | Beyblade/lmao, Troll/lmao | Nyform | Beyblade/lmao, Troll/lmao ← Orphaned by the deletion! |

---

## 10. Getting Design Wrong — ER Diagram과 설계 결정 *(슬라이드 p.86~89)*

### ER Diagram은 의사소통 도구 *(p.87)*
슬라이드 예시 테이블 (이 둘 사이에 어떤 multiplicity를 골라야 하는가?):

| UserID | Name | Job | Salary |
|---|---|---|---|
| 123 | Leslie | TA | 50k |
| 345 | Frances | TA | 60k |
| 567 | Magda | Prof | 120k |
| 789 | Quinn | Prof | 100k |

| UserID | Car | Year |
|---|---|---|
| 123 | Charger | 2009 |
| 567 | Civic | 2016 |
| 567 | Ferrari | 2000 |
| 789 | Picklemobile | 2018 |

- 좋은 설계는 다양한 이해관계자로부터 **피드백**을 요구함 — 예: Payroll/Registry 테이블에서 (UserID→Job/Salary), (UserID→Car/Year) 각각에 어떤 multiplicity를 선택할지는 실제 데이터(한 사람이 여러 직업/여러 차를 가질 수 있는지)를 보고 상의해서 결정해야 함
  - **답(예시 데이터 기준)**:
    - Payroll—Registry(차): 567(Magda)이 차 두 대(Civic, Ferrari)를 가지므로 사람 한 명에 차 여러 대 허용. Registry 한 행(차 한 대)은 한 사람(UserID)에게만 속하므로 **many-to-one, 화살표는 Payroll(사람) 쪽**. 345(Frances)처럼 차가 없는 사람도 있으니 Payroll 쪽은 필수가 아니다.
    - Payroll 안의 Job/Salary: UserID가 PK라서 한 사람당 직업 하나(one-to-one 성격). 다만 "한 사람이 직업을 여러 개 가질 수 있는가"는 데이터에 나타난 패턴일 뿐 현실의 규칙인지는 알 수 없으므로 domain knowledge로 확인해야 한다.

### Data Interrelationships 판단 근거 *(p.88)*
데이터 간 관계를 규정하는 규칙을 어디서 얻는가:
- **Domain knowledge**: 우리가 직접 정한 규칙, 또는 현실 세계와 대응되는 규칙 — 예: 항공기 모델이 날개폭(wingspan)을 결정한다는 것을 항공 엔지니어는 알고 있음
- **Pattern analysis**: 실제 데이터 패턴을 분석해서 관계를 유추

### ER Diagram은 곧 설계 결정(Decision) *(p.89)*
- 데이터 설계는 본질적으로 설계자의 **의식적인 편견(prejudice), 무의식적인 편향(bias), 오해(misunderstanding)**를 내포함
- 대응 방안:
  - 다양한 구성원으로부터 피드백을 구함
  - 출시 **전과 후** 모두 피드백을 구하고 반영
  - **제약을 적게(유연성 ↑)** vs **제약을 많이(안전성 ↑)** 사이의 trade-off를 신중히 판단

---

## 수업에서 다룬 섹션

1. Database Design 개요
2. ER Diagram 소개
3. Entity Sets and Attributes
4. Relationships (정의/attribute, multiplicity, SQL 표현, 마이그레이션, required 관계)
5. Multi-Way Relationships
6. Subclassing
7. Weak Entity Sets
8. Union Types
9. Integrity Constraints (CHECK, Global Assertion, Referential Constraints)
10. Getting Design Wrong
