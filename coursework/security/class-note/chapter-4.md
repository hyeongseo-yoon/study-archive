# Chapter 4 수업노트

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*(수업일: 2026-10-23, 참조 노트: `notes/chapter-4.md`)*

## 0. 선수 지식 복습

- **Authentication**: 사용자가 주장하는 신원이 진짜인지 확인하는 것 ("너 누구야?")
- **Authorization**: 인증된 사용자가 어떤 자원에 무엇을 해도 되는지 정책(policy)에 따라 결정하는 것 ("너 뭘 할 수 있어?")
- `-rwxr-xr--` 읽는 법: 맨 앞 `-`는 파일 종류(일반 파일 `-`, 디렉토리 `d`). 나머지 9칸은 3칸씩 owner `rwx`(읽기·쓰기·실행 모두) / group `r-x`(읽기·실행, 쓰기 불가) / other `r--`(읽기만).
- 기밀성(허용된 사람만 볼 수 있게)과 무결성(승인되지 않은 방식으로 위조·변조되지 않음)의 구분은 뒤의 BLP vs BiBa를 가르는 핵심.

---

## 1. Access Control 개념 *(p.3~7)*

**Access control**: 인증된 주체(subject)가 어떤 객체(object)에 어떤 방식(access right)으로 접근할 수 있는지를 정책으로 정하고, 그 정책을 시스템이 강제하는 것.

**전체 흐름 (Figure 4.1, p.5)**: User → Authentication function → Access control function → System resources. Access control function은 Authorization database를 보고 허용 여부를 결정하고, 이 DB는 security administrator가 관리. 전체 과정은 Auditing이 감시.

- Authorization은 **정책(policy)** 에 초점. 누가 무엇을 할 수 있는지를 정하는 쪽.
- Enforcement mechanism은 그 정책을 **실제로 어떻게 구현하고 강제하는지**.

**기본 구성요소 (p.6)**
- **Subject**: 객체에 접근하는 능동적 개체. Owner, Group, World 세 클래스 (`rwx` 세 묶음이 이 분류).
- **Object**: 접근이 통제되는 자원. 파일처럼 정보를 담거나 받는 개체.
- **Access right**: subject가 object에 접근하는 방식. Read, Write, Execute, Delete, Create, Search 등.

**정책 4가지 개요 (p.7)**
- **DAC**: 요청자의 신원과 "이 사람은 이걸 해도 된다/안 된다"는 규칙(authorization) 기준
- **MAC**: 보안 라벨(security label)과 사용자의 허가(clearance) 비교
- **RBAC**: 사용자의 역할(role)과 "그 역할에 허용된 접근" 규칙 기준
- **ABAC**: 사용자, 자원, 환경의 속성(attribute) 기준

**Q&A**
- `chmod`로 친구에게 파일을 열어주는 건 DAC. 개요만으로는 네 정책이 비슷해 보이는데, 구분하는 핵심은 **누가 권한을 결정하느냐** (p.21의 DAC 정의).
  - DAC: 자원의 주인(owner)이 재량(discretion)껏 다른 사람에게 접근을 허용.
  - MAC: 주인의 의사와 상관없이 시스템 정책이 등급 비교로 강제. 주인이 열어주고 싶어도 등급이 안 맞으면 못 열어.

---

## 2. Mandatory Access Control (MAC) *(p.8~20)*

**MAC**: 객체에는 보안 라벨(security label)이, 주체에는 허가 등급(security clearance)이 붙어 있고, 시스템이 둘을 비교해 접근을 강제로 통제하는 방식. 대표 모델 4개: **Bell-LaPadula**, **BiBa**, **Clark-Wilson**, **Chinese-Wall**.

### 2-1. Bell-LaPadula (BLP) *(p.9~11)*

- DoD가 TCSEC에서 multilevel security와 MAC을 지원하려고 정의. 경직되고 형식적(formal)인 모델.
- 목적은 **기밀성(confidentiality)**. 정보가 낮은 등급에서 높은 등급으로만 흐르게 함 (사병 → 장교 → 사령관).
- 단점: **무결성을 보장하지 못함**. 낮은 등급이 write로 정보를 수정·삭제하거나 거짓 정보를 퍼뜨릴 수 있음.

