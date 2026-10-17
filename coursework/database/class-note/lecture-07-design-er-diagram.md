# Lecture 7: Conceptual Design and ER Diagrams — 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

정리 노트: `notes/lecture-07-design-er-diagram.md` (슬라이드 p.4~89)
오늘 목표: ER diagram을 보고 `CREATE TABLE`(PK/FK/UNIQUE/NOT NULL)로 변환할 수 있고, 요구사항에서 multiplicity를 판단해 ER diagram으로 그릴 수 있다.

## 0. 선수 개념 점검

### UNIQUE
**UNIQUE**: 그 컬럼(또는 컬럼 조합)에서 같은 값이 두 행에 들어갈 수 없게 막는 제약.

**PRIMARY KEY와의 차이**
- **개수**: PK는 테이블당 1개, UNIQUE는 여러 개 가능
- **NULL**: PK는 NULL 불가, UNIQUE는 NULL 허용이 일반적 (DBMS에 따라 NULL 여러 개 허용)
- **의미**: PK는 행을 대표하는 식별자, UNIQUE는 "중복만 막는" 제약

```sql
CREATE TABLE Person (
    ssn INT PRIMARY KEY,
    email VARCHAR(64) UNIQUE   -- 중복 불가, PK는 아님
);
```
이 UNIQUE는 4번 섹션에서 one-to-one, many-to-one을 SQL로 표현할 때 핵심으로 쓰인다.

## 1. Database Design 개요 *(p.4~10)*

**Database Design**: 저장할 데이터가 무엇이고 데이터끼리 어떤 관계인지를 고려해, 그 데이터를 relation(테이블)과 attribute로 조직하는 과정.

- 지금까지는 테이블과 컬럼이 이미 주어진 상태에서 query만 짰다. 이제부터는 테이블과 컬럼 자체를 어떻게 설계할지를 배운다.
- relational model은 데이터를 어떻게 조직할 수 있는지만 정해주고, 어떻게 조직해야 하는지는 정해주지 않는다. 같은 데이터를 담는 설계도 여러 가지가 나오기 때문에 설계 방법이 따로 필요하다.

설계 4단계
1. **Conceptual Model**: ER diagram으로 표현 (이번 강의)
2. **Relational Model + Schema + Constraints**: 다이어그램을 테이블 구조로 변환 (이번 강의)
3. **Conceptual Schema + Normalization**: 다음 강의
4. **Physical Schema + Indexing**: 추후 강의

### 왜 바로 CREATE TABLE이 아니라 conceptual model을 거치는가
- **conceptualize**: 구조화해서 전체 그림을 먼저 잡고 만드는 게 효율적이다.
- **communicate**: 다른 사람(팀원, 고객, 도메인 전문가)에게 설계를 전달하고 피드백을 받기 쉽다. SQL 코드보다 그림이 비개발자도 읽기 쉽다. (10번 섹션에서 다시 나옴)

## 2. ER Diagram 소개 *(p.12~16)*

**ER Diagram**: 데이터를 entity set, attribute, relationship으로 나눠 그림으로 표현하는, 코드로 깔끔하게 매핑되는 표준화된 설계 도구.

- **rigorous**: 그림의 각 요소가 SQL 구조로 정확히 대응된다.
- **standardized**: 표기법이 정해져 있어 누구나 같은 방식으로 읽는다. 방언이 여럿 있는데 이 강의는 교재 스타일(직사각형/다이아몬드/타원)을 쓴다.
- running example: Product(이름, 가격)를 저장하는 앱. 어느 Company가 만들었는지(name/ceo/address), 어느 Person이 샀는지(name/address/ssn)도 저장.

| 요소 | 도형 |
|---|---|
| Entity set | 직사각형 |
| Attribute | 타원 |
| Relationship | 다이아몬드 |
| Subclass | 삼각형 ("is a") |
| Weak Entity | 이중 테두리 직사각형 + 이중 테두리 다이아몬드 |

## 3. Entity Sets and Attributes *(p.17~18)*

**Entity set**: 같은 종류의 대상들을 모아놓은 집합. 프로그래밍의 class에 해당한다.

| ER 개념 | 프로그래밍 비유 | SQL |
|---|---|---|
| Entity set | class | table |
| Attribute | field | column |
| Entity | object | row |

- attribute에 **underline**이 있으면 그 attribute가 primary key의 일부.
- 모든 entity set은 primary key(또는 그로부터 유도된 key)를 가져야 한다.

