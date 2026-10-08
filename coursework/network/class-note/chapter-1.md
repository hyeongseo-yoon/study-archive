# Chapter 1 수업노트: Introduction

**이번 수업 목표**: 인터넷이 뭘로 구성돼 있고(구조), 데이터가 어떻게 흘러가며(core), 성능은 뭘로 결정되고(delay/throughput), 계층 구조로 어떻게 설계됐는지를 자기 말로 설명할 수 있게 되는 것.

선수지식 없는 챕터라 확인질문은 스킵하고 진행함.

---

## 1. What is the Internet? *(슬라이드 p.3~8)*

인터넷을 설명하는 방법은 두 가지 관점: "뭘로 만들어졌나" / "뭘 해주나".

### 관점 ① Nuts and bolts (구성 요소) *(p.3, p.5)*
"너트와 볼트"는 부품 단위로 뜯어본다는 뜻.

- **host (= end system)**: 네트워크 앱이 실제로 돌아가는 종단 장치. 폰, 노트북, 웹 서버 전부 해당. 인터넷 "가장자리(edge)"에 있다고 해서 edge라고도 부름.
- **packet switch**: 데이터 조각(packet)을 받아서 다음 곳으로 넘겨주는 장치. 대표적으로 router와 switch.
- **communication link**: 장치들을 잇는 통로. 광섬유, 구리선, 무선, 위성 등. 성능은 **bandwidth(전송 속도, 예: 1Gbps)**로 표현.
- **network**: 장치 + 라우터 + 링크를 묶은 집합 하나. 보통 한 조직이 관리 (학교망, 회사망, 통신사망).
- **Internet**: 이런 네트워크들을 다시 서로 연결한 **"network of networks"**. 정확히는 상호 연결된 ISP들의 집합.

**protocol**: 부품들이 서로 말이 통하려면 규칙이 있어야 하고, 그 규칙이 protocol. HTTP, TCP, IP, WiFi, Ethernet, 4G/5G가 전부 protocol. 쉽게 말해 "데이터를 주고받는 방법(절차)".

규칙은 표준으로 관리됨.
- **RFC** (Request for Comments): 표준 문서. 1만 개 이상.
- **IETF** (Internet Engineering Task Force): 이 표준을 만드는 단체.

### 관점 ② Services (서비스) *(p.6)*
부품이 아니라 **기능** 쪽에서 봄. 인터넷은 애플리케이션들이 가져다 쓰는 **infrastructure(기반 시설)**. 웹, 스트리밍, 화상회의, 이메일, 게임, 전자상거래, SNS가 전부 그 위에서 돌아감.

개발자가 앱을 만들 때 "패킷이 어떤 광케이블을 타고 갈지"까지 신경 쓰지 않는 건, 인터넷이 앱에 **programming interface(API)**를 제공해서 앱이 "이 데이터 저쪽에 보내줘"라고 요청만 하면 되게 해주기 때문. 이 API는 앱을 인터넷 전송 서비스에 연결해 주는 **"hook(걸이)"** 역할.

> 우체국 비유: 편지를 쓰는 사람(앱)은 "이 주소로 보내주세요"만 말하면 됨. 비행기로 가든 트럭으로 가든 몰라도 되고, 그 부분을 우체국(인터넷)이 맡음.

### Protocol이란 정확히 뭔가 *(p.7~8)*
> Protocols define the **format**, **order** of messages sent and received among network entities, and **actions taken** on message transmission, receipt.

| 요소 | 의미 | 사람 대화로 비유 |
|---|---|---|
| **format** | 메시지를 어떤 모양/구조로 쓰나 | 한국어로 말한다, 문장 구조 |
| **order** | 메시지를 어떤 순서로 주고받나 | 인사 → 질문 → 대답 |
| **actions** | 메시지를 보내거나 받았을 때 뭘 하나 | 인사를 받으면 인사로 답한다 |

```
사람:     "Hi"  →  "Hi"  →  "몇 시야?"  →  "2:00"
네트워크:  TCP 연결 요청 → TCP 연결 응답 → GET 요청 → 파일 응답
```

먼저 말을 걸어서 상대가 응답하는지 확인(연결)하고, 그다음 본론(요청)을 말하면 답이 옴. 사람 사이의 규약이 인사와 질문 같은 예절이라면, 네트워크 protocol은 장치 간의 예절. **인터넷에서 일어나는 모든 통신 활동은 protocol의 지배를 받음.**

