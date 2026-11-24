# Chapter 7: Denial-of-Service Attacks

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

슬라이드 우측 하단 쪽번호 기준(`p.N`).
흐름: DoS 정의·자원 분류 → Classic DoS(ping flood) → Source address spoofing → Flooding(ICMP/UDP/SYN) → SYN spoofing → HTTP 기반 공격 → DDoS/Botnet → Reflection·Amplification → 방어·대응

## 1. DoS 공격이란? *(p.2~4)*

- **NIST 정의**: CPU, memory, bandwidth, disk space 같은 자원을 **고갈**시켜 네트워크·시스템·애플리케이션의 **정당한 사용을 막거나 저해**하는 행위 *(p.3)*
- **DoS**: 서비스의 **가용성(availability)** 에 대한 공격 *(p.4)*
- 공격 대상 자원 3분류 *(p.4)*

| 분류 | 설명 |
|---|---|
| **Network bandwidth** | 서버를 인터넷에 연결하는 **네트워크 링크의 용량**과 관련. 대부분 조직에서는 **ISP 연결** |
| **System resources** | 네트워크 처리 소프트웨어를 **과부하시키거나 crash** 시킴 |
| **Application resources** | 각각 상당한 자원을 소모하는 **다수의 유효한 요청**으로 서버가 **다른 사용자의 요청에 응답하지 못하게** 함 |

- 슬라이드 목차(p.2) 요약
  - Network bandwidth: ICMP(flooding ping), UDP, (TCP)
  - System resources: TCP SYN flooding
  - Application resources: HTTP flooding
  - DDoS, Botnet / Reflection·amplification / 방어

### 예시 네트워크 (Figure 7.1) *(p.5)*
- 구성: 두 ISP(A, B)와 각 ISP의 broadband 가입자·사용자, 인터넷, Router, Large Company LAN, Medium Size Company LAN, Web Server, LAN PCs and workstations
- 공격 대상 자원이 어디인지(링크/서버/애플리케이션) 보여주는 그림

## 2. Classic DoS Attacks: Flooding ping command *(p.6)*

- **Ping command**: UNIX에서 **ICMP echo message**를 보내고 받는 명령어 (ICMP echo request/reply)
- 장점 (공격자 입장)
  1. 만들기 쉽다
  2. 대부분 라우터에서 통과된다
  3. 대부분의 서버가 reply를 한다
- **공격 목적**: 대상 조직의 **네트워크 연결 용량을 압도**
  - 대상 시스템을 목적지 주소로 하는 **대량의 패킷** 생성
  - 최종 **낮은 용량 링크**에 연결된 라우터에서 **혼잡(congestion)** 발생 → 네트워크 성능 눈에 띄게 저하
- 단점
  - **단점1**: 트래픽은 경로상의 **더 높은 용량 링크**에서는 처리되지만, 용량이 줄어드는 지점에서 패킷이 **버려진다**
  - **단점2**: **spoofed address**를 쓰지 않으면 공격 **출처가 명확히 식별**된다

## 3. Source Address Spoofing *(p.7)*

- **Source address spoofing**: **위조된 source address**를 사용
  - 보통 OS의 **raw socket interface**를 통해 수행
  - 공격 시스템을 **식별하기 어렵게** 만든다
- 식별하려면 네트워크 엔지니어가 라우터에서 **flow information을 직접 조회**해야 한다
- 결과: 응답 패킷이 **흩어짐** → **Backscatter traffic**
- **Honeynet Project**: 사용하지 않는 IP 주소에 대한 **경로를 광고(advertise)** 해서 공격 트래픽을 모니터링

## 4. Flooding Attacks *(p.8)*

- **사용된 네트워크 프로토콜**로 분류
- 목적: 서버로 가는 **어떤 링크의 네트워크 용량을 과부하**시키는 것
- 사실상 **어떤 종류의 패킷이든** 사용 가능

| 종류 | 설명 |
|---|---|
| **ICMP flood** | **ICMP echo request** 패킷으로 ping flood. ping이 유용한 진단 도구라 관리자들이 전통적으로 이 패킷을 네트워크에 **허용**해 왔음 |
| **UDP flood** | 대상 시스템의 **특정 포트 번호**로 향하는 UDP 패킷 사용 |
| **TCP SYN flood** | 대상으로 TCP 패킷 전송. 시스템 코드가 아니라 **패킷의 총량**이 공격 목표 |

## 5. System Resources: SYN Spoofing *(p.9~11)*

- **SYN spoofing**: 흔한 DoS 공격. 서버가 연결 요청을 관리하는 **테이블을 overflow**시켜 **이후 연결 요청에 응답하는 능력**을 공격 → 정당한 사용자가 서버에 접근 못 함
- 따라서 **system resources**(OS의 **네트워크 처리 코드**)에 대한 공격 *(p.9)*

