# Chapter 7: Denial-of-Service Attacks (수업노트)

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

## 0. 선수 지식

### TCP 3-way handshake
**TCP 3-way handshake**: TCP 연결을 맺기 전에 클라이언트와 서버가 SYN, SYN-ACK, ACK 3개 패킷을 주고받아 서로 연결할 준비가 됐는지 확인하는 절차.

전화 통화 비유
1. 클라이언트: "여보세요, 내 말 들려?" → **SYN**
2. 서버: "응 들려, 너는 내 말 들려?" → **SYN-ACK**
3. 클라이언트: "응 들려" → **ACK**

- 서버는 SYN을 받으면 "이 클라이언트와 연결 진행 중"이라는 기록을 **메모리 테이블**에 만들고 3번째 ACK를 기다린다.
- 이 테이블은 **크기가 한정**돼 있다. → SYN flooding의 핵심

### ICMP와 ping
**ICMP(Internet Control Message Protocol)**: IP 네트워크에서 상태 확인이나 오류 보고에 쓰는 제어용 프로토콜.
- **ping**: ICMP **echo request**를 보내고 상대가 **echo reply**를 돌려주면 "살아있고 통신 된다"를 확인하는 명령어.
- 진단에 유용해서 대부분의 네트워크가 ping 패킷을 통과시킨다. 공격자는 이 점을 이용한다.

### TCP vs UDP
- **TCP**: 연결을 먼저 맺고(handshake), 데이터가 빠짐없이 순서대로 가도록 보장. (전화)
- **UDP**: 연결 없이 그냥 던진다. 확인도 재전송도 없어서 빠르고 가볍다. (엽서)

### IP spoofing
**IP spoofing**: 패킷의 source IP 주소 칸에 진짜 주소 대신 **가짜 주소**를 적어 보내는 것.
- 편지 봉투의 보내는 사람 주소를 아무렇게나 적는 것과 같다.
- 답장은 **적힌 주소로** 간다. 위조한 주소가 피해자 주소면 응답이 전부 피해자에게 몰린다. 공격자는 응답을 못 받지만, 응답이 필요 없는 공격이면 상관없다.
- 공격자를 **추적하기 어려워진다**.
- (Q&A) 응답이 피해자에게 가니 공격자를 추적하기 어렵다는 건 맞고, 하나 더 그 응답 패킷들이 **피해자를 향한 공격 트래픽**이 된다. 뒤의 reflection 공격의 원리.

### Bot(좀비)
**Bot(좀비)**: 악성코드에 감염돼서 주인 몰래 공격자의 명령을 따르게 된 일반 사용자의 PC.
- 이런 PC 수천~수만 대를 한 명이 조종하는 것이 **botnet**.

## 1. DoS 정의와 공격 대상 자원 *(p.2~5)*

**DoS(Denial-of-Service) 공격**: 서버의 CPU, 메모리, 대역폭, 디스크 같은 자원을 고갈시켜서 정당한 사용자가 서비스를 쓰지 못하게 만드는, **가용성(availability)** 에 대한 공격. *(p.3 NIST 정의)*

- 보안의 3요소(CIA) 중 **A**를 노린다. 데이터를 훔치거나 바꾸는 게 아니라 **그냥 못 쓰게** 만드는 게 목적.

### 공격 대상 자원 3가지 *(p.4)*

| 대상 | 무엇을 고갈시키나 | 비유 (식당) |
|---|---|---|
| **Network bandwidth** | 서버를 인터넷에 연결하는 **링크 용량** (보통 ISP 연결) | 식당 앞 **도로**를 차로 막아서 손님이 못 들어옴 |
| **System resources** | OS의 **네트워크 처리 코드** 등을 과부하·crash | 식당의 **예약 장부**를 가짜 예약으로 가득 채움 |
| **Application resources** | 각각 자원을 많이 쓰는 **유효한 요청**을 다수 보내 앱 마비 | 주방이 오래 걸리는 **주문만 수천 개** 받아서 다른 손님 주문을 못 함 |

