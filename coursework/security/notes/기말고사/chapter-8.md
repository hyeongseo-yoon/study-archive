# Chapter 8: Intrusion Detection System

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

슬라이드 번호는 PDF 페이지 기준(`p.N`). 슬라이드 하단 쪽번호는 일부 장에만 있고 1씩 어긋나서 쓰지 않음.
흐름: 침입자·침입 → IDS 정의·필요성·목적 → IDS 종류(HIDS/NIDS/분산) → 기본율 오류·요구사항 → 분석 방식(Anomaly/Signature) → HIDS → NIDS → Honeypot → Snort

## 1. 침입자(Intruder)와 침입 *(p.3~4)*

### Cyber Criminals *(p.3)*
- 금전적 보상을 목적으로 하는 **개인 또는 조직범죄 집단**
- 활동: Identity theft, 금융 인증정보 탈취, **Corporate espionage(산업스파이)**, 데이터 탈취, **Data ransoming**(데이터 인질 협박)
- 전형적으로 젊은 동유럽·러시아·동남아 해커이며 웹에서 사업처럼 활동
- **underground forum**에서 팁과 데이터를 거래하고 공격을 조율

### 침입 사례 *(p.4)*
- Remote root compromise
- Web server defacement
- 패스워드 추측/크래킹
- 신용카드 번호가 든 데이터베이스 복사
- 인가 없이 민감 데이터 열람
- Packet sniffer 실행
- 불법 복제 소프트웨어 배포
- 보호되지 않은 modem으로 내부망 접근
- 임원을 사칭해 정보 획득
- 자리 비운 workstation 사용

## 2. 침입탐지 시스템 정의 *(p.5)*

- **침입탐지(Intrusion detection)**: 보안 방어선을 뚫고 비인가된 방법으로 내부 자원에 접근하거나 시도하는 사건을 **모니터링·분석**해 보안 사고의 징후를 찾아내고 **기록**하며 **경고**하는 일련의 과정
- **IDS(Intrusion Detection System)**: 침입 탐지 작업을 **자동으로 수행**해서, 보안 관리자나 다른 보안장치가 침입에 적절히 **대응**할 수 있게 지원하는 시스템

## 3. IDS의 필요성 *(p.6)*

- 보통 내부 자원 보호에 **사용자 인증, 접근 제어, 방화벽**을 쓰지만 이것만으로는 부족하다
- 이유
  1. 새로운 공격 방법이 **끊임없이 개발**됨
  2. 사용자가 **악성코드를 정상적으로 다운받아 실행**하는 경우 막기 어려움
  3. **사회공학 공격**을 막기 어려움
  4. **내부 사용자의 부주의나 변심**에 의한 공격을 막기 어려움

## 4. IDS의 목적 *(p.7)*

- 목적: 침입에 의한 **손실 방지/억지**, **침입 예방 정보 수집**, **침입 탐지**
- **침입 예방(prevention)이나 침입 방지가 아니다**
  - IDS는 모든 event/action에 **개입해서 check-then-pass/deny를 하지 않는다**
- cf. event/action에 개입해 check-then-pass/deny 하는 보안장비: **방화벽(Firewall)**, **IPS(Intrusion Prevention System)**

## 5. IDS 종류와 구성요소 *(p.8)*

| 종류 | 설명 |
|---|---|
| **Host-based IDS (HIDS)** | **단일 호스트**의 특성을 모니터링해 의심스러운 활동을 찾음 |
| **Network-based IDS (NIDS)** | **네트워크 트래픽**을 모니터링하고 network·transport·application 프로토콜을 분석해 의심스러운 활동을 찾음 |
| **Distributed or hybrid IDS** | 여러 sensor(호스트·네트워크 기반 모두 가능)의 정보를 **중앙 analyzer**에서 결합해 침입 활동을 더 잘 식별하고 대응 |

- IDS는 3개의 **논리 구성요소**로 이루어진다
  - **Sensors**: 데이터를 수집
  - **Analyzers**: 침입이 발생했는지 판단
  - **User interface**: 출력을 보거나 시스템 동작을 제어

## 6. 침입자와 정상 사용자의 행동 프로파일 (Figure 8.1) *(p.9)*

- 가로축: 측정 가능한 행동 파라미터(Measurable behavior parameter), 세로축: 확률밀도함수(Probability density function)
- **침입자 행동 프로파일**과 **인가된 사용자 행동 프로파일**이 각각 분포를 이루고, 두 분포의 평균(average behavior of intruder / of authorized user)이 다르다
- 두 분포가 **겹치는 구간(overlap in observed or expected behavior)** 이 존재 → 이 구간 때문에 오탐/미탐이 불가피하다

