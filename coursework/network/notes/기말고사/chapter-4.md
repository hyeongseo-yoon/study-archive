# Chapter 4: Network Layer: Data Plane

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

*Computer Networking: A Top-Down Approach, 8th ed. (Kurose & Ross)*

이 자료는 슬라이드 우측 하단에 "Network Layer: 4-N" 형식의 쪽번호가 있어, 아래 `p.N`은 그 N을 그대로 가리킨다. (마지막 Middlebox 파트 슬라이드는 쪽번호가 인쇄되지 않아 앞 슬라이드에서 이어 센 값이다.)

## 1. Network Layer 개요 *(p.2~12)*

### 목표와 로드맵 *(p.2~3)*
- 목표: data plane 중심으로 network layer service model, forwarding vs routing, router 내부 동작, addressing, generalized forwarding, Internet architecture 이해
- 인터넷에서의 구현: IP protocol, NAT, middlebox
- 로드맵: Network layer overview(data/control plane) → What's inside a router → IP(datagram format, addressing, NAT, IPv6) → Generalized Forwarding·SDN(match+action, OpenFlow) → Middleboxes

### Network-layer services and protocols *(p.4)*
- 송신 host → 수신 host로 transport segment를 전달
  - sender: segment를 **datagram**으로 encapsulate해서 link layer로 넘김
  - receiver: segment를 transport layer로 deliver
- network layer protocol은 **모든 인터넷 장치(host, router)**에 존재
- **router**: 자신을 통과하는 모든 IP datagram의 header field를 검사하고, datagram을 input port에서 output port로 옮겨 end-to-end 경로를 따라 전달

### Two key network-layer functions *(p.5)*
- **forwarding**: packet을 router의 input link에서 적절한 output link로 옮기는 것
- **routing**: packet이 source에서 destination까지 가는 경로(route)를 결정하는 것 (routing algorithm)
- 여행 비유: forwarding = 한 교차로(interchange)를 통과하는 과정, routing = 출발지에서 목적지까지 여행 계획을 세우는 과정

### Data plane vs Control plane *(p.6~8)*
- **Data plane**: router별 **local** 기능. router input port에 도착한 datagram을 header 값에 따라 output port로 forward하는 방법을 결정
- **Control plane**: **network-wide** 로직. datagram이 source host에서 destination host까지 router들을 거쳐 어떻게 route될지 결정
- control plane 구현 방식 두 가지
  - **traditional routing algorithm**: 각 router 안에서 구현. 모든 router의 routing algorithm 구성요소가 control plane에서 서로 상호작용 *(p.7, Per-router control plane)*
  - **SDN(Software-Defined Networking)**: (원격) server에서 구현. remote controller가 forwarding table을 계산해서 router에 설치. 각 router의 CA(control agent)가 controller와 통신 *(p.8)*

### Network service model *(p.9~11)*
- 질문: sender → receiver로 datagram을 나르는 "channel"에 어떤 service model을 제공할까?
- 개별 datagram에 대한 서비스 예: guaranteed delivery, 40 msec 미만 delay로 guaranteed delivery
- datagram **flow**에 대한 서비스 예: in-order delivery, flow에 최소 bandwidth 보장, inter-packet spacing 변화 제한
- QoS(Quality of Service) 보장 비교표

| Architecture | Service Model | Bandwidth | Loss | Order | Timing |
|---|---|---|---|---|---|
| Internet | best effort | none | no | no | no |
| ATM | Constant Bit Rate | constant rate | yes | yes | yes |
| ATM | Available Bit Rate | guaranteed min | no | yes | no |
| Internet | Intserv Guaranteed (RFC 1633) | yes | yes | yes | yes |
| Internet | Diffserv (RFC 2475) | possible | possibly | possibly | no |

- **Internet "best effort" service**: 아무 보장도 없다. (i) destination까지의 성공적 delivery, (ii) delivery의 timing/order, (iii) end-end flow에 사용 가능한 bandwidth 모두 보장 안 함

### Reflections on best-effort service *(p.12)*
- 메커니즘이 단순해서 인터넷이 널리 배포(adopt)될 수 있었음
- bandwidth를 충분히 provisioning하면 실시간 앱(voice, video)도 "대부분의 시간 충분히 좋은" 성능
- 복제된(replicated) application-layer 분산 서비스(datacenter, CDN)가 client 네트워크 가까이 연결되어 여러 위치에서 서비스 제공 가능
- "elastic" 서비스의 congestion control이 도움
- 결론: **best-effort service model의 성공은 반박하기 어렵다**

## 2. What's inside a router *(p.13~41)*

