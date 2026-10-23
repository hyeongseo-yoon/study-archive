# Chapter 5 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*(수업일: 2026-10-23, 참조 노트: `notes/chapter-5.md`)*

## 0. 선수 지식 복습

1. **row / column / primary key**: row는 한 개체의 정보를 담은 한 줄(tuple/record), column은 같은 타입의 속성(attribute/field), primary key는 각 row를 유일하게 식별하는 하나 이상의 column.
2. 조건 조회 SQL: `SELECT * FROM Users WHERE user = 'me';`
3. 문자열 이어붙이기로 query를 만들 때 입력에 `'`가 들어가면 문자열 리터럴이 거기서 끝나고, 그 뒤의 내용은 데이터가 아니라 **SQL 코드**로 해석된다. 이게 SQL injection의 원리.
4. **DAC** vs **RBAC**: DAC는 자원 소유자가 권한을 직접 줄 수 있는 방식, RBAC는 사용자에게 role을 주고 권한은 role에 붙이는 방식 (관리 부담 감소, 일관된 권한 관리).
5. 대량 데이터에는 **대칭키**를 쓴다. 공개키는 연산이 훨씬 느려서 보통 키 교환에만 쓰고 데이터는 대칭키로 암호화.

---

## 1. Database와 DBMS *(p.2~3)*

**Database**: 하나 이상의 애플리케이션이 쓰도록 저장한 구조화된 데이터 모음. **DBMS**: 그 데이터베이스를 구축·유지하면서 여러 사용자에게 query 인터페이스를 제공하는 프로그램 모음.

- Database는 데이터 항목들과 그 사이의 **관계**까지 포함하고, 민감한 데이터를 담을 수 있어 보안이 필요하다.
- DBMS는 **ad hoc query**(미리 정해두지 않은 즉석 질의)를 지원하고, **query language**가 DB에 대한 통일된 인터페이스 역할을 한다.

**DBMS 아키텍처 (Figure 5.1)**
- 사용자 query는 두 갈래로 처리된다: **DDL processor**(data definition language, 스키마 정의), **DML and query language processor**(data manipulation language, 데이터 조작·질의).
- 그 아래에 **Transaction manager**, **File manager**, **Physical database**.
- DBMS가 관리하는 테이블: **Database description tables**(스키마 정보), **Authorization tables**(누가 뭘 할 수 있는지), **Concurrent access tables**(동시 접근 제어).
- 짚을 점: DBMS 자체가 권한 정보(Authorization tables)를 들고 있어서 DB 접근 제어가 DBMS 안에서 일어난다.

**확인 질문 - DDL과 DML**: DDL은 스키마 정의, DML은 데이터 조작. (DML은 "분류"가 아니라 조작과 질의: 삽입·삭제·수정·조회. DDL은 구조를 정의하고, DML은 그 구조 안의 데이터를 다룬다.)

---

## 2. 관계형 데이터베이스와 SQL *(p.4~10)*

**관계형 DB**: 데이터를 행과 열로 된 테이블에 저장하고, 테이블들을 공통 키로 연결해서 관계형 query language로 조건에 맞는 데이터를 꺼내 쓰는 DB.

**기본 구조 *(p.4)***
- 각 열은 특정 타입의 데이터를 담고, 각 행은 열마다 값을 하나씩 가진다.
- 이상적으로는 값이 모두 유일한 열이 하나 있어서 그 행의 식별자(키)가 된다.
- 모든 테이블에 존재하는 고유 식별자로 여러 테이블을 연결할 수 있다.

**예시 모델 (Figure 5.2) *(p.5)***: 전화 서비스 DB. PRIMARY TABLE, CALLER ID TABLE, ADDITIONAL SUBSCRIBER TABLE, BILLING HISTORY TABLE, CURRENT BILL TABLE. 모든 테이블이 **PhoneNumber** 필드를 키로 서로 연결된다.

**용어 (Table 5.1) *(p.6~7)***

| 일반 용어 | 대응 용어 |
|---|---|
| Relation | table / file |
| Tuple | row / record |
| Attribute | column / field |

