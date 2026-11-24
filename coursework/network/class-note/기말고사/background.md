# Chapter 4 사전 배경지식 수업노트

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

## 시험 범위 : 기말 (Chapter 4 Network Layer: Data Plane, Chapter 5 예정)

**수업 목표**: Chapter 4를 따라가기 위해 필요한 중간고사 범위의 배경지식 7개를 처음부터 하나씩 이해한다.

중간고사를 공부하지 못한 상태에서 기말 대비로 진행. 모든 개념을 처음 배우는 것으로 가정하고 설명함.

진행 순서
1. 인터넷의 기본 구성과 계층/캡슐화
2. Packet switching과 큐잉
3. Transport 기초 (port, TCP/UDP)
4. 이진수와 prefix
5. Broadcast와 MAC
6. DNS
7. Forwarding과 routing 구분 (Control plane 맛보기)

---

## 1. 인터넷의 기본 구성과 계층/캡슐화 *(중간 Ch1)*

### 1-1. 등장인물 4개

**인터넷**: 전 세계의 장치들이 링크로 얽혀서 서로 packet(데이터 조각)을 주고받게 해주는 네트워크의 네트워크.

- **host**: 데이터를 보내고 받는 끝단 장치 (PC, 폰, 서버)
- **link**: 장치끼리 잇는 통로 (광케이블, 구리선, WiFi 같은 무선)
- **router**: 여러 링크가 만나는 지점에서 들어온 packet을 어느 링크로 내보낼지 골라주는 장치
- **protocol**: 통신할 때 지키는 약속. 메시지 형식, 보내는 순서, 받았을 때 할 행동을 정해둠

비유: host = 집, router = 우체국 분류센터, link = 도로, protocol = 우편 규칙(주소 쓰는 법, 우표 붙이는 법)

### 1-2. 왜 계층(layer)으로 나누나

**계층 구조**: 복잡한 통신을 역할별 층으로 나누고, 각 층은 바로 아래 층의 서비스만 믿고 자기 일만 하게 만든 설계.

- 네트워크는 할 일이 많음: 앱 데이터 형식, 신뢰성 있는 전달, 경로 선택, 한 링크 안의 전달, 실제 신호 전송
- 한 덩어리로 만들면 하나만 바꿔도 전부 뜯어고쳐야 함
- 층으로 나누면 WiFi를 광케이블로 바꿔도 위층은 그대로 사용 가능

인터넷 5계층 (위에서 아래로)

| 층 | 하는 일 | 대표 protocol |
|---|---|---|
| application (5계층) | 앱끼리의 대화 | HTTP, DNS |
| transport (4계층) | 프로세스끼리 전달 | TCP, UDP |
| **network (3계층)** | **host끼리 packet 전달 (경로 선택)** | **IP** ← Ch4 |
| link (2계층) | 바로 이웃한 장치 사이 전달 | Ethernet, WiFi |
| physical (1계층) | 비트를 신호로 전송 | 광, 전파 |

Ch4는 3층인 network layer만 다룸.

### 1-3. 캡슐화 (Encapsulation)

**캡슐화**: 데이터가 위층에서 아래층으로 내려갈 때 각 층이 자기 용도의 header(주소·제어 정보)를 앞에 덧붙이는 과정.

편지 비유: 편지 내용 = application의 message → "몇 호 사람에게" 쪽지와 봉투 = transport → "어느 도시 어느 주소" 큰 봉투 = network → "이번 구간 트럭 번호" = link

```
application   message
   ↓ + transport header
transport     segment
   ↓ + IP header
network       datagram      ← Ch4에서 계속 나오는 단어
   ↓ + link header
link          frame
```

- segment가 **datagram의 payload(내용물)** 로 들어가고 앞에 IP header가 붙음
- 수신 쪽은 반대로 올라가며 header를 하나씩 벗김 (**decapsulation**)

### 1-4. Router는 어디까지 열어보나

- host는 5층 전부 처리
- router는 보통 **아래 3층(network까지)** 만 열어봄. datagram의 IP header에서 목적지 주소를 읽고 어느 링크로 내보낼지 정하면 끝
- 안의 segment(TCP/UDP)나 앱 데이터는 열어보지 않는 게 원칙
- 그래서 나중에 NAT가 port를 건드리는 게 "원칙 위반이라 논란"이 됨