```sql
CREATE TABLE Person (
    ssn INT PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(100));
```

확인 문제: `Company`(name, ceo, address), name에 underline → name을 PK로 두고 나머지는 문자열.
```sql
CREATE TABLE Company (
    name VARCHAR(100) PRIMARY KEY,
    ceo VARCHAR(100),
    address VARCHAR(100));
```

## 4. Relationships *(p.19~40)*

### 4-1. 정의와 relationship attribute *(p.19~24)*

**Relationship**: 두 entity set A, B 사이의 연결. 수학적으로는 A × B의 부분집합.

- A × B는 가능한 모든 짝의 집합(카르테시안 곱). 그 중 실제로 연결된 짝만 골라낸 게 relationship이다.
- 예: Product = {Beyblade, Trolls}, Company = {Hasbro, Nyform}이면 A × B는 4개 짝이고, `makes`는 (Beyblade, Hasbro), (Trolls, Hasbro) 같은 실제 제조 관계만 담는다.
- 슬라이드 예시: `Product —makes— Company`, `Person —buys— Product`, `Company —employs— Person`
- SQL에서는 relationship을 별도 테이블로 만들고, 참여하는 entity를 각각 FK로 참조한다.
```sql
CREATE TABLE Makes
    (pname VARCHAR(100) REFERENCES Product,
     cname VARCHAR(100) REFERENCES Company);
```
- relationship 자체도 attribute를 가질 수 있다. 예: `makes`에 `quantity`. 이 값은 Product 소속도 Company 소속도 아니고 "그 회사가 그 제품을 만든 관계"에 속하는 정보다.

확인 문제: `Person —buys— Product`에서 date는 왜 Person이나 Product의 attribute가 아닌가? → 두 사이의 관계에 관한 정보라 `buys`에서 저장해야 한다.
- Person의 attribute로 두면 한 사람이 여러 제품을 다른 날 샀을 때 date를 하나만 저장할 수 있어 어느 제품의 날짜인지 알 수 없다.
- Product의 attribute로 두면 한 제품을 여러 사람이 다른 날 샀을 때 같은 문제가 생긴다.
- date는 (Person, Product) 짝에 붙는 값이고 `Buys` 테이블의 컬럼이 된다.

### 4-2. Relationship Multiplicity *(p.25~30)*

**Multiplicity**: relationship에서 한쪽 entity 하나가 상대편 entity와 최대 몇 개까지 연결될 수 있는지를 나타내는 제약.

- **One-to-one**: 양쪽 모두 최대 하나씩
- **Many-to-one**: 한쪽은 여러 개와, 다른 쪽은 최대 하나와 연결
- **Many-to-many**: 양쪽 모두 제한 없음

표기: 다이아몬드와 entity를 잇는 선의 끝
- **화살표(→)**: 그 entity가 "많아야 하나(at most one)"로 제약된다는 뜻
- **실선(—)**: 제약 없음

**화살표는 "제약되는 쪽"을 향한다** *(p.29)*. `Product → Company` 화살표는 "각 Product는 많아야 하나의 Company에 연결된다"는 뜻이다. Product 하나를 정하면 Company가 최대 하나로 정해지고, 회사 하나가 제품 여러 개를 만드는 건 괜찮다.

슬라이드 예시 (Product: Beyblade, Trolls... / Company: Hasbro, Nyform...)
- 양쪽 다 화살표(one-to-one)면 회사가 제품을 딱 하나만 만든다는 뜻이라 현실과 안 맞는다 *(p.30)*.
- 그래서 `makes`는 Company 쪽으로만 화살표를 둔 many-to-one. 각 product는 한 company에서만 만들어지고, 한 company는 여러 product를 만든다 *(p.31)*.

확인 문제와 풀이
1. `Person —buys— Product` (여러 제품을 사고, 한 제품도 여러 사람에게 팔림) → many-to-many
2. `Person —has— Passport` (여권 하나, 한 여권은 한 사람 것) → one-to-one
3. `Employee —worksIn— Department` (한 직원은 한 부서, 한 부서에는 여러 직원) → many-to-one, **화살표는 Department 쪽(오른쪽)**
   - 화살표 끝 entity에 대해 "상대편 하나를 정하면 얘가 최대 하나로 정해지나?"를 물어본다. 직원 한 명을 정하면 부서는 하나로 정해지므로 Department 쪽에 화살표. 부서 하나를 정하면 직원은 여러 명이므로 Employee 쪽은 실선.