**형식 규칙 (p.10)**: 객체 o와 주체 s에 보안 단계 L(o), L(s) 부여. Top secret > secret > confidential > restricted > uncleared.
- **ss-property (Simple Security)**: 주체는 자기와 같거나 **낮은** 단계의 객체만 읽을 수 있음. L(o) ≤ L(s), **No read up**.
- **\*-property (Star)**: 주체는 자기와 같거나 **높은** 단계의 객체만 쓸 수 있음. L(o) ≥ L(s), **No write down**.

**Q&A: 왜 "아래로 쓰기(write down)"까지 막아야 하나?**
- 철수는 Top secret 허가의 장교, 영희는 restricted 사병. `notice.txt`는 restricted 파일이라 영희가 읽을 수 있음.
- \*-property가 없어서 철수가 `notice.txt`에 극비 작전 내용을 쓸 수 있다고 가정. 파일 등급은 restricted 그대로인데 내용은 극비. 영희가 읽으면 극비를 알게 됨 → 기밀성 붕괴.
- 이때 영희가 한 행동(restricted 파일 읽기)은 ss-property가 **허용하는** 행동. 규칙을 하나도 위반하지 않았는데 기밀성이 깨짐.
- 즉 ss-property는 위로 읽는 길만 막고, **정보가 파일을 통해 아래로 새는 길**은 못 막음. 그래서 \*-property(No write down)가 따로 필요. 두 규칙이 합쳐져서 정보가 낮은 등급 → 높은 등급으로만 흐름.
- p.11 그림: No read up / No write down을 Simple Confidentiality Rule(read only), Star Confidentiality Rule(write only)로 시각화.

### 2-2. BiBa *(p.12~14)*

**BiBa**: BLP의 구조를 뒤집어서, 기밀성 대신 데이터 **무결성(integrity)** 을 지키는 모델.
- 목적: 정보를 **변조 없이 아래 단계로 전달** (군대 작전명령 하달, 뉴스 전파).
- 단점: 기밀성은 보장하지 않음.
- 객체와 주체에 무결성 단계 I(o), I(s) 부여.

**Q&A (p.14 비유)**: 위쪽은 New York Times (검증된 사실, 높은 무결성), 아래쪽은 The Inquirer (소문, 낮은 무결성).
- NYT 기자가 Inquirer의 소문을 읽고 기사에 쓰면 잘못된 정보를 믿고 퍼뜨릴 수 있음 → 상위 주체가 하위 객체를 **읽으면 안 됨**.
- Inquirer 기자가 NYT 지면에 직접 쓸 수 있으면 똑같이 오염 → 하위 주체가 상위 객체에 **쓰면 안 됨**.

**형식 규칙 (p.13)**
- **si-property (Simple Integrity)**: 주체는 자기와 같거나 **높은** 무결성 단계의 객체만 읽을 수 있음. I(o) ≥ I(s), **No read down**. (신뢰할 수 없는 자료가 수집되어 위로 올라가는 것을 막음)
- **\*-integrity property (Star Integrity)**: 주체는 자기와 같거나 **낮은** 무결성 단계의 객체만 쓸 수 있음. I(o) ≤ I(s), **No write up**. (신뢰할 수 없는 자료가 상위 객체를 오염시키는 것을 막음)
- invocation property도 있다고 슬라이드에 언급만 됨.

**BLP와 BiBa의 대칭**

| | 목적 | Read | Write |
|---|---|---|---|
| BLP | 기밀성 | No read up | No write down |
| BiBa | 무결성 | No read down | No write up |

정보가 흐르는 방향을 어느 쪽으로 막느냐가 목적을 결정.

**Q&A: BLP와 BiBa를 한 시스템에 동시에 쓰면?** 읽기와 쓰기가 모두 같은 등급 안에서만 가능해짐. 등급끼리 서로 완전히 고립된 섬이 되어 정보 전달이 안 되므로 현실적으로 쓰기 어려움.

### 2-3. Clark-Wilson *(p.15~16)*

**Clark-Wilson**: 사용자가 데이터에 직접 접근하지 못하게 막고, 미리 정의된 well-formed transaction을 통해서만 접근하게 하며, 업무를 여러 사람에게 분리해서 무결성을 지키는 모델. BLP·BiBa가 등급으로 막았다면 이 모델은 **절차**로 막음.

