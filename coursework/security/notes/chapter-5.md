# Chapter 5: Database Security

> 이 슬라이드에는 쪽번호가 인쇄되어 있지 않아서, 아래 `p.N`은 PDF 파일의 페이지 순서(1부터 시작)를 가리킨다.
> 흐름: DB/DBMS 기본 → 관계형 DB 용어 → **SQL Injection** → (DB 접근 제어) → **Inference** → **Database encryption**. (요약 슬라이드에는 Cloud 항목도 적혀 있지만 본문 슬라이드는 없다.)

## 1. Database와 DBMS *(p.2~3)*

- **Database**: 하나 이상의 애플리케이션이 쓰기 위해 저장한 **구조화된 데이터 모음**
  - 데이터 항목들과 그룹 사이의 **관계**를 포함하고, 보안이 필요한 **민감한 데이터**를 담을 수 있다
- **DBMS(Database Management System)**: 데이터베이스를 구축·유지하는 프로그램 모음
  - 여러 사용자/애플리케이션에 **ad hoc query 기능** 제공
  - **Query language**가 데이터베이스에 대한 **통일된 인터페이스**를 제공

### DBMS 아키텍처 (Figure 5.1) *(p.3)*
- 구성 요소: User applications, User queries, **DDL processor**(data definition language), **DML and query language processor**(data manipulation language), Database utilities, **Transaction manager**, **File manager**, **Physical database**
- DBMS가 관리하는 테이블: **Database description tables**, **Authorization tables**, **Concurrent access tables**

## 2. 관계형 데이터베이스 (Relational Database) *(p.4~9)*

### 기본 개념 *(p.4)*
- 행(row)과 열(column)로 이루어진 **테이블**
  - 각 열은 특정 타입의 데이터를 담고, 각 행은 열마다 특정 값을 가진다
  - 이상적으로는 값이 모두 유일한 열이 하나 있어 그 행의 **식별자/키**가 된다
- 모든 테이블에 존재하는 **고유 식별자(key)**로 여러 테이블을 연결할 수 있다
- **관계형 query language**로 접근하며, 주어진 **조건에 맞는 데이터를 요청**할 수 있다

### 예시 모델 (Figure 5.2) *(p.5)*
- 전화 서비스 DB: PRIMARY TABLE(PhoneNumber, Last name, First name, address), CALLER ID TABLE, ADDITIONAL SUBSCRIBER TABLE(Has service? Y/N, List of subscribers), BILLING HISTORY TABLE(Date, Transaction type, Transaction amount), CURRENT BILL TABLE(Current date, Previous balance, Current charges, Date of last payment, Amount of last payment)
- **모든 테이블이 `PhoneNumber` 필드를 키로 서로 연결**된다

### 용어 (Table 5.1) *(p.6~7)*
| 일반 용어 | 대응 용어 |
|---|---|
| Relation | table / file |
| Tuple | row / record |
| Attribute | column / field |

- **Primary key**: 행을 유일하게 식별, 하나 이상의 column 이름으로 구성
- **Foreign key**: 한 테이블을 다른 테이블의 속성에 연결
- **View / virtual table**: 하나 이상의 테이블에서 **선택된 행과 열을 반환하는 query의 결과**

### 추상 모델 (Figure 5.3) *(p.8)*
- N개의 record(행) × M개의 attribute(열) `A1 … AM`, 각 칸 `x_ij`

### 예시 (Figure 5.4) *(p.9)*
- (a) Employee Table(Ename, Did, Salarycode, Eid, Ephone)과 Department Table(Did, Dname, Dacctno) 두 테이블. Employee의 `Did`는 **foreign key**, Department의 `Did`는 **primary key**
- (b) 두 테이블에서 파생된 **view** (Dname, Ename, Eid, Ephone만 보임)

### SQL *(p.10)*
- 관계형 DB에서 **스키마 정의, 데이터 조작, 질의**를 위한 표준화된 언어 (ANSI/ISO 표준의 유사한 여러 버전, 모두 기본 문법·의미는 동일)
- SQL로 할 수 있는 일: **테이블 생성, 데이터 삽입/삭제, view 생성, query문으로 데이터 조회**

## 3. SQL Injection Attacks (SQLi) *(p.11~23)*

### 개요 *(p.11)*
- 가장 흔하고 위험한 **네트워크 기반 보안 위협** 중 하나
- **웹 애플리케이션 페이지의 특성**을 악용하도록 설계됨
- 악의적인 SQL 명령을 **데이터베이스 서버로 전송**
- 가장 흔한 공격 목표는 **대량 데이터 추출(bulk extraction)**
- 환경에 따라 **데이터 수정/삭제, 임의의 OS 명령 실행, DoS 공격**에도 쓰일 수 있음