- p.5 Figure 7.1은 이 세 가지가 네트워크의 어느 지점(ISP 링크, 서버, 웹앱)에 해당하는지 보여준다.
- Network bandwidth: ICMP flood, UDP flood, (TCP)
- System resources: **TCP SYN flooding**
- Application resources: **HTTP flooding**
- (Q&A) 오래 걸리는 DB 검색 요청을 정상 요청처럼 대량 전송 → **Application resources**. 요청 하나하나는 유효한데 각각 자원을 많이 써서 앱이 다른 사용자를 처리 못 하기 때문.

## 2. Classic DoS: Flooding ping *(p.6)*

**Flooding ping**: 대상 시스템에 ICMP echo request를 엄청난 양으로 쏟아부어서 대상 네트워크의 **연결 용량을 압도**하는 가장 고전적인 DoS 공격. (Network bandwidth 공격)

### 공격자 입장의 장점 3가지
1. **만들기 쉽다.** ping 명령어만 있으면 된다.
2. **대부분 라우터가 통과시킨다.** ping은 진단용이라 허용해 두는 경우가 많다.
3. **대부분 서버가 reply를 한다.** 응답까지 생겨 트래픽이 더 늘어난다.

### 어떻게 효과가 나나
- 대상을 목적지로 한 패킷을 대량으로 보내면 경로 중간의 **고용량 링크**는 잘 처리한다.
- 하지만 마지막 **저용량 링크**에서 라우터가 못 감당해 **혼잡(congestion)** 이 생기고 패킷이 버려져 성능이 눈에 띄게 떨어진다.

### 단점 2가지 (공격자 입장)
- **단점1**: 중간 고용량 링크에서는 문제없이 흐르다가 용량이 줄어드는 지점에서야 버려진다. 공격자는 **대상 링크 용량보다 더 큰 트래픽**을 만들어야 효과가 있다.
- **단점2**: source 주소를 위조하지 않으면 **공격 출처가 그대로 드러난다.**

(Q&A) 공격자가 10Mbps 회선에서 1Gbps 서버에 flooding ping을 쏘면 효과 없음. 서버 링크 용량보다 작은 트래픽은 그냥 소화되기 때문. 이 한계를 넘으려고 나온 게 **DDoS**(여러 대가 동시에 공격).

## 3. Source Address Spoofing *(p.7)*

**Source address spoofing**: 패킷의 source 주소를 **위조**해서 공격 시스템을 식별하기 어렵게 만드는 기법.

- 보통 OS의 **raw socket interface**로 수행. 일반 소켓은 OS가 source 주소를 알아서 채우지만, raw socket은 패킷 헤더를 **직접 만들어 넣을 수 있어서** 위조가 가능.
- 위조하면 출처 식별이 어렵다. 추적하려면 네트워크 엔지니어가 **라우터에서 flow 정보를 직접 조회**해야 한다.

### Backscatter traffic
- 공격자가 **랜덤한 가짜 주소**로 패킷을 보내면 서버의 응답이 그 가짜 주소들로 **사방에 흩어진다.** 이 흩어진 응답이 **backscatter traffic**.
- 흩어진 응답을 관찰하면 **누군가 spoofing 공격을 하고 있다**는 걸 알 수 있다.

### Honeynet Project
- **사용하지 않는 IP 주소 대역의 경로를 광고(advertise)** 해 둔다. 위조된 패킷의 응답(backscatter)이 이쪽으로 흘러들어오고, 이걸로 **공격 트래픽을 모니터링**한다.
- 빈집 주소를 우체국에 등록해 놓고 거기로 오는 이상한 우편물을 관찰하는 것.

(Q&A) 공격자가 랜덤한 가짜 주소를 쓰는 이유 (슬라이드엔 없고 보충 설명)
1. **정체 숨기기**: 진짜 주소를 쓰면 바로 추적된다.
2. **차단 회피**: source가 하나로 고정되면 "이 주소 차단"으로 쉽게 막힌다. 매번 다른 주소를 쓰면 주소 기반 필터링이 거의 무의미해진다.
- 랜덤 주소는 **응답을 공격자가 받을 필요가 없는 공격**(flooding, SYN flood 등)에서 쓴다. 응답을 받아야 하는 공격에는 못 쓴다.
- backscatter가 생기는 이유: 서버는 요청의 source 주소를 보고 응답을 보내는데 그 주소가 가짜라 응답이 엉뚱한 주소들로 흩어진다.