- **업무 분리(separation of duty)**: 사용자 간 업무를 확실히 나누는 원칙.
- **Well-formed transaction**: 객체에 대한 직접 접근 대신 쓰는, 정해진 절차를 거치는 접근 방식.
- 예시 (p.16): 송금 업무를 ① 송금 요청 처리 ② 송금 검증 ③ 계정 처리로 쪼개 각각 다른 담당자에게 맡기고, 담당자는 계좌 데이터를 직접 만지지 못하고 transaction으로만 처리.
- 단점: 처리 과정이 복잡하고 느려져 시스템 오류·정지 확률이 올라갈 수 있음. Formal description은 생략.

**Q&A: 한 담당자가 3과정을 다 맡으면?** 세 과정이 모두 엮여 있어서 한 사람이 3과정을 같이 위조하면 막을 수 없음. 분리하면 담당자들이 다 같이 위조(공모, collusion)하지 않는 한 막을 수 있음. 공모까지는 이 모델로 막지 못함.

### 2-4. Chinese-Wall (Brewer-Nash, 만리장성) *(p.17)*

**Chinese-Wall**: 이익 충돌(conflict of interest)이 생길 수 있는 정보에 한 주체가 양쪽 모두 접근하지 못하게 막는 모델.
- 직무 분리를 접근통제에 반영한 개념. 슬라이드에 따르면 **MAC과 DAC을 함께** 이용하는 형태. 자세한 이론은 생략.
- 예시(슬라이드엔 없음): 컨설팅 회사 직원이 경쟁 관계인 A은행 자료를 한번 봤다면 그 뒤로 B은행 자료엔 접근 불가. 어떤 자료를 봤는지가 이후 접근 권한을 바꿈.

### 2-5. MAC 종합 평가 *(p.20)*

- 장점: 원칙이 단순해서 대규모 사용자와 데이터를 관리하기 쉬움.
- 단점: **Not so flexible** (높은 등급은 거의 다 할 수 있고 최하위는 할 수 있는 게 거의 없음). 현실적 문제에 대한 대처 부족: 등급 변경 시 처리, write에 생성·수정·삭제를 포함할지, 디렉토리·파일 삭제와 read의 의미 등.

**Q&A (MAC 마무리)**
- 군 기밀문서에서 사병이 극비를 못 읽게 하려면 → BLP. 기밀성이 목적이고 read up을 막음.
- 은행에서 송금 승인과 실행을 한 사람이 못 하게 하려면 → Clark-Wilson. 업무 분리 + well-formed transaction.

---

## 3. Discretionary Access Control (DAC) *(p.21~28, 31)*

**DAC**: 한 entity(주로 자원의 owner)가 다른 entity에게 특정 자원에 대한 접근 권한을 재량으로 허용할 수 있는 방식. 보통 **access matrix**로 구현.

### 3-1. Access Matrix *(p.21~24)*
- 한 축은 접근을 시도하는 subject, 다른 축은 접근 대상 object. 각 칸은 그 subject가 그 object에 대해 가진 access right.
- 예시 (슬라이드 Figure 4.2와 같은 구조, 값은 수업에서 임의로 만든 것):

| | File 1 | File 2 | File 3 |
|---|---|---|---|
| User A | Own, Read, Write | | Read |
| User B | Read | Own, Read, Write | Write |
| User C | Read, Write | Read | Own, Read, Write |

- 실제로 저장하면 빈 칸이 많아서 두 방식으로 쪼갬 (Figure 4.2 (b), (c)).
  - **ACL (Access Control List)**: **열(object)** 기준. object마다 "누가 무슨 권한을 갖는가". 한 파일의 접근자를 묻는 질문에 빠름.
  - **Capability list**: **행(subject)** 기준. subject마다 "무슨 object에 무슨 권한을 갖는가". 한 사용자의 권한 전체를 묻는 질문에 빠름.
  - 반대 방향 질문은 어느 쪽이든 전체를 훑어야 해서 느림. UNIX의 파일별 `rwx`는 파일(object)에 권한이 붙어 있으니 ACL 쪽 발상.
- Table 4.1: 같은 정보를 (Subject, Access Mode, Object) 3열로 풀어 쓴 Authorization Table (p.24).