### 1-5. Interface

**interface**: 장치와 링크가 만나는 접점. IP address는 장치가 아니라 이 접점에 붙음.

- host는 보통 interface 1~2개 (유선 랜카드, WiFi)
- router는 링크가 여러 개 연결돼 interface가 여러 개이고, 각각이 IP를 따로 가짐

### 1-6. 보충: transport층은 커널에서 구현되는데 "프로세스끼리의 통신"인 이유

- **어디서 구현되나**: TCP/UDP 코드는 OS 커널 안에서 돌아감
- **무슨 일을 하나**: 그 코드가 제공하는 서비스가 "프로세스 A ↔ 프로세스 B 사이의 논리적 통신"
- 슬라이드의 정의: logical communication between processes

socket 호출 시 흐름
1. 앱(프로세스)이 데이터를 socket에 넘김
2. 커널의 TCP가 header를 붙여 segment 생성
3. 커널의 IP가 header를 붙여 datagram 생성
4. NIC 드라이버와 하드웨어가 frame으로 내보냄

- 받는 쪽에서는 커널이 segment의 **port number**를 보고 어느 프로세스 socket에 줄지 결정
- application층은 사용자 공간에서, transport 이하는 대부분 커널(링크 일부는 NIC 하드웨어)에서 동작
- 계층은 "어디서 실행되나"가 아니라 "누구와 누구 사이의 통신을 책임지나"로 나눔
  - transport: end host의 프로세스 사이
  - network: host 사이
  - link: 이웃한 장치 사이
- 이 구분이 Ch4 끝의 end-to-end argument(기능을 네트워크 안이 아니라 끝단 host에 둔다)와 이어짐

### 1-7. 보충: application layer ≠ 프로세스

**계층은 프로세스가 아니라 protocol(약속)을 층으로 나눈 것.**

- **application layer**: 앱끼리 하는 대화의 규칙. HTTP라면 "GET /index.html 을 보내면 서버는 200 OK와 내용을 준다" 같은 메시지 형식과 순서. 크롬 프로그램 자체가 아니라 그 프로그램이 따르는 규칙
- **프로세스**: 그 규칙대로 실제로 말하는 실행 주체 (크롬, 웹서버 프로세스)
- **transport layer**: "그 말을 어느 프로세스에게, 어떤 방식으로 전달할까"의 규칙. 커널의 TCP/UDP가 처리
- 프로세스는 계층이 아니라 계층을 이용하는 쪽. 크롬 프로세스는 application layer 규칙(HTTP)을 직접 구현하고 transport는 커널에 맡김

편지 비유: 편지 쓰는 사람 = 프로세스, 편지 쓰는 규칙(인사말, 형식) = application layer, "몇 호 사람에게 전달할지, 분실 시 재발송할지" = transport layer

**application layer protocol이 정하는 세 가지**
- **형식**: 메시지를 어떻게 생기게 쓸지 (HTTP는 첫 줄에 `GET /index.html HTTP/1.1`, 그 아래 header들)
- **순서**: 누가 먼저 말하고 어떤 메시지에 어떤 답이 오는지 (요청 → 응답)
- **행동**: 메시지를 받았을 때 뭘 할지 (404 응답이면 "없는 페이지"로 처리)

형식·순서·행동 세 가지는 어느 계층의 protocol이든 동일하고, 정하는 대상만 계층마다 다름
- application: 앱끼리의 메시지
- transport: segment 형식과 재전송 같은 전달 방식
- network(IP): datagram 형식과 주소 체계

### 확인 질문
1. datagram은 network층(3계층), segment는 transport층(4계층)의 데이터 덩어리. segment에 IP header를 붙여 datagram이 됨
2. router는 3계층까지 열어보고, IP header의 목적지 주소를 보고 판단
3. IP address는 interface에 붙음. interface가 여러 개면 IP도 각각 생기기 때문

---

## 2. Packet switching과 큐잉 *(중간 Ch1)*

Ch4 router 내부 파트 전체가 이 현상 위에 있음.

### 2-1. Packet과 전송 속도

**packet**: 큰 데이터를 일정 크기로 쪼갠 조각. 조각마다 header가 붙어 독립적으로 목적지를 찾아감.