## 4. Flooding Attacks *(p.8)*

**Flooding attack**: 특정 네트워크 프로토콜의 패킷을 대량으로 보내서 서버로 가는 링크의 용량을 과부하시키는 공격. **프로토콜 종류**로 분류한다.

- 사실상 **어떤 패킷이든** 쓸 수 있다. 목표는 패킷 내용이 아니라 **양**.

| 종류 | 설명 |
|---|---|
| **ICMP flood** | ICMP echo request로 ping flood. ping이 유용한 진단 도구라 관리자들이 **전통적으로 허용**해 와서 막히지 않는 경우가 많다 |
| **UDP flood** | 대상 시스템의 **특정 포트 번호**로 UDP 패킷을 보냄 |
| **TCP SYN flood** | 대상에 TCP 패킷을 보냄. 시스템 코드가 아니라 **패킷의 총량**이 목표 |

- 헷갈리기 쉬운 포인트: p.8의 **TCP SYN flood**는 패킷 **총량**으로 링크를 채우는 대역폭 공격, p.9의 **SYN spoofing**은 연결 테이블을 overflow시키는 **시스템 자원** 공격. 둘 다 SYN을 쓰지만 **노리는 대상이 다르다**.
- (Q&A) 사용자 답: 하나는 패킷 양으로 링크 용량을 초과시켜 과부하, 하나는 SYN으로 시스템 자원을 공격. 보정: SYN spoofing은 버퍼 오버플로우 같은 **코드 취약점**을 쓰는 게 아니라, TCP의 **정상 동작(handshake 중 상태 저장)** 을 악용해 연결 관리 **테이블을 가득 채우는** 것. 정상 기능만으로 되는 공격이라 패치로 막기도 어렵다.

## 5. SYN Spoofing *(p.9~11)*

**SYN spoofing**: source를 위조한 SYN 패킷을 대량으로 보내 서버의 **연결 관리 테이블을 가득 채워서**, 정당한 사용자의 새 연결 요청을 받지 못하게 만드는 공격. (System resources 공격: OS의 네트워크 처리 코드가 대상)

### handshake를 서버 관점으로 *(p.10, Figure 7.2)*
1. 클라이언트 SYN (seq=x)
2. 서버 SYN-ACK (seq=y, ack=x+1) → **서버는 이 시점에 "진행 중 연결" 엔트리를 테이블에 만들고 ACK를 기다림**
3. 클라이언트 ACK (ack=y+1) → 연결 완성

### 공격 과정 *(p.11, Figure 7.3)*
1. 공격자가 **위조된 source 주소**로 SYN을 보낸다.
2. 서버는 정상대로 그 주소로 **SYN-ACK**를 보내고 엔트리를 만들어 둔다. 그 주소는 **존재하지 않는 클라이언트**라 SYN-ACK는 **버려진다**.
3. 3번째 ACK가 영원히 안 오니 서버는 **timeout 후 SYN-ACK를 재전송**해보다가 **연결 요청 실패로 간주**하고 엔트리를 지운다.

- 공격자가 SYN을 계속 쏘면 대기 중 엔트리가 만료되기도 전에 새 엔트리가 쌓여 테이블이 가득 차고, 진짜 사용자의 SYN은 **자리가 없어서 거부**된다.
- 위조 주소를 쓰는 이유 (보충): 진짜 주소를 쓰면 그 PC가 SYN-ACK를 받고 RST로 정리해 엔트리가 빨리 지워지고 출처도 드러난다. 존재하지 않는 주소를 쓰면 응답 없이 엔트리가 오래 남는다.
- (Q&A) 공격자가 ACK로 답하지 않으면: 서버는 응답을 기다리다 만료되면 엔트리를 지우지만, 기다리는 시간보다 빠르게 새 엔트리가 생겨 테이블이 가득 차 사용자가 TCP 연결을 못 한다. 이 SYN만 받고 ACK를 못 받은 상태가 **half-open** 연결.

## 6. Application Resources: HTTP 기반 공격 *(p.12)*

앞의 공격들은 네트워크/OS 수준, 이번엔 **애플리케이션(웹서버)** 이 대상.

