# Chapter 1: Introduction

*Computer Networking: A Top-Down Approach, 8th ed. (Kurose & Ross)*

## 1. What is the Internet?

### "Nuts and bolts" view *(슬라이드 p.3, p.5)*
인터넷을 구성하는 물리적 요소들.

- **hosts (= end systems)**: 네트워크 앱이 돌아가는 종단 장치. 인터넷의 "edge"에 위치.
- **packet switches**: 패킷(데이터 조각)을 forward하는 장치 — router, switch
- **communication links**: fiber, copper, radio, satellite 등. 전송 속도(bandwidth)로 성능 표현 (예: 1Gbps)
- **networks**: device + router + link의 집합, 하나의 조직이 관리
- **Internet**: "network of networks" — 상호연결된 ISP들의 집합
- **protocols**: 메시지 송수신을 통제하는 규칙. 예) HTTP, TCP, IP, WiFi, 4G/5G, Ethernet → 데이터를 주고받는 방법(절차)
- **Internet standards**: RFC(Request for Comments, 표준 문서 — 1만 개 이상), IETF(Internet Engineering Task Force, 표준을 만드는 기관/단체)

### "Services" view *(슬라이드 p.6)*
Internet = 애플리케이션에 서비스를 제공하는 *infrastructure*.
- Web, streaming, teleconferencing, email, game, e-commerce, social media 등에 서비스 제공
- 분산 애플리케이션에 **programming interface(API)** 제공 — 앱이 인터넷 전송 서비스를 사용하도록 연결해주는 "hook"

### What's a protocol? *(슬라이드 p.7~8)*
> Protocols define the **format**, **order** of messages sent and received among network entities, and **actions taken** on message transmission, receipt.

사람 사이의 규약(인사, 질문 등)과 마찬가지로, 네트워크 프로토콜은 컴퓨터(장치) 간의 규약이다. 인터넷의 모든 통신 활동은 프로토콜에 의해 지배된다.

예: TCP 연결 요청 → 연결 응답 → GET 요청 → file 응답 (사람의 "Hi" → "Hi" → "몇 시야?" → "2:00"와 같은 구조)

---

## 2. Network Edge *(슬라이드 p.9~25)*

**Network edge** = hosts(clients/servers, servers는 주로 데이터센터에 밀집) *(p.10~12)*

### Access networks — host를 edge router에 어떻게 연결하는가? *(슬라이드 p.13)*
1. **residential access nets** (가정)
2. **institutional access networks** (학교, 회사)
3. **mobile access networks** (WiFi, 4G/5G)

#### Cable-based access (HFC: hybrid fiber coax) *(슬라이드 p.14~15)*
- data/TV가 서로 다른 주파수로 **shared cable** 위에서 전송됨 (FDM: frequency division multiplexing)
- 비대칭: downstream 최대 40Mbps~1.2Gbps, upstream 30~100Mbps
- cable headend의 CMTS(cable modem termination system)까지 광섬유+동축 공유망으로 연결, 이후 ISP로

#### DSL (Digital Subscriber Line) *(슬라이드 p.16)*
- 기존 전화선을 그대로 이용, central office의 DSLAM까지 **dedicated line**
- voice와 data가 서로 다른 주파수로 전송 (data→인터넷, voice→전화망)
- downstream 24~52Mbps, upstream 3.5~16Mbps (dedicated라 cable보다 안정적이지만 보통 더 느림)

#### Home networks *(슬라이드 p.17)*
WiFi AP + router/firewall/NAT + cable/DSL modem이 보통 한 박스로 결합되어 있음. 유선 Ethernet은 최대 1Gbps.

#### Wireless access networks *(슬라이드 p.18~19)*
- **WLAN (WiFi)**: 건물 내/주변(~100ft), 802.11 시리즈. Wi-Fi 4~8까지 세대가 있으며 속도가 계속 증가 (최신 Wi-Fi 7/8은 수 Gbps~수십 Gbps)
- **wide-area cellular**: 이동통신사 제공, 수십 km 범위, 4G/5G