4. `Student —enrolledIn— University` (한 학생은 한 대학, 한 대학에는 여러 학생) → 화살표는 University 쪽.

### 4-3. Multiplicity의 SQL 표현 *(p.26~29)*

**Multiplicity는 relationship 테이블에서 FK 컬럼에 거는 제약(UNIQUE, PRIMARY KEY)으로 SQL에 표현된다.**

**One-to-one**: 양쪽 FK에 `UNIQUE` *(p.26)*
```sql
CREATE TABLE Makes (
    cname VARCHAR(100) UNIQUE REFERENCES Company,
    pname VARCHAR(100) UNIQUE REFERENCES Product);
```
- cname이 UNIQUE면 한 회사는 Makes에 한 번만 나온다 (제품을 하나만 만들 수 있음).
- pname이 UNIQUE면 한 제품도 한 번만 나온다.

**Many-to-many**: UNIQUE를 걸 수 없고, 두 컬럼 조합을 PK로 *(p.27)*
```sql
CREATE TABLE Makes (
    cname VARCHAR(100) REFERENCES Company,
    pname VARCHAR(100) REFERENCES Product,
    PRIMARY KEY (cname, pname));
```
- 같은 (회사, 제품) 짝이 중복되지 않는다는 뜻.
- 같은 회사가 여러 제품과, 같은 제품이 여러 회사와 짝지어지는 건 허용된다.

**Many-to-one**: "각 product는 하나의 company에서만 만들어진다" → `pname`에 `UNIQUE` *(p.35)*
```sql
CREATE TABLE Makes (
    cname VARCHAR(100) REFERENCES Company,
    pname VARCHAR(100) UNIQUE REFERENCES Product);
```
- Company가 화살표를 받으니 "product 하나 → company 하나"여야 하고, 그러려면 pname이 `Makes`에 한 번만 나와야 한다.
- cname에는 UNIQUE가 없으므로 같은 회사가 여러 제품을 만드는 건 허용된다.

### 4-4. 마이그레이션 *(p.31~40)*

위 many-to-one `Makes`는 pname이 UNIQUE라서 각 행이 product 하나에 정확히 대응한다. 즉 "product마다 company 하나"라는 정보만 들어 있으므로 이 정보를 `Product` 테이블 안에 컬럼으로 넣을 수 있다.

**One-to-one과 many-to-one은 relationship 테이블 없이, "많아야 하나"로 제약된 쪽 테이블에 상대편을 참조하는 FK를 직접 넣어 표현할 수 있다. 이것을 마이그레이션이라 한다.** *(p.33~36)*
```sql
CREATE TABLE Company (
    name VARCHAR(100) PRIMARY KEY);
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100) REFERENCES Company);
```
- Product 한 행에 cname이 하나뿐이라 자동으로 "product 하나당 company 하나"가 보장된다.
- `Makes` 테이블이 필요 없어 테이블 수가 줄고, 조회 시 join도 하나 덜 한다.
- relationship에 attribute가 있었다면(예: `mfr_location`) 그것도 `Product`로 같이 옮긴다 *(p.37~38)*.
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100) REFERENCES Company,
    mfr_location VARCHAR(100));
```
- **Many-to-many는 마이그레이션이 안 된다.** FK 하나로는 여러 상대를 가리킬 수 없어 relationship 테이블이 계속 필요하다 *(p.37)*.

확인 문제: `Student —enrolledIn— University`(many-to-one, 화살표는 University)를 relationship 테이블 없이 쓰면?
```sql
CREATE TABLE University (
    uname VARCHAR(100) PRIMARY KEY);
CREATE TABLE Student (
    sid INT PRIMARY KEY,
    name VARCHAR(100),
    uname VARCHAR(100) REFERENCES University);
```
FK는 **Student** 테이블에 들어간다. 규칙은 "많아야 하나"로 제약되는 쪽(화살표가 출발하는 쪽, many 쪽)의 테이블이 FK를 가진다는 것.

### 4-5. Required 관계와 한계 *(p.36, p.39)*

**Required 관계**: "많아야 하나(at most one)"가 아니라 "정확히 하나(exactly one)"를 요구하는 관계.

- 일반 화살표(→)는 많아야 하나를 뜻해서 연결이 없어도 된다 (FK가 NULL인 행 가능).
- 둥근 화살표는 정확히 하나를 뜻해서 반드시 연결이 있어야 한다. SQL에서는 보통 `NOT NULL`로 강제 *(p.39)*.
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100) NOT NULL REFERENCES Company);
```
- 위 Student는 uname이 NULL이어도 되므로 "대학 없이 등록된 학생"이 가능하다. 모든 학생이 반드시 대학에 속해야 하면 `uname VARCHAR(100) NOT NULL REFERENCES University`.