### 3-2. 확장된 Access Control 구조 *(p.25~27)*
- **Figure 4.3 확장 matrix (p.25)**: subject뿐 아니라 process, disk drive도 object로 포함. right도 control, owner, read, write, wakeup, seek, execute, stop 등으로 늘어남. 복사 가능 여부를 나타내는 copy flag(\*)도 있음 (받은 권한을 다른 사람에게 또 줄 수 있는지 표시).
- **Table 4.2 명령어 규칙 R1~R8 (p.26)**: matrix를 바꾸는 명령 8개(transfer, grant, delete, read, create object, destroy object, create subject, destroy subject)를 각각 Command / Authorization 조건 / Operation으로 정의. 핵심은 아무나 matrix를 고칠 수 없고 조건을 만족해야만 고칠 수 있다는 것.
- **Figure 4.4 (p.27)**: Subject의 요청(read F, wakeup P, grant, delete 등)이 Access control mechanism을 거쳐 Object(Files, Segments&pages, Processes 등)에 도달. 그 안의 Access matrix monitor가 matrix를 읽고 써서 허용 여부를 판단.

### 3-3. Protection Domains *(p.28)*
- 실제로 접근하는 주체는 사용자가 아니라 machine, process, module.
- **Protection domain**: namespace(file system 뷰), userid/group id, 보유 object 집합(capability list), 보유 권한(permissions)을 가질 수 있는 추상 객체.
- 보호는 언어 type system, 하드웨어 MMU, 컴파일러(SFI) 등으로 강제. 이 수업의 주요 관심사는 아님.

### 3-4. DAC 장단점 *(p.31)*
- 장점: **Flexibility**. 객체·주체마다 개별 설정 가능.
- 단점: 보안 위배를 체크하기 어렵고, 자료구조가 비대해져 성능 저하.

**Q&A: "보안 위배 체크가 어렵다"는 시나리오**
1. 철수의 파일 `F`, owner는 철수, 영희에게 read를 줌.
2. 영희가 `F`를 읽고 내용을 복사해 새 파일 `G`를 만듦. `G`의 owner는 영희.
3. owner는 자기 파일 권한을 재량으로 줄 수 있으므로 영희가 `G`를 영수에게 열어줌.
4. 영수는 `F`에 권한이 없는데도 `F`의 내용을 읽게 됨.

`F`의 접근 목록은 여전히 철수와 영희뿐이지만 **내용**이 새나감. DAC는 새로 만든 파일을 만든 사람의 재량으로 두므로 이를 강제하지 못함. MAC에서는 영희가 읽은 `F`보다 낮은 등급의 `G`에 쓰는 게 write down이라 \*-property가 금지. BLP에서 본 "파일을 통해 새는 길"과 같은 이야기.

**Q&A: DAC의 유연함과 새는 문제의 공통 뿌리?** 다른 사람에게 권한을 유연하게 줄 수 있는 성질, 곧 owner의 **재량(discretion)**. MAC은 이 재량을 없애서 통제를 얻고 유연성을 잃은 것.

---

## 4. UNIX Access Control *(p.30~35)*

UNIX는 DAC를 실제로 구현한 대표 사례.

### 4-1. 통제 대상 자원 *(p.30)*
- **Files**: 일반 파일뿐 아니라 device, IPC(domain socket, named pipe, mmap shared memory)도 파일로 취급.
- **Network**: TCP/UDP port address space.
- **Other**: Sys V IPC는 자체 namespace를 가짐. kernel module을 로드하는 능력도 통제 대상.

### 4-2. inode *(p.31~32)*
**inode(index node)**: 특정 파일에 필요한 핵심 정보를 담은 제어구조.
- 파일 이름 여러 개가 하나의 inode를 가리킬 수 있지만 active inode는 정확히 한 파일에 대응.
- 파일의 속성, 권한, 제어정보가 inode에 저장됨. owner ID, group ID, protection bit도 포함.
- 디스크의 inode table에 모든 파일의 inode가 있고, 파일을 열면 메모리의 inode table로 올라옴.
- 디렉토리는 계층 트리 구조로, 파일 이름과 대응 inode 포인터를 담음.
- 각 사용자는 고유 user ID와 primary group ID. 권한은 **12개의 protection bit**: owner/group/other 각각의 rwx가 9비트, 나머지 3비트가 setUID, setGID, sticky.