### Router architecture overview *(p.14~15)*
- 구성: **input ports**, **high-speed switching fabric**, **output ports**, **routing processor**
- **routing/management control plane**: **software**, **millisecond** 단위로 동작 (routing processor가 담당)
- **forwarding data plane**: **hardware**, **nanosecond** 단위로 동작 (input port - switching fabric - output port)
- 비유(p.15): station manager = routing processor(control plane), roundabout = switching fabric, entry stations = input ports, exit roads = output ports

### Input port functions *(p.16~17)*
- 처리 순서: line termination(physical layer: bit-level reception) → link layer protocol(receive)(예: Ethernet, chapter 6) → **lookup, forwarding** → queueing → switch fabric
- **decentralized switching**: header field 값을 이용해 input port 메모리에 있는 **forwarding table**로 output port를 lookup ("match plus action")
- 목표: input port 처리를 **line speed**로 완료
- **input port queuing**: datagram이 switch fabric으로 들어가는 forwarding rate보다 빨리 도착하면 queueing 발생
- **destination-based forwarding**: 오직 destination IP address만 보고 forward (전통적 방식)
- **generalized forwarding**: header field 값의 임의 조합으로 forward

### Destination-based forwarding *(p.18)*
- forwarding table: Destination Address Range → Link Interface
  - `11001000 00010111 00010000 00000000` ~ `11001000 00010111 00010111 11111111` → 0
  - `11001000 00010111 00011000 00000000` ~ `11001000 00010111 00011000 11111111` → 1
  - `11001000 00010111 00011001 00000000` ~ `11001000 00010111 00011111 11111111` → 2
  - otherwise → 3
- Q: range가 이렇게 딱 떨어지지 않으면? → longest prefix matching

### Longest prefix matching *(p.19~22)*
- **longest prefix match**: forwarding table entry를 찾을 때, destination address와 **일치하는 가장 긴 address prefix**를 사용
- 표

| Destination Address Range | Link interface |
|---|---|
| `11001000 00010111 00010*** ********` | 0 |
| `11001000 00010111 00011000 ********` | 1 |
| `11001000 00010111 00011*** ********` | 2 |
| otherwise | 3 |

- 예제 1: `11001000 00010111 00010110 10100001` → 첫 번째 entry(`00010***`)에만 match → **interface 0**
- 예제 2: `11001000 00010111 00011000 10101010` → 두 번째(`00011000`)와 세 번째(`00011***`) 모두 match, 더 긴 prefix인 두 번째 선택 → **interface 1**

### Switching fabrics *(p.24~28)*
- 역할: packet을 input link에서 적절한 output link로 전달
- **switching rate**: packet이 input에서 output으로 전달되는 속도. 보통 input/output line rate의 배수로 측정. input N개면 line rate의 **N배**(NR)가 이상적
- 세 가지 주요 종류: **memory**, **bus**, **interconnection network**
- **Switching via memory** *(p.26)*: 1세대 router. CPU의 직접 제어 아래 switching하는 전통적 컴퓨터. packet이 system memory로 복사되고, 속도는 memory bandwidth에 제한됨(datagram당 bus 2번 crossing)
- **Switching via a bus** *(p.27)*: input port memory에서 output port memory로 **shared bus**를 통해 datagram 전달. **bus contention**: switching 속도가 bus bandwidth에 제한. 예: 32 Gbps bus, Cisco 5600 — access router에는 충분한 속도
- **Switching via interconnection network** *(p.28)*: crossbar, Clos network 등. 원래 multiprocessor에서 processor를 연결하려고 개발됨
  - **multistage switch**: 작은 switch를 여러 단 연결해 n×n switch 구성 (그림: 3×3 crossbar, 작은 switch로 만든 8×8 multistage)
  - **병렬성 활용**: 입구에서 datagram을 고정 길이 **cell**로 fragment → cell을 fabric으로 switch → 출구에서 datagram으로 reassemble

### Input port queuing *(p.30)*
- switch fabric이 모든 input port를 합친 속도보다 느리면 input queue에서 queueing 발생 → **queueing delay와 input buffer overflow에 의한 loss**
- **HOL(Head-of-the-Line) blocking**: queue 맨 앞의 datagram이 막혀서 뒤의 datagram들이 (output이 비어 있어도) 못 나가는 현상
- 그림: output port contention으로 한 packet만 전달 가능 → 한 packet time 뒤, 앞 packet에 막힌 다른 packet이 HOL blocking을 겪음