확인 문제: 필수 관계인데 NOT NULL을 안 걸면? → **DB 입장에서는 규칙 위반이 아니다.** NOT NULL이 없으면 FK 컬럼에 NULL이 들어가도 DBMS는 에러 없이 받는다. FK 제약은 값이 있을 때만 참조 대상이 존재하는지 검사하고, NULL이면 검사를 건너뛴다.
- 그래서 "대학이 없는 학생"이 조용히 저장되고, 설계 의도(반드시 소속)는 깨진다.
- 나중에 join이나 집계에서 빠진 행으로 드러나 찾기 어려운 버그가 된다.
- NOT NULL은 이런 위반을 DB가 입력 시점에 막게 하는 장치다.

슬라이드 Q *(p.39)*: exactly one과 at most one을 구분하고 싶은 경우는 언제인가? → 상대편 없이도 그 entity가 현실에서 존재할 수 있는지에 따라 갈린다.
- **exactly one(필수)**: 상대편 없이는 존재 의미가 없을 때. 예: 모든 Product는 반드시 제조사 Company가 있다 → `cname NOT NULL REFERENCES Company`
- **at most one(선택)**: 상대편이 없을 수 있을 때. 예: Person —has— Passport(여권 없는 사람 있음), Student —enrolledIn— University(미등록 상태 허용) → FK가 NULL 가능
- 필수 관계를 일반 화살표로 그리면 NOT NULL이 빠져 "소속 없는 행"이 조용히 저장되고, 선택 관계를 필수로 그리면 정상 데이터(여권 없는 사람)의 입력이 막힌다.

**한계**: ER diagram으로는 표현할 수 있어도 기본 SQL로는 표현 못 하는 제약이 있다. 예: "각 회사는 최대 20개 제품만 만든다"는 개수 제약은 PK/UNIQUE/FK만으로는 못 쓴다 *(p.36)*.

슬라이드 Q *(p.33)*: "`Makes`의 CREATE TABLE문을 써보라. 그런데 `Makes` 테이블이 꼭 필요한가? 다른 표현 방법은?" → 위 4-3(테이블 유지)과 4-4(마이그레이션)가 그 답이다. 단, 마이그레이션 방식에서는 회사가 만드는 제품이 0개면 Product 행이 없어 그 회사와 관련된 행이 나타나지 않는다(슬라이드 주석).

## 5. Multi-Way Relationships *(p.41~50)*

**Multi-way relationship**: 세 개 이상의 entity set이 한꺼번에 얽히는 relationship. 수학적으로는 A × B × C의 부분집합.

- 대부분은 두 entity 사이의 binary relationship이지만, 셋이 동시에 묶여야 의미가 생기는 경우가 있다.
- 예: `Purchase`(product + buyer + company), `Wedding Ceremony`(partner1 + partner2 + venue)

세 FK를 모두 가진 테이블로 표현 *(p.43~44)*
```sql
CREATE TABLE Purchase (
    cname VARCHAR(100) REFERENCES Company,
    pname VARCHAR(100) REFERENCES Product,
    bname INT REFERENCES Buyer,
    PRIMARY KEY (cname, pname, bname));
```
- PK를 세 컬럼 전부로 잡으면 같은 (회사, 제품, 구매자) 조합만 중복이 막히고 나머지는 자유롭다. (Frances, Soap, Dial)과 (Frances, Soap, Dove)가 둘 다 들어갈 수 있다.
- PK를 두지 않는 선택지도 동등하게 가능하다(제약이 느슨해짐).

**PK 선택이 곧 비즈니스 규칙이다.**

"한 구매자는 같은 제품을 항상 같은 회사에서만 산다"를 넣으려면 *(p.45~47)*
```sql
PRIMARY KEY (bname, pname)
```
- (bname, pname) 쌍이 PK라 한 쌍은 한 행에만 나오고, 그 쌍에 대응하는 cname도 하나뿐이다.
- (Frances, Soap, Dial)이 있으면 (Frances, Soap, Dove)는 막힌다.
- 이제는 PK가 반드시 있어야 이 더 제한적인 설계를 표현할 수 있다 *(p.47)*.