### 4-3. 프로세스의 신원 *(p.33)*
프로세스는 접근 결정에 쓰이는 신원 집합을 가짐.
- **uid / euid**: real user ID / effective user ID
- **gid / egid**: real group ID / effective group ID
- **real**: 이 프로세스를 실제로 실행시킨 사람. **effective**: 접근통제 결정 때 커널이 실제로 쓰는 신원. 대부분 같지만 다를 수도 있게 설계되어, 다르면 "실행한 사람은 나인데 권한 판단은 다른 사람 기준"이 됨. 접근 결정은 보통 effective 쪽으로 함.

**Q&A: 일반 사용자가 `passwd`로 root 전용 파일 `/etc/shadow`를 어떻게 고치나?** uid는 본인 그대로, 실행하는 동안만 euid가 root가 됨. 그럼 누가 euid를 바꿔주느냐 → SetUID.

### 4-4. SetUID / SetGID / Sticky bit / Superuser *(p.33)*
**SetUID / SetGID**: 실행 파일에 이 비트가 켜져 있으면, 그 프로그램을 실행한 프로세스의 euid / egid가 실행한 사람이 아니라 **그 파일의 owner / group**의 것이 됨.
- `/usr/bin/passwd`는 owner가 root고 setUID가 켜져 있음. 일반 사용자가 실행하면 uid는 그대로, euid는 root가 되어 `/etc/shadow`를 수정할 수 있음. 프로그램이 끝나면 프로세스와 함께 root 권한도 사라짐.
- `ls -l /usr/bin/passwd`에서 owner의 실행 칸에 `x` 대신 `s`가 보임 (`-rwsr-xr-x`).
- 슬라이드 표현: 일반적으로 접근 불가능한 자원에 권한 있는 프로그램이 접근하도록 해주는 장치. 사용자에게 root 자체를 주는 게 아니라 정해진 프로그램이 하는 일만 허용.
- 주의: 이는 그 프로그램이 안전하게 짜여 있다는 전제에서 성립. root 소유 setuid 프로그램에 버그가 있으면 공격자가 root 권한을 얻을 수 있음.

**Sticky bit**: 디렉토리에 적용하면 그 디렉토리 안의 파일을 **파일 owner만** rename, move, delete 할 수 있게 제한.
- 파일 **내용 수정**은 그 파일 자체의 권한(owner/group/other)이 결정.
- 파일 **삭제·이름 변경**은 파일이 아니라 **그 파일이 들어 있는 디렉토리**의 write 권한이 결정.
- `/tmp`는 누구나 파일을 만들 수 있게 `rwxrwxrwx`. sticky bit가 없으면 내용은 못 고쳐도 남의 파일을 지우거나 이름을 바꿀 수 있음. sticky bit가 이를 막음.

**Superuser**: 일반적인 access control 제약이 면제되고 시스템 전역에 접근 가능 (root).

### 4-5. UNIX의 ACL *(p.34~35)*
owner/group/other 세 묶음만으로는 표현이 모자라서 현대 UNIX(FreeBSD, OpenBSD, Linux, Solaris 등)는 ACL을 지원.

**FreeBSD 기준**
- `setfacl` 명령으로 UNIX user ID, group 목록 지정.
- 임의 개수의 user, group을 한 파일에 연결 가능.
- read/write/execute 권한 비트 사용.
- 파일이 ACL을 꼭 가질 필요는 없음.
- 확장 ACL이 있는지 나타내는 추가 protection bit가 있음.

**접근 요청 시 두 단계**: ① 가장 적합한 ACL entry 선택 ② 매칭된 entry가 요청한 권한을 충분히 포함하는지 확인.

**Figure 4.5**: 전통적 minimal ACL은 owner/group/other에 각각 `rw-`/`r--`/`---`처럼 3개만. Extended ACL은 거기에 `user:joe:rw-`처럼 특정 사용자 entry를 추가.

**Q&A: 친구 joe 한 명에게만 읽기·쓰기를 주려면?** joe가 내 group에 속하지 않는다면 9비트로는 불가능. owner/group/other 세 부류만 구분해서 개인 한 명을 가리킬 방법이 없음. 우회로는 joe와 나만 있는 새 group을 만드는 건데, group 생성은 보통 관리자 권한이 필요하고 파일마다 하면 group이 폭증. 그래서 ACL이 필요.