### Output port queuing *(p.31~32)*
- 구성: switch fabric(rate NR) → datagram buffer(queueing) → link layer protocol(send) → line termination → link(rate R)
- fabric에서 도착하는 속도가 link transmission rate보다 빠르면 **buffering 필요**. buffer가 없으면 datagram이 **congestion/buffer 부족으로 loss** 가능
- **drop policy**: 빈 buffer가 없을 때 어느 datagram을 버릴 것인가
- **scheduling discipline**: queue에 있는 datagram 중 전송할 것을 선택. priority scheduling — 누가 최고 성능을 얻는가, **network neutrality**와 연결
- p.32: 시각 t에 여러 packet이 input에서 같은 output으로 이동 → switch를 통한 도착률이 output line speed를 넘으면 buffering, **output port buffer overflow에 의한 queueing delay와 loss**
- 슬라이드 강조: "This is a really important slide"

### Buffer Management *(p.34)*
- 추상화: queue (packet arrivals → queue(waiting area) → link(server, rate R) → packet departures)
- **drop**: buffer가 가득 찼을 때 어떤 packet을 추가/버릴 것인가
  - **tail drop**: 도착한 packet을 버림
  - **priority**: priority 기준으로 drop/remove
- **marking**: congestion을 알리기 위해 어떤 packet에 mark할 것인가 (ECN, RED)

### Packet Scheduling *(p.35~38)*
- **packet scheduling**: link에서 다음에 전송할 packet을 결정. 종류: first come first served, priority, round robin, weighted fair queueing
- **FCFS** *(p.35)*: packet이 output port에 도착한 순서대로 전송. **FIFO**라고도 함
- **Priority scheduling** *(p.36)*: 도착 traffic을 분류해 class별로 queue에 넣음(분류에는 어떤 header field든 사용 가능). **buffered packet이 있는 가장 높은 priority queue**에서 packet 전송. priority class 내에서는 FCFS
  - 그림 예: arrivals 1~5, high/low priority queue에 따라 departure 순서가 1 3 2 4 5
- **Round Robin (RR)** *(p.37)*: 도착 traffic을 class별로 분류해 queue에 넣음. server가 class queue를 **순환하며 반복적으로 scan**, (있으면) 각 class에서 **완전한 packet 하나씩** 전송
- **Weighted Fair Queueing (WFQ)** *(p.38)*: **generalized Round Robin**. 각 class i가 weight wi를 가지고 매 cycle마다 wi / Σj wj 만큼의 service를 받음. class별 **최소 bandwidth 보장**

### Sidebar: Network Neutrality *(p.39~41)*
- **network neutrality**란?
  - 기술적: ISP가 자원을 어떻게 공유/할당해야 하는가 — packet scheduling, buffer management가 그 메커니즘
  - 사회·경제적 원칙: 표현의 자유 보호, 혁신과 경쟁 장려
  - 법적으로 강제되는 규칙과 정책 (나라마다 입장이 다름)
- **2015 US FCC Order (Protecting and Promoting an Open Internet)** — 세 가지 "clear, bright line" 규칙
  - **no blocking**: 합법적 content, application, service, 해롭지 않은 device를 막으면 안 됨(합리적 network management는 예외)
  - **no throttling**: content/application/service/device를 이유로 합법적 인터넷 traffic을 손상·저하시키면 안 됨(합리적 network management는 예외)
  - **no paid prioritization**: 유료 우선 처리 금지
- **ISP: telecommunications service or information service?** — 규제 관점에서 매우 중요
  - US Telecommunication Act of 1934, 1996
  - **Title II**: telecommunications service에 "common carrier duties" 부과 — 합리적 요금, 차별 금지, 규제 필요
  - **Title I**: information service에 적용 — common carrier 의무 없음(규제 안 함). 단, FCC에 "…as may be necessary in the execution of its functions" 권한 부여

## 3. IP: the Internet Protocol *(p.42~80)*

### Network Layer: Internet *(p.43)*
- host, router의 network layer 기능
  - **IP protocol**: datagram format, addressing, packet handling conventions
  - **path-selection(routing) algorithm**: routing protocol(OSPF, BGP), SDN controller로 구현 → **forwarding table** 채움
  - **ICMP protocol**: error reporting, router "signaling"
- 위에는 transport layer(TCP, UDP), 아래에는 link/physical layer

### IP Datagram format *(p.44)*
- 32 bits 폭 기준 필드 (위→아래)
  - ver(IP protocol version number), head. len(header length, bytes), type of service(diffserv 0:5, ECN 6:7), length(**total datagram length**, bytes)
  - 16-bit identifier, flgs, fragment offset — **fragmentation/reassembly**용
  - time to live(**TTL**: 남은 max hops, router마다 decrement), upper layer(상위 protocol, 예: TCP/UDP), header checksum
  - 32-bit source IP address, 32-bit destination IP address
  - options(if any): 예) timestamp, record route taken
  - payload data(가변 길이, 보통 TCP 또는 UDP segment)