- **Primary key**: 행을 유일하게 식별. 하나 이상의 column 이름으로 구성.
- **Foreign key**: 한 테이블을 다른 테이블의 속성에 연결.
- **View / virtual table**: 하나 이상의 테이블에서 선택된 행과 열을 반환하는 **query의 결과**. 실제로 저장된 테이블이 아니라 query로 만든 가상의 테이블.

**추상 모델과 예시 (Figure 5.3, 5.4) *(p.8~9)***
- 추상 모델: N개 record × M개 attribute(A1…AM), 각 칸 x_ij.
- Employee Table(Ename, Did, Salarycode, Eid, Ephone)과 Department Table(Did, Dname, Dacctno). Employee의 `Did`는 **foreign key**, Department의 `Did`는 **primary key**.
- 두 테이블에서 파생한 **view**는 Dname, Ename, Eid, Ephone만 보여준다. Salarycode 같은 민감한 열은 숨긴다. view가 접근 제어에 쓰이는 이유가 이것이고, Inference(5번)에서 다시 나온다.

**확인 질문 - foreign key와 view**
- foreign key로 Employee의 한 행이 Department의 어느 행에 속하는지 연결되고, 두 테이블을 합쳐 "직원 이름 + 부서 이름" 같은 걸 한 번에 볼 수 있다. Figure 5.4(b)의 view가 그렇게 만든 것.
- view는 원본 전체가 아니라 query가 골라낸 행과 열만 보여준다. 어떤 사용자에게 원본 테이블 대신 view에만 권한을 주면 민감한 열을 볼 수 없다. 다만 view로 가려도 새는 경우가 있고, 그게 Inference.

**SQL *(p.10)***
- 관계형 DB에서 스키마 정의, 데이터 조작, 질의를 하는 표준화된 언어. ANSI/ISO 표준의 여러 버전이 있으나 기본 문법과 의미는 같다.
- 테이블 생성, 데이터 삽입/삭제, view 생성, query문으로 데이터 조회가 가능.

---

## 3. SQL Injection *(p.11~23)*

### 취약한 로그인 예제 *(p.13~17)*

```
set ok = execute( "SELECT * FROM Users
    WHERE user='" & form("user") & "'
    AND pwd='" & form("pwd") & "'" );
if not ok.EOF
    login success
else fail;
```

`form("user")`, `form("pwd")`는 사용자가 웹 폼에 입력한 값, `&`는 문자열 이어붙이기, `ok.EOF`는 결과 행이 하나도 없을 때 true.

정상 입력(user=`me`, pwd=`1234`)이면 DB에는 `SELECT * FROM Users WHERE user='me' AND pwd='1234'`가 간다.

**진단 질문**: user 칸에 `' or 1=1 --`를 넣으면? (`--`는 그 줄의 나머지를 주석으로 만든다.)

```
SELECT * FROM Users WHERE user='' or 1=1 --' AND pwd='아무거나'
```

- 입력의 첫 `'`가 `user='`의 문자열을 바로 닫아서 `user=''`는 빈 문자열과 비교하는 조건이 된다.
- 뒤의 `or 1=1`은 데이터가 아니라 **SQL 코드**. `1=1`은 항상 참이라 WHERE 전체가 참.
- `--` 뒤는 주석이라 `AND pwd=...` 검사가 통째로 사라진다.
- Users의 모든 행이 반환되고 `ok.EOF`가 false가 되어 로그인 성공. 비밀번호를 몰라도 로그인된다.

**근본 원인**: 사용자 입력(데이터)을 문자열로 그냥 이어붙여 query(코드)를 만들었다. 그래서 입력이 데이터와 코드의 경계를 깨고 코드로 해석된다.