`PRIMARY KEY (bname, cname)`이면 "각 (구매자, 회사) 쌍은 하나의 product만"이 된다 *(p.48~49)*. (Frances, Soap, Dial)이 있으면 (Frances, Shampoo, Dial)이 막힌다. (Frances, Soap, Dove)는 (bname, cname) 쌍이 달라 이 설계에서는 허용된다.

확인 문제: `PRIMARY KEY (pname, cname)`이 표현하는 규칙? → 특정 회사의 특정 제품을 구매한 사람은 한 명이다. (pname, cname) 쌍이 한 행에만 나오므로 그 행의 bname도 하나뿐. 따라서 (Frances, Soap, Dial)과 (Quinn, Soap, Dial)은 (Soap, Dial) 쌍이 중복이라 같이 들어갈 수 없다.

슬라이드 Q *(p.50)*: Frances/Chips/Tim's Cascade, Quinn/Chips/Tim's Cascade 두 행이 `PRIMARY KEY (bname, pname)` 설계에서 허용되는가? → 허용된다. (bname, pname) 쌍이 (Frances, Chips)와 (Quinn, Chips)로 서로 달라서 둘 다 들어간다. 구매자마다 같은 제품을 같은 회사에서 산다는 규칙만 지키면 되므로, 다른 구매자가 같은 회사에서 같은 제품을 사는 건 문제없다.

## 6. Subclassing *(p.51~60)*

**Subclass**: 다른 entity set(superclass)의 특수한 한 종류로, superclass의 모든 attribute, key, relationship을 상속하면서 자기만의 attribute를 추가하는 entity set. 다이어그램에서는 `isA` 삼각형.

- 예: `Product`의 subclass로 `Toy`(age 추가), `Candy`(chocolateType 추가). Toy는 Product의 name, price를 그대로 갖고 age가 더해진다.
- SQL에서는 (DBMS의 inheritance 기능 대신) relation + key + FK로 표현한다. subclass 테이블이 superclass를 FK로 참조.
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    price INTEGER);
CREATE TABLE Toy (
    pname REFERENCES Product PRIMARY KEY,
    age INTEGER);
CREATE TABLE Candy (
    pname REFERENCES Product PRIMARY KEY,
    chocType VARCHAR(100));
```
- Toy의 한 행은 Product의 특정 행 하나를 `pname`으로 가리킨다. 상속된 name, price는 그 Product 행에 있고 Toy에는 age만 저장된다.
- `pname`이 **FK이면서 동시에 PK**인 점이 중요하다 *(p.55~60)*.

| Product.name | price |
|---|---|
| Lego | 99 |
| M&M | 5 |

| Candy.pname | chocType |
|---|---|
| M&M | milk |
| M&M | dark ← FK만 있을 때는 들어가지만, PK이면 막힘 |

- PK가 아니고 FK만이면 같은 Product(M&M)를 가리키는 Candy 행이 여러 개 생길 수 있다. 같은 M&M이 milk이면서 dark인 건 한 제품의 chocType이 둘이라는 모순이다.
- PK이기도 하면 pname이 중복될 수 없어 Product 하나당 subclass 행이 최대 하나로 보장된다.
- 일부 DBMS는 inheritance를 지원하지만 core SQL에서는 FK로 표현한다 *(p.61)*.

확인 문제: 이 FK+PK 조합은 어떤 multiplicity인가? → **one-to-one**. 4-3에서 one-to-one은 양쪽 FK에 UNIQUE인데, pname이 PK면 UNIQUE 효과가 있어 Candy가 같은 Product를 두 번 가리킬 수 없고, Candy 행은 pname으로 반드시 Product 하나를 가리킨다. Product 하나는 Candy 행을 **최대 하나**, Candy 행 하나는 Product를 **정확히 하나** 가진다. Product 중에는 Candy가 아닌 것(예: Lego)도 있으므로 non-symmetric한 one-to-one이다. 즉 subclass는 `isA`라는 특별한 one-to-one 관계다.

## 7. Weak Entity Sets *(p.61~65)*

**Weak entity set**: 자기 attribute만으로는 key가 안 되고, 다른 entity set의 key를 빌려와야 유일하게 식별되는 entity set.

- 슬라이드 Q *(p.62)*: 학번이나 전화번호는 한 사람을 유일하게 식별하지만, 어떤 대상은 이름만으로는 식별이 안 된다. key 선택이 항상 자명하지 않다는 질문.
- 슬라이드 예시: `Team`(sport, tname)이 `University`(size, uname)와 `affiliation` 관계를 가진다. `tname`은 "Tigers"처럼 여러 대학에 같은 이름이 있을 수 있어 유일하지 않다. 그래서 Team의 key는 **(tname, uname)** 조합 — 소속 대학의 key를 포함한다.
- 다이어그램에서는 weak entity set과 그것이 의존하는 relationship을 **이중 테두리**로 그린다 *(p.63~64)*.
```sql
CREATE TABLE University (
    name VARCHAR(64) PRIMARY KEY,
    size INTEGER);