### TCP 3-way handshake (Figure 7.2) *(p.10)*
1. Client → Server: **SYN** (seq = x)
2. Server → Client: **SYN-ACK** (seq = y, ack = x+1)
3. Client → Server: **ACK** (ack = y+1)

### TCP SYN spoofing 공격 (Figure 7.3) *(p.11)*
1. Attacker가 **spoofed source**로 SYN (seq = x) 전송
2. Server는 SYN-ACK (seq = y, ack = x+1)를 spoofed client(**존재하지 않는 client**)로 전송 → 그 SYN-ACK는 **버려짐**
3. Server는 timeout 후 **SYN-ACK를 재전송**하고, 결국 **연결 요청 실패로 간주**
- 그동안 서버의 연결 관리 테이블 엔트리가 점유된다

## 6. Application Resources: HTTP 기반 공격 *(p.12)*

### HTTP flood
- Web server에 **HTTP 요청을 폭격**하는 공격, 상당한 자원 소모
- **Spidering**: bot이 주어진 HTTP 링크에서 시작해 해당 웹사이트의 **모든 링크를 재귀적으로 따라감**

### Slowloris (2009)
- **끝나지 않는 HTTP 요청**을 보내 자원을 독점하려 함
  - 대상 웹서버에 연결을 열고 **부분 요청(partial request)** 전송
  - 주기적으로 **후속 HTTP 헤더를 추가로 전송**하지만 요청을 **절대 완료하지 않음**
  - 영향받은 서버는 이 연결들을 계속 열어 두어 **최대 동시 연결 풀이 가득 참** → 다른 클라이언트의 추가 연결 시도 거부
- 결국 웹서버의 **연결 수용량(connection capacity)** 을 소진
- **정상적인 HTTP 트래픽**을 이용함
- **signature 기반** 기존 IDS/IPS는 Slowloris를 **일반적으로 탐지하지 못한다**

## 7. DDoS (Distributed Denial of Service) *(p.13~14)*

- **DDoS**: **여러 시스템**을 이용해 공격 생성
- 공격자가 OS나 흔한 애플리케이션의 **취약점**으로 접근 권한을 얻고 자신의 프로그램을 설치 (**zombie**)
- 한 공격자의 통제 하에 있는 이런 시스템들의 대규모 집합 = **botnet**
- 예: **Tribe Flood Network (TFN), TFN2K**

### DDoS 공격 구조 (Figure 7.4) *(p.14)*
- **Attacker → Handler zombies → Agent zombies → Target**

## 8. Botnet *(p.15~20)*

### Botnet 개요 *(p.15)*
| 용어 | 의미 |
|---|---|
| **Bot-master** | malware로 botnet을 구성하고 bot에 **명령과 제어**를 보냄 |
| **Bot** | bot-master가 개발한 malware. client 머신에서 **악의적 활동** 수행 |
| **Botnet** | 다수의 bot과 bot-master로 구성된 네트워크 |
| **Command & Control (C&C) server** | bot-master의 명령·제어를 bot에게 **전달하는 중간 서버** |

### 감염 경로 *(p.16)*
- 원형 그래프 (슬라이드 우측 하단 쪽번호 16 기준)
  - **Browser Exploits 65%**
  - **Email Attachments 13%**
  - **OS Exploits 11%**
  - **Downloaded Files 9%**
  - **Others 2%**

### Botnet의 악의적 활동 *(p.17)*
- **Spam mails**
- **DDoS attacks**
- **Traffic sniffing**
- **Key logging**
- **Phishing**
- **malware installation**

### Botnet의 특징 *(p.18)*
- **복잡한 구조**: worm/virus, backdoor, spyware, rootkit 등의 **조합**
- **대응이 어려움**
  - 일반 사용자의 PC 사용 → **합법적인 IP 주소**
  - PC당 생성하는 **공격 패킷 수가 적음**
  - DDoS 시 **정상 사용자 트래픽과 botnet 트래픽 구분이 어려움**
  - 새로운 botnet 기술이 **계속 개발**됨

### Botnet 동작 메커니즘 *(p.19)*
1. **전파(propagate)**: 취약점, 이메일 등을 통해 malware 전파 (Botmaster 측)
2. **propagation**: botnet 확산
3. bot이 **C&C server**(Webserver, IRC 등)에 **접속**
4. **command/control** 전달 (Botmaster ↔ C&C)
5. **commands / bot updates** 전달 (C&C → botnet)
6. **DDoS 공격, spam mail** 등을 Victims에게 수행

### Botnet 네트워크 구조 *(p.20)*
- **IRC (Internet Relay Chat)**
- **HTTP**
- **P2P**
- **Social media** (Facebook, Twitter 등)
- **DNS request/reply**
- 기타

## 9. Reflection Attacks *(p.21~22)*