**link rate R**: 링크가 1초에 밀어낼 수 있는 비트 수(bps). R = 1 Mbps면 1초에 100만 비트.

packet 하나를 링크에 다 밀어내는 데 걸리는 시간이 **transmission delay**

```
transmission delay = L / R
(L = packet 크기(비트), R = 링크 속도(bps))
```

예: L = 8000비트(1000바이트), R = 1 Mbps → 8000 / 1,000,000 = 0.008초(8 ms)

### 2-2. Store-and-forward

**store-and-forward**: router는 packet 전체를 다 받은 뒤에야 다음 링크로 내보내기 시작한다는 규칙.

- 비트가 들어오는 대로 흘려보내지 않음. 한 packet이 통째로 도착해야 header를 읽고 판단할 수 있기 때문
- router 하나를 지날 때마다 최소 L/R만큼 시간이 걸림

### 2-3. 큐잉 (Queueing)

- router에 들어온 packet들이 같은 output 링크로 나가야 하는데, 링크는 한 번에 한 packet씩만 밀어낼 수 있어 나머지는 기다림
- 이 줄이 **queue**, 기다리는 시간이 **queueing delay**
- 줄이 서는 조건: **packet이 도착하는 속도가 링크가 내보내는 속도(R)보다 빠를 때**
- 도착이 R보다 느리면 줄이 잘 안 쌓이고, 빠르면 점점 길어짐

### 2-4. Packet loss

**packet loss**: router의 buffer(대기 공간)는 유한해서, 줄이 가득 찬 상태에서 새 packet이 오면 버려지는 현상.

- 버려진 packet은 사라지고, 인터넷의 network layer는 복구해주지 않음
- Ch4 첫머리의 "best-effort"(최선은 다하지만 보장은 안 한다)와 연결
- 복구가 필요하면 위층(TCP)이 재전송으로 해결

### 2-5. Ch4와 연결

- input port와 output port에도 queue가 있음
- buffer가 가득 차면 어떤 packet을 버릴지 정하는 것이 **drop policy**
- 줄 선 packet 중 누구를 먼저 보낼지 정하는 것이 **scheduling**

### 확인 질문
1. 4000비트 packet, R = 2 Mbps → 4000 / 2,000,000 = 0.002초 (2 ms)
2. queue가 쌓이는 조건: packet의 도착 속도가 링크가 내보내는 속도보다 빠를 때
3. loss: 버퍼가 가득 찼는데 packet이 또 들어올 때

---

## 3. Transport 기초: port, TCP/UDP *(중간 Ch3)*

Ch4에서 NAT와 DHCP를 읽을 때 필요한 만큼만. TCP 내부 동작(흐름·혼잡 제어)은 Ch4에서 안 씀.

### 3-1. 왜 port가 필요한가

host 하나에서는 프로세스 여러 개가 동시에 통신함 (크롬, 카톡, 게임). IP address는 host까지만 찾아주므로, 그 안에서 어느 프로세스에게 줄지 구분할 번호가 필요함.

**port number**: 한 host 안에서 통신 중인 프로세스(socket)를 구분하는 16비트 번호 (0~65535).

- **IP address = 건물, port = 호수**
- 자주 쓰는 고정 번호(well-known port): HTTP 80, ssh 22, DHCP 서버 67 / 클라이언트 68
- Ch4 OpenFlow 예시의 "TCP d-port = 22 → drop"은 ssh를 막는 방화벽 규칙

### 3-2. 통신 하나를 식별하는 법

연결 하나는 **(출발지 IP, 출발지 port, 목적지 IP, 목적지 port)** 로 구분.

- 클라이언트의 출발지 port는 OS가 임의로 빈 번호를 붙임 (예: 3345)
- 서버의 목적지 port는 80처럼 고정된 번호
- NAT에서 이 번호를 바꿔치기함

### 3-3. TCP와 UDP

- **TCP**: 연결을 먼저 맺고, 순서와 도착을 보장하고, 빠지면 재전송. 믿을 수 있는 대신 무겁고 느림
- **UDP**: 연결 없이 그냥 던짐. 순서·도착 보장 없고 재전송 없음. 가볍고 빠름