### 전형적인 SQLi 공격 (Figure 5.5) *(p.12)*
- 해커가 인터넷 → 라우터/스위치/방화벽 → **웹 서버 → 웹 애플리케이션 서버 → 데이터베이스 서버** 경로로 양방향 통신하며, 데이터베이스에서 **신용카드 데이터를 추출**하는 구성도

### 예제: 취약한 로그인 페이지 (ASP) *(p.13~17)*
```
set ok = execute( "SELECT * FROM Users
    WHERE user=' " & form("user") & " '
    AND pwd=' " & form("pwd") & " '" );
if not ok.EOF
    login success
else fail;
```
- 질문: "Is this exploitable?" — 사용자 입력을 **문자열로 그대로 이어 붙여** query를 만들기 때문에 취약
- **정상 입력** *(p.14)*: 사용자가 username/password 입력 → 웹 서버가 `SELECT * FROM Users WHERE user='me' AND pwd='1234'`를 DB로 전달 (Normal Query)
- **Bad input** *(p.15)*: `user = ' or 1=1 --` 이면 `WHERE user=' ' or 1=1 -- …`
  - `--`가 **뒤의 나머지 줄을 무시**하게 만든다
  - 조건이 항상 참 → `ok.EOF`가 항상 false → **로그인 성공**. 많은 사이트에 쉽게 로그인할 수 있다는 나쁜 소식
- **Even worse** *(p.16)*: `user = ' ; DROP TABLE Users --` → `WHERE user=' ' ; DROP TABLE Users …` → **Users 테이블 삭제**. 비슷하게 사용자 추가, 비밀번호 재설정 등도 가능
- **Even worse …** *(p.17)*: `' ; exec cmdshell 'net user badguy badpwd' / ADD --` → SQL 서버가 **"sa" 권한**으로 실행 중이면 공격자가 **DB 서버에 계정**을 얻는다

### Injection Technique *(p.18)*
- SQLi는 보통 **텍스트 문자열을 조기에 종료**시키고 **새 명령을 덧붙이는** 방식
- 삽입된 명령 뒤에 다른 문자열이 더 붙어 실행될 수 있으므로, 공격자는 주입한 문자열을 **주석 기호 `--`로 종료**
- 이후의 텍스트는 실행 시 무시된다

### SQLi 공격 경로 (Attack Avenues) *(p.19)*
- **User input**: 공격자가 정교하게 만든 사용자 입력으로 SQL 명령 주입
- **Server variables**: HTTP/네트워크 헤더 값을 **위조**하여, 헤더에 데이터를 직접 넣는 방식으로 취약점 악용
- **Second-order injection**: 시스템/DB에 **이미 존재하는 데이터**를 이용해 공격을 유발. query를 변조하는 입력이 사용자가 아니라 **시스템 내부**에서 온다
- **Cookies**: 쿠키를 변조해서, 애플리케이션 서버가 쿠키 내용으로 SQL query를 만들 때 query의 구조·기능이 바뀌게 한다
- **Physical user input**: 웹 요청 영역 밖에서 공격을 구성하는 사용자 입력을 적용

### SQLi 공격 유형 (Attack Types)

**(1) In-band attack** *(p.20)*
- SQL 코드를 주입하는 채널과 결과를 받는 채널이 **같다**. 가져온 데이터가 **애플리케이션 웹 페이지에 직접 표시**됨
- 종류:
  - **Tautology**: 하나 이상의 조건문에 코드를 주입해 **항상 참**이 되게 함
  - **End-of-line comment**: 특정 필드에 코드를 주입한 뒤, **줄 끝 주석**으로 뒤따르는 정상 코드를 무효화
  - **Piggybacked queries**: 의도된 query **뒤에 추가 query를 덧붙여**, 정상 요청에 편승해 공격

**(2) Inferential attack** *(p.21)*
- **실제 데이터 전송은 없지만**, 특정 요청을 보내고 웹사이트/DB 서버의 **반응을 관찰**해서 정보를 재구성
- 종류:
  - **Illegal/logically incorrect queries**: 백엔드 DB의 **종류와 구조에 관한 중요한 정보**를 얻게 해준다. 다른 공격을 위한 **예비 정보 수집 단계**로 간주됨
  - **Blind SQL injection**: DB에 **참/거짓 질문**을 던지고 **애플리케이션의 응답**으로 답을 판단. 시스템이 오류 정보를 표시하지 않을 만큼 충분히 안전해도 DB에 있는 데이터를 **추론**할 수 있게 해준다