**더 심한 경우 *(p.16~17)***
- user=`' ; DROP TABLE Users --` → `WHERE user='' ; DROP TABLE Users --...`. `;`로 query를 끝내고 새 명령을 붙인 것이라 **Users 테이블 삭제**. 사용자 추가, 비밀번호 재설정도 같은 방식으로 가능.
- user=`' ; exec cmdshell 'net user badguy badpwd' / ADD --` → SQL 서버가 **"sa" 권한**(관리자급)으로 실행 중이면 공격자가 **DB 서버 OS에 계정**을 만든다. DB 서버가 통째로 넘어간다.

### Injection Technique *(p.18)*
- SQLi는 보통 **텍스트 문자열을 조기에 종료**시키고 **새 명령을 덧붙이는** 방식.
- 삽입한 명령 뒤에 정상 코드가 더 붙어 있으면 에러가 나거나 실행에 방해가 되므로, 공격자는 주입 문자열 끝을 **`--` 주석**으로 마무리해 뒤의 텍스트를 무시하게 한다.

### 공격 경로 (Attack Avenues) *(p.19)*
폼 입력만이 아니라 query에 들어가는 값이면 어디든 경로가 된다.
- **User input**: 정교하게 만든 사용자 입력 (위 예제).
- **Server variables**: HTTP/네트워크 헤더 값을 위조해서 주입.
- **Second-order injection**: DB에 **이미 저장된 데이터**가 나중에 query에 쓰일 때 발동. 입력 시점이 아니라 나중에 터지고, query를 바꾸는 입력이 사용자가 아닌 **시스템 내부**에서 온다.
- **Cookies**: 쿠키를 변조해서, 서버가 쿠키 내용으로 query를 만들 때 구조를 바꾼다.
- **Physical user input**: 웹 요청 밖에서 공격 입력을 적용 (예: 바코드나 RFID 같은 물리적 입력).

**확인 질문 - Second-order**: 첫 주입 시점에는 티가 안 나고, 나중에 시스템 내부에서 그 값을 쓴 query를 만들 때 코드로 실행되어 터진다. 저장하는 시점에는 입력이 그냥 문자열 데이터로 DB에 들어가 아무 일도 안 일어난다. 나중에 시스템이 "내 DB에 있는 값이니 안전하겠지" 하고 그 값을 이어붙여 새 query를 만들 때 코드로 해석된다. 그래서 입력 검증을 입구에서만 하면 놓친다.

### SQLi 공격 유형 *(p.20~22)*
분류 기준: 주입 채널과 결과를 받는 채널이 같은지, 결과가 직접 보이는지.

**(1) In-band attack *(p.20)***
- SQL 코드를 주입하는 채널과 결과를 받는 채널이 **같다**. 가져온 데이터가 애플리케이션 웹 페이지에 **직접 표시**된다.
- **Tautology**: 조건문에 코드를 넣어 **항상 참**으로 만든다 (`or 1=1`).
- **End-of-line comment**: 필드에 코드를 주입한 뒤 **줄 끝 주석(`--`)**으로 뒤의 정상 코드를 무효화 (`AND pwd=...`를 없앤 것).
- **Piggybacked queries**: 의도된 query **뒤에 추가 query를 덧붙여** 편승 (`; DROP TABLE Users`).

**(2) Inferential attack *(p.21)***
- 실제 데이터가 페이지에 오지 않는다. 특정 요청을 보내고 웹사이트/DB 서버의 **반응을 관찰**해 정보를 재구성한다.
- **Illegal/logically incorrect queries**: 일부러 문법이 틀리거나 논리가 맞지 않는 query를 보내 **에러 메시지**를 유도, 백엔드 DB의 **종류와 구조**를 알아낸다. 다른 공격을 위한 **예비 정보 수집 단계**.
- **Blind SQL injection**: DB에 **참/거짓 질문**을 던지고 **애플리케이션의 응답**으로 답을 판단한다. 시스템이 에러 정보를 안 보여줄 만큼 안전해도 데이터를 **추론**할 수 있다.

**Blind SQLi 원리**: 페이지에 데이터는 안 나와도, query 결과에 따라 페이지 동작이 달라지면 그 차이가 1비트짜리 답이 된다. 예를 들어 `item?id=5`에서
- `id=5 AND 1=1` → 조건이 참이라 상품이 정상 표시.
- `id=5 AND 1=2` → 조건이 거짓이라 빈 페이지.