---

## 2. Network Edge *(슬라이드 p.9~25)*

인터넷을 크게 나누면 **edge(가장자리)**와 **core(중심부)**.

### Network edge란 *(p.10~12)*
**network edge = host들**. 역할에 따라 둘로 나뉨.
- **client**: 서비스를 요청하는 쪽 (폰, 노트북)
- **server**: 서비스를 제공하는 쪽. 주로 **데이터센터**에 몰려 있음.

질문은 "이 host들을 인터넷 안쪽(edge router)에 **어떻게 연결**하나?" → 그 연결 방식이 access network.

### Access network 3종류 *(p.13)*
1. **residential access nets**: 가정
2. **institutional access networks**: 학교, 회사
3. **mobile access networks**: WiFi, 4G/5G

### 가정용: 두 가지 대표 방식

**① Cable-based access (HFC: hybrid fiber coax)** *(p.14~15)*
케이블TV 선을 인터넷에도 같이 쓰는 방식.
- 이름 그대로 **광섬유(fiber) + 동축(coax)**을 섞어서 사용. 방송국 쪽 cable headend까지는 광섬유, 집 쪽 마지막 구간은 동축.
- 한 선을 이웃들과 **공유(shared cable)**. data와 TV가 같은 선에 있지만 **서로 다른 주파수**를 써서 안 섞임. 이걸 **FDM(frequency division multiplexing, 주파수 분할 다중화)**이라 함.
- **비대칭**: downstream(받는 방향)이 upstream(보내는 방향)보다 훨씬 빠름. downstream 최대 40Mbps~1.2Gbps, upstream 30~100Mbps. 보통 사용자는 올리는 것보다 내려받는 게 많으니까 이렇게 설계.
- headend에는 **CMTS(cable modem termination system)**가 있어서, 여러 집의 케이블 모뎀 신호를 모아 ISP로 넘김.

**② DSL (Digital Subscriber Line)** *(p.16)*
이미 깔려 있는 **전화선**을 재활용하는 방식.
- 집에서 통신사 **central office의 DSLAM**까지 **전용선(dedicated line)**.
- voice와 data가 **서로 다른 주파수**를 써서 한 선에 공존. data는 인터넷으로, voice는 전화망으로 분리돼 나감.
- downstream 24~52Mbps, upstream 3.5~16Mbps.

**cable과 DSL의 핵심 차이**: cable은 이웃과 선을 **공유**, DSL은 나만 쓰는 **전용선**. 그래서 DSL이 더 안정적이지만 속도는 보통 cable보다 느림.

### Home network *(p.17)*
공유기 한 박스에 여러 기능이 들어 있음.
- WiFi **AP**(무선 접속 장치) + **router/firewall/NAT** + **cable/DSL modem**

보통 한 박스로 합쳐져 있고, 유선 Ethernet은 최대 1Gbps.

### 무선 access *(p.18~19)*

| 종류 | 범위 | 특징 |
|---|---|---|
| **WLAN (WiFi)** | 건물 안팎, 약 100ft | 802.11 시리즈. Wi-Fi 4~8로 세대가 올라갈수록 빨라져서 최신 Wi-Fi 7/8은 수 Gbps~수십 Gbps |
| **wide-area cellular** | 수십 km | 통신사가 제공, 4G/5G |

### Enterprise / Data center *(p.20~21)*
- **Enterprise network** *(p.20)*: 회사나 학교는 **Ethernet switch**(유선, 100Mbps~10Gbps) + **WiFi AP**(무선)를 조합해서 내부망을 만들고, **institutional router**를 통해 ISP로 나감.
- **Data center network** *(p.21)*: 수백~수천 대 서버를 잇는 **초고대역폭(10s~100s Gbps)** 링크.

### Physical media (링크의 물리적 매체) *(p.23~25)*
- **bit**: 송신자-수신자 쌍 사이를 **전파(propagate)**되는 데이터의 기본 단위.

매체는 신호가 **고체 안에서** 가느냐 **공기 중으로** 가느냐로 나뉨.