#### Enterprise networks *(슬라이드 p.20)*
Ethernet switch(유선, 100Mbps~10Gbps) + WiFi AP(무선) 조합으로 기관 내부망 구성, institutional router를 통해 ISP로 연결

#### Data center networks *(슬라이드 p.21)*
수백~수천 대 서버를 연결하는 고대역폭(10s~100s Gbps) 링크

### Physical media (링크의 물리적 매체) *(슬라이드 p.23~25)*
- **bit**: 송신자-수신자 쌍 사이를 전파(propagate)되는 단위
- **guided media** (신호가 고체 매체 내에서 전파): copper, fiber, coax *(p.23~24)*
  - **Twisted pair (TP, 랜선)**: 구리선 두 가닥. Cat5(100Mbps~1Gbps), Cat6(10Gbps) *(p.23)*
  - **Coaxial cable (동축)**: 두 개의 동심 구리 도체. 양방향, broadband(여러 주파수 채널 다중화) *(p.24)*
  - **Fiber optic**: 유리 섬유로 빛 펄스 전송. 고속(10s~100s Gbps), 저에러율, 전자기 노이즈에 강함 *(p.24)*
- **unguided media** (신호가 자유롭게 전파): radio *(p.25)*
  - WiFi(10~100s Mbps, 수십m), wide-area 4G/5G(10s Mbps, ~10km), Bluetooth(단거리), terrestrial microwave(45Mbps), satellite(<100Mbps, 정지궤도는 왕복지연 270msec)

---

## 3. Network Core *(슬라이드 p.26~46)*

**Network core** = 라우터들의 mesh(interconnected routers) → "network of networks" *(p.26~27)*

### Packet switching *(슬라이드 p.27~30)*
- host가 애플리케이션 메시지를 **packet**으로 쪼갠다
- 네트워크는 패킷을 source→destination 경로 상의 라우터를 거쳐 forward한다

두 가지 핵심 기능: *(p.28~30)*
- **Forwarding (= switching)**: local action. 라우터가 들어온 패킷을 로컬 forwarding table을 보고 알맞은 output link로 이동시키는 것
- **Routing**: global action. source-destination 경로를 결정하는 것 (routing algorithm이 forwarding table을 만듦)

#### Store-and-forward *(슬라이드 p.22, p.31)*
전체 패킷(L bit)이 라우터에 다 도착해야 다음 링크로 전송을 시작할 수 있음.
- 전송 지연(transmission delay) = L/R (초)
- 예: L=10Kbit, R=100Mbps → 한 홉 전송지연 = 0.1msec

#### Queueing & loss *(슬라이드 p.32~33)*
도착률(arrival rate)이 출력 링크의 전송률(transmission rate)을 초과하면:
- 패킷이 큐에서 대기 (queueing delay)
- 라우터 버퍼(메모리)가 가득 차면 패킷 drop (loss)

### Circuit switching (패킷 스위칭의 대안) *(슬라이드 p.34~35)*
- source-destination 간 call을 위해 **end-to-end 자원을 미리 예약/할당**
- 전용 자원 → 공유 없음, 회선급(guaranteed) 성능 보장
- 사용 안 해도 그 구간(circuit segment)은 idle 상태로 남음 (낭비)
- 전통적인 전화망에서 주로 사용
- **FDM**: 주파수를 좁은 대역으로 나눠 call마다 할당
- **TDM**: 시간을 슬롯으로 나눠 call마다 주기적 슬롯 할당

### Packet switching vs circuit switching *(슬라이드 p.36~37)*
예시: 1Gbps 링크, 사용자당 활성 시 100Mbps, 활성 확률 10%
- circuit switching: 딱 **10명**만 동시 수용 가능 (자원이 고정 예약되므로)
- packet switching: 35명이 있어도 10명 넘게 동시 활성일 확률 < 0.0004 (resource sharing 덕분에 훨씬 많은 사용자 수용 가능)

packet switching이 항상 우월한 건 아님:
- 장점: bursty data에 적합, 자원 공유, call setup 불필요, 단순
- 단점: 과도한 congestion 가능 (버퍼 오버플로우로 인한 delay/loss) → 신뢰성 있는 전송, 혼잡 제어를 위한 프로토콜이 필요