## 7. 기본율 오류 (Base-rate Fallacy) *(p.10)*

- **False positive (오긍정)**: **정상 사용자**를 침입자로 판정
- **False negative (오부정)**: **침입자**를 정상 사용자로 판정
- **기본율 오류(Base-rate Fallacy)**: 정상적인 사용의 수에 비해 **실제 침입 수가 작을 때**, 오긍정 판정으로 인한 **경고 발생 비율이 높아지는** 현상
  - 잦은 오류가 나면 관리자가 **IDS 기능을 꺼버린다**

## 8. IDS 요구사항 *(p.11)*

- 지속적으로 실행(Run continuously)
- **Fault-tolerant, attack-resistance** (Graceful degradation)
- 낮은 오버헤드(Overhead should be low)
- **보안 정책에 맞게 설정** 가능
- 대규모 시스템/사용자를 지원하도록 **확장 가능(Scalable)**
- **동적 재설정(dynamic reconfiguration)** 허용

## 9. 분석 방식 (Analysis Approaches) *(p.12~14)*

| | Anomaly detection | Signature/Heuristic detection |
|---|---|---|
| 방식 | 일정 기간 **합법 사용자의 행동 데이터**를 수집하고, 현재 관찰된 행동이 합법 사용자의 것인지 침입자의 것인지 분석 | **알려진 악성 데이터 패턴이나 공격 규칙** 집합을 현재 행동과 비교 |
| 다른 이름 | | **Misuse detection** |
| 한계 | | **패턴·규칙이 있는 알려진 공격만** 식별 가능 |

### Anomaly Detection의 분류 접근법 *(p.13)*
- **Statistical**: 관찰된 지표(metrics)의 **univariate, multivariate, time-series 모델**로 관찰 행동을 분석
- **Knowledge based**: **expert system**이 합법 행동을 모델링한 **규칙 집합**에 따라 관찰 행동을 분류
- **Machine-learning**: **data mining** 기법으로 학습 데이터에서 적절한 분류 모델을 **자동으로 결정**

### Signature or Heuristic Detection *(p.14)*
- **Signature approaches**: 악성 데이터의 **알려진 패턴 대규모 모음**을, 시스템에 저장된 데이터나 네트워크로 전송 중인 데이터와 매칭
  - signature는 **false alarm rate를 최소화**할 만큼 충분히 크면서도 악성 데이터의 상당 부분을 탐지해야 한다
  - **anti-virus 제품, network traffic scanning proxy, NIDS**에서 널리 사용
- **Rule-based heuristic identification**: **알려진 침투**나 **알려진 취약점을 악용하는 침투**를 식별하는 규칙 사용
  - 규칙은 기존 사용 패턴의 범위 안에 있더라도 **의심스러운 행동**을 식별하도록 정의할 수도 있다
  - 보통 사용되는 규칙은 **특정 상황에 특화**되어 있다
  - **SNORT**가 rule-based NIDS의 예

### Signature의 예 *(p.15)*
- **Host-based IDS**: Root 사용자 로그인 시도 로그, 패스워드 파일 복제 시도 로그, 시스템 파일 변경 시도 로그 …
- **Network-based IDS**: 인터넷 웜 XYZ 악성코드 청크 패턴, APT 공격의 커맨드 …

## 10. Host-Based IDS (HIDS) *(p.16~20)*

### 개요 *(p.16)*
- 취약하거나 민감한 시스템에 **특화된 보안 소프트웨어 계층**을 추가
- **anomaly** 방식, **signature·heuristic** 방식 모두 사용 가능
- 활동을 모니터링해 의심스러운 행동을 탐지
  - 주 목적: **침입 탐지, 의심 이벤트 로깅, 경고(alert) 전송**
  - **외부 침입과 내부 침입 모두** 탐지 가능

### Data Sources and Sensors *(p.17)*
- **Log 파일** (로그파일 분석기)
- **System calls** (시스템 콜 분석기)
- **Registry access** (레지스트리 분석기)
- **System files integrity** (시스템 파일 체크기)