**① Guided media (유도 매체)**: 신호가 고체 매체 안에서 전파 *(p.23~24)*
- **Twisted pair (TP, 랜선)**: 구리선 두 가닥을 꼬아놓은 것. Cat5는 100Mbps~1Gbps, Cat6는 10Gbps. *(p.23)*
- **Coaxial cable (동축)**: **동심** 구리 도체 두 개로 된 케이블. 양방향이고, 여러 주파수 채널을 다중화하는 **broadband**. HFC가 이걸 사용. *(p.24)*
- **Fiber optic (광섬유)**: 유리 섬유로 **빛 펄스** 전송. 속도 10s~100s Gbps, 에러율이 낮고, **전자기 노이즈에 강함**. *(p.24)*

**② Unguided media (비유도 매체)**: 신호가 자유롭게 퍼져나감 = **radio** *(p.25)*

| 종류 | 속도/범위 |
|---|---|
| WiFi | 10~100s Mbps, 수십 m |
| wide-area 4G/5G | 10s Mbps, ~10km |
| Bluetooth | 단거리 |
| terrestrial microwave | 45Mbps |
| satellite | <100Mbps, 정지궤도는 **왕복 지연 270msec** |

위성은 속도보다 **지연(delay)**이 큰 게 단점. 지구에서 아주 먼 궤도까지 신호가 올라갔다 내려와야 하기 때문. (섹션 4의 propagation delay와 연결)

---

## 3. Network Core *(슬라이드 p.26~46)*

edge가 "끝단 장치들"이라면, **core**는 그 사이를 이어주는 **라우터들의 그물(mesh)**. 여러 네트워크를 잇는 "network of networks"의 실체. *(p.26~27)*

### Packet switching *(p.27~30)*
인터넷 core의 기본 방식.

1. 송신 host가 애플리케이션 메시지를 **packet**(작은 조각)으로 **쪼갠다**.
2. 네트워크가 이 패킷들을 source → destination 경로상의 **라우터들을 거쳐 forward**한다.

택배 비유: 이삿짐 전체를 한 번에 보내는 게 아니라 **작은 상자 여러 개로 나눠서** 각각 배송.

라우터가 하는 일은 두 가지이고, 구분이 중요. *(p.28~30)*

| | **Forwarding (= switching)** | **Routing** |
|---|---|---|
| 범위 | **local** action | **global** action |
| 하는 일 | 들어온 패킷을 로컬 forwarding table을 보고 알맞은 output link로 이동 | source-destination 경로 자체를 결정 |
| 비유 | 교차로에서 표지판 보고 방향 고르기 | 출발 전에 지도 보고 전체 경로 짜기 |

관계: routing algorithm이 경로를 계산해서 **forwarding table을 만들어주고**, 라우터는 패킷이 올 때마다 그 table을 **조회**.

#### Store-and-forward *(p.22, p.31)*
**패킷 전체(L bit)가 라우터에 다 도착해야** 그다음 링크로 내보내기 시작할 수 있음. 일부만 받고 먼저 내보내는 건 안 됨.

- 한 링크에서 패킷을 밀어 넣는 시간 = **transmission delay = L / R** (L: 패킷 길이 bit, R: 링크 전송률 bps)
- 예: L = 10Kbit, R = 100Mbps → 10,000 / 100,000,000 = **0.1 msec** (한 홉당)

패킷이 라우터를 하나씩 거칠 때마다 이 시간이 **또 쌓임**.

#### Queueing & loss *(p.32~33)*
여러 곳에서 패킷이 한 라우터로 몰릴 때의 문제.

- **도착률(arrival rate) > 출력 링크의 전송률**이면, 초과분은 **큐에서 대기** → **queueing delay**
- 라우터의 **버퍼(메모리)가 가득 차면** 새로 온 패킷은 **버려짐(drop)** → **packet loss**

톨게이트 비유: 차가 몰리면 줄을 서고(queueing), 대기 공간이 꽉 차면 더 못 들어옴(loss).

### Circuit switching (대안 방식) *(p.34~35)*
패킷 스위칭과 반대되는 방식. 전통 **전화망**이 사용.

- 통신(call) 시작 전에 source-destination 사이 **end-to-end 자원을 미리 예약/할당**.
- **전용 자원**이라 공유가 없고, 성능이 **보장**됨 (회선급).
- 단점: 내가 말을 안 하고 있어도 그 구간은 **idle 상태로 낭비**. 다른 사람이 쓸 수 없음.

자원을 쪼개는 방법:
- **FDM**: **주파수**를 좁은 대역으로 나눠서 call마다 할당
- **TDM**: **시간**을 슬롯으로 나눠서 call마다 주기적으로 슬롯 할당