### HTTP flood
**HTTP flood**: 웹서버에 HTTP 요청을 대량으로 보내 상당한 자원을 소모시키는 공격.
- **Spidering**: bot이 주어진 HTTP 링크에서 시작해 그 사이트의 **모든 링크를 재귀적으로 따라가며** 요청. 검색엔진 크롤러와 같아서 서버 입장에서는 정상 요청처럼 보인다. 요청마다 페이지 생성, DB 조회 등 자원이 들어가 부하가 커진다.

### Slowloris (2009)
**Slowloris**: 완성되지 않는 HTTP 요청을 천천히 계속 보내 연결을 붙잡아두는 방식으로 웹서버의 연결 수용량을 소진시키는 공격.

1. 대상 웹서버에 연결을 열고 **부분 요청(partial request)** 만 보낸다.
2. 주기적으로 **후속 헤더를 조금씩 추가**로 보낸다. 요청을 완성하지는 않으면서 연결이 끊기지 않게 유지.
3. 서버는 요청이 끝나길 기다리며 이 연결들을 계속 열어둔다.
4. **최대 동시 연결 풀**이 가득 차면 다른 클라이언트의 연결을 거부한다.

무서운 이유
- 트래픽 양이 적어 대역폭을 안 쓴다. 느리게 보내므로 **정상 HTTP 트래픽**처럼 보인다.
- **signature 기반 IDS/IPS는 일반적으로 탐지하지 못한다.** 공격 패킷에 특별한 패턴이 없다.

### 비교 (Q&A 정리)
| | 고갈시키는 것 | 방식 |
|---|---|---|
| flooding ping | 링크 **대역폭** | 트래픽 **양**으로 압도 |
| SYN spoofing | TCP 연결 **테이블** | 완성 안 된 **handshake**를 붙잡음 |
| Slowloris | 웹서버 **연결 풀** | 완성 안 된 **HTTP 요청**을 붙잡음 |

- SYN spoofing과 Slowloris는 둘 다 **연결 슬롯을 점유**해 새 연결을 못 받게 만든다. 계층 차이: TCP 테이블 vs 웹서버 연결 풀.
- Slowloris는 트래픽이 적어도 되므로 양 기준으로 이상을 감지하는 방어에도 안 걸린다.

## 7. DDoS *(p.13~14)*

flooding ping은 공격자 회선이 대상 링크보다 작으면 효과가 없다는 한계가 있었다. 이를 해결한 것이 DDoS.

**DDoS**: 여러 시스템을 동원해 동시에 한 대상을 공격해서, 단일 공격자 회선의 한계와 단순 차단을 모두 넘어서는 DoS 공격.

### 여러 시스템 확보 *(p.13)*
- 공격자가 **OS나 흔한 애플리케이션의 취약점**으로 다른 사람의 컴퓨터에 침투해 자기 프로그램을 설치. 이렇게 조종당하는 컴퓨터가 **zombie**.
- 한 공격자가 통제하는 이런 시스템의 대규모 집합이 **botnet**.
- 예: **Tribe Flood Network (TFN), TFN2K** (초기 DDoS 도구)

### DDoS 공격 구조 *(p.14, Figure 7.4)*
**Attacker → Handler zombies → Agent zombies → Target**
- **Attacker**: 명령을 내리는 공격자
- **Handler zombies**: 공격자의 명령을 받아 agent들에게 **전달·관리**하는 중간 계층
- **Agent zombies**: 실제로 **공격 트래픽을 쏘는** 말단 PC
- 계층 구조 덕분에 공격자는 수많은 agent를 직접 다루지 않고 뒤로 숨는다.

### DDoS가 강력한 이유 (보충)
- 각 PC가 조금씩만 쏴도 합치면 **대상 링크 용량을 넘긴다.**
- 공격 출처가 수천 곳이라 **한 곳만 차단해서는 못 막는다.**

(Q&A) handler zombie가 있는 이유: Attacker가 직접 명령하면 위험하므로 중간 계층이 **신원을 보호하는 완충 역할**(추적당해도 handler에서 끊김). 보충: 수천 대를 직접 다루는 것보다 handler가 일부씩 맡는 **관리 효율**도 이유.