### Table 8.2: 모니터링하는 Linux System Calls와 Windows DLLs *(p.18)*
- **(a) Ubuntu Linux System Calls**: accept, access, acct, adjtime, aiocancel, aioread, aiowait, aiowrite, alarm, async_daemon, auditsys, bind, chdir, chmod, chown, chroot, close, connect, creat, dup, dup2, execv, execve, exit, exportfs, fchdir, fchmod, fchown, fchroot, fcntl, flock, fork, fpathconf, fstat, fstatfs, fsync, ftime, ftruncate, getdents, getdirentries, getdomainname, getdopt, getdtablesize, getfh, getgid, getgroups, gethostid, gethostname, getitimer, getmsg, getpagesize, getpeername, getpgrp, getpid, getpriority, getrlimit, getrusage, getsockname, getsockopt, gettimeofday, getuid, gtty, ioctl, kill, killpg, link, listen, lseek, lstat, madvise, mctl, mincore, mkdir, mknod, mmap, mount, mprotect, mpxchan, msgsys, msync, munmap, nfs_mount, nfssvc, nice, open, pathconf, pause, pcfs_mount, phys, pipe, poll, profil, ptrace, putmsg, quota, quotactl, read, readlink, readv, reboot, recv, recvfrom, recvmsg, rename, resuba, rfssys, rmdir, sbreak, sbrk, select, semsys, send, sendmsg, sendto, setdomainname, setdopt, setgid, setgroups, sethostid, sethostname, setitimer, setpgid, setpgrp, setpriority, setquota, setregid, setreuid, setrlimit, setsid, setsockopt, settimeofday, setuid, shmsys, shutdown, sigblock, sigpause, sigpending, sigsetmask, sigstack, sigsys, sigvec, socket, socketaddr, socketpair, sstk, stat, statfs, stime, stty, swapon, symlink, sync, sysconf, time, times, truncate, umask, umount, uname, unlink, unmount, ustat, utime, utimes, vadvise, vfork, vhangup, vlimit, vpixsys, vread, vtimes, vtrace, vwrite, wait, wait3, wait4, write, writev
- **(b) Key Windows DLLs and Executables**: comctl32, kernel32, msvcpp, msvcrt, mswsock, ntdll, ntoskrnl, user32, ws2_32

### Distributed IDS 구조 (Figure 8.2) *(p.19)*
- 구성: **LAN Monitor**(+Agent module), **Host**(+Agent module), Router, Internet, **Central Manager**(Manager module)
- LAN monitor와 각 host의 **agent module**이 수집한 정보를 **Central Manager의 manager module**로 모아 분석

### Agent Architecture (Figure 8.3) *(p.20)*
- 흐름: **OS audit function**이 만든 OS audit information → **Filter for security interest** → **Reformat function** → **Host audit record(HAR)** → **Analysis module**
- **Logic module**: Notable activity, Signatures, Noteworthy sessions, Templates를 바탕으로 Analysis module과 상호작용(Modifications)
- Analysis module → **Alerts** → **Central manager**, Central manager와 **Query/response**를 주고받음

## 11. Network-Based IDS (NIDS) *(p.21~25)*

### 개요 *(p.21)*
- 네트워크의 **선택된 지점에서 트래픽을 모니터링**
- 트래픽을 **패킷 단위로 실시간 또는 거의 실시간**으로 검사
- **network, transport, application** 계층 프로토콜 활동을 검사할 수 있음
- 구성: 다수의 **sensor**, NIDS 관리 기능용 **server** 1개 이상, 사람용 인터페이스인 **management console** 1개 이상
- 트래픽 패턴 분석은 **sensor**, **management server**, 또는 둘의 조합에서 수행

### Passive NIDS Sensor (Figure 8.4) *(p.22)*
- Network traffic을 **Monitoring interface**로 받는다
  - monitoring interface는 **IP가 없고 promiscuous mode**
- **Management interface**는 **IP를 가진다**

### NIDS Sensor 배치 예 (Figure 8.5) *(p.23)*
- 구성: Internet, **external firewall**, **service network**(Web, Mail, DNS 등), **LAN switch or router**, **internal firewall**, internal server and data resource networks, workstation networks
- sensor 배치 위치 4곳(그림의 번호 1~4)
  - 1: **external firewall 안쪽, service network 쪽**
  - 2: **external firewall 바깥(Internet 쪽)**
  - 3: **internal server and data resource networks** 바로 앞(internal firewall → LAN switch 뒤, 서버 네트워크 쪽 링크)
  - 4: **workstation networks** 바로 앞(internal firewall → LAN switch 뒤, workstation 네트워크 쪽 링크)

### Intrusion Detection Techniques *(p.24)*