**(3) Out-of-band attack** *(p.22)*
- 데이터를 **다른 채널**로 가져온다
- 정보 조회에 제한이 있지만, **DB 서버의 outbound 연결이 느슨할 때** 사용 가능

### SQLi Countermeasures *(p.23)*
- 세 가지 유형:
  - **Defensive coding**: 수동 방어적 코딩 관행(manual defensive coding practices), **Parameterized query insertion**, **SQL DOM**
  - **Detection**: **Signature based**, **Anomaly based**, **Code analysis**
  - **Run-time prevention**: 실행 중에 query가 **예상되는 query의 모델**에 부합하는지 검사

## 4. Database Access Control *(p.24~28)*

### 접근 제어 시스템이 결정하는 것 *(p.24)*
- 사용자가 **데이터베이스 전체에** 접근할 수 있는지, **일부에만** 접근할 수 있는지
- 사용자가 가진 **접근 권한(access rights)**: create, insert, delete, update, read, write
- 지원하는 관리 정책의 범위:
  - **Centralized administration**: 소수의 **특권 사용자**만 접근 권한을 부여/회수
  - **Ownership-based administration**: 테이블의 **생성자**가 그 테이블의 권한을 부여/회수
  - **Decentralized administration**: 테이블 소유자가 **다른 사용자에게 권한 부여/회수 권한까지 위임**하여, 그들이 다시 접근 권한을 주고 뺏을 수 있게 함

### SQL 기반 접근 정의 *(p.25)*
- 접근 권한 관리 명령 두 개:
  - **GRANT**: 하나 이상의 접근 권한을 부여하거나 사용자를 **role에 지정**
  - **REVOKE**: 접근 권한을 회수
- 일반적인 접근 권한: **Select, Insert, Update, Delete, References**

### Cascading authorizations *(p.26, Figure 5.6)*
- 권한을 부여받은 사용자가 다른 사용자에게 다시 권한을 부여하면 **권한 부여 그래프**가 만들어지고, 각 화살표에 부여 **시점 t**가 표시된다
  - 회수 전: Ann → Bob (t=10), Ann → Chris (t=20), Bob → David (t=30), David → Ellen (t=40), Chris → David (t=50), David → Frank (t=60), Ellen → Jim (t=70)
- "**Bob Revokes Privilege from David**": Bob이 David에게 준 권한(t=30)을 회수
  - David는 **Chris로부터 받은 권한(t=50)**이 남아 있어 권한 자체는 유지된다
  - 하지만 David가 Ellen에게 준 권한(t=40)은 David가 Chris에게서 권한을 받은 시점(t=50)**보다 앞서** 부여된 것이라 효력을 잃고, Ellen이 Jim에게 준 권한(t=70)도 함께 사라진다 (**cascading revoke**)
  - David → Frank (t=60)는 t=50 이후에 부여된 것이라 남는다
  - 회수 후 그래프: Ann → Bob, Ann → Chris, Chris → David (t=50), David → Frank (t=60)

### Role-Based Access Control (RBAC) *(p.27)*
- RBAC는 **관리 부담을 줄이고 보안을 향상**시킴
- DB RBAC가 제공해야 할 기능: **role 생성/삭제**, **role의 permission 정의**, **사용자를 role에 지정/취소**
- DB 사용자 분류:
  - **Application owner**: 애플리케이션의 일부로서 **데이터베이스 객체를 소유**하는 end user
  - **End user**: 특정 애플리케이션을 통해 DB 객체를 조작하지만 **객체를 소유하지는 않는** 사용자
  - **Administrator**: DB의 일부 또는 전체에 대한 **관리 책임**을 가진 사용자

### Microsoft SQL Server의 Fixed Roles (Table 5.2) *(p.28)*
- **Fixed Server Roles**
  - `sysadmin`: SQL Server의 모든 작업 수행, 모든 DB 기능에 대한 완전한 통제
  - `serveradmin`: 서버 전체 설정 옵션 지정, 서버 종료
  - `setupadmin`: linked server와 startup procedure 관리
  - `securityadmin`: 로그인과 `CREATE DATABASE` 권한 관리, 에러 로그 읽기, 비밀번호 변경
  - `processadmin`: SQL Server에서 실행 중인 프로세스 관리
  - `dbcreator`: 데이터베이스 생성/변경/삭제
  - `diskadmin`: 디스크 파일 관리
  - `bulkadmin`: `BULK INSERT` 문 실행
