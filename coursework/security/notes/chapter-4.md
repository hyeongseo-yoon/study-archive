# Chapter 4: Access Control

*Hanyang University, Division of Computer Science and Engineering*

## 1. Access Control 개념 *(슬라이드 p.3~7)*

### Authentication vs Authorization *(슬라이드 p.3)*
- **Authentication**: Who are you? (신원 확인)
- **Authorization (access control)**: What are you allowed to do — 정책(policy)에 초점
- **Enforcement mechanism**: 그 정책이 어떻게 구현/강제되는지

### Access Control과 다른 보안 기능의 관계 (Figure 4.1) *(슬라이드 p.5)*
User → **Authentication function** → **Access control function** → System resources. Security administrator는 Authorization database를 관리하고, Access control function이 이 DB를 참조해 접근을 결정. 전체 과정은 **Auditing**으로 감시됨.

### Subjects, Objects, Access Rights *(슬라이드 p.6)*
- **Subject**: 객체(object)에 접근할 수 있는 개체(entity). 세 클래스로 분류 — Owner, Group, World
- **Object**: 접근이 통제되는 자원(resource). 정보를 담거나 받는 개체
- **Access right**: subject가 object에 접근하는 방식을 정의. Read/Write/Execute/Delete/Create/Search 등을 포함할 수 있음

### Access Control Policies 개요 *(슬라이드 p.7)*
- **DAC (Discretionary Access Control)**: requestor의 신원과, requestor가 할 수 있는(또는 할 수 없는) 일을 명시한 access rule(authorization)에 기반해 접근을 통제
- **MAC (Mandatory Access Control)**: security label과 security clearance를 비교해 접근을 통제
- **RBAC (Role-based Access Control)**: 사용자가 시스템 내에서 가지는 role과, 특정 role의 사용자에게 허용된 접근을 명시한 규칙에 기반해 통제
- **ABAC (Attribute-based Access Control)**: 사용자, 접근 대상 자원, 현재 환경 조건의 속성(attribute)에 기반해 통제

---

## 2. Mandatory Access Control (MAC) *(슬라이드 p.8~20)*

### 개요 *(슬라이드 p.8)*
security label과 security clearance 비교로 접근 통제. 4가지 대표 모델: **Bell-LaPadula model**, **BiBa model**, **Clark-Wilson model**, **Chinese-wall model**

### Bell-LaPadula (BLP) 모델 *(슬라이드 p.9~11)*
- DoD가 TCSEC에서 multilevel security와 MAC 지원을 위해 정의. 경직되고(inflexible) 형식적(formal)인 모델 *(p.9)*
- 목적: **Confidentiality**(정보수집 방지) — 정보는 아래 보안단계에서 위로만 흐름(예: 사병→장교→사령관) *(p.9)*
- 장점: 기밀성 유지 / 단점: **Integrity 보장 못함** — 하위 등급이 write로 수정·삭제·거짓정보 배포가 가능해질 수 있음 *(p.9)*
- **형식 규칙** *(p.10)*: 객체 o와 주체 s에 각각 보안단계 L(o), L(s) 할당 (Top secret > secret > confidential > restricted > uncleared)
  - **ss-property (Simple Security Property)**: 주체는 자신과 같거나 낮은 보안단계의 객체만 읽을 수 있음 — L(o) ≤ L(s), 즉 **No read up**
  - **\*-property (Star Property)**: 주체는 자신과 같거나 높은 보안단계의 객체만 쓸 수 있음 — L(o) ≥ L(s), 즉 **No write down**
- 그림 요약 *(p.11)*: No read up / No write down을 통해 Simple Confidentiality Rule(read only)과 Star Confidentiality Rule(write only)을 시각화

### BiBa 모델 *(슬라이드 p.12~14)*
- 데이터 **무결성(integrity)** 보장을 위해 설계됨 — 정보를 수정되지 않은 채로 아래 단계로 전달하는 것이 목적(예: 군대 작전명령 하달, 뉴스 전파) *(p.12)*
- 단점: confidentiality는 보장하지 않음 *(p.12)*
- **형식 규칙** *(p.13)*: 객체 o와 주체 s에 무결성 단계 I(o), I(s) 할당
  - **si-property (Simple Integrity Property)**: 주체는 자신과 같거나 높은 무결성 단계의 객체만 읽을 수 있음 — I(o) ≥ I(s), **No read down** (아니면 신뢰할 수 없는 자료가 수집·상부 전달됨)
  - **\*-integrity property (Star Integrity Property)**: 주체는 자신과 같거나 낮은 무결성 단계의 객체만 쓸 수 있음 — I(o) ≤ I(s), **No write up** (아니면 신뢰할 수 없는 자료가 상부로 전달됨)
  - (invocation property도 존재)