이 차이로 참/거짓을 판별한다. `id=5 AND (admin 비밀번호의 첫 글자가 'a'이다)`를 보내 정상이면 첫 글자가 `a`, 빈 페이지면 아니므로 `b`, `c`, ...로 바꿔가며 묻는다. 한 글자씩 한 자리씩 반복하면 값을 통째로 복원할 수 있다. 데이터가 직접 오는 게 아니라 **응답의 차이**로 한 비트씩 추론하기 때문에 "inferential"이라 부르고, 에러 메시지를 숨겨도 막히지 않는다. 실제로는 자동화 도구가 이 반복을 대신한다.

**(3) Out-of-band attack *(p.22)***
- 데이터를 **다른 채널**로 가져온다. 주입 채널로는 정보 조회에 제한이 있을 때, **DB 서버의 outbound 연결이 느슨하면** 사용 가능. 예: DB 서버가 공격자 쪽으로 데이터를 보내게 만든다.

### SQLi Countermeasures *(p.23)*
- **Defensive coding**: 수동 방어적 코딩 관행, **Parameterized query insertion**, **SQL DOM**
- **Detection**: **Signature based**, **Anomaly based**, **Code analysis**
- **Run-time prevention**: 실행 중에 query가 **예상되는 query의 모델**에 맞는지 검사

슬라이드는 이름만 나열한다. 핵심만 보충하면, **Parameterized query**는 query 구조를 먼저 고정하고 사용자 입력은 나중에 **값으로만** 채워 넣는 방식이다. 입력에 `'`나 `or 1=1`이 있어도 코드가 아니라 문자열 값으로 취급된다. 원인이 "데이터와 코드의 경계가 깨지는 것"이었으므로 원인을 직접 막는 방어.

---

## 4. Database Access Control *(p.24~28)*

### 접근 제어 시스템이 결정하는 것 *(p.24)*
- 사용자가 DB **전체**에 접근할 수 있는지, **일부**에만 접근할 수 있는지.
- 사용자가 가진 **접근 권한(access rights)**: create, insert, delete, update, read, write.
- 관리 정책의 범위
  - **Centralized administration**: 소수의 **특권 사용자**만 권한을 부여/회수.
  - **Ownership-based administration**: 테이블의 **생성자**가 그 테이블의 권한을 부여/회수.
  - **Decentralized administration**: 소유자가 **다른 사용자에게 권한 부여/회수 권한까지 위임**. 위임받은 사용자가 다시 권한을 주고 뺏을 수 있다.

### SQL 기반 접근 정의 *(p.25)*
- **GRANT**: 하나 이상의 접근 권한을 부여하거나, 사용자를 **role에 지정**.
- **REVOKE**: 접근 권한을 회수.
- 일반적인 권한: **Select, Insert, Update, Delete, References**. (`References`는 다른 테이블의 foreign key가 이 테이블의 column을 참조하도록 허용하는 권한.)

### Cascading authorizations *(p.26, Figure 5.6)*
Decentralized administration에서는 권한이 사람 사이에 전파되어 **권한 부여 그래프**가 생기고, 화살표마다 부여 **시점 t**가 적혀 있다.

회수 전 그래프:
- Ann → Bob (t=10), Ann → Chris (t=20)
- Bob → David (t=30), Chris → David (t=50)
- David → Ellen (t=40), David → Frank (t=60)
- Ellen → Jim (t=70)

**Bob이 David에게 준 권한(t=30)을 회수**하면:
- David는 **Chris에게서 받은 권한(t=50)**이 남아 있어 권한 자체는 유지된다.
- 하지만 David가 Ellen에게 준 권한(t=40)은 **t=50보다 앞서** 부여된 것이다. David는 t=30~t=50 사이에는 Bob에게서 받은 권한으로 Ellen에게 줬는데 그 근거가 사라진 것이므로 효력을 잃고, Ellen이 Jim에게 준 권한(t=70)도 따라서 사라진다. 이것이 **cascading revoke**.
- David → Frank (t=60)는 t=50 **이후**에 준 것이라 Chris에게서 받은 권한이 근거가 되어 남는다.