- **Fixed Database Roles**
  - `db_owner`: DB 안의 모든 권한
  - `db_accessadmin`: 사용자 ID 추가/제거
  - `db_datareader`: DB의 모든 user table에서 데이터 select
  - `db_datawriter`: 모든 user table의 데이터 수정
  - `db_ddladmin`: 모든 DDL 문 실행
  - `db_securityadmin`: 모든 permission, 객체 소유권, role, role 멤버십 관리
  - `db_backupoperator`: `DBCC`, `CHECKPOINT`, `BACKUP` 문 실행
  - `db_denydatareader`: DB에서 데이터 select 권한을 **거부**
  - `db_denydatawriter`: DB의 데이터 변경 권한을 **거부**

## 5. Inference *(p.29~31)*

### Inference channel *(p.29, Figure 5.7)*
- **비민감 데이터(Nonsensitive data)**와 **메타데이터(Metadata)**로부터 추론을 통해 **민감 데이터(Sensitive data)**에 **간접적으로 접근**하는 경로
- 접근 제어(Access Control)는 **Authorized access**만 허용하지만, 추론 채널을 통하면 **Unauthorized access**가 가능해진다

### 예시 (Figure 5.8) *(p.30)*
- (a) Employee table: Name, Position, Salary, Department, Dept. Manager (Andy/Calvin/Cathy는 strip 부서, Dennis/Herman/Ziggy는 panel 부서 등)
- (b) 두 개의 view: (Position, Salary)와 (Name, Department)처럼 각각은 **민감하지 않게** 설계됨
- (c) 두 query 결과를 **결합**하면 Name, Position, Salary, Department가 모두 복원되어 **민감한 정보(이름과 급여의 대응)가 드러난다**

### Inference Detection *(p.31)*
- 두 가지 접근
  1. **설계 시 inference detection**: DB 구조를 바꾸거나 **접근 제어 체계를 바꿔** inference channel 자체를 제거. 불필요하게 접근 제어가 엄격해져 **가용성(availability)이 떨어질 수 있다**
  2. **질의 시(query time) inference detection**: 하나의 query 또는 query 연속에서 inference channel 위반을 제거. **채널이 탐지되면 query를 거부하거나 변경**
- 두 접근 모두 **inference detection 알고리즘**이 필요
- multilevel secure database와 statistical database에 대해서는 구체적인 탐지 기법이 진전되어 있음

## 6. Database Encryption *(p.32~33)*

### 개요와 단점 *(p.32)*
- DB는 보통 조직의 **가장 가치 있는 정보 자원**이라 **여러 보안 계층**(firewall, authentication, 일반 access control, DB access control, database encryption)으로 보호된다
- 그 중 **암호화는 DB 보안의 마지막 방어선(last line of defense)**
- 적용 단위: **전체 DB, record level, attribute level, 개별 field level**
- 단점:
  - **Key management**: 권한 있는 사용자는 자기가 접근할 수 있는 데이터의 **복호화 키**에 접근할 수 있어야 함
  - **Inflexibility**: DB의 일부 또는 전체가 암호화되면 **record 검색이 더 어려워짐**

### Database Encryption Scheme (Figure 5.9) *(p.33)*
- 4개 주체:
  - **Data owner**: **통제된 공개**를 위해 데이터를 만들어내는 조직
  - **User**: 시스템에 query를 던지는 사람
  - **Client**: 사용자 query를 **암호화된 데이터에 대한 query로 변환**하는 frontend (Query Processor, Encrypt/Decrypt, Meta Data 보유)
  - **Server**: 데이터 소유자로부터 **암호화된 데이터를 받아 클라이언트에게 제공**하는 조직 (Query Executor, Encrypted database)
- 처리 순서: ① Original query (User → Client) → ② **Transformed query** (Client → Server) → ③ **Encrypted result** (Server → Client) → ④ **Plaintext result** (Client → User)

## 7. Summary *(p.34)*
- 슬라이드의 요약 목차: The need for database security / DBMS / Relational databases(요소, SQL) / SQL injection attacks(전형적 공격, injection technique, 공격 경로와 유형, 대응책) / Inference / Database access control(SQL 기반 접근 정의, cascading authorizations, RBAC) / Database encryption / **Cloud computing**(요소, 참조 아키텍처) / Cloud security risks and countermeasures / Data protection in the cloud / Cloud security as a service
- 이 PDF에는 Cloud 관련 본문 슬라이드는 없고 목차에만 언급된다