---

## 5. Role-Based Access Control (RBAC) *(p.36~41)*

**RBAC**: 사용자에게 권한을 직접 주지 않고, 사용자를 **role**에 배정하고 권한은 role에 붙여서 접근을 통제하는 방식.

### 5-1. 구조 *(p.36~37)*
- Users → Roles → Resources로 한 단계를 끼워 넣은 구조. 여러 User가 Role 1/2/3 중 하나 이상에 매핑되고 각 Role이 특정 Resource에 대한 권한을 가짐.
- Figure 4.7: User × Role 배정 행렬과 Role × Object 접근 행렬을 함께 보여줌. RBAC도 access matrix로 표현 가능하되 행의 주체가 user가 아니라 role.

### 5-2. 모델 계열 *(p.38~39)*
- **RBAC₀ (Base)**: **User Assignment(UA)** 로 Users ↔ Roles, **Permission Assignment(PA)** 로 Roles ↔ Permissions(Operations + Objects) 연결. Sessions로 user_sessions, session_roles 관리.
- **RBAC₁**: RBAC₀ + **Role Hierarchy(RH)**.
- **RBAC₂**: RBAC₀ + **Constraints**.
- **RBAC₃**: RBAC₁ + RBAC₂ 통합 모델.

| 모델 | Hierarchies | Constraints |
|---|---|---|
| RBAC₀ | No | No |
| RBAC₁ | Yes | No |
| RBAC₂ | No | Yes |
| RBAC₃ | Yes | Yes |

### 5-3. Role Hierarchy *(p.40)*
Figure 4.9: Director → Project Lead 1/2 → Production/Quality Engineer 1/2 → Engineer 1/2 → Engineering Dept 순의 계층. 상위 role이 하위 role의 권한을 **상속**.

### 5-4. Constraints *(p.41)*
조직 정책에 맞춰 role 관련 조건을 거는 수단.
- **Mutually exclusive roles**: 한 사용자는 집합 안의 role 중 하나에만 배정 가능. 한 permission도 집합 안의 하나의 role에만 부여 가능.
- **Cardinality**: 한 role에 배정할 수 있는 최대 인원 수.
- **Prerequisite roles**: 다른 특정 role을 이미 가진 사용자만 이 role에 배정 가능.

**Q&A**
- 직원 100명에게 권한을 줬는데 한 명이 경리팀에서 영업팀으로 이동하면?
  - **DAC**: 권한이 사람에게 직접 붙어 있어서 관리자가 그 사람의 경리 관련 권한을 하나하나 회수(revoke)하고 영업 관련 권한을 하나하나 새로 부여(grant)해야 함. 권한이 20개면 40번쯤 건드림. 빠뜨리면 옛 권한이 남는 사고도 남.
  - **RBAC**: User Assignment(UA) 하나만 "경리 → 영업"으로 바꾸면 끝. role에 묶인 권한(PA)은 그대로.
  - 핵심: 사용자와 권한 사이에 role이라는 중간층이 있어서 사람이 바뀌는 일과 권한이 바뀌는 일이 분리됨.
- mutually exclusive roles는 Clark-Wilson의 **업무 분리(separation of duty)** 와 닮음. "송금 요청자"와 "송금 승인자"를 mutually exclusive로 묶으면 한 사용자가 두 role을 동시에 가질 수 없어 자기가 요청한 송금을 자기가 승인하는 부정이 구조적으로 막힘. Clark-Wilson이 사람을 나눠서 막은 걸 RBAC은 role 배정 제약으로 막는 것.

---

## 6. Attribute-Based Access Control (ABAC) *(p.42~45)*

**ABAC**: 주체, 객체, 환경의 **속성(attribute)** 에 대한 조건을 규칙으로 정의하고, 접근 요청 때마다 그 규칙을 평가해서 허용 여부를 결정하는 방식.