비유: 식당 **예약석**을 잡아두는 게 circuit switching (내가 안 와도 자리는 비워둠). 패킷 스위칭은 **선착순 공용 좌석**.

### Packet vs Circuit switching 비교 *(p.36~37)*
> 1Gbps 링크, 사용자는 활성 상태일 때 100Mbps 사용, 각 사용자는 전체 시간 중 **10%만** 활성.

- **circuit switching**: 사용자당 100Mbps를 **고정 예약**하니 1Gbps / 100Mbps = **딱 10명**만 수용 가능.
- **packet switching**: 사용자가 **35명**이어도 괜찮음. 동시에 10명보다 많이 활성일 확률이 **0.0004 미만**이라 사실상 문제 없음.

이유: 사용자들이 대부분의 시간엔 아무것도 안 보내고 가끔 몰아서(bursty) 보내는데, packet switching은 그 빈 시간을 다른 사용자가 **공유해서** 쓰니까 훨씬 많은 사람을 수용 (**statistical multiplexing**의 효과).

| | 내용 |
|---|---|
| **장점** | bursty data에 적합, 자원 공유, call setup 불필요, 단순 |
| **단점** | 과도한 **congestion** 가능 (버퍼 오버플로우로 delay/loss 발생) |

그래서 packet switching 위에서는 **신뢰성 있는 데이터 전송**과 **혼잡 제어**를 위한 protocol이 필요. (나중에 transport layer/TCP에서 다룰 내용의 씨앗)

### Internet structure: network of networks *(p.38~46)*
호스트는 **access ISP**를 통해 인터넷에 붙으니, 어디서든 두 호스트가 통신하려면 access ISP들이 서로 연결돼 있어야 함. **단계적으로 발전하는 과정**으로 설명.

**단계 1. 모든 access ISP를 서로 직접 연결** *(p.39~40)*
→ 연결이 N개면 약 N²개의 링크 필요(O(N²)), **규모가 안 따라감**. 현실적으로 불가능.

**단계 2. 하나의 global transit ISP에 모두 연결** *(p.41)*
→ 링크가 N개로 줄어듦. access ISP는 global ISP의 **customer**, global ISP는 **provider**가 되는 **경제적 계약 관계** 발생.

**단계 3. global ISP가 여러 개로 경쟁** *(p.42~43)*
→ 돈 되는 사업이니 경쟁사가 생기고, 이들끼리도 연결 필요.
- **IXP (Internet Exchange Point)**: ISP들이 한곳에 모여 서로 연결하는 장소
- **peering link**: ISP끼리 서로 직접 연결 (보통 서로 트래픽 비용 없이 교환)

**단계 4. regional ISP 등장** *(p.44)*
→ access net들을 regional ISP에 묶고, regional ISP가 global ISP에 연결.

**단계 5. content provider network 등장** *(p.45)*
→ Google, Microsoft, Akamai 같은 업체가 **자체 사설 네트워크**를 구축해서, 서비스와 콘텐츠를 **end user 가까이에** 배치.

**최종 구조** *(p.46)*: 중심에 소수의 대형 네트워크.
- **tier-1 ISP** (Level 3, Sprint, AT&T, NTT 등): 전국/국제 커버리지를 가진 최상위
- **content provider network** (Google, Facebook 등): 자체 데이터센터를 연결하는 사설망, tier-1/regional ISP를 **우회**해서 쓰는 경우도 많음

정리: **access → regional → tier-1**의 계층 구조에 IXP/peering이 옆으로 이어주고, content provider가 그 바깥에 자체망을 얹은 모양.

---

## 4. Performance: Loss, Delay, Throughput *(슬라이드 p.47~59)*

### Packet delay: 4가지 요소 *(p.49~50)*
패킷이 라우터 하나(= 노드)를 지나갈 때 걸리는 총 시간.

```
d_nodal = d_proc + d_queue + d_trans + d_prop
```

| 요소 | 이름 | 무엇에 의해 결정되나 |
|---|---|---|
| **d_proc** | processing delay | 비트 에러 체크, output link 결정 같은 처리. 보통 수 마이크로초 미만이라 거의 무시 |
| **d_queue** | queueing delay | output link로 나가려고 **대기하는 시간**. 라우터의 혼잡 정도에 따라 달라짐 |
| **d_trans** | transmission delay | **L / R** (L: 패킷 길이 bit, R: 링크 전송률 bps) |
| **d_prop** | propagation delay | **d / s** (d: 물리적 링크 길이, s: 전파 속도, 약 2×10^8 m/sec) |