CREATE TABLE Team (
    tname VARCHAR(64),
    uname VARCHAR(64) REFERENCES University,
    sport VARCHAR(64),
    PRIMARY KEY (tname, uname));
```
- `uname`은 relationship 역할의 FK이면서 PK의 일부다.
- 앞의 subclass도 key를 부모에게서 빌려오므로 일종의 weak entity로 볼 수 있다.

확인 문제: `Team`의 PK를 `tname` 하나로 잡으면? → 같은 팀 이름에 다른 학교 소속인 팀을 표현할 수 없다. 예: (Tigers, 연세대)가 있을 때 (Tigers, 한양대)를 못 넣는다. 서로 다른 대학에 같은 이름의 팀이 있는 건 현실에서 자연스러운 일이다.

## 8. Union Types *(p.66~73)*

**Union type**: 어떤 entity가 두 entity set 중 하나(xor)와 관계를 맺어야 할 때, 그 둘의 합집합을 참조하는 설계 문제.

예시: 회사가 Windows 노트북과 Mac 노트북을 둘 다 보유하고, 각 Employee는 그 중 **하나만** 지급받는다 *(p.67~68)*.

**잘못된 설계** *(p.69~71)*: Employee가 Windows와 Mac 각각에 대해 별도 관계(`ownsW`, `ownsM`)를 가지게 하면, 각 관계가 many-to-one이어도 한 Employee가 Windows 하나와 Mac 하나를 **동시에** 가질 수 있다. 각 관계는 따로 검사되므로 "둘 중 하나만"이라는 xor를 강제하지 못한다.

**올바른 설계** *(p.72~73)*
- `Windows`와 `Mac`을 공통 superclass `Laptop`의 subclass로 만든다.
- Employee는 `Laptop`과 직접 `owns` 관계를 가진다 (Employee → Laptop 화살표, many-to-one).
- Employee 한 명은 Laptop 하나만 가질 수 있고, 그 Laptop이 Windows든 Mac이든 상관없다. xor가 자연스럽게 강제된다.
- 더 개선하면 공통 attribute(예: `id`)는 subclass가 아니라 `Laptop`에 한 번만 둔다.
- 앞에서 배운 subclassing을 응용해 union을 부모 클래스를 통한 관계로 바꾼 것.

확인 문제: `Employee`가 `Car` 또는 `Bicycle` 중 하나만 통근 수단으로 등록 → `Car`와 `Bicycle`을 `Vehicle`의 subclass(`isA`)로 두고 `Employee —commutesBy— Vehicle`을 many-to-one으로 만든다. 화살표는 Vehicle 쪽. 직원 한 명당 Vehicle이 최대 하나이므로 car와 bicycle을 동시에 등록할 수 없다. (여러 직원이 같은 Vehicle을 쓰는 것까지 막고 싶으면 one-to-one)

## 9. Integrity Constraints *(p.74~85)*

**Integrity constraint**: 데이터가 항상 만족해야 하는 조건을 DBMS가 자동으로 강제하게 하는 제약. PK/FK/UNIQUE/NOT NULL도 모두 여기에 속한다.

### 9-1. CHECK 제약과 Global Assertion *(p.75~77)*

**`CHECK (조건)`**: 조건이 항상 참이도록 DBMS가 강제한다.
- **Attribute constraint**: 단일 attribute에 거는 제약
- **Tuple constraint**: 한 행의 여러 attribute를 함께 쓰는 제약
```sql
CREATE TABLE User (
    uid INT PRIMARY KEY,
    firstName VARCHAR(32),
    lastName VARCHAR(32),
    age INT CHECK (age > 12 AND age < 120),            -- attribute constraint
    email VARCHAR(64),
    phone VARCHAR(32),
    CHECK (email IS NOT NULL OR phone IS NOT NULL)     -- tuple constraint
);
```
- `age`는 13~119만 들어갈 수 있다.
- 마지막 `CHECK`는 email과 phone 중 최소 하나는 있어야 한다는 뜻. 한 행 안의 조건이라 DBMS가 쉽게 검사한다.

**Global Assertion**: 여러 테이블에 걸친 조건을 거는 제약 *(p.77)*
```sql
CREATE ASSERTION myAssert CHECK (
    NOT EXISTS (
      SELECT Product.name FROM Product, Purchase
      WHERE Product.name = Purchase.prodName
      GROUP BY Product.name HAVING COUNT(*) > 200)
);
```
- "어떤 제품도 구매 건수가 200을 넘으면 안 된다"처럼 테이블 전체를 훑어야 확인되는 조건.
- 데이터가 바뀔 때마다 검사해야 해서 비용이 크다. 그래서 실무에서는 거의 안 쓰고 대신 trigger를 쓰는데, trigger도 자체적인 문제가 있다.

### 9-2. Referential Constraints *(p.78~85)*

**참조 무결성(referential constraint)**: FK가 가리키는 대상 행이 실제로 존재하도록 DBMS가 유지하는 제약.

문제는 참조 **대상**(부모) 행이 update/delete될 때, 그 행을 가리키던 자식 행들을 어떻게 할지다. `ON UPDATE` / `ON DELETE`로 정하고, 옵션은 네 가지다 *(p.79)*.

| 옵션 | 동작 |
|---|---|
| **NO ACTION** (기본값) | 에러를 내고 작업을 막음 |
| **CASCADE** | 참조하는 자식 행도 같이 update/delete |
| **SET NULL** | 자식의 FK를 NULL로 바꿈 |
| **SET DEFAULT** | 자식의 FK를 기본값으로 바꿈 (테이블 생성 시 `DEFAULT`가 지정돼 있어야 함) |
```sql
CREATE TABLE T (
    id INT DEFAULT 42 REFERENCES OtherTable
);
```

**예시 1: `ON UPDATE CASCADE`** *(p.80~81)*
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
Company의 Hasbro가 'lmao'로 바뀌면, Hasbro를 가리키던 Beyblade, Troll의 cname도 자동으로 'lmao'가 된다.

| Company.name | | Product.name | cname |
|---|---|---|---|
| Hasbro → **lmao** | | Beyblade | Hasbro → **lmao** |
| Nyform | | Troll | Hasbro → **lmao** |

**예시 2: `ON DELETE SET NULL`** *(p.82~83)*
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
'lmao' 회사가 삭제되면 Beyblade, Troll의 cname이 NULL이 된다. 제품은 남고 소속만 사라진다.

| 실행 전 Company | 실행 전 Product (name, cname) | 실행 후 Company | 실행 후 Product |
|---|---|---|---|
| lmao, Nyform | Beyblade/lmao, Troll/lmao | Nyform | Beyblade/NULL, Troll/NULL |

**예시 3: `ON DELETE NO ACTION`** *(p.84~85)*
```sql
CREATE TABLE Product (
    name VARCHAR(100) PRIMARY KEY,
    cname VARCHAR(100)
        REFERENCES Company
        ON DELETE NO ACTION);