### 6-1. 개요 *(p.42)*
- 자원과 주체 양쪽의 속성에 대한 조건을 담아 authorization을 정의 가능.
- 강점은 **유연성**과 **표현력**.
- 도입을 막는 주된 걸림돌은 성능. 매 접근마다 속성에 대한 predicate를 평가해야 하는 부담.
- Web service에서 **XACML(eXtensible Access Control Markup Language)** 을 도입하며 선도해왔고, cloud 서비스에 적용하는 데 관심이 큼.

### 6-2. 속성의 세 종류 *(p.43)*
- **Subject attributes**: 능동적 개체(사용자, 프로세스)의 신원과 특성. 예: 이름, 허가 등급(clearance), 소속(affiliation).
- **Object attributes**: 수동적 개체(자원)의 속성. 예: 종류(type), 소유자(owner), 분류(classification).
- **Environment attributes**: 접근이 일어나는 운영적, 기술적, 상황적 맥락. 지금까지 대부분의 정책에서 크게 무시되어온 속성. 예: 시간, 위치.

### 6-3. 특징 *(p.44)*
- 엔티티, 연산, 환경의 속성에 대한 **규칙 평가**로 통제한다는 점이 구별점.
- subject 속성, object 속성, 그리고 주어진 환경에서 허용되는 operation을 정의한 **formal relationship(access control rule)** 평가에 의존.
- DAC, RBAC, MAC 개념을 **모두 강제할 수 있음**.
- 무제한 개수의 속성을 조합 가능.

### 6-4. Figure 4.10 단순 ABAC 시나리오 *(p.45)*
① Subject가 접근 요청 → ② Access Control Mechanism이 정책(a), Subject 속성(b), Object 속성(c), 환경 조건(d)을 종합해 Rule 평가 → ③ 결과에 따라 Object 접근 허용 또는 거부.

**Q&A: "의사는 자기 담당 환자의 진료기록을 근무 시간에만 열람할 수 있다"를 RBAC으로 구현하면?**
- RBAC으로 어려운 점 2가지
  1. **시간 조건**: role에는 "근무시간에만 유효" 같은 조건을 붙일 구조가 없음.
  2. **"자기 담당" 조건**: "의사 role" 전체에 열람 권한을 주면 모든 환자의 기록을 볼 수 있음. 의사별로 role을 따로 만들면 의사와 환자 수만큼 role이 폭증. role은 사람이 아니라 직무를 표현하는 도구라서 "이 의사와 이 환자 사이의 관계"를 담기 어려움.
- ABAC 속성 분류
  - **Subject = 의사** (접근을 요청하는 주체는 의사뿐, 환자는 요청하지 않음). 속성 예: 직무=의사, 담당 환자 목록.
  - **Object = 진료기록**. 속성 예: 해당 환자 ID. 환자는 subject가 아니라 기록에 딸린 정보(object 속성).
  - **Environment = 현재 시각**. 속성 예: 근무시간 여부.
- 규칙: 직무가 의사이고, 기록의 환자 ID가 의사의 담당 환자 목록에 포함되고, 현재 시각이 근무시간이면 열람 허용.
- "기록의 환자 ID가 의사의 담당 환자 목록에 포함된다"는 **subject 속성과 object 속성을 서로 비교**하는 조건. 슬라이드가 말한 "subject-object 속성 조합" 평가가 정확히 이것이고, 이게 ABAC만의 힘.

---

## 7. 마무리 정리: 4개 정책 비교

| 정책 | 결정 기준 | 누가 결정? | 특징 |
|---|---|---|---|
| DAC | 신원 + 접근 규칙(access matrix) | owner의 재량 | 유연하지만 정보가 새는 걸 못 막음 |
| MAC | 보안 라벨 vs clearance | 시스템 정책(강제) | 강력하지만 유연성 낮음 |
| RBAC | 사용자의 role | 관리자가 role 배정 | 사람 변동과 권한 변동을 분리 |
| ABAC | subject·object·environment 속성 | 규칙 평가 | 가장 유연, 성능이 과제 |

**Q&A (마무리 질문)**
1. 내가 만든 파일을 내 재량으로 친구에게 공유 → **DAC**
2. 병원 직원이 직무에 따라 서로 다른 시스템 권한을 가짐 → **RBAC**
3. 군에서 문서 등급과 개인 허가 등급을 비교해 통제 → **MAC** (BLP)
4. 소속, 문서 분류, 접속 시간·위치를 조합해 접근 결정 → **ABAC**