#### d_trans vs d_prop
- **d_trans**: 패킷의 비트들을 **링크에 밀어 넣는** 데 걸리는 시간. **패킷 크기와 링크 속도**가 결정.
- **d_prop**: 밀어 넣은 비트가 링크를 따라 **물리적으로 이동하는** 시간. **거리와 매체**가 결정. 패킷 크기나 링크 속도와는 **무관**.

**caravan(카라반) 비유** *(p.51~52)*
- car = bit
- caravan(자동차 행렬) = packet
- toll booth(톨게이트) = link(router)

카라반 전체가 톨게이트를 **다 통과하는 시간**이 **transmission delay**, 통과한 차들이 다음 톨게이트까지 **도로를 달려가는 시간**이 **propagation delay**.

결론:
- 링크 속도(R)를 올리면 → d_trans만 줄어듦
- 링크를 더 짧게/빠른 매체로 바꾸면 → d_prop만 줄어듦
- 위성의 270msec 지연은 거리 때문, 즉 **d_prop**이 큰 것

### Traffic intensity와 queueing delay *(p.53)*
```
traffic intensity = L * a / R
(a: 평균 패킷 도착률 packets/sec, L: 패킷 길이 bit, R: 링크 대역폭 bps)
```
분자 L*a는 **초당 들어오는 비트 양**(arrival rate of bits), 분모 R은 **초당 내보낼 수 있는 비트 양**(service rate of bits). 즉 "들어오는 속도 / 처리하는 속도" 비율.

| La/R | 평균 대기 지연 |
|---|---|
| **≈ 0** | 작음 |
| **→ 1** | 급격히 커짐 |
| **> 1** | 처리 가능한 양보다 도착량이 더 많음 → 큐가 계속 쌓여 평균 지연 **무한대** |

**1에 가까워질수록 선형이 아니라 급격히** 늘어남. 도로가 가득 찬 상태에서는 작은 증가에도 정체가 폭발하는 것과 같음. 그래서 설계할 때 **traffic intensity가 1을 넘지 않도록** 하는 게 원칙.

### traceroute *(p.54~55)*
실제 인터넷에서 경로와 지연을 **직접 측정**하는 도구.

- 목적지까지 경로상의 라우터 i마다 **TTL = i**인 패킷을 3개씩 보냄.
- TTL은 라우터를 지날 때마다 1씩 줄어 0이 되면 라우터가 패킷을 버리고 발신자에게 알려줌. TTL=1이면 첫 번째 라우터에서, TTL=2면 두 번째에서 응답이 옴.
- 이 응답이 돌아오는 **왕복 시간(RTT)**을 측정해서 각 홉까지의 지연을 알아냄.
- 출력의 `* * *`는 **응답 없음** (probe 손실 또는 라우터 무응답).

### Packet loss *(p.56)*
큐(버퍼)의 용량은 **유한**. 가득 찬 큐에 도착한 패킷은 **drop(loss)**. 손실된 패킷은 이전 노드나 source end system이 **재전송할 수도, 안 할 수도** 있음. 재전송 여부는 그 위에서 돌아가는 protocol(TCP면 재전송, UDP면 안 함 등)에 달림.

### Throughput *(p.57~59)*
송신자 → 수신자로 **비트가 실제로 전달되는 속도**(bits/time).

- **instantaneous throughput**: 특정 시점의 속도
- **average throughput**: 더 긴 시간에 걸친 평균 속도

bandwidth는 링크의 **용량(최대치)**, throughput은 **실제로 나오는 속도**.

#### Bottleneck link *(p.58)*
end-to-end 경로에서 throughput을 **제한하는 링크**. 파이프 여러 개를 이어붙이면 가장 좁은 파이프가 전체 유량을 결정하는 것과 같음.

경로에 두 구간 R_s(서버쪽), R_c(클라이언트쪽)가 있다면:
```
throughput = min(R_s, R_c)
```
예: R_s = 2Mbps, R_c = 1Mbps → throughput은 **1Mbps**.

#### 여러 connection이 공유할 때 *(p.59)*
여러 connection이 backbone 링크(속도 R)를 **같이 쓰면**, 각자 R을 **균등하게 나눠** 가짐.