- 그림 예시 *(p.14)*: New York Times(상위, Fact) / The Inquirer(하위, Rumor) 비유로 Simple Integrity Axiom(상위 read만 가능, 하위 read 금지)과 \*-Integrity Axiom(하위 write만 가능, 상위 write 금지)을 설명

### Clark-Wilson 모델 *(슬라이드 p.15~16)*
- 보다 현실적인 MAC 모델. 데이터 **무결성** 유지가 목표 *(p.15)*
- **업무 분리(separation of duty)** 원칙: 사용자 간 업무를 확실히 분리 — 예: 송금, 송금 검증, 계정처리 담당자를 각각 다르게 둠 *(p.15)*
- 객체에 대한 **직접 접근을 막고**, **Well-formed transaction**을 통해서만 객체에 접근하도록 함 *(p.15)*
- 예시: 송금 업무를 송금/검증/계정처리 3단계로 분리하는 Well-formed Transaction을 정의하고 각 담당자를 다르게 둠 (한 담당자가 전 과정을 맡으면 부정송금이 가능해짐) *(p.16)*
- Formal description은 생략. 단점: 처리과정이 복잡해지고 느려져 시스템 오류/정지 확률 증가 가능 *(p.16)*

### Chinese-Wall (Brewer-Nash, 만리장성) 모델 *(슬라이드 p.17)*
이익 충돌(conflict of interest) 회피를 위한 모델. 직무 분리를 접근 통제에 반영한 개념으로, **MAC과 DAC을 함께 이용**하는 형태 (자세한 이론은 생략)

### MAC 종합 평가 *(슬라이드 p.20)*
- 장점: 간단한 원칙으로 대규모 유저/데이터 관리 가능
- 단점: **not so flexible** (높은 등급 유저는 모든 것을 할 수 있는 반면 최하위 유저는 할 수 있는 게 거의 없음), 현실적 문제(등급 변경 시 처리, write의 생성/수정/삭제 포함 여부, directory·file의 삭제/read 의미 등)에 대한 대처 방안 부족

---

## 3. Discretionary Access Control (DAC) *(슬라이드 p.21~28)*

### 정의 *(슬라이드 p.21)*
한 entity가 다른 entity에게 특정 resource에 대한 접근을 허용할 수 있는 scheme. 흔히 **access matrix**로 구현 — 한 차원은 접근을 시도할 수 있는 subject들, 다른 차원은 접근 대상이 되는 object들. 행렬의 각 entry는 특정 subject가 특정 object에 대해 갖는 access right을 나타냄

### Access Matrix 예시 (Figure 4.2) *(슬라이드 p.22~23)*
- (a) Access matrix: User A/B/C × File 1~4에 대한 Own/Read/Write 권한을 표로 표현
- (b) **Access control lists (ACL)**: File 기준으로 어떤 subject가 어떤 권한을 갖는지 연결리스트로 표현
- (c) **Capability lists**: User 기준으로 어떤 object에 어떤 권한을 갖는지 연결리스트로 표현
- Table 4.1: Figure 4.2의 access matrix를 (Subject, Access Mode, Object) 3열 테이블로 풀어쓴 Authorization Table *(p.24)*

### 확장된 Access Control 구조 *(슬라이드 p.25~27)*
- **Figure 4.3 Extended Access Control Matrix** *(p.25)*: subject 뿐 아니라 process, disk drive까지 object로 포함하고, control/owner/read/write/wakeup/seek/execute/stop 등 다양한 access right과 copy flag(\*)를 표현
- **Table 4.2 Access Control System Commands (R1~R8)** *(p.26)*: transfer, grant, delete, read, create object, destroy object, create subject, destroy subject 각각에 대한 Command / Authorization 조건 / Operation을 정의한 규칙 집합
- **Figure 4.4 Access Control 함수의 구성** *(p.27)*: Subject의 요청(read F, wakeup P, grant/delete 등)이 Access control mechanism(File system, Process manager, Access matrix monitor 등 System intervention 영역)을 거쳐 Object(Files, Segments&pages, Processes 등)에 도달하는 구조. Access matrix monitor는 access matrix를 read/write하며 권한을 판단

### Protection Domains *(슬라이드 p.28)*
- 사용자가 아니라 machine, process, module이 실제로 존재하는 단위
- Protection domain은 namespace(예: file system view), userid/group id, 보유 object 집합(capability list), 보유 권한 집합(permissions)을 가질 수 있는 추상 객체
- 보호는 language type system, hardware MMU(process, virtual machine), compiler(SFI) 등으로 강제됨 (이 수업의 주요 관심사는 아님)