- 최대 길이 64K bytes, 보통 1500 bytes 이하
- **overhead**: TCP 20 bytes + IP 20 bytes = 40 bytes + app layer overhead (TCP+IP 사용 시)

### IP addressing: introduction *(p.45~47)*
- **IP address**: host 또는 router **interface**에 연결된 **32-bit identifier**
- **interface**: host/router와 physical link 사이의 연결
  - router는 보통 interface가 여러 개, host는 보통 1~2개(예: wired Ethernet, wireless 802.11)
- **dotted-decimal notation**: 예) 223.1.1.1 = `11011111 00000001 00000001 00000001` (223, 1, 1, 1)
- interface끼리 실제로 어떻게 연결되나? (chapter 6, 7에서 학습)
  - wired Ethernet interface는 Ethernet switch로 연결
  - wireless WiFi interface는 WiFi base station으로 연결
  - 지금은 router를 거치지 않고 interface 하나가 다른 interface와 어떻게 연결되는지는 신경 쓰지 않아도 됨

### Subnets *(p.48~50)*
- **subnet**: 중간에 router를 거치지 않고 **물리적으로 서로 도달할 수 있는** device interface들의 집합
- IP address는 구조를 가짐
  - **subnet part**: 같은 subnet의 device는 상위(high order) bit가 공통
  - **host part**: 나머지 하위(low order) bit
- 예: 3개 subnet으로 이루어진 network (223.1.1.0/24, 223.1.2.0/24, 223.1.3.0/24)
- **subnet 정의 recipe**: 각 interface를 host/router에서 떼어내 고립된 "섬(island)" 네트워크를 만든다. 고립된 각 네트워크가 subnet
- **subnet mask: /24** — 상위 24 bit가 IP address의 subnet part
- 연습(p.50): 그림에서 subnet 위치와 /24 subnet address 찾기 (223.1.1/24, 223.1.2/24, 223.1.3/24, 223.1.7/24, 223.1.8/24, 223.1.9/24)

### (Obsolete) Classful addressing *(p.51~52)*
- 첫 byte의 앞 bit로 class 구분

| Class | Binary(첫 byte) | Dotted-decimal(첫 byte) | Number of Blocks | Block Size | Application |
|---|---|---|---|---|---|
| A | 0 | 0~127 | 128 | 16,777,216 | Unicast |
| B | 10 | 128~191 | 16,384 | 65,536 | Unicast |
| C | 110 | 192~223 | 2,097,152 | 256 | Unicast |
| D | 1110 | 224~239 | 1 | 268,435,456 | Multicast |
| E | 1111 | 240~255 | 1 | 268,435,456 | Reserved |

- A는 첫 byte, B는 첫 두 byte, C는 첫 세 byte가 network 부분(그림의 노란 칸)

### IP addressing: CIDR *(p.53)*
- **CIDR**: Classless InterDomain Routing ("cider"로 발음)
  - subnet 부분의 길이가 **임의**
  - address format: **a.b.c.d/x** (x = address의 subnet 부분 bit 수)
  - 예: `11001000 00010111 00010000 00000000` = **200.23.16.0/23** (앞 23 bit가 subnet part, 나머지가 host part)

### IP addresses: how to get one? *(p.54)*
- 두 가지 질문
  1. host는 자기 network 안에서 IP address(host part)를 어떻게 얻나?
  2. network는 자기 IP address(network part)를 어떻게 얻나?
- host가 IP address를 얻는 방법
  - sysadmin이 config file에 hard-code (예: UNIX의 /etc/rc.config)
  - **DHCP** (Dynamic Host Configuration Protocol): server로부터 동적으로 받음 — "plug-and-play"

### DHCP *(p.55~60)*
- 목표: host가 network에 "join"할 때 network server로부터 IP address를 동적으로 획득
  - 사용 중인 address의 **lease를 renew** 가능
  - address **재사용** 가능 (연결/켜져 있는 동안에만 address 보유)
  - network에 join/leave하는 **mobile user** 지원
- **DHCP overview** (4단계)
  1. host가 **DHCP discover** 메시지 broadcast [optional]
  2. DHCP server가 **DHCP offer** 메시지로 응답 [optional]
  3. host가 IP address 요청: **DHCP request** 메시지
  4. DHCP server가 address 전송: **DHCP ack** 메시지