```
per-connection throughput = min(R_c, R_s, R / (connection 수))
```
보통 backbone R은 아주 크지만, connection이 엄청 많아지면 R/(수)가 R_c, R_s보다 작아져서 **backbone이 병목**이 될 수 있음. 평소엔 access link(R_c 또는 R_s)가 병목인 경우가 많음.

---

## 5. Security *(슬라이드 p.60~65)*

### 왜 인터넷은 보안이 약한가 *(p.60~61)*
인터넷은 원래 보안을 염두에 두고 설계된 게 아님. 초기 비전은 **"서로 신뢰하는 사용자들이 투명한 네트워크에 붙어 있다"**. 대학이나 연구소 몇 곳을 잇던 시절이라 악의적인 사용자를 가정하지 않았음.

인터넷이 전 세계로 퍼지면서 그 가정이 깨졌고, 지금은 protocol 설계자들이 보안을 **사후에 계속 따라잡는** 중. 이 챕터는 "어떤 공격이 있고, 어떤 방어선이 있나"를 개관하는 수준.

### 공격 유형 *(p.62~64)*

**① Packet sniffing** *(p.62)*
- **broadcast media**(공유 Ethernet, 무선)에서는 신호가 지나가면 같은 매체에 붙은 모든 장치가 받을 수 있음.
- 공격자가 NIC(network interface)를 **promiscuous 모드**로 설정하면, 자기한테 온 게 아닌 패킷까지 **전부 읽음**. 암호화 안 된 **비밀번호**도 포함.
- **Wireshark**가 무료 패킷 스니퍼 (원래는 네트워크 분석용 도구이고, 같은 원리라 공격에도 쓰일 수 있음).

카페 공용 WiFi에서 암호화 안 된 사이트에 로그인하면 위험하다는 말이 이 원리에서 나옴.

**② IP spoofing** *(p.63)*
패킷의 출발지 주소를 **거짓으로 써서** 주입하는 공격. IP는 패킷에 적힌 source 주소를 그대로 믿기 때문에, 공격자가 남의 주소인 척하면 받는 쪽이 속음.

**③ DoS (Denial of Service)** *(p.64)*
공격자가 **대량의 가짜 트래픽**을 보내서 서버나 대역폭 같은 자원을 고갈시키고, **정상 사용자가 서비스를 못 쓰게** 막는 공격. 보통 **botnet**(감염된 여러 대의 컴퓨터)을 이용.

1. 공격 target을 선정
2. 인터넷에 있는 **여러 호스트를 침입**해서 장악(botnet 구성)
3. 장악한 호스트들이 **동시에 target으로 패킷을 전송**

여러 곳에서 동시에 오기 때문에 출처 하나만 차단해서는 막기 어려운 게 특징. 섹션 4 개념으로 보면, traffic intensity를 억지로 1 이상으로 올려서 큐를 터뜨리는 공격.

### 방어선 *(p.65)*

| 방어선 | 하는 일 |
|---|---|
| **authentication** | **신원 증명**. 셀룰러망은 **SIM카드**로 하드웨어 기반 인증. 전통적인 인터넷에는 이런 하드웨어 보조가 없음 |
| **confidentiality** | **암호화(encryption)**로 내용을 숨김 (sniffing 대응) |
| **integrity checks** | **디지털 서명**으로 변조를 막거나 탐지 |
| **access restrictions** | 비밀번호로 보호되는 **VPN** 등으로 접근 제한 |
| **firewalls** | access/core network에 놓인 **middlebox**. 기본적으로 **차단(off-by-default)**하고 허용된 것만 통과. 송신자/수신자/애플리케이션 단위로 제한하고, DoS 탐지/대응도 함 |

공격-방어 짝:
- sniffing → **confidentiality**(암호화)
- spoofing → **authentication**(신원 증명)
- 변조 → **integrity check**
- DoS → **firewall**의 탐지/대응

---

## 6. Protocol Layers & Service Models *(슬라이드 p.66~81)*

### 왜 계층(layer)으로 나누나 *(p.67~70)*
네트워크는 host, 라우터, 링크, 앱, protocol, 하드웨어가 얽힌 복잡한 시스템. 이걸 다루는 방법이 **layering(계층화)**.