Ch4에서 필요한 부분
- IP header의 **upper layer** 필드가 "datagram 안의 segment가 TCP인지 UDP인지"를 알려줌
- **DHCP는 UDP** 사용. IP가 없는 host가 서버를 찾는 상황이라 연결 설정을 하는 TCP는 쓸 수 없고, 연결 없이 broadcast로 던지는 UDP가 맞음 (핵심은 빠르기가 아니라 연결 설정이 필요 없다는 점)
- header 크기: TCP 20바이트 + IP 20바이트 = 40바이트

### 3-4. 1단계와의 연결

router는 3계층까지만 열어보므로 port(4계층 header)는 원래 안 봄. NAT나 firewall이 port를 보면 "원칙을 넘는 장치"가 되고, 이게 Ch4 후반 논쟁.

### 확인 질문
1. IP address는 host, port number는 프로세스(목표 socket)를 찾음
2. DHCP가 UDP를 쓰는 이유: 연결 설정 없이 가볍게 던지기 위해 (IP가 없는 상태에서 TCP 연결은 불가)
3. 크롬 탭 두 개가 같은 서버 `203.0.113.5:80`에 접속할 때 구분 기준: 출발지 port 번호 (나머지 세 값은 동일)

---

## 4. 이진수와 prefix *(Ch4 계산 문제의 도구)*

longest prefix match, CIDR, subnet 문제를 풀기 위한 기본 도구.

### 4-1. IP address의 구조

**IP address(IPv4)**: 32비트짜리 번호. 8비트씩 4덩어리로 끊어 각각 10진수로 표기.

```
11001000 00010111 00010000 00000001
   200      23       16        1      →  200.23.16.1
```

8비트 하나는 0~255 (2^8 = 256가지). 변환은 자리값으로 계산.

```
자리값:  128  64  32  16  8  4  2  1
비트  :   1    1   0   0  1  0  0  0   → 128+64+8 = 200
```

외워둘 것: 128, 64, 32, 16, 8, 4, 2, 1 / 2^8=256, 2^10=1024, 2^16=65536, 2^24=16,777,216

### 4-2. Network 부분과 host 부분

- 주소 32비트는 왼쪽이 **network(subnet) 부분**, 오른쪽이 **host 부분**
- 같은 네트워크의 장치들은 왼쪽 비트가 같고 오른쪽 비트만 다름
- 우편주소로 비유하면 "서울시 강남구" = network 부분, "101호" = host 부분

### 4-3. Prefix 표기 /x

**/x 표기**: 왼쪽 x비트가 network 부분이라는 뜻.

```
200.23.16.0/23
= 11001000 00010111 0001000|0 00000000
                           ↑ 앞 23비트가 network, 나머지 9비트가 host
```

- 앞 x비트가 같으면 같은 네트워크
- host 비트가 (32 - x)개이므로 들어갈 주소 개수는 2^(32-x)개
- /24면 host 8비트 → 256개, /23이면 host 9비트 → 512개

### 4-4. Prefix 매칭 (longest prefix match의 기초)

어떤 주소가 `a.b.c.d/x`에 속하는지는 앞 x비트를 비교.

예: 목적지 `11001000 00010111 00010110 10100001`, 규칙 `11001000 00010111 00010***` (앞 21비트 고정, 나머지 와일드카드) → 앞 21비트가 같아 **매치**

여러 규칙이 동시에 매치되면 **가장 긴 prefix**(앞에서부터 더 많은 비트가 일치하는 규칙)를 선택. 이것이 Ch4의 longest prefix matching 규칙 (본 수업에서 다시 다룸).

### 확인 질문
1. `00001010` → 8 + 2 = 10
2. 10.1.2.0/24의 주소 개수: host 비트 8개 → 2^8 = 256개
3. `192.168.5.7`이 규칙 A 192.168.0.0/16, 규칙 B 192.168.5.0/24에 모두 매치 → B (앞 24비트 일치 > 앞 16비트 일치, 더 긴 prefix 선택)

---

## 5. Broadcast와 MAC *(중간 Ch1, Ch6 예고)*

DHCP 예시에 나오는 `255.255.255.255`와 `FFFFFFFFFFFF`를 읽기 위한 배경.

### 5-0. 용어 풀이