### Internet structure: "network of networks" *(슬라이드 p.38~46)*
호스트는 access ISP를 통해 인터넷에 연결. access ISP들이 상호연결되어야 어디서든 두 호스트가 통신 가능.

접근 ISP 수백만 개를 어떻게 연결할까? (단계적으로 발전)
1. 모든 access ISP를 직접 서로 연결 → O(N²), scale 안 됨 *(p.39~40)*
2. 하나의 global transit ISP에 연결 → customer-provider 경제적 계약 관계 *(p.41)*
3. global ISP가 여러 개(경쟁사) 등장 → 서로 연결 필요 → **IXP(Internet Exchange Point)**, **peering link** 등장 *(p.42~43)*
4. 지역 ISP(regional ISP) 등장 → access net을 ISP에 연결 *(p.44)*
5. content provider network(Google, Microsoft, Akamai 등)가 자체 네트워크를 구축, 서비스/콘텐츠를 end user 가까이 배치 *(p.45)*

최종 구조 *(슬라이드 p.46)*: 중심에 소수의 대형 네트워크
- **tier-1 ISP** (Level 3, Sprint, AT&T, NTT 등): 전국/국제 커버리지
- **content provider network** (Google, Facebook 등): 자체 데이터센터를 인터넷에 연결하는 사설망, tier-1/regional ISP를 우회하는 경우도 많음

---

## 4. Performance: Loss, Delay, Throughput *(슬라이드 p.47~59)*

### Packet delay: 4가지 요소 *(슬라이드 p.49~50)*
```
d_nodal = d_proc + d_queue + d_trans + d_prop
```
- **d_proc (processing delay)**: 비트 에러 체크, output link 결정 등. 보통 수 마이크로초 미만
- **d_queue (queueing delay)**: output link 전송을 위해 대기하는 시간. 라우터의 congestion 정도에 따라 달라짐
- **d_trans (transmission delay)**: L/R (L=패킷 길이 bit, R=링크 전송률 bps)
- **d_prop (propagation delay)**: d/s (d=물리적 링크 길이, s=전파 속도 ~2×10⁸ m/sec)

d_trans와 d_prop은 성격이 매우 다름 — trans는 "패킷을 링크에 밀어넣는" 시간, prop은 "비트가 물리적으로 이동하는" 시간.

**caravan(카라반) 비유** *(슬라이드 p.51~52)*: car = bit, caravan = packet, toll booth = link(router). 톨부스 통과시간 = transmission delay, 두 부스 사이 이동시간 = propagation delay.

### Traffic intensity와 queueing delay *(슬라이드 p.53)*
```
La/R  (a=평균 패킷 도착률, L=패킷 길이, R=링크 대역폭)
```
= "arrival rate of bits" / "service rate of bits" = **traffic intensity**

- La/R ≈ 0: 평균 대기지연 작음
- La/R → 1: 평균 대기지연 급격히 커짐
- La/R > 1: 서비스 가능한 양보다 더 많은 작업이 도착 → 평균 지연 무한대!

### traceroute *(슬라이드 p.54~55)*
실제 인터넷 경로/지연을 측정하는 도구. 경로상의 라우터 i마다 TTL=i인 패킷 3개를 보내고, 라우터가 발신자에게 되돌려주는 시간을 측정. `* * *`는 응답 없음(probe 손실 또는 라우터 무응답).

### Packet loss *(슬라이드 p.56)*
큐(버퍼)의 용량은 유한. 가득 찬 큐에 도착한 패킷은 drop(loss)됨. 손실된 패킷은 이전 노드, source end system에 의해 재전송될 수도, 안 될 수도 있음.

### Throughput *(슬라이드 p.57~59)*
송신자→수신자로 비트가 전송되는 속도(bits/time).
- **instantaneous**: 특정 시점의 속도
- **average**: 더 긴 시간에 걸친 평균 속도
- **bottleneck link**: end-to-end 경로에서 throughput을 제한하는 링크 (경로 상 가장 느린 링크가 병목)
- 경로에 R_s, R_c 두 구간이 있으면 throughput = min(R_s, R_c)
- 여러 connection이 backbone 링크 R을 공유하면: per-connection throughput = min(R_c, R_s, R/(connection 수))