### DAC 장단점 *(슬라이드 p.31)*
- 장점: **Flexibility** — 각 객체·주체에 맞게 개별 설정 가능
- 단점: 보안성 위배를 체크하기 어려움, 자료구조가 비대해지며 성능 저하

---

## 4. UNIX Access Control *(슬라이드 p.30~35)*

### UNIX 자원의 종류 *(슬라이드 p.30)*
- **Files**: device, IPC(domain socket, named pipe, mmap shared memory) 포함
- **Network**: TCP/UDP port address space
- **Other**: Sys V IPC는 자체 namespace를 가짐, kernel module을 로드하는 능력

### UNIX File Access Control — inode 구조 *(슬라이드 p.31~32)*
- UNIX 파일은 **inode(index node)**로 관리됨: 특정 파일에 필요한 핵심 정보를 담은 제어구조. 여러 파일 이름이 하나의 inode를 가리킬 수 있지만, active inode는 정확히 하나의 파일에 대응. 파일 속성·권한·제어정보가 inode에 저장됨. 디스크의 inode table(inode list)에 모든 파일의 inode가 있고, 파일이 열리면 그 inode가 메모리 상주 inode table로 올라옴
- 디렉토리는 계층적 트리 구조로, 파일/다른 디렉토리를 포함할 수 있으며 파일 이름과 대응 inode에 대한 포인터를 담음
- 각 사용자는 고유 user ID를 가지며 하나의 primary group(group ID)에 속하고 특정 그룹에 소속. **12개의 protection bit**로 owner/group/other 각각에 대한 read/write/execute 권한을 지정 (owner ID, group ID, protection bit는 inode의 일부) *(p.32)*

### Traditional UNIX File Access Control — 프로세스 신원과 권한 *(슬라이드 p.33)*
- 각 프로세스는 access control 결정에 쓰이는 신원 집합을 가짐: uid(real user ID)/euid(effective user ID), gid(real group ID)/egid(effective group ID)
- **SetUID / SetGID**: 시스템이 실제 사용자 권한에 더해 파일 owner/group의 권한을 일시적으로 사용하게 함 — 일반적으로 접근 불가능한 파일/자원에 권한 있는 프로그램이 접근하도록 함
- **Sticky bit**: 디렉토리에 적용되면 그 디렉토리 내 파일을 owner만 rename/move/delete 가능하도록 제한
- **Superuser**: 일반적인 access control 제약이 면제되고 시스템 전역 접근 권한을 가짐

### UNIX의 Access Control Lists (ACL) *(슬라이드 p.34~35)*
- FreeBSD, OpenBSD, Linux, Solaris 등 현대 UNIX 시스템이 ACL을 지원
- **FreeBSD**: `setfacl` 명령으로 UNIX user ID/group 목록을 지정. 임의 개수의 user/group을 파일에 연결 가능, read/write/execute 권한 비트 사용, 파일이 ACL을 꼭 가질 필요는 없음, 확장 ACL 보유 여부를 나타내는 추가 protection bit 존재
- 프로세스가 파일 시스템 객체에 접근 요청 시 두 단계: (1) 가장 적합한 ACL 선택 (2) 매칭된 entry가 충분한 권한을 포함하는지 확인
- **Figure 4.5**: 전통적 minimal ACL(owner/group/other 각 rw-/r--/---)과, `user:joe:rw-`처럼 특정 사용자를 masked entry로 추가하는 Extended ACL을 비교하는 그림

---

## 5. Role-Based Access Control (RBAC) *(슬라이드 p.36~41)*

### 개념 (Figure 4.6, 4.7) *(슬라이드 p.36~37)*
Users → Roles → Resources 구조로 접근을 매개함 (예: 여러 User가 Role 1/2/3 중 하나 이상에 매핑되고, 각 Role이 특정 Resource에 대한 접근을 가짐). Figure 4.7은 User×Role 배정 행렬과, Role×Object(파일·프로세스·디스크 등) access control matrix를 함께 보여줌 — RBAC 역시 access matrix로 표현 가능하되 subject가 user 대신 role이 됨

### RBAC 모델 계열 (Figure 4.8, Table 4.3) *(슬라이드 p.38~39)*
- **RBAC₀ (Base model)**: User Assignment(UA)로 Users↔Roles, Permission Assignment(PA)로 Roles↔Permissions(Operations+Objects) 연결, Sessions를 통해 user_sessions/session_roles 관리
- **RBAC₁ (Role hierarchies)**: RBAC₀ + Role Hierarchy(RH) 추가
- **RBAC₂ (Constraints)**: RBAC₀ + 제약조건 추가
- **RBAC₃ (Consolidated model)**: RBAC₁ + RBAC₂를 모두 포함
- Table 4.3: RBAC₀(Hierarchies:No, Constraints:No) / RBAC₁(Yes,No) / RBAC₂(No,Yes) / RBAC₃(Yes,Yes)