- 공격자가 **중간자(intermediary)** 의 알려진 서비스로, **source address를 실제 대상 시스템으로 위조**한 패킷을 보냄
- 중간자가 응답하면 그 **응답이 대상에게 전달**됨 → 중간자(**reflector**)에서 공격이 **"반사"**
- 목표: 중간자가 **눈치채지 못하게** 대상 링크를 flood할 만큼 충분한 패킷량 생성
- **기본 방어**: **spoofed-source 패킷 차단**

### Amplification Attack (Figure 7.7) *(p.22)*
- 구조: **Attacker → Zombies → Reflector intermediaries → Target**

## 10. DNS Amplification Attacks *(p.23)*

- **정당한 DNS server**를 중간 시스템으로 사용
- 공격자가 **대상 시스템의 주소로 source를 위조한 DNS 요청**을 연속 생성
- **DNS 동작을 악용**해 **작은 요청을 훨씬 큰 응답으로 변환(amplification)**
- 대상은 응답들로 flood됨
- **기본 방어**: **spoofed source address 사용 방지**

## 11. DoS Attack Defenses *(p.24)*

- **DDoS 방어의 4개 라인**
  1. **Attack prevention and preemption** — 공격 **전**
  2. **Attack detection and filtering** — 공격 **중**
  3. **Attack source traceback and identification** — 공격 **중·후**
  4. **Attack reaction** — 공격 **후**
- 이런 공격은 **완전히 막을 수 없다**
- 때로는 **트래픽 폭증이 정당한 것**일 수도 있다

## 12. DoS Attack Prevention *(p.25~26)*

- **Spoofed source address 차단** *(p.25)*
  - 가능한 한 **source에 가까운 라우터**에서
  - 필터로 **claimed source address로 돌아가는 경로가 현재 패킷이 온 경로와 같은지** 확인
  - **Cisco router**: `ip verify unicast reverse-path`
    - 라우터로 들어오는 패킷을 검사해, **source IP 주소가 패킷이 도착한 같은 인터페이스를 가리키는 경로**를 **CEF(Cisco Express Forwarding) Table**에 가지고 있지 않으면 **패킷을 버린다**
- **수정된 TCP connection 처리 코드** 사용 *(p.25)*
  - 핵심 정보를 **암호학적으로 인코딩한 cookie**를 서버의 **initial sequence number**로 전송
    - 정당한 client는 **증가된 sequence number cookie**를 담은 **ACK**로 응답
  - 테이블이 overflow되면 **미완료 연결 엔트리를 테이블에서 제거**
- **IP directed broadcast 차단** *(p.26)*
  - **IP directed broadcast**: 보내는 머신에 직접 연결되지 않은 **서브넷의 broadcast 주소**로 보내는 datagram
- **의심스러운 서비스와 조합 차단**
- 애플리케이션 공격은 **graphical puzzle(captcha)** 로 **정당한 사람의 요청**을 구분해 관리
- **일반적인 좋은 시스템 보안 관행**
- 고성능·고신뢰성이 필요하면 **mirrored and replicated servers** 사용

## 13. Responding to DoS Attacks *(p.27~28)*

- 사전 준비 *(p.27)*
  - **Antispoofing, IP directed broadcast 차단, rate limiting 필터**가 미리 구현돼 있어야 함
  - 이상적으로 **network monitor와 IDS**로 비정상 트래픽 패턴을 탐지·통보
- 대응 절차 *(p.28)*
  1. **공격 유형 식별**
     - 패킷 **캡처·분석**
     - 공격 트래픽을 **upstream**에서 차단하는 필터 설계
     - 또는 **시스템/애플리케이션 버그**를 식별·수정
  2. **ISP가 패킷 흐름을 source까지 추적**
     - 어렵고 오래 걸릴 수 있음
     - **법적 조치**를 계획한다면 필수
  3. **Contingency plan 실행**
     - **대체 백업 서버**로 전환
     - **새 사이트에 새 주소로 새 서버**를 가동
  4. **Incident response plan 갱신**
     - 향후 대응을 위해 공격과 대응을 분석

## 14. Summary *(p.29)*

- Denial-of-service attacks: DoS의 본질 / Classic DoS / Source address spoofing / SYN spoofing
- Flooding attacks: ICMP flood / UDP flood / TCP SYN flood
- Defenses against DoS attacks, Responding to a DoS attack
- Distributed denial-of-service attacks
- Application-based bandwidth attacks: HTTP-based attacks
- Reflection & amplifier attacks: Reflection attacks / DNS amplification attacks

## 수업에서 다룬 섹션

1. DoS 정의와 공격 대상 자원 3분류
2. Classic DoS: flooding ping
3. Source address spoofing
4. Flooding attacks (ICMP/UDP/SYN)
5. SYN spoofing
6. HTTP 기반 공격 (HTTP flood, Slowloris)
7. DDoS
8. Botnet
9. Reflection attacks
10. DNS amplification
11. DoS 방어 4개 라인
12. DoS 공격 예방
13. DoS 대응 절차
14. Summary