---

## 5. Security *(슬라이드 p.60~65)*

인터넷은 원래 보안을 염두에 두고 설계되지 않음 — "서로 신뢰하는 사용자들이 투명한 네트워크에 붙어있다"는 게 원래 비전이었음. 이후 프로토콜 설계자들이 계속 보안을 "따라잡는" 중.

### 공격 유형 *(슬라이드 p.62~64)*
- **packet sniffing**: broadcast media(공유 Ethernet, 무선)에서 promiscuous 네트워크 인터페이스로 지나가는 모든 패킷(비밀번호 포함)을 읽음. (Wireshark = 무료 패킷 스니퍼) *(p.62)*
- **IP spoofing**: 가짜 출발지 주소로 패킷을 주입 *(p.63)*
- **DoS (Denial of Service)**: 공격자가 봇넷 등으로 대량의 가짜 트래픽을 보내 서버/대역폭 자원을 고갈시켜 정상 트래픽을 차단. (target 선정 → 여러 호스트 침입 → 침해된 호스트들에서 target으로 패킷 전송) *(p.64)*

### 방어선 *(슬라이드 p.65)*
- **authentication**: 신원 증명 (셀룰러망은 SIM카드로 하드웨어 인증, 전통적 인터넷엔 그런 하드웨어 보조 없음)
- **confidentiality**: 암호화(encryption)
- **integrity checks**: 디지털 서명으로 변조 방지/탐지
- **access restrictions**: 비밀번호 보호 VPN
- **firewalls**: access/core network의 middlebox. 기본적으로 차단(off-by-default), 송신자/수신자/애플리케이션 제한, DoS 탐지/대응

---

## 6. Protocol Layers & Service Models *(슬라이드 p.66~81)*

### Why layering? *(슬라이드 p.67~70)*
복잡한 시스템을 설계/논의하는 접근법.
- 명시적 구조 → 시스템 구성요소와 관계를 식별 가능 (layered reference model)
- 모듈화 → 유지보수/업데이트 용이. 한 계층의 구현이 바뀌어도 나머지 시스템에는 투명함

비유: 항공 여행 시스템 — ticketing, baggage, gate, runway, airplane routing 각각이 하나의 layer이고, 각 layer는 자신의 내부 작업 + 아래 layer가 제공하는 서비스를 이용해 자신의 서비스를 구현한다.

### Internet protocol stack (5 layers) *(슬라이드 p.71)*
| Layer | 역할 | 예시 프로토콜 |
|---|---|---|
| **application** | 네트워크 앱 지원 | HTTP, IMAP, SMTP, DNS |
| **transport** | process-process 데이터 전송 | TCP, UDP |
| **network** | 출발지→목적지 datagram 라우팅 | IP, routing protocols |
| **link** | 인접한 네트워크 요소 간 데이터 전송 | Ethernet, 802.11(WiFi), PPP |
| **physical** | 회선 위의 비트 | — |

### OSI 7-layer model *(슬라이드 p.72, p.74)*
ISO(International Standards Organization)가 만든 국제표준. Internet stack의 5계층 + **presentation**(데이터 번역/암호화/압축) + **session**(세션 수립/관리/종료) 2개가 더해진 7계층 모델. 실제 인터넷은 이 두 계층 기능을 필요시 애플리케이션이 직접 구현.

```
7 Application   — 네트워크 자원 접근 허용
6 Presentation  — 데이터 번역/암호화/압축
5 Session       — 세션 수립/관리/종료
4 Transport     — 신뢰성 있는 process-to-process 전달, 에러 복구
3 Network       — 패킷을 출발지→목적지로 이동, 인터네트워킹
2 Data link     — 비트를 프레임으로 조직, hop-to-hop 전달
1 Physical      — 매체 위로 비트 전송, 기계적/전기적 스펙
```

### TCP/IP 계층별 실제 프로토콜 매핑 *(슬라이드 p.75)*
OSI 7계층 관점에서 TCP/IP 스택의 각 계층에 실제로 속하는 프로토콜들:

| 계층 | 소속 프로토콜 |
|---|---|
| Application (~ OSI 5-7) | SMTP, FTP, HTTP, DNS, SNMP, TELNET 등 |
| Transport | SCTP, **TCP**, UDP |
| Network (internet) | **IP** (+ ICMP, IGMP는 제어용, ARP/RARP는 주소 변환용) |
| Data link / Physical | 하위 네트워크가 정의하는 프로토콜 (host-to-network) |

- ARP(Address Resolution Protocol) = 이름 그대로 "주소 해석" — IP주소→MAC주소 변환
- RARP(Reverse ARP) = 반대로 MAC주소→IP주소 변환
- ICMP(Internet Control Message Protocol) = 오류/제어 메시지 (예: traceroute, ping이 이걸 씀)
- IGMP(Internet Group Management Protocol) = 멀티캐스트 그룹 관리

### Encapsulation *(슬라이드 p.76~81)*
각 계층은 상위 계층에서 받은 데이터에 자신의 헤더를 붙여(encapsulate) 다음 계층으로 넘긴다. **마트료시카 인형**처럼 겹겹이 감싸는 구조.

- application: **message** (M)
- transport: **segment** (H_t + M) — process 간 전송(예: 신뢰성 있게)을 위해 M을 캡슐화
- network: **datagram** (H_n + H_t + M) — host 간 전송을 위해 segment를 캡슐화
- link: **frame** (H_l + H_n + H_t + M) — 인접 호스트 간 전송을 위해 datagram을 캡슐화

**end-to-end view**: source에서 destination까지 가는 동안 중간 노드(switch는 link/physical만, router는 network/link/physical까지)는 각자 필요한 계층까지만 열어보고 처리한 뒤 다시 캡슐화해서 넘긴다.

---

## 7. Internet History (요약) *(슬라이드 p.83~87)*

| 시기 | 주요 사건 | 슬라이드 |
|---|---|---|
| **1961-1972** | Kleinrock 큐잉이론(1961), Baran 군용 패킷교환(1964), ARPAnet 고안(1967)→첫 노드(1969)→공개 데모(1972), NCP, 첫 이메일, 노드 15개 | p.83 |
| **1972-1980** | ALOHAnet(1970), Cerf&Kahn 인터네트워킹 아키텍처(1974) — minimalism/autonomy, best-effort, stateless routing, decentralized control 원칙이 오늘날 인터넷 아키텍처를 정의, Ethernet(1976), 사설 프로토콜(DECnet 등), 노드 200개(1979) | p.84 |
| **1980-1990** | TCP/IP 배포(1983), SMTP(1982), DNS(1983), FTP(1985), TCP 혼잡제어(1988), CSnet/BITnet/NSFnet 등 신규 국가망, 호스트 10만 개 | p.85 |
| **1990-2000s** | ARPAnet 퇴역, NSFnet 상업적 사용 허용(1991), Web(HTML/HTTP: Berners-Lee, Mosaic 1994), 상업화, 인스턴트 메시징/P2P, 네트워크 보안 부상, 호스트 5천만+/사용자 1억+ | p.86 |
| **2005-현재** | 광대역 가정 접속 확대, SDN(2008), 4G/5G/WiFi 고속 무선 확산, 대형 서비스업체 자체망 구축, 클라우드(AWS, Azure), 모바일 기기가 유선 초과(2017), ~150억 대 기기 연결(2023) | p.87 |

---

## Chapter 1 핵심 요약 *(슬라이드 p.88)*

- 인터넷의 구조(nuts and bolts / services 두 관점), 프로토콜의 정의
- Network edge(hosts, access network, physical media) vs Network core(packet/circuit switching, Internet structure)
- 성능: delay(4요소), loss, throughput
- 보안 개요
- 계층화(layering)와 캡슐화(encapsulation)
- 인터넷 역사

이 챕터는 "feel"과 용어를 잡는 개론 — 각 주제(access network 세부, 라우팅, 전송 계층, 보안 등)는 이후 장에서 깊게 다룸.