- **DHCP client-server scenario** *(p.56)*: 보통 DHCP server는 router에 함께 있으며(co-located), router가 연결된 모든 subnet에 서비스. 해당 network의 address가 필요한 client가 도착
- **메시지 교환 예** *(p.57)* (DHCP server: 223.1.2.5, arriving client)
  - **DHCP discover**: src 0.0.0.0, 68 / dest 255.255.255.255, 67 / yiaddr 0.0.0.0 / transaction ID 654 — "Is there a DHCP server out there?"
  - **DHCP offer**: src 223.1.2.5, 67 / dest 255.255.255.255, 68 / yiaddr 223.1.2.4 / transaction ID 654 / lifetime 3600 secs — "I'm a DHCP server! Here's an IP address you can use"
  - **DHCP request**: src 0.0.0.0, 68 / dest 255.255.255.255, 67 / yiaddr 223.1.2.4 / transaction ID 655 / lifetime 3600 secs — "OK. I would like to use this IP address!"
  - **DHCP ACK**: src 223.1.2.5, 67 / dest 255.255.255.255, 68 / yiaddr 223.1.2.4 / transaction ID 655 / lifetime 3600 secs — "OK. You've got that IP address!"
  - 위 두 단계(discover, offer)는 client가 이전에 할당받은 network address를 기억하고 재사용하려는 경우 생략 가능 [RFC 2131]
- **DHCP: more than IP addresses** *(p.58)* — DHCP는 subnet 상의 할당 IP address 외에도 반환 가능
  - client의 **first-hop router** address
  - **DNS server**의 이름과 IP address
  - **network mask** (address의 network 부분 vs host 부분 표시)
- **DHCP example** *(p.59~60)*
  - 접속하는 laptop이 DHCP로 IP address, first-hop router address, DNS server address를 얻음
  - DHCP REQUEST 메시지는 UDP로, UDP는 IP로, IP는 Ethernet으로 encapsulate
  - Ethernet frame이 LAN에서 broadcast(dest: FFFFFFFFFFFF)되어 DHCP server가 돌고 있는 router에서 수신. Ethernet → IP → UDP → DHCP 순으로 de-mux
  - DHCP server가 client의 IP address, first-hop router의 IP address, DNS server의 이름과 IP address를 담은 **DHCP ACK**를 만들어 encapsulate해 client로 forward, client에서 DHCP까지 de-mux
  - client는 이제 자신의 IP address, DNS server의 이름과 IP address, first-hop router의 IP address를 알게 됨

### IP addresses: network의 address 획득 *(p.61)*
- Q: network는 IP address의 subnet part를 어떻게 얻나? A: **provider ISP의 address space 중 일부를 할당**받는다
- 예: ISP block `11001000 00010111 00010000 00000000` = 200.23.16.0/20 → 8개 block으로 나눠 조직에 할당
  - Organization 0: 200.23.16.0/23
  - Organization 1: 200.23.18.0/23
  - Organization 2: 200.23.20.0/23
  - …
  - Organization 7: 200.23.30.0/23

### Hierarchical addressing *(p.62~64)*
- **route aggregation**: 계층적 addressing 덕분에 routing 정보를 효율적으로 advertise 가능
  - Fly-By-Night-ISP가 인터넷에 "200.23.16.0/20으로 시작하는 주소는 전부 나한테 보내라"고 하나만 광고 (조직 0~7 전체를 대표). ISPs-R-Us는 "199.31.0.0/16으로 시작하는 주소는 나한테 보내라"고 광고
- **more specific routes**: Organization 1이 Fly-By-Night-ISP에서 ISPs-R-Us로 옮기는 경우
  - ISPs-R-Us가 "199.31.0.0/16 **또는 200.23.18.0/23**"을 광고 — Organization 1에 대한 **더 구체적인 route**
  - (longest prefix matching 덕분에 200.23.18.0/23 대상 packet은 ISPs-R-Us로 감)

### IP addressing: last words *(p.65)*
- Q: ISP는 address block을 어떻게 얻나? A: **ICANN**(Internet Corporation for Assigned Names and Numbers)
  - 5개 regional registry(RR)를 통해 IP address를 할당(RR이 다시 local registry에 할당할 수 있음)
  - DNS root zone을 관리하고 개별 TLD(.com, .edu, …) 관리 권한을 위임
- Q: 32-bit IP address가 충분한가?
  - ICANN이 마지막 IPv4 address chunk를 RR에 할당한 것이 **2011년**
  - **NAT**가 IPv4 address space 고갈 완화에 도움
  - **IPv6**는 128-bit address space
  - Vint Cerf 인용: "Who the hell knew how much address space we needed?" (IPv4 address를 32 bit로 정한 결정을 돌아보며)

### NAT: network address translation *(p.67~72)*
- **NAT**: 외부 세계 입장에서는 local network의 모든 device가 **IPv4 address 하나**를 공유
  - local network를 떠나는 모든 datagram은 같은 source NAT IP address(예: 138.76.29.7)를 갖지만 **source port number는 다름**
  - local network 안(예: 10.0.0/24)에서는 source/destination 모두 10.0.0/24 address를 (평소처럼) 사용