- **명시적 구조**: 시스템의 구성요소와 그 관계를 식별할 수 있음 (layered reference model).
- **모듈화**: 유지보수와 업데이트가 쉬워짐. 한 계층의 구현이 바뀌어도 **나머지 시스템에는 투명(영향 없음)**.

**항공 여행 비유**: 티켓 구매 → 짐 부치기 → 게이트 탑승 → 이륙 → 항로 운항. 각각이 하나의 layer. 각 layer는 **자기 내부 작업**을 하고, **바로 아래 layer가 제공하는 서비스를 이용해서** 자기 서비스를 구현. "짐 부치기" 담당은 비행기가 어떤 항로로 가는지 몰라도 되고, 항로를 바꿔도 짐 부치는 절차는 안 바뀜.

### Internet protocol stack: 5계층 *(p.71)*

| Layer | 역할 | 예시 프로토콜 |
|---|---|---|
| **application** | 네트워크 앱 지원 | HTTP, IMAP, SMTP, DNS |
| **transport** | **process ↔ process** 데이터 전송 | TCP, UDP |
| **network** | 출발지 → 목적지 **datagram 라우팅** | IP, routing protocols |
| **link** | **인접한** 네트워크 요소 간 데이터 전송 | Ethernet, 802.11(WiFi), PPP |
| **physical** | 회선 위의 **비트** | - |

각 계층의 "전달 범위":
- transport: **프로세스 간** (같은 host 안의 어느 앱인지까지)
- network: **host 간** (출발지 host → 목적지 host 전체 경로)
- link: **바로 옆 노드 간** (한 홉)

### OSI 7계층 모델 *(p.72, p.74)*
ISO(International Standards Organization)가 만든 국제 표준 모델. Internet 5계층에 **presentation**과 **session** 두 계층이 더해진 **7계층**.

```
7 Application   - 네트워크 자원 접근 허용
6 Presentation  - 데이터 번역/암호화/압축
5 Session       - 세션 수립/관리/종료
4 Transport     - 신뢰성 있는 process-to-process 전달, 에러 복구
3 Network       - 패킷을 출발지 → 목적지로 이동, 인터네트워킹
2 Data link     - 비트를 프레임으로 조직, hop-to-hop 전달
1 Physical      - 매체 위로 비트 전송, 기계적/전기적 스펙
```

Internet stack에는 presentation과 session이 **없음**. 실제 인터넷에서는 이 두 기능이 필요하면 **애플리케이션이 직접 구현**. Internet 5계층의 application 계층 하나가 OSI의 5~7계층 역할을 다 포함한다고 보면 됨.

### TCP/IP 계층별 실제 프로토콜 매핑 *(p.75)*

| 계층 | 소속 프로토콜 |
|---|---|
| **Application** (OSI 5~7에 해당) | SMTP, FTP, HTTP, DNS, SNMP, TELNET 등 |
| **Transport** | SCTP, **TCP**, UDP |
| **Network (internet)** | **IP** (+ ICMP, IGMP는 제어용 / ARP, RARP는 주소 변환용) |
| **Data link / Physical** | 하위 네트워크가 정의하는 프로토콜 (host-to-network) |

- **ARP** (Address Resolution Protocol): "주소 해석". **IP주소 → MAC주소** 변환
- **RARP** (Reverse ARP): 반대로 **MAC주소 → IP주소** 변환
- **ICMP** (Internet Control Message Protocol): **오류/제어 메시지**. traceroute와 ping이 사용 (traceroute에서 TTL이 0이 되면 돌아오는 응답이 ICMP)
- **IGMP** (Internet Group Management Protocol): **멀티캐스트 그룹** 관리

network 계층의 핵심 프로토콜은 **IP**, ARP/RARP/ICMP/IGMP는 IP를 보조.

### Encapsulation (캡슐화) *(p.76~81)*
각 계층은 **위 계층에서 받은 데이터에 자기 헤더를 붙여서(encapsulate)** 아래 계층으로 넘김. **마트료시카 인형**처럼 겹겹이 감싸는 구조.

| 계층 | 데이터 단위 이름 | 구조 | 하는 일 |
|---|---|---|---|
| application | **message** | M | 앱이 보내려는 원본 데이터 |
| transport | **segment** | H_t + M | process 간 전송(예: 신뢰성 있게)을 위해 M을 캡슐화 |
| network | **datagram** | H_n + H_t + M | host 간 전송을 위해 segment를 캡슐화 |
| link | **frame** | H_l + H_n + H_t + M | 인접 호스트 간 전송을 위해 datagram을 캡슐화 |