- **네트워크 카드(NIC)**: 컴퓨터를 네트워크에 연결해주는 부품 (유선 랜카드, WiFi 칩). 앞서 말한 **interface**에 해당. 제조 시 고유 MAC address가 새겨져 있음
- **link**: 장치 두 개(또는 여럿)를 **직접** 잇는 연결 한 구간. 집 PC와 공유기 사이의 랜선이 link 하나, 공유기와 통신사 장비 사이가 또 다른 link. 인터넷은 link들을 router로 이어 붙인 것. link 계층은 "바로 이웃한 장치까지" 전달하는 일을 맡음
- **frame**: link 계층의 데이터 덩어리 이름. datagram에 link header(MAC 주소 등)를 붙인 것. 이웃 장치까지 가는 한 구간에서만 쓰이고, 구간이 끝나면 벗겨져 다음 구간에서 새 frame으로 다시 포장됨
- **LAN**(Local Area Network): 집, 사무실, 학교 건물처럼 좁은 지역에서 장치들이 서로 직접 연결된 네트워크. 이 안에서는 router를 안 거치고 서로 frame을 주고받고, broadcast가 닿는 범위도 LAN 안
- **DHCP**: host가 네트워크에 접속할 때 IP address를 자동으로 빌려주는 서비스. 카페 WiFi에 붙으면 IP를 직접 입력하지 않아도 되는 것이 DHCP 덕분. IP가 없는 host가 LAN 전체에 broadcast로 요청하면 서버가 번호를 알려줌 (4단계 과정은 Ch4에서)

### 5-1. MAC address

**MAC address**: 네트워크 카드(interface)에 붙은 48비트 주소로, 같은 LAN 안에서 frame을 전달할 때 쓰는 link 계층 주소.

- 16진수 12자리로 표기: `22:A7:23:11:E1:02`
- 하드웨어에 고정되어 있어 기본적으로 안 바뀜

### 5-2. IP와 MAC은 왜 둘 다 필요한가

| | IP address | MAC address |
|---|---|---|
| 층 | network (3계층) | link (2계층) |
| 범위 | 인터넷 전체, 끝에서 끝 (end-to-end) | 이웃한 장치 사이 한 구간 (LAN 안) |
| 성격 | 위치를 따라 바뀜 (네트워크가 바뀌면 달라짐) | 카드에 붙은 고유값 |

택배 비유: IP = "최종 수취인 주소", MAC = "이번 구간에서 짐을 받을 이웃 정류장"

- datagram이 여러 router를 거치는 동안 IP header의 주소 필드는 안 바뀜 (TTL 같은 필드는 router마다 바뀌고, NAT는 주소도 바꿈)
- 구간마다 frame의 MAC 주소는 새로 바뀜 (그 구간의 송신·수신 interface를 가리키므로)
- router는 frame을 받아 벗기고 IP datagram만 꺼내 판단한 뒤, 다음 구간의 새 frame에 담아 내보냄

### 5-3. Broadcast

**broadcast**: 같은 네트워크(LAN) 안의 모든 장치에게 한꺼번에 보내는 방식.

- IP broadcast 주소: `255.255.255.255` (모든 비트 1)
- MAC broadcast 주소: `FF:FF:FF:FF:FF:FF` (48비트 전부 1)
- 받는 장치가 누군지 모를 때 쓰는 "여기 누구 있어요?" 방식

### 5-4. DHCP와의 연결

DHCP discover 메시지
- 출발지는 IP를 아직 못 받아 `0.0.0.0`
- 목적지는 서버 주소를 모르니 `255.255.255.255` (broadcast)
- Ethernet frame의 목적지 MAC도 `FF:FF:FF:FF:FF:FF`로 broadcast
- 즉 IP도 없고 서버도 모르는 상태에서 LAN 전체에 소리치는 것

### 확인 질문
1. 범위: IP = 인터넷 전체(end-to-end, network층), MAC = LAN 안의 한 구간(link층)
2. router 3개를 거칠 때 IP header의 목적지 주소는 안 바뀌고, frame의 MAC 주소는 구간마다 바뀜
3. discover에서 출발지가 `0.0.0.0`이고 목적지가 broadcast인 이유: IP를 아직 못 받았고 서버가 누군지 모르니 LAN 전체에 뿌림

---

## 6. DNS *(중간 Ch2)*

**DNS**: 사람이 읽는 도메인 이름(`google.com`)을 IP address로 바꿔주는 전화번호부 같은 시스템.