| Signature detection에 적합한 공격 | Anomaly detection에 적합한 공격 |
|---|---|
| Application layer attacks | **Denial-of-service (DoS)** attacks |
| Transport layer attacks | **Scanning** |
| Network layer attacks | **Worms** |
| Unexpected application services | |
| Policy violations | |

### Logging of Alerts *(p.25)*
- NIDS sensor가 보통 기록하는 정보
  - Timestamp
  - Connection or session ID
  - Event or alert type
  - Rating
  - Network, transport, application layer protocols
  - Source / destination IP addresses
  - Source / destination TCP or UDP ports, 또는 ICMP types and codes
  - 연결로 전송된 **bytes 수**
  - **Decoded payload data** (application request/response 등)
  - State-related information

## 12. Honeypot *(p.26~28)*

### 개요 *(p.26)*
- **Honeypot**: 공격자를 **유인**하는 **decoy(미끼) 시스템**
  - 공격자를 **중요 시스템에서 멀리 유인**
  - 공격자의 활동 정보를 **수집**
  - 관리자가 대응할 수 있을 만큼 공격자가 **시스템에 오래 머물도록** 유도
- 정상 사용자가 접근하지 않을 **fabricated(조작된) 정보**로 채워짐
- **production value가 없는 자원**
  - 그래서 **들어오는 통신**은 대부분 probe, scan, 공격
  - 시스템이 **먼저 시작한 outbound 통신**은 이미 **침해당했다**는 뜻

### 분류 *(p.27)*

| | Low interaction honeypot | High interaction honeypot |
|---|---|---|
| 정의 | 특정 IT 서비스·시스템을 **에뮬레이션**하는 소프트웨어 패키지. 현실적인 초기 상호작용은 제공하지만 **전체 서비스·시스템을 실행하지는 않음** | **완전한 OS, 서비스, 애플리케이션을 갖춘 실제 시스템**에 계측(instrument)을 해서 공격자가 접근 가능한 곳에 배치 |
| 현실성 | **덜 현실적**인 목표 | **더 현실적**이라 공격자를 **오래 붙잡아 둘 수** 있음 |
| 장점 | 분산 IDS의 구성요소로서 **임박한 공격을 경고**하는 용도로 충분한 경우가 많음 | |
| 단점 | | **훨씬 많은 자원** 필요, **침해되면 다른 시스템 공격의 발판**이 될 수 있음 |

### Honeypot 배치 예 (Figure 8.8) *(p.28)*
- 구성: Internet, external firewall, LAN switch or router, **Service network**(Web, Mail, DNS 등), **Internal network**
- Honeypot 배치 위치 3곳(그림의 번호 1~3)
  - 1: **external firewall 바깥(Internet 쪽)**
  - 2: **service network 안**
  - 3: **internal network 안**

## 13. Snort *(p.29~34)*

### 개요 *(p.29)*
- **Snort**: 오픈소스이며 **설정 가능성이 높고 이식성 좋은** host-based 또는 network-based IDS
- **실시간 packet capture, protocol analysis, content searching & matching** 수행
- **규칙 집합(rule)** 에 기반해 다양한 공격을 탐지
- 현재 버전: 3.0

### Snort Architecture (Figure 8.9) *(p.30)*
- 흐름: **Packet → Decoder → Detection Engine → Log / Alert**

### Snort Rule Format (Figure 8.10) *(p.31)*
- **(a) Rule Header**: `Action` `Protocol` `Source IP address` `Source Port` `Direction` `Dest IP address` `Dest Port`
- **(b) Options**: `Option Keyword` + `Option Arguments`을 여러 개 나열(• • •)

### Table 8.3: Snort Rule Actions *(p.32)*

| Action | 설명 |
|---|---|
| **alert** | 선택된 alert method로 경고를 만든 뒤 **패킷을 로그** |
| **log** | 패킷을 로그 |
| **pass** | 패킷을 **무시** |
| **activate** | alert 후 **다른 dynamic rule을 켠다** |
| **dynamic** | activate rule로 켜질 때까지 **대기**, 켜지면 log rule처럼 동작 |
| **drop** | iptables가 패킷을 **drop**하게 하고 **로그** |
| **reject** | iptables가 패킷을 drop하고 로그한 뒤, TCP면 **TCP reset**, UDP면 **ICMP port unreachable** 전송 |
| **sdrop** | iptables가 패킷을 drop하지만 **로그는 남기지 않음** |

### Table 8.4: Snort Rule Options 예 *(p.33)*