DELETE FROM Company
WHERE name = 'lmao';
```
슬라이드의 결과는 Company에서 'lmao'가 사라졌는데 Product의 cname에는 'lmao'가 그대로 남아 존재하지 않는 회사를 가리키는 **고아(orphaned) 행**이 생기는 모습이다. 참고로 일반적인 DBMS에서 NO ACTION의 기본 동작은 이런 삭제를 에러로 막는 쪽이다. 슬라이드는 "참조 무결성이 깨진 상태"를 보여주려는 예시로 이해하면 된다.

| 실행 전 Company | 실행 전 Product | 실행 후 Company | 실행 후 Product |
|---|---|---|---|
| lmao, Nyform | Beyblade/lmao, Troll/lmao | Nyform | Beyblade/lmao, Troll/lmao ← Orphaned by the deletion! |

확인 문제: 쇼핑몰에서 `Customer`가 탈퇴(DELETE)해도 `Order` 기록은 매출 통계 때문에 남겨야 한다. Order의 FK에 적절한 옵션? → **`ON DELETE SET NULL`**.
- CASCADE: 고객이 삭제되면 주문도 같이 지워져 매출 통계가 사라진다.
- NO ACTION: 주문이 남아 있는 고객은 삭제 자체가 막혀 탈퇴 처리가 안 된다.
- SET NULL: 고객 정보만 지워지고 주문 기록은 customer 없는 상태로 남는다.
- 주의: SET NULL을 쓰려면 그 FK 컬럼이 **NOT NULL이 아니어야 한다**. 필수 관계라서 NOT NULL을 건 경우엔 SET NULL을 쓸 수 없다.

## 10. Getting Design Wrong *(p.86~89)*

**ER diagram은 단순한 그림이 아니라 설계자가 내린 판단을 의사소통하는 도구다.** 어떤 multiplicity를 고르느냐가 곧 현실에 대한 가정이고, 가정이 틀리면 설계가 틀린다.

슬라이드의 Payroll/Registry 예시 *(p.87)*

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

- 567은 차를 두 대 갖고 있으므로 최소한 "사람 한 명이 차 여러 대"는 허용해야 한다.
- "한 사람이 직업을 여러 개 가질 수 있나?"는 데이터만으로는 알 수 없어, 실제 이해관계자와 상의해서 정해야 한다.

슬라이드 Q *(p.87)*: 두 테이블 사이에 어떤 multiplicity를 골라야 하는가? (위 예시 데이터 기준)
- **Payroll—Registry(차)**: 567(Magda)이 차 두 대(Civic, Ferrari)를 가지므로 사람 한 명에 차 여러 대 허용. Registry 한 행(차 한 대)은 한 사람(UserID)에게만 속하므로 **many-to-one, 화살표는 Payroll(사람) 쪽**. 345(Frances)처럼 차가 없는 사람도 있으니 Payroll 쪽은 필수가 아니다.
- **Payroll 안의 Job/Salary**: UserID가 PK라서 한 사람당 직업 하나(one-to-one 성격). 다만 "한 사람이 직업을 여러 개 가질 수 있는가"는 데이터에 나타난 패턴일 뿐 현실의 규칙인지는 알 수 없으므로 domain knowledge로 확인해야 한다.

**데이터 간 관계의 근거** *(p.88)*
- **Domain knowledge**: 현실 세계의 규칙이나 우리가 정한 규칙. 예: 항공기 모델이 날개폭(wingspan)을 결정한다는 건 항공 엔지니어는 안다.
- **Pattern analysis**: 실제 데이터의 패턴을 분석해서 관계를 유추한다.

**설계에는 설계자의 편견이 들어간다** *(p.89)*: 의식적인 편견(prejudice), 무의식적인 편향(bias), 오해(misunderstanding)가 모두 스며들 수 있다. 대응 방안
- 다양한 구성원에게 피드백을 구한다.
- 출시 **전과 후** 모두 피드백을 받아 반영한다.
- **제약을 적게 걸면 유연성이 높아지고, 많이 걸면 안전성이 높아지는** trade-off를 신중히 판단한다.
- 예: "한 사람은 이름이 하나"라고 UNIQUE나 단일 컬럼으로 못 박았다가 별명, 개명, 여러 이름 문화를 반영하지 못해 나중에 고치는 일이 생길 수 있다.

확인 문제: 제약을 많이 걸수록 안전하니 항상 최대한 많이 거는 게 좋은가? → 아니다. 제약이 많으면 유연성이 떨어져 외부 규칙이 바뀔 때 스키마 수정 비용이 커진다. 현실을 너무 단정한 제약은 실제 데이터를 못 담아 입력이 막히기도 한다.

---

## 핵심 요약

- ER diagram은 설계를 개념화(conceptualize)하고 소통(communicate)하는 표준 도구. entity set → table, attribute → column, underline → PK.
- Multiplicity는 화살표(at most one)로 표시하고, SQL에서는 relationship 테이블의 UNIQUE(one-to-one, many-to-one) 또는 복합 PK(many-to-many)로 표현한다.
- one-to-one/many-to-one은 "many 쪽" 테이블에 FK를 직접 넣는 마이그레이션이 가능하고, many-to-many는 relationship 테이블이 필요하다. 필수 관계는 NOT NULL.
- Multi-way relationship에서는 PK로 고른 attribute 조합이 곧 비즈니스 규칙이다.
- Subclass는 FK+PK(one-to-one)로, weak entity는 부모 key를 포함한 복합 PK로, union type은 공통 superclass를 통한 관계로 표현한다.
- CHECK는 attribute/tuple 단위로 쓰고 Global Assertion은 비용 때문에 거의 안 쓴다. FK의 부모 변경 시 동작은 NO ACTION/CASCADE/SET NULL/SET DEFAULT로 정한다.
- 설계는 설계자의 가정과 편견을 담는 결정이다. 피드백을 받고, 제약의 적고 많음 사이의 trade-off를 판단한다.