### 6-1. 왜 필요한가
- 네트워크는 IP address로만 packet을 보낼 수 있는데, 사람은 `142.250.x.x` 같은 숫자를 못 외움
- 브라우저에 `google.com`을 치면 먼저 DNS에 "이 이름의 IP가 뭐야?"라고 묻고, 답받은 IP로 접속

### 6-2. 누구에게 묻나
- 질문을 받아주는 서버가 **DNS server**
- host가 이 서버의 주소를 아는 방법이 Ch4와의 접점: **DHCP가 IP를 줄 때 DNS server 주소도 같이 알려줌**
- DHCP가 IP 외에 주는 것 세 가지: **DNS server 주소, first-hop router(밖으로 나가는 첫 관문) 주소, network mask(/24 같은 것)**. 슬라이드 "DHCP: more than IP addresses"

### 6-3. 한 가지 더
- DNS는 application 층 protocol이고 보통 UDP 사용
- 이름 하나를 IP로 바꾸는 과정(root, TLD, 권한 서버)은 중간 Ch2 내용이라 기말에는 불필요

### 확인 질문
1. DNS: 도메인 이름에 매칭되는 IP address를 주는 일
2. DHCP가 IP 외에 주는 것: DNS server 주소, first-hop router, network mask

---

## 7. Forwarding vs Routing (Control plane 맛보기)

### 7-1. 두 가지 일

- **forwarding**: router가 packet을 받았을 때, 지금 이 순간 이 router의 어느 output 링크(interface)로 내보낼지 정해서 옮기는 일. router 한 대 안의 일 (local)
- **routing**: 출발지에서 목적지까지 가는 전체 경로를 정하는 일. 네트워크 전체를 보는 일 (network-wide)

여행 비유: forwarding = 교차로에서 "여기서 왼쪽으로 꺾자"고 고르는 순간, routing = 출발 전에 지도를 보고 "서울 → 대전 → 부산" 경로를 짜는 일

### 7-2. Forwarding table

router는 forwarding 때 **forwarding table**("이런 목적지 주소면 이 output으로"를 적은 표)을 봄. 4단계의 prefix 규칙표가 이것.

- routing이 경로를 계산해서 **표를 채움**
- forwarding은 그 표를 **보고 packet을 옮김** (router가 읽어서 사용)

### 7-3. Data plane vs Control plane

| | Data plane | Control plane |
|---|---|---|
| 하는 일 | forwarding (packet 옮기기) | routing (경로 계산, 표 채우기) |
| 범위 | router 한 대 (local) | 네트워크 전체 |
| 속도 | 아주 빠름 (나노초, 하드웨어) | 상대적으로 느림 (밀리초, 소프트웨어) |

- **Ch4**는 data plane: router 한 대가 packet을 어떻게 옮기는지, 주소가 어떻게 생겼는지
- **Ch5**(예정)는 control plane: 경로 계산 알고리즘(OSPF, BGP 등)
- Ch4 슬라이드에 control plane이 잠깐 나옴 (traditional routing algorithm vs SDN). 이름만 알면 됨

### 확인 질문
1. forwarding: 이 router의 어느 output 링크로 옮길지 / routing: 네트워크 전체 경로를 어떻게 설정할지
2. forwarding table은 routing이 채우고, router가 읽어서 사용

---

## 배경 7단계 요약

| 단계 | 핵심 |
|---|---|
| 1 | 5계층, 캡슐화(message → segment → datagram → frame), router는 3계층까지만 열어봄, IP는 interface에 붙음 |
| 2 | queue는 도착 속도 > 링크 속도일 때 생기고, buffer가 차면 loss |
| 3 | port는 host 안의 프로세스를 구분, TCP/UDP, DHCP는 UDP |
| 4 | 32비트 주소, /x는 앞 x비트가 network, longest prefix 선택 |
| 5 | IP는 end-to-end, MAC은 한 구간, broadcast는 LAN 전체 |
| 6 | DNS는 이름 → IP, DHCP가 DNS server 주소도 줌 |
| 7 | forwarding은 local, routing은 전체, data plane vs control plane |

다음 수업: Chapter 4 본 수업 (notes/기말고사/chapter-4.md 기준, p.2부터)