회수 후 그래프: Ann → Bob, Ann → Chris, Chris → David (t=50), David → Frank (t=60).

**확인 질문**: Chris → David가 t=25였다면(David → Ellen t=40보다 앞)? Bob이 t=30 권한을 회수해도 Ellen과 Jim의 권한은 남는다. David가 Ellen에게 준 시점(t=40)에 이미 Chris에게서 받은 권한(t=25)이 있었으니 그것이 근거가 되기 때문.

**규칙**: 어떤 권한 부여는 **그 시점에 부여자가 유효한 권한을 갖고 있었을 때만** 유효하다. 회수 후에도 부여 시점 기준으로 근거가 남아 있으면 살아남고, 근거가 없어지면 연쇄적으로 무효가 된다.

### Role-Based Access Control (RBAC) *(p.27)*
**DB RBAC**: 권한을 사용자 개별이 아니라 **role**에 붙이고, 사용자를 role에 지정해서 관리하는 접근 제어 방식.

- **관리 부담을 줄이고 보안을 향상**시킨다. 사용자가 바뀌어도 role 지정만 바꾸면 된다.
- DB RBAC가 제공해야 할 기능: role 생성/삭제, role의 permission 정의, 사용자를 role에 지정/취소.
- DB 사용자 분류
  - **Application owner**: 애플리케이션의 일부로서 **DB 객체를 소유**하는 end user.
  - **End user**: 애플리케이션을 통해 DB 객체를 조작하지만 **소유하지는 않는** 사용자.
  - **Administrator**: DB의 일부 또는 전체에 대한 **관리 책임**이 있는 사용자.

### Microsoft SQL Server의 Fixed Roles (Table 5.2) *(p.28)*
미리 정의된 role. 서버 단위와 DB 단위 두 계층.

**Fixed Server Roles**

| role | 하는 일 |
|---|---|
| `sysadmin` | 모든 작업 수행, 모든 DB 기능에 대한 완전한 통제 |
| `serveradmin` | 서버 전체 설정 옵션 지정, 서버 종료 |
| `setupadmin` | linked server와 startup procedure 관리 |
| `securityadmin` | 로그인과 `CREATE DATABASE` 권한 관리, 에러 로그 읽기, 비밀번호 변경 |
| `processadmin` | 실행 중인 프로세스 관리 |
| `dbcreator` | 데이터베이스 생성/변경/삭제 |
| `diskadmin` | 디스크 파일 관리 |
| `bulkadmin` | `BULK INSERT` 문 실행 |

**Fixed Database Roles**

| role | 하는 일 |
|---|---|
| `db_owner` | DB 안의 모든 권한 |
| `db_accessadmin` | 사용자 ID 추가/제거 |
| `db_datareader` | 모든 user table에서 데이터 select |
| `db_datawriter` | 모든 user table의 데이터 수정 |
| `db_ddladmin` | 모든 DDL 문 실행 |
| `db_securityadmin` | 모든 permission, 객체 소유권, role, role 멤버십 관리 |
| `db_backupoperator` | `DBCC`, `CHECKPOINT`, `BACKUP` 문 실행 |
| `db_denydatareader` | 데이터 select 권한을 **거부** |
| `db_denydatawriter` | 데이터 변경 권한을 **거부** |

`admin`, `owner`처럼 관리 중심인 role과 `datareader`/`datawriter`처럼 데이터 중심인 role로 나뉜다. 마지막 두 개(`deny...`)는 허용이 아니라 **거부**하는 role이라는 점이 특이하다.