| 분류 | 옵션 | 설명 |
|---|---|---|
| **meta-data** | `msg` | 패킷이 이벤트를 발생시킬 때 보낼 **메시지** 정의 |
| | `reference` | 추가 정보를 제공하는 **외부 공격 식별 시스템 링크** 정의 |
| | `classtype` | 패킷이 시도한 **공격 유형** 표시 |
| **payload** | `content` | 패킷 payload에서 특정 내용(텍스트/바이너리)을 **대소문자 구분**해 검색 |
| | `depth` | 패킷 안에서 패턴을 **얼마나 깊이까지** 검색할지 지정(직전 content 수식) |
| | `offset` | 패턴 검색을 **어디서부터 시작**할지 지정(직전 content 수식) |
| | `nocase` | 패턴을 **대소문자 무시**하고 검색(직전 content 수식) |
| **non-payload** | `ttl` | IP **time-to-live** 값 확인. traceroute 시도 탐지용 |
| | `id` | IP **ID 필드** 확인. 일부 exploit·scanner가 특정 값(예: 31337)을 설정 |
| | `dsize` | 패킷 **payload 크기** 검사. 비정상 크기 탐지, **buffer overflow 탐지**에 유용 |
| | `flags` | **TCP flags** 설정 검사 |
| | `seq` | 특정 **TCP sequence number** 확인 |
| | `icmp-id` | 특정 **ICMP ID** 값 확인. 일부 covert channel 프로그램이 고정 ICMP 필드를 쓰므로 유용(**stacheldraht DDoS agent** 탐지용으로 개발) |
| **post-detection** | `logto` | 규칙에 맞는 패킷을 **지정한 파일에 로그** |
| | `session` | **TCP 세션**에서 사용자 데이터를 추출. telnet, rlogin, ftp, 웹 세션에서 사용자가 입력한 내용을 볼 때 유용 |

### Snort Rule 예제 *(p.34)*
- 예제 1
  ```
  alert tcp any 21 -> 10.199.12.8 any (msg: "TCP Packet is detected"; sid:1000010)
  ```
  - 모든 IP의 21번 포트에서 10.199.12.8의 모든 포트로 가는 **TCP 패킷**에 대해 "TCP Packet is detected" 메시지를 **경고**로 발생
  - 구조: Action=`alert`, Protocol=`tcp`, Source Address=`any`, Source Port=`21`, Direction=`->`, Destination Address=`10.199.12.8`, Destination Port=`any`, Rule Option=`(msg: ...; sid: ...)`
  - `sid`: snort rule id 번호
- 예제 2 (`local.rules`)
  ```
  alert tcp any any -> any 80 (msg: "Error Based SQL Injection Detected" ; content: "%27"; sid:100000011;)
  ```
  - 모든 IP·포트에서 any IP의 **80번 포트**로 가는 TCP 패킷 중 **content에 `%27`**(작은따옴표 `'`의 URL 인코딩)이 포함된 경우 "Error based SQL Injection Detection" 메시지를 경고로 발생

## 14. Summary *(p.35)*

- Intruders: Intruder behavior
- Intrusion detection: Basic principles, **The base-rate fallacy**, Requirements
- Analysis approaches: **Anomaly detection**, **Signature or heuristic detection**
- Distributed or hybrid intrusion detection
- Intrusion detection exchange format
- Honeypots
- Host-based intrusion detection: Data sources and sensors, Anomaly HIDS, Signature or heuristic HIDS, Distributed HIDS
- Network-based intrusion detection: Types of network sensors, NIDS sensor deployment, Intrusion detection techniques, Logging of alerts
- Example system: **Snort** (Snort architecture, Snort rules)

## 수업에서 다룬 섹션

1. 침입자(Cyber Criminals)와 침입 사례
2. IDS 정의
3. IDS의 필요성
4. IDS의 목적 (방화벽·IPS와의 차이)
5. IDS 종류(HIDS/NIDS/Distributed)와 논리 구성요소
6. 침입자·정상 사용자 행동 프로파일 (Figure 8.1)
7. 기본율 오류 (False positive/negative)
8. IDS 요구사항
9. 분석 방식: Anomaly vs Signature/Heuristic, Signature의 예
10. Host-Based IDS (데이터 소스, Table 8.2, Distributed 구조, Agent Architecture)
11. Network-Based IDS (Passive sensor, 배치, 탐지 기법, 경고 로깅)
12. Honeypot (개요, 분류, 배치)
13. Snort (구조, Rule format, Actions, Options, 예제)
14. Summary