## 8. Botnet *(p.15~20)*

**Botnet**: bot-master가 malware로 구성한 다수의 bot(감염 PC)과 그 조종자로 이루어진 네트워크.

### 용어 *(p.15)*
| 용어 | 의미 |
|---|---|
| **Bot-master** | malware로 botnet을 만들고 bot에 **명령과 제어**를 보내는 사람 |
| **Bot** | bot-master가 개발한 malware. client 머신에서 **악의적 활동** 수행 |
| **Botnet** | 다수의 bot + bot-master로 이뤄진 네트워크 |
| **C&C server** (Command & Control) | bot-master의 명령을 bot들에게 **전달하는 중간 서버** |

### 감염 경로 *(p.16)*
- **Browser Exploits 65%** (압도적 1위)
- Email Attachments 13%
- OS Exploits 11%
- Downloaded Files 9%
- Others 2%

### 악의적 활동 *(p.17)*
- **Spam mails**, **DDoS attacks**, **Traffic sniffing**, **Key logging**, **Phishing**, 추가 **malware 설치**
- DDoS만 하는 게 아니다.

### 특징: 왜 대응이 어려운가 *(p.18)*
- **복잡한 구조**: worm/virus, backdoor, spyware, rootkit 등의 조합
- **일반 사용자의 PC**를 쓰니 **합법적인 IP 주소**
- PC 한 대당 보내는 공격 패킷이 **적어서** 눈에 안 띔
- DDoS가 터져도 **정상 사용자 트래픽과 botnet 트래픽을 구분하기 어려움**
- 새 botnet 기술이 **계속 개발**됨

(Q&A) 일반 PC를 쓰는 게 유리한 이유: 합법적인 IP라 spoofing 필터나 "수상한 IP 차단"이 안 통하고 차단하면 무고한 사용자를 막게 된다. PC당 패킷이 적어 개별로는 정상 트래픽과 똑같아 보이고 합쳐졌을 때만 거대해진다. → 방어자가 "누굴 막아야 하는지" 정하기 힘들다.

### 동작 메커니즘 *(p.19)*
1. **전파**: 취약점, 이메일 등으로 malware 전파
2. 감염된 PC들이 **botnet**을 이룸
3. bot이 **C&C server**(웹서버, IRC 등)에 **접속**
4. Botmaster가 C&C를 통해 **command/control** 전달
5. C&C가 bot들에게 **명령과 bot update** 전달
6. bot들이 Victim에게 **DDoS, spam mail** 등 수행

### 통신 구조 *(p.20)*
C&C 통신 채널: **IRC**, **HTTP**, **P2P**, **Social media**(Facebook, Twitter 등), **DNS** request/reply
- 일반적인 서비스 트래픽에 섞여 숨기려는 목적. HTTP나 SNS 트래픽은 방화벽도 허용하는 경우가 많다.

## 9. Reflection Attacks *(p.21~22)*

**Reflection attack**: source 주소를 **피해자 주소로 위조**한 패킷을 제3의 서버(중간자)에 보내서, 그 서버의 **응답이 피해자에게 쏟아지게** 만드는 공격.

### 동작 *(p.21)*
1. 공격자가 알려진 서비스를 제공하는 **중간자(intermediary)** 에게 패킷을 보낸다. source는 **실제 대상(Target)의 주소로 위조**.
2. 중간자는 정상 동작대로 **응답을 보내는데 그 응답은 Target으로** 간다.
3. 공격이 중간자에서 **"반사(reflect)"** 되어 Target에게 도달. 그래서 중간자를 **reflector**라 한다.

- 목표: 중간자가 **눈치채지 못하게** Target의 링크를 flood할 만큼 충분한 패킷량을 만드는 것. 중간자 입장에선 정상 요청에 정상 응답을 한 것뿐.
- 공격자에게 유리한 점: 트래픽이 공격자가 아니라 **reflector에서** 오는 것처럼 보여 출처를 숨길 수 있고, 수많은 정상 서버를 reflector로 쓰면 출처가 매우 분산된다.
- **기본 방어**: **spoofed-source 패킷 차단**. 위조된 source만 막으면 공격이 성립하지 않는다.