**확인 질문 - SQLi 피해 줄이기**: 웹 애플리케이션이 `sa`로 접속했기 때문에 `exec cmdshell`까지 먹혔다. 웹 애플리케이션이 쓰는 DB 계정에 **필요한 최소 권한만** 주는 것(least privilege)이 답이다.
- `sa`/`sysadmin`으로 접속시키지 않는다. 그러면 SQLi 한 번에 DB 서버 전체와 OS 명령 실행까지 넘어간다.
- 로그인 페이지처럼 읽기만 하면 되는 기능이면 `db_datareader` 정도의 제한된 role만 준다. 필요하면 `db_datawriter`만 더하고, `db_denydatawriter`로 변경 권한을 명시적으로 막는 것도 방법.
- 서버 단위 role(`sysadmin`, `serveradmin` 등)은 애플리케이션 계정에 주지 않는다.
- SQLi가 뚫려도 **피해 범위**가 그 role의 권한 안으로 제한된다. SQLi 자체를 막는 건 parameterized query 같은 방어고, 이건 뚫렸을 때를 대비한 **다층 방어**.

---

## 5. Inference *(p.29~31)*

### 예시 진단 *(p.30, Figure 5.8)*
수업에서 쓴 예시 표(Name, Position, Salary, Department)의 숫자와 view 정의는 슬라이드 값이 아니라 설명용으로 임의로 만든 것이다. 노트에는 "(b) 두 view는 각각 민감하지 않게 설계됨, (c) 두 query 결과를 결합하면 Name, Position, Salary, Department가 복원됨"까지만 있고 정확한 view 정의는 확인되지 않는다.

- 임의 예시에서 두 view를 **(Position, Salary)**와 **(Name, Department)**로 잡았는데 공통 열이 없어서 단순 join은 불가능하다. 질문이 부실했다.
- join이 되려면 두 view에 **공통 속성**이 있어야 한다. 예를 들어 V1이 (Position, Salary), V2가 (Name, Position)이면 둘 다 Position을 가져 Position으로 연결된다. 어떤 Position의 사람이 한 명뿐이면 "Cathy의 Position → 그 Position의 Salary"로 이름과 급여가 대응된다. 여러 명이면 후보가 좁혀질 뿐이지만 여러 query를 조합하면 더 좁혀진다.
- 학생의 답 "두 view를 join해서 이름에 대응하는 급료를 뽑아낸다"는 inference의 핵심 방향이 맞다.

### Inference channel *(p.29, Figure 5.7)*
**Inference channel**: **비민감 데이터(Nonsensitive data)**와 **메타데이터(Metadata)**로부터 추론해서 **민감 데이터(Sensitive data)에 간접적으로 접근**하는 경로.

- **접근 제어**는 허가된 접근(Authorized access)만 통과시킨다. 그런데 사용자가 합법적으로 얻은 비민감 데이터와 메타데이터(예: 열 사이의 관계, 값의 분포)를 조합하면, 접근 제어를 거치지 않고도 민감 데이터에 닿는다. 이것이 **Unauthorized access**.
- 중요한 점: 각 query가 **개별적으로는 정책을 위반하지 않는다**. 그래서 접근 제어만으로는 못 막는다.

### 예시 (Figure 5.8) *(p.30)*
- (a) Employee table: Name, Position, Salary, Department, Dept. Manager
- (b) 각각은 민감하지 않게 설계된 두 view
- (c) 두 query 결과를 **결합**하면 Name, Position, Salary, Department가 모두 복원되어 **이름과 급여의 대응**이 드러난다.

### Inference Detection *(p.31)*
1. **설계 시 detection**: DB 구조를 바꾸거나 접근 제어 체계를 바꿔서 inference channel 자체를 없앤다. 단점은 접근 제어가 불필요하게 엄격해져서 **가용성(availability)이 떨어질 수 있다**는 것 (슬라이드에 명시).
2. **질의 시(query time) detection**: 한 query 또는 query 연속에서 inference channel 위반을 제거한다. 탐지되면 **query를 거부하거나 변경**한다.

두 접근 모두 **inference detection 알고리즘**이 필요하다. multilevel secure database와 statistical database에 대해서는 구체적인 탐지 기법이 진전되어 있다.