### Role Hierarchy 예시 (Figure 4.9) *(슬라이드 p.40)*
Director → Project Lead 1/2 → Production/Quality Engineer 1/2 → Engineer 1/2 → Engineering Dept 순의 계층 구조로, 상위 role이 하위 role의 권한을 상속하는 형태

### RBAC Constraints *(슬라이드 p.41)*
조직의 관리·보안 정책 특성에 RBAC을 맞추기 위한 수단으로, role 간의 관계나 role 관련 조건을 정의:
- **Mutually exclusive roles**: 한 사용자는 집합 내 하나의 role에만 배정 가능(세션 중이든 정적으로든), 하나의 permission은 집합 내 하나의 role에만 부여 가능
- **Cardinality**: role에 대해 허용되는 최대 인원 수를 설정
- **Prerequisite roles**: 사용자가 이미 다른 특정 role에 배정되어 있어야만 해당 role에 배정될 수 있도록 제한

---

## 6. Attribute-Based Access Control (ABAC) *(슬라이드 p.42~45)*

### 개요 *(슬라이드 p.42)*
- 자원(resource)과 주체(subject) 양쪽의 속성(property)에 대한 조건을 표현하는 authorization을 정의할 수 있음
- 강점은 **유연성(flexibility)과 표현력(expressive power)**
- 실제 시스템 도입의 주요 걸림돌: 매 접근마다 resource/user 속성에 대한 predicate를 평가하는 성능 영향에 대한 우려
- Web service들이 **XACML(eXtensible Access Control Markup Language)** 도입을 통해 선도적으로 기술을 개척해옴
- cloud 서비스에 이 모델을 적용하는 것에 대한 관심이 상당함

### ABAC 모델의 속성 종류 *(슬라이드 p.43)*
- **Subject attributes**: 정보 흐름을 일으키거나 시스템 상태를 바꾸는 능동적 개체(subject)의 신원과 특성을 정의
- **Object attributes**: 정보를 담거나 받는 수동적 개체(object/resource)의 속성 — access control 결정에 활용 가능
- **Environment attributes**: 정보 접근이 일어나는 운영적·기술적·상황적 환경/맥락을 기술 — 지금까지 대부분의 access control 정책에서 크게 무시되어온 속성

### ABAC의 특징 *(슬라이드 p.44)*
- entity·operation·환경(environment)의 속성에 대해 규칙(rule)을 평가해 object에 대한 접근을 통제한다는 점에서 구별됨
- subject 속성, object 속성, 그리고 주어진 환경에서 subject-object 속성 조합에 허용되는 operation을 정의하는 formal relationship(access control rule)의 평가에 의존
- 시스템은 DAC, RBAC, MAC 개념을 모두 강제(enforce)할 수 있음
- 무제한 개수의 속성을 조합할 수 있음

### Figure 4.10 Simple ABAC Scenario *(슬라이드 p.45)*
Subject(①)가 접근을 요청하면, Access Control Mechanism이 Access Control Policy(②a), Subject Attributes(Name/Clearance/Affiliation 등, ②b), Object Attributes(Type/Owner/Classification 등, ②c), Environmental Conditions(②d)를 종합해 Rule을 평가(Decision)하고 Enforce하여 Object에 대한 접근(③)을 허용/거부함

---

## 핵심 요약

- **Authentication(누구인지) vs Authorization/Access control(무엇을 할 수 있는지)**, subject·object·access right이 access control의 기본 구성요소
- **MAC**: security label/clearance 비교로 통제, 유연성은 낮지만 강력함. **BLP**(confidentiality, no read up/no write down) vs **BiBa**(integrity, no read down/no write up)가 대칭적 대비를 이룸. **Clark-Wilson**(well-formed transaction + 업무분리)과 **Chinese-wall**(MAC+DAC 결합, 이익충돌 방지)은 더 현실적인 모델
- **DAC**: access matrix(ACL/capability list로 구현)로 유연하게 권한 설정, 단 관리·성능 부담 존재. UNIX는 12-bit 권한(owner/group/other)과 setUID/setGID/sticky bit/superuser, 그리고 현대 시스템에서는 ACL로 DAC을 구현
- **RBAC**: user-role-permission의 3단 매개 구조. RBAC₀(base)~RBAC₃(hierarchy+constraint 모두 포함)로 확장되며, role hierarchy로 권한 상속, constraint(mutually exclusive/cardinality/prerequisite)로 정책 세밀화
- **ABAC**: subject/object/environment 속성 기반 rule 평가로 가장 유연하고 표현력이 높으며, DAC/RBAC/MAC을 모두 포괄할 수 있음 — 다만 성능이 과제