### Amplification Attack 구조 *(p.22, Figure 7.7)*
**Attacker → Zombies → Reflector intermediaries → Target**
- Attacker가 zombie들을 동원하고, zombie들이 여러 reflector에 spoofed 패킷을 보내 reflector들이 Target을 때린다. DDoS와 reflection이 합쳐진 구조.
- 그림 제목이 "Amplification"인 이유: reflection만으로는 보낸 양만큼만 가지만 응답이 요청보다 **훨씬 크면 증폭**된다.

(Q&A) Target 입장에서 출발지는 **reflector**로 보인다. 공격자까지 가는 경로가 여러 겹이라 찾기 힘들다. 보충: reflector 로그에도 공격자가 아니라 "Target이 요청한 것"처럼 남고, reflector를 차단하면 **정상 서비스(예: 공용 DNS 서버)** 까지 막게 된다.

## 10. DNS Amplification Attacks *(p.23)*

**DNS amplification attack**: 정당한 DNS 서버를 reflector로 써서, 작은 DNS 요청이 훨씬 큰 응답으로 부풀려지는 점을 이용해 대상을 응답 폭탄으로 flood하는 reflection 공격.

- **DNS**: 도메인 이름(예: `google.com`)을 IP 주소로 바꿔주는 서비스. 보통 UDP라 handshake가 없어 source 위조가 쉽다.

### 동작
1. 공격자가 **대상(Target)의 주소를 source로 위조한 DNS 요청**을 연속으로 만들어 DNS 서버에 보낸다.
2. DNS 서버는 정상 동작대로 **응답을 Target에게** 보낸다.
3. **DNS의 동작을 악용**해 작은 요청이 **훨씬 큰 응답으로 변환(amplification)** 되게 한다. Target은 큰 응답들로 flood된다.

- 요청은 수십 바이트로 작지만 응답은 레코드를 많이 담아 **수십~수백 배** 커질 수 있다(구체적 배율은 슬라이드에 없는 보충). 공격자는 적은 대역폭으로 큰 공격 트래픽을 만든다.
- **기본 방어**: **spoofed source address 사용을 막는 것.** 공격의 뿌리가 source 위조.

### reflection vs amplification (Q&A 정리)
- **Reflection**: 제3의 서버를 거쳐서 **출처를 숨기고 응답을 Target에게 돌리는** 것. (방향 전환)
- **Amplification**: 작은 요청이 **큰 응답으로 커지는** 성질을 이용해 **트래픽을 부풀리는** 것. (크기 증폭) DNS 전용 개념이 아니고 DNS는 예시 중 하나.
- **DNS amplification**: DNS 서버를 reflector로 쓰고(reflection) 그 응답이 요청보다 크다는 점(amplification)까지 쓰는 **두 가지의 결합**.

## 11. DoS 방어: 4개 라인 *(p.24)*

- **DoS 공격은 완전히 막을 수 없다.** 트래픽 폭증이 **정당한 사용자 몰림**(이벤트, 뉴스 등)일 수도 있어 많다고 무조건 차단할 수도 없다. 그래서 방어를 시간 순서로 4단계로 나눈다.

| 단계 | 시점 | 하는 일 |
|---|---|---|
| **1. Attack prevention and preemption** | 공격 **전** | 공격이 성립하지 못하게 사전 차단 |
| **2. Attack detection and filtering** | 공격 **중** | 공격을 탐지하고 해당 트래픽을 필터링 |
| **3. Attack source traceback and identification** | 공격 **중·후** | 공격 출처를 역추적·식별 |
| **4. Attack reaction** | 공격 **후** | 공격에 대응하고 사후 처리 |

## 12. DoS 공격 예방 *(p.25~26)*

### (1) spoofed source 주소 차단 *(p.25)*
- 가능한 한 **source에 가까운 라우터**에서 차단. 위조 패킷이 인터넷으로 퍼지기 전에 막는 게 가장 효율적.
- 패킷의 source 주소로 **돌아가는 경로**가 지금 이 패킷이 들어온 경로와 같은지 확인하는 필터를 쓴다.
- Cisco 예: `ip verify unicast reverse-path`
  - 라우터가 들어오는 패킷을 검사해, **source IP로 가는 경로가 그 패킷이 도착한 같은 인터페이스를 가리키는 항목이 CEF(Cisco Express Forwarding) 테이블에 없으면 패킷을 버린다.**
  - "이 주소가 저쪽 방향에 있다고 아는데 왜 이쪽에서 왔지?" 하고 위조로 판단. **reverse path filtering**이라고도 한다(보충 용어).