**확인 질문 - 트레이드오프**
- 설계 시 detection: 희생하는 건 **가용성**. channel이 생길 만한 조합을 미리 전부 막으려고 구조나 접근 제어를 빡빡하게 바꾸면 정당한 사용자도 필요한 데이터를 못 본다. 대신 운영 중 추가 부담은 없다.
- 질의 시 detection: 접근 제어를 느슨하게 둘 수 있어 정당한 사용을 덜 막는다. 감당할 건 **query마다 검사하는 비용과 복잡도**(한 query만이 아니라 그 사용자의 이전 query 이력과 조합해서 봐야 하므로 이력을 계속 추적). 정상 query가 막히는 오탐 위험도 있다. (이 부분은 슬라이드가 아니라 방식에서 끌어낸 추론.)

---

## 6. Database Encryption *(p.32~33)*

### 개요와 단점 *(p.32)*
**Database encryption**: DB에 저장된 데이터를 암호화해서, 다른 보호 계층이 뚫려도 데이터 내용을 못 읽게 하는 **마지막 방어선**.

- DB는 보통 조직의 **가장 가치 있는 정보 자원**이라 여러 보안 계층(firewall, authentication, 일반 access control, DB access control, database encryption)으로 보호된다. 암호화가 가장 안쪽이라 **last line of defense**.
- 적용 단위: **전체 DB, record level, attribute level, 개별 field level**.
- 단점
  - **Key management**: 권한 있는 사용자는 자기가 접근할 수 있는 데이터의 **복호화 키**를 가져야 한다. 사용자별로 키를 안전하게 나누고 관리하는 게 부담.
  - **Inflexibility**: 일부 또는 전체가 암호화되면 **record 검색이 어려워진다**. 암호문 상태에서는 `WHERE salary > 40000` 같은 조건 비교나 정렬을 서버가 못 하기 때문.

### Database Encryption Scheme (Figure 5.9) *(p.33)*

| 주체 | 역할 |
|---|---|
| **Data owner** | **통제된 공개**를 위해 데이터를 만들어내는 조직 |
| **User** | 시스템에 query를 던지는 사람 |
| **Client** | 사용자 query를 **암호화된 데이터에 대한 query로 변환**하는 frontend. Query Processor, Encrypt/Decrypt, Meta Data 보유 |
| **Server** | 데이터 소유자에게서 **암호화된 데이터를 받아 보관**하고 클라이언트에 제공하는 조직. Query Executor와 Encrypted database 보유 |

처리 순서:
1. **Original query**: User → Client
2. **Transformed query**: Client → Server (암호화된 데이터에 맞게 변환된 query)
3. **Encrypted result**: Server → Client
4. **Plaintext result**: Client → User (Client가 복호화)

요점: **Server는 평문을 보지 못한다.** 평문과 키는 Client 쪽에만 있고 Server는 암호문 위에서 변환된 query만 실행한다. 그래서 Server가 침해되어도 내용은 보호된다. 대신 Server가 암호문만 다루므로 Inflexibility 문제가 생기고, 그걸 줄이려고 Client가 Meta Data를 들고 query를 변환한다.

**확인 질문 - 마지막 방어선과 악의적 Server 관리자**
- 마지막 방어선: SQLi나 접근 제어가 뚫려 공격자가 DB 파일이나 테이블 내용을 손에 넣어도, 데이터가 암호문이면 **키가 없는 한** 읽을 수 없다. 앞 계층이 다 실패했을 때도 마지막으로 내용 자체를 지킨다.
- 악의적인 Server 관리자: 데이터가 암호문이라서, 그리고 **복호화 키가 Server에 없고 Client 쪽에만 있기 때문**에 안전하다. 암호문과 키가 따로 있어야 안전하고, 둘이 같은 곳에 있으면 의미가 없다.

---

## 참고: 다루지 않은 부분
- 슬라이드 p.34(Summary)의 요약 목차에는 Cloud computing 관련 항목(요소, 참조 아키텍처, 보안 위험과 대응책, 클라우드 데이터 보호, Security as a service)이 적혀 있으나, 이 PDF에는 해당 본문 슬라이드가 없어 수업에서 다루지 않았다.