H는 **header**, 아래첨자는 계층(t = transport, n = network, l = link). 아래로 내려갈수록 헤더가 **앞에 하나씩 덧붙음**. 수신 측에서는 반대로 위로 올라가면서 헤더를 **하나씩 벗겨냄(decapsulation)**.

**message → segment → datagram → frame**은 시험에 자주 나오는 부분.

**End-to-end 관점**: 데이터가 source에서 destination까지 가는 동안, 중간 장치는 **자기가 필요한 계층까지만** 열어봄.

| 중간 장치 | 처리하는 계층 |
|---|---|
| **switch** | link, physical까지 |
| **router** | network, link, physical까지 |
| **end host (송수신 단말)** | 5계층 전부 |

router는 datagram의 목적지 IP 주소만 보고 forwarding table을 조회하면 되니까, transport 헤더나 application 데이터는 열어볼 필요가 없음. 각자 필요한 계층까지만 열어 처리한 뒤, 다시 캡슐화해서 다음 노드로 넘김. 계층화의 **모듈화** 이점이 실제로 나타나는 부분.

---

## 7. Internet History *(슬라이드 p.83~87)*

큰 흐름: 패킷 스위칭 이론 → ARPAnet(최초의 패킷망) → 네트워크가 여러 개로 늘어남 → TCP/IP로 통일 → Web으로 대중화·상업화 → 모바일/클라우드 시대

### 1961~1972: 패킷 스위칭의 탄생 *(p.83)*
- **1961** Kleinrock가 큐잉 이론 발표
- **1964** Baran이 군사용 패킷 교환 연구
- **1967** ARPAnet 고안 → **1969** 첫 노드 가동 → **1972** 공개 데모
- **NCP**(최초의 host-host protocol), 첫 이메일 등장, 노드는 15개

### 1972~1980: 인터네트워킹의 원칙 *(p.84)*
- **1970** ALOHAnet (하와이의 무선 패킷망)
- **1974** **Cerf & Kahn**이 인터네트워킹 아키텍처 제안. 이때 정한 원칙이 오늘날 인터넷 아키텍처를 정의.
  - **minimalism / autonomy** (네트워크는 최소한만 하고, 각 망은 자율적)
  - **best-effort** (최선을 다하지만 보장은 안 함)
  - **stateless routing** (라우터가 연결 상태를 기억하지 않음)
  - **decentralized control** (분산 제어)
- **1976** Ethernet, DECnet 같은 사설 프로토콜이 난립, **1979** 노드 200개

### 1980~1990: TCP/IP 시대 *(p.85)*
- **1982** SMTP, **1983** **TCP/IP 배포** + DNS, **1985** FTP
- **1988** **TCP 혼잡제어** (섹션 3의 packet switching congestion 문제의 해법)
- CSnet, BITnet, NSFnet 등 각국의 신규망, 호스트 **10만 개**

### 1990~2000년대: Web과 상업화 *(p.86)*
- ARPAnet 퇴역, **1991** NSFnet이 상업적 사용을 허용
- **Web**(HTML/HTTP)은 Berners-Lee가 만들었고, **1994** Mosaic 브라우저가 대중화
- 상업화, 인스턴트 메시징, P2P, 네트워크 **보안**이 부상
- 호스트 5천만+, 사용자 1억+

### 2005~현재 *(p.87)*
- 가정 **광대역** 접속 확대, **SDN**(2008)
- **4G/5G/WiFi** 고속 무선 확산
- 대형 서비스업체의 **자체망** 구축 (섹션 3의 content provider network), **클라우드**(AWS, Azure)
- **2017** 모바일 기기가 유선을 초과, **2023** 약 150억 대 기기 연결

---

## Chapter 1 핵심 요약 *(p.88)*

- 인터넷 구조(nuts and bolts / services 두 관점), protocol의 정의
- **Network edge**(hosts, access network, physical media) vs **Network core**(packet/circuit switching, Internet 구조)
- 성능: delay(4요소), loss, throughput
- 보안 개요
- 계층화(layering)와 캡슐화(encapsulation)
- 인터넷 역사

사전 지식 없이 "feel"과 용어를 잡는 개론. access network 세부, 라우팅, 전송 계층, 보안 같은 각 주제는 이후 장에서 깊게 다룸.