- local network의 device는 **private IP address space**의 32-bit address를 가지며, 이는 local network에서만 사용 가능
  - **Addresses for private networks** *(p.71)*

| Range | Total |
|---|---|
| 10.0.0.0 ~ 10.255.255.255 (10/8) | 2^24 |
| 172.16.0.0 ~ 172.31.255.255 (172.16/12) | 2^20 |
| 192.168.0.0 ~ 192.168.255.255 (192.168/16) | 2^16 |

- **장점** *(p.68)*
  - provider ISP로부터 모든 device에 대해 IP address **하나만** 필요
  - local network host의 address를 외부에 알리지 않고 변경 가능
  - local network device의 address를 바꾸지 않고 ISP 변경 가능
  - **보안**: local net 안의 device는 외부 세계가 직접 addressing하거나 볼 수 없음
- **구현** *(p.69)*: NAT router는 (투명하게) 다음을 해야 함
  - **outgoing datagram**: 모든 outgoing datagram의 (source IP address, port #)를 (NAT IP address, new port #)로 교체. 원격 client/server는 (NAT IP address, new port #)를 destination address로 삼아 응답
  - **NAT translation table**에 모든 (source IP address, port #) ↔ (NAT IP address, new port #) 변환 쌍을 기억
  - **incoming datagram**: 모든 incoming datagram의 destination field에 있는 (NAT IP address, new port #)를 table에 저장된 (source IP address, port #)로 교체
- **예** *(p.70)*
  1. host 10.0.0.1이 128.119.40.186, 80으로 datagram 전송 (S: 10.0.0.1, 3345 / D: 128.119.40.186, 80)
  2. NAT router가 source address를 10.0.0.1, 3345 → 138.76.29.7, 5001로 바꾸고 table 갱신 (WAN side `138.76.29.7, 5001` ↔ LAN side `10.0.0.1, 3345`)
  3. 응답 도착 (S: 128.119.40.186, 80 / D: 138.76.29.7, 5001)
  4. NAT router가 destination을 138.76.29.7, 5001 → 10.0.0.1, 3345로 바꿔 전달
- **NAT는 논쟁적** *(p.72)*
  - router는 layer 3까지만 처리해야 한다
  - address "부족"은 IPv6로 해결해야 한다
  - **end-to-end argument 위반** (network layer 장치가 port # 조작)
  - **NAT traversal**: NAT 뒤의 server에 client가 접속하려면?
- 그럼에도 NAT는 계속 쓰임: 가정/기관 network, 4G/5G cellular net에서 광범위하게 사용

### IPv6 *(p.73~80)*
- **동기**
  - 초기 동기: 32-bit IPv4 address space가 곧 모두 할당될 것
  - 추가 동기: **40-byte 고정 길이 header**로 처리/forwarding 속도 향상, "flow"에 대한 서로 다른 network-layer 처리 가능
- **IPv6 datagram format** *(p.74)*
  - 필드: ver, pri(priority), flow label, payload len, next hdr, hop limit, source address(128 bits), destination address(128 bits), payload(data)
  - **priority**: flow 내 datagram 간 priority 구분
  - **flow label**: 같은 "flow"의 datagram을 식별 ("flow" 개념은 잘 정의되어 있지 않음)
  - **IPv4와 비교해 없어진 것**
    - **checksum 없음** (router 처리 속도를 높이기 위해)
    - **fragmentation/reassembly 없음**
    - **options 없음** (upper-layer, next-header protocol로 사용 가능)
- **Transition from IPv4 to IPv6** *(p.75)*
  - 모든 router를 동시에 upgrade할 수 없음 → **"flag day" 없음**
  - IPv4와 IPv6 router가 섞인 network는 어떻게 동작? → **tunneling**: IPv6 datagram을 IPv4 router들 사이에서 **IPv4 datagram의 payload로** 운반 ("packet within a packet")
  - tunneling은 다른 맥락(4G/5G)에서도 광범위하게 사용
  - 그림: IPv4 header field(IPv4 source, dest addr) + IPv4 payload 안에 IPv6 header field(IPv6 source, dest addr) + UDP/TCP payload(IPv6 datagram)
- **Tunneling and encapsulation** *(p.76~77)*
  - Ethernet으로 연결된 두 IPv6 router: IPv6 datagram이 link-layer frame의 payload로 들어감 (평소와 같음)
  - IPv4 network로 연결된 두 IPv6 router: IPv4 tunnel을 통해 IPv6 datagram이 **IPv4 datagram의 payload**로 들어감
- **Tunneling 예** *(p.78)*: A, B, E, F는 IPv6 (B, E는 IPv6/v4), C, D는 IPv4
  - logical view: A-B-E-F가 IPv6로 직접 연결된 것처럼 보임
  - physical view: B-C-D-E 구간은 IPv4. A→B는 IPv6 datagram(Flow X, Src A, Dest F). B에서 이 datagram 전체를 IPv4 datagram(src B, dest E)의 payload에 넣어 C, D를 거쳐 E까지 전달("IPv6 inside IPv4"). E에서 IPv4 header를 벗겨 IPv6 datagram을 E→F로 전달
  - 주의: 안쪽 IPv6의 source/destination은 A, F, 바깥 IPv4 header의 source/destination은 B, E
- **IPv6 adoption** *(p.79~80)*
  - Google: 약 40%의 client가 IPv6로 서비스에 접근(2023), NIST: 미국 정부 도메인의 1/3이 IPv6 지원
  - 배포·사용에 **매우 오랜 시간** — 25년 넘게 진행 중. 지난 25년간 application-level 변화(WWW, social media, streaming media, gaming, telepresence 등)와 비교. Why? (슬라이드가 던지는 질문)

## 4. Generalized Forwarding, SDN *(p.81~91)*

### Generalized forwarding: match plus action *(p.82)*
- 복습: 각 router는 forwarding table(= **flow table**)을 가짐
- **"match plus action" abstraction**: 도착한 packet의 bit를 match하고 action을 수행
  - **destination-based forwarding**: destination IP address 기준으로 forward
  - **generalized forwarding**: 여러 header field로 action 결정 가능, 가능한 action도 다양 (drop/copy/modify/log packet)

### Flow table abstraction *(p.83~84)*
- **flow**: header field 값으로 정의됨 (link-, network-, transport-layer field)
- generalized forwarding = 단순한 packet-handling rule
  - **match**: packet header field의 pattern 값
  - **actions**: 매치된 packet에 대해 drop, forward, modify, 또는 controller로 전송
  - **priority**: 겹치는 pattern을 구별
  - **counters**: #bytes, #packets
- router의 flow table이 router의 match+action rule을 정의
- 예 (`*` = wildcard)
  - src=\*.\*.\*.\*, dest=3.4.\*.\* → forward(2)
  - src=1.2.\*.\*, dest=\*.\*.\*.\* → drop
  - src=10.1.2.3, dest=\*.\*.\*.\* → send to controller

### OpenFlow: flow table entries *(p.85)*
- entry = **Match** + **Action** + **Stats**(packet + byte counters)
- Action: (1) packet을 port(s)로 forward (2) packet drop (3) header field modify (4) encapsulate해서 controller로 forward
- match할 header field: Ingress Port, Src MAC, Dst MAC, Eth Type, VLAN ID, VLAN Pri(이상 link layer), IP Src, IP Dst, IP Proto, IP ToS(network layer), TCP/UDP Src Port, TCP/UDP Dst Port(transport layer)

### OpenFlow: examples *(p.86~87)*
- **Destination-based forwarding**: IP Dst = 51.6.0.8 → action port6 (51.6.0.8로 가는 IP datagram은 router output port 6으로 forward)
- **Firewall**: TCP d-port = 22 → drop (TCP port 22(ssh)로 가는 모든 datagram을 막음)
- **Firewall**: IP Src = 128.119.1.1 → drop (host 128.119.1.1이 보낸 모든 datagram을 막음)
- **Layer 2 destination-based forwarding**: MAC dst = 22:A7:23:11:E1:02 → port3 (해당 destination MAC의 layer 2 frame을 output port 3으로)

### OpenFlow abstraction *(p.88)*
- match+action이 서로 다른 종류의 장치를 **하나로 통합**하는 abstraction
  - **Router**: match = longest destination IP prefix / action = link로 forward
  - **Switch**: match = destination MAC address / action = forward or flood
  - **Firewall**: match = IP address와 TCP/UDP port number / action = permit or deny
  - **NAT**: match = IP address와 port / action = address와 port rewrite

### OpenFlow example *(p.89~90)*
- 토폴로지: switch s1, s2, s3, controller, host h1(10.1.0.1), h2(10.1.0.2), h3(10.2.0.3), h4(10.2.0.4), h5(10.3.0.5), h6(10.3.0.6)
- orchestrated table들이 network-wide behavior를 만들 수 있음. 예: h5와 h6의 datagram은 h3 또는 h4로 가야 하되, s1을 거쳐 거기서 s2로 보낸다
- s3의 rule: IP Src = 10.3.\*.\* & IP Dst = 10.2.\*.\* → forward(3)
- s1의 rule: ingress port = 1, IP Src = 10.3.\*.\*, IP Dst = 10.2.\*.\* → forward(4)
- s2의 rule: ingress port = 2, IP Dst = 10.2.0.3 → forward(3) / ingress port = 2, IP Dst = 10.2.0.4 → forward(4)

### Generalized forwarding: summary *(p.91)*
- "match plus action" abstraction: 어떤 layer든 packet header(s)의 bit를 match하고 action 수행
  - 많은 field(link-, network-, transport-layer)에 대한 matching
  - local action: drop, forward, modify, 또는 matched packet을 controller로 전송
  - network-wide behavior를 "프로그램"할 수 있음
- "network programmability"의 단순한 형태: 프로그래밍 가능한 per-packet "processing". 역사적 뿌리는 **active networking**, 오늘날은 더 일반화된 프로그래밍인 **P4**(p4.org)

## 5. Middleboxes *(p.92~101)*

### Middleboxes *(p.93~94)*
- **Middlebox (RFC 3234)**: "source host와 destination host 사이의 data path 상에서, 일반적인 표준 IP router 기능 이외의 기능을 수행하는 모든 중간 장치"
- 어디에나 존재 (그림)
  - **NAT**: 가정, cellular, 기관
  - **Firewalls, IDS**: 기업, 기관, 서비스 제공자, ISP
  - **Load balancers**: 기업, 서비스 제공자, data center, mobile net
  - **Caches**: 서비스 제공자, mobile, CDN
  - **Application-specific**: 서비스 제공자, 기관, CDN
- 발전 방향
  - 처음: 독점(proprietary, closed) 하드웨어 솔루션
  - **"whitebox" 하드웨어 + open API**로 이동: 독점 하드웨어에서 벗어나고, match+action으로 local action을 프로그래밍 가능, 혁신/차별화가 **software**로 이동
  - **SDN**: (논리적으로) 중앙집중 control·configuration 관리, 보통 private/public cloud에 위치
  - **NFV(network functions virtualization)**: white box networking, computation, storage 위에서 프로그래밍 가능한 서비스

### The IP hourglass *(p.95~96)*
- 인터넷의 **"thin waist"**: network layer protocol은 **IP 하나**뿐이며, 인터넷에 연결된 수십억 개의 모든 장치가 구현해야 함
- 위쪽(application/transport)에는 HTTP, SMTP, RTP, QUIC, DASH, TCP, UDP 등 많은 protocol, 아래쪽(link/physical)에는 Ethernet, PPP, PDCP, WiFi, Bluetooth, copper, radio, fiber 등 많은 protocol — 모래시계 모양
- **at middle age**: 인터넷의 "love handles" — 네트워크 내부에서 동작하는 middlebox(caching, firewalls 등)가 허리에 붙은 군살처럼 생김

### Architectural Principles of the Internet *(p.97)*
- RFC 1958: "인터넷 커뮤니티의 많은 구성원은 아키텍처가 없고 전통만 있다고 주장할 것이다 … 하지만 매우 일반적으로, 커뮤니티는 **목표는 connectivity, 도구는 Internet Protocol, 그리고 intelligence는 network 내부에 숨겨지지 않고 end to end에 있다**고 믿는다."
- 세 가지 cornerstone belief
  - **simple connectivity**
  - **IP protocol: that narrow waist**
  - **intelligence, complexity는 network edge에**

### The end-end argument *(p.98~99)*
- 일부 network 기능(예: reliable data transfer, congestion control)은 **network 내부** 또는 **network edge**에서 구현할 수 있음
  - end-end 구현: reliable data transfer를 양 끝 host의 transport에서 구현
  - hop-by-hop(in-network) 구현: 각 link/hop마다 reliable data transfer를 구현
- 인용 (Saltzer, Reed, Clark 1981): "문제의 기능은 통신 시스템의 end point에 있는 application의 지식과 도움이 있어야만 완전하고 올바르게 구현될 수 있다. 따라서 그 기능을 통신 시스템 자체의 feature로 제공하는 것은 불가능하다. (통신 시스템이 제공하는 불완전한 버전은 성능 향상으로서 유용할 수 있다.)" → low-level 기능 구현에 반대하는 이 논리를 **end-to-end argument**라 함

### Where's the intelligence? *(p.100)*
- 20세기 전화망: intelligence/computing이 **network switch**에 있음
- 인터넷(2005 이전): intelligence, computing이 **edge**에 있음
- 인터넷(2005 이후): **programmable network device**, 그리고 edge에 intelligence, computing, 대규모 application-level 인프라
- Chapter 4: done!