### (2) 수정된 TCP 연결 처리: SYN cookie *(p.25)*
SYN spoofing 방어법.
- 서버가 핵심 정보를 **암호학적으로 인코딩한 cookie**를 만들어 SYN-ACK의 **initial sequence number**로 보낸다.
- 서버는 이 시점에 **상태를 테이블에 저장하지 않아도 된다.**
- 정당한 클라이언트는 **cookie+1**을 담은 ACK로 응답하고, 서버는 그 값을 검증한 뒤에야 연결을 만든다. 위조 주소의 공격자는 SYN-ACK를 못 받으니 cookie를 몰라서 완성된 연결을 못 만든다.
- 추가로 테이블이 overflow되면 **미완료 연결 엔트리를 제거**.
- (Q&A) SYN cookie 앞에서 SYN spoofing이 무력한 이유: 서버가 half-open 상태를 **저장하지 않으니** 테이블이 가득 찰 일이 없다.

### (3) 그 외 예방책 *(p.26)*
- **IP directed broadcast 차단**: 보내는 머신에 **직접 연결되지 않은 서브넷의 broadcast 주소**로 보내는 datagram. 열어두면 한 패킷이 그 서브넷 모든 호스트로 퍼져 증폭에 악용된다.
- **의심스러운 서비스와 조합 차단**
- **CAPTCHA** 같은 graphical puzzle로 애플리케이션 공격 관리 → **사람의 요청과 봇을 구분**
- **일반적인 좋은 시스템 보안 관행**
- 고성능·고신뢰성이 필요하면 **mirrored and replicated servers** 사용

## 13. DoS 공격 대응 *(p.27~28)*

### 사전 준비 *(p.27)*
- **Antispoofing**, **IP directed broadcast 차단**, **rate limiting 필터**가 구현돼 있어야 한다. (rate limiting: 단위 시간당 트래픽 양 제한)
- 이상적으로는 **network monitor와 IDS**가 비정상 트래픽 패턴을 탐지·통보.

### 대응 절차 *(p.28)*
1. **공격 유형 식별**
   - 패킷 **캡처·분석**
   - 공격 트래픽을 **upstream에서 차단하는 필터** 설계 (upstream: ISP 등 공격이 들어오는 위쪽)
   - 또는 **시스템/애플리케이션 버그**를 식별·수정
2. **ISP가 패킷 흐름을 source까지 추적**
   - **어렵고 시간이 오래 걸릴 수 있다.**
   - 하지만 **법적 조치**를 계획한다면 **필수**.
3. **Contingency plan 실행**
   - **대체 백업 서버**로 전환
   - **새 사이트에 새 주소로 새 서버** 가동
4. **Incident response plan 갱신**
   - 공격과 대응을 **분석**해서 향후 대응에 반영

앞 단계의 4개 라인(예방/탐지·필터/역추적/사후)이 이 절차에 그대로 대응된다.

## 14. Summary *(p.29)*

- **DoS**: 본질 / Classic DoS / Source address spoofing / SYN spoofing
- **Flooding**: ICMP / UDP / TCP SYN flood
- **DDoS**
- **Application-based bandwidth attack**: HTTP 기반 공격
- **Reflection & amplifier**: Reflection / DNS amplification
- **방어 및 대응**

## 종료 점검 (Q&A)

- 공격 분류 매핑: flooding ping → **Network bandwidth**, SYN spoofing → **System resources**(TCP 연결 테이블, source 위조), HTTP flood·Slowloris → **Application resources**
- DDoS: 구조는 **Attacker → Handler → Agent zombies → Target**의 계층. DoS보다 강력한 이유는 합산 트래픽이 **대상 링크 용량을 넘기고**, 출처가 합법적인 IP로 분산돼 **차단이 안 된다**는 것.
