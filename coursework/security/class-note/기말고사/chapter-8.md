# Chapter 8: Intrusion Detection System (수업노트)

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

슬라이드 번호는 PDF 페이지 기준(`p.N`).

## 선수 개념

1. **방화벽**: 미리 정한 규칙에 따라 네트워크 트래픽을 **허용/차단(check-then-pass/deny)** 하는 장비. 트래픽 경로에 직접 끼어 있어서 IDS와 달리 막을 수 있음
2. **계층 구조**: network 계층은 IP로 주소를 보고 라우팅, transport 계층은 TCP/UDP로 포트와 연결을 다룸, application 계층은 HTTP, FTP, DNS 같은 실제 서비스 프로토콜. NIDS는 이 세 계층을 다 검사할 수 있음
3. **promiscuous mode**: NIC가 자기 MAC 주소로 온 패킷만이 아니라 지나가는 **모든 패킷을 수신**하는 모드. NIDS sensor가 트래픽을 엿볼 때 사용
4. **False positive / false negative**: false positive(오긍정)는 정상 사용자를 침입자로 판정, false negative(오부정)는 침입자를 정상으로 놓치는 것
5. **시스템 콜**: 유저 프로그램이 파일, 프로세스, 네트워크 같은 커널 기능을 쓰려고 호출하는 **커널 진입 인터페이스**(`open`, `fork`, `execve` 등). HIDS가 이걸 감시해서 이상 행동을 찾음

## 1. 침입자와 침입 *(p.3~4)*

**Cyber Criminals**: 금전적 보상을 목적으로 하는 개인 또는 조직범죄 집단.
- 활동: Identity theft, 금융 인증정보 탈취, 산업스파이(Corporate espionage), 데이터 탈취, Data ransoming(데이터 인질 협박)
- underground forum에서 팁과 데이터를 거래하고 공격을 조율

p.4의 침입 사례는 기술적인 것(remote root compromise, 웹 defacement, 패스워드 크래킹, packet sniffer 실행)만 있는 게 아니다. **사회공학**(임원 사칭)이나 **물리적 부주의**(자리 비운 workstation 사용, 보호 안 된 modem)도 침입으로 분류된다. 이게 나중에 "왜 방화벽만으로 부족한가"의 근거가 된다.

## 2. IDS 정의 *(p.5)*

**침입탐지(Intrusion detection)**: 보안 방어선을 뚫고 비인가된 방법으로 내부 자원에 접근하거나 시도하는 사건을 모니터링·분석해서, 보안 사고의 징후를 찾아내고 기록하고 경고하는 일련의 과정.

**IDS**: 이 탐지 작업을 자동으로 수행해서, 보안 관리자나 다른 보안장치가 침입에 적절히 대응할 수 있게 지원하는 시스템. 핵심은 **지원**이다. IDS가 직접 막는 게 아니라 알려주는 역할이다.

## 3. IDS의 필요성 *(p.6)*

보통 내부 자원은 사용자 인증, 접근 제어, 방화벽으로 보호하지만 이것만으로는 부족하다.
1. 새로운 공격 방법이 끊임없이 나온다.
2. 사용자가 악성코드를 정상적으로 다운받아 실행하면 막기 어렵다. 인증도 통과하고 방화벽도 통과한 정상 행위처럼 보이기 때문이다.
3. 사회공학 공격은 기술적 방어선을 우회한다.
4. 내부 사용자의 부주의나 변심은 이미 인가된 사람이라 막기 어렵다.

## 4. IDS의 목적 *(p.7)*

- 침입에 의한 손실 방지/억지
- 침입 예방 정보 수집
- 침입 탐지

슬라이드가 **"침입 예방도, 침입 방지도 아니다"** 라고 못 박아놨다. IDS는 모든 event/action에 끼어들어서 check-then-pass/deny를 하지 않는다. 그건 **방화벽**이나 **IPS(Intrusion Prevention System)** 가 하는 일이다.

### 방화벽 vs IDS
- 방화벽은 "의심 트래픽"만 막는 게 아니라 **정해둔 규칙(정책)** 에 따라 허용/차단을 판단한다. 의심스러운지는 따지지 않고, 규칙에 안 맞으면 막는다.
- 결정적 차이는 **트래픽 경로에 개입하느냐**이다. 방화벽은 길목에 서서 패킷을 통과시킬지 막을지 결정하니까 판단 전에는 패킷이 못 지나간다. IDS는 옆에서 지켜보다가(트래픽을 가로막지 않고) 징후가 보이면 경고만 한다. 그래서 IDS가 알아챌 때쯤엔 이미 트래픽이 지나갔을 수 있다.
- "비상벨"이라는 비유가 정확하다.
- IPS는 IDS처럼 탐지를 하면서 방화벽처럼 길목에서 차단까지 하는 장비이다.

## 5. IDS 종류와 구성요소 *(p.8)*

- **HIDS(Host-based)**: **단일 호스트**의 특성을 모니터링해서 의심스러운 활동을 찾는다.
- **NIDS(Network-based)**: **네트워크 트래픽**을 모니터링하고 network, transport, application 프로토콜을 분석해서 의심스러운 활동을 찾는다.
- **Distributed/hybrid IDS**: 여러 sensor(호스트 기반, 네트워크 기반 모두 가능)의 정보를 **중앙 analyzer**에서 결합해서, 침입 활동을 더 잘 식별하고 대응한다.

종류와 상관없이 **논리적으로 3개 구성요소**로 이루어진다.
- **Sensors**: 데이터를 수집
- **Analyzers**: 침입이 발생했는지 판단
- **User interface**: 출력을 보거나 시스템 동작을 제어

데이터 수집(sensor), 판단(analyzer), 사람과의 접점(UI)으로 역할이 나뉜다.

## 6. 행동 프로파일 (Figure 8.1) *(p.9)*

가로축은 측정 가능한 행동 파라미터, 세로축은 확률밀도이다. **침입자의 행동 분포**와 **인가된 사용자의 행동 분포**가 각각 종 모양으로 그려지는데, 평균은 서로 다르지만 **겹치는 구간**이 있다. 이 겹침이 핵심이다. 그 구간의 행동은 정상인지 침입인지 구분이 안 되기 때문에 오탐/미탐이 불가피하다.

## 7. 기본율 오류 *(p.10)*

- **False positive(오긍정)**: 정상 사용자를 침입자로 판정
- **False negative(오부정)**: 침입자를 정상 사용자로 판정

**기본율 오류(Base-rate Fallacy)**: 정상적인 사용의 수에 비해 실제 침입 수가 작을 때, 오긍정 때문에 경고 중 헛경고의 비율이 높아지는 현상. 잦은 오류가 나면 관리자가 IDS를 꺼버리게 된다.

### 계산 예제
하루 이벤트 10,000건, 진짜 침입 1건, 탐지율 99%, 오탐률 1%일 때 경고가 울렸을 때 진짜 침입일 확률은? 사람 수 세듯이 센다.
- 진짜 침입 1건 중 잡히는 건 1 × 0.99 = **0.99건**
- 정상 9,999건 중 오탐은 9,999 × 0.01 = **99.99건**
- 경고는 총 0.99 + 99.99 = 100.98건이고, 그중 진짜는 0.99건
- 0.99 / 100.98 ≈ **약 0.98%**

경고가 울려도 진짜 침입일 확률은 1%도 안 된다. 경고 100개 중 99개는 헛경고라는 뜻이다. 탐지율 99%로 성능은 훌륭한데도 이렇게 되는 이유는 **정상 이벤트 수가 압도적으로 많아서**이다. 오탐률이 1%밖에 안 돼도 정상 9,999건에 곱해지면 숫자가 커진다. 그래서 경고가 쌓이고, 관리자는 지쳐서 IDS를 꺼버린다.

### 개선 방향
분모를 키우는 건 거의 전부 오탐(99.99건)이고, 탐지율은 이미 0.99라서 더 올려봐야 0.99가 1.0이 되는 정도이다. 따라서 **오탐률을 낮추는 것**이 효과적이다. 오탐률을 0.1%로만 낮춰도 오탐이 약 10건으로 줄어서 경고의 신뢰도가 10%까지 올라간다.

다만 trade-off가 있다. Figure 8.1의 두 분포가 겹쳐 있으므로, 오탐을 줄이려고 판정 기준을 빡빡하게 올리면 진짜 침입도 정상으로 보내는 false negative가 늘어난다. 둘을 동시에 0으로 만드는 건 불가능하다.

## 8. IDS 요구사항 *(p.11)*

1. **지속적 실행**: 항상 돌아가고 있어야 한다.
2. **Fault-tolerant, attack-resistance**: 장애나 공격을 받아도 견뎌야 하고, 문제가 생겨도 **graceful degradation**(전체가 멈추지 않고 기능을 줄여가며 서서히 성능 저하)으로 동작해야 한다.
3. **낮은 오버헤드**: 감시 대상 시스템의 성능을 해치지 않아야 한다.
4. **보안 정책에 맞게 설정** 가능해야 한다.
5. **확장성(Scalable)**: 큰 시스템과 많은 사용자를 지원해야 한다.
6. **동적 재설정**: 중단 없이 설정을 바꿀 수 있어야 한다.

2번의 "attack-resistance"가 눈에 띈다. IDS 자체가 공격 대상이 될 수 있어서, 침입자가 제일 먼저 IDS를 끄거나 속이려 하기 때문이다.

## 9. 분석 방식 *(p.12~15)*

**Anomaly detection**: 일정 기간 합법 사용자의 행동 데이터를 모아두고, 현재 행동이 정상 범위를 벗어나는지 분석해서 침입을 찾는 방식.

**Signature/Heuristic detection**: 알려진 악성 패턴이나 공격 규칙을 미리 갖고 있다가 현재 행동과 비교해서 일치하면 침입으로 판단하는 방식. **misuse detection**이라고도 한다. 알려진 공격만 잡을 수 있다는 게 한계이다.

### 약점 비교
- **Anomaly의 약점**
  - 침입 행동이 정상 사용자 행동을 **흉내 내면** 못 잡는다 (**false negative**).
  - 정상 행동의 범위를 "과거에 관찰된 행동"으로 정하니까, **정상인데 평소와 다른 행동**(출장 가서 접속, 새 업무로 처음 쓰는 명령)이 침입으로 판정된다 (**false positive**가 많아짐). 기본율 오류가 이 경우에 터지기 쉽다.
  - 학습 기간에 이미 침입자가 활동하고 있었다면 그 행동이 "정상"으로 학습돼버린다.
- **Signature의 약점**: 오탐은 적지만, **처음 보는 공격(zero-day)** 은 못 잡는다.

| | 강점 | 약점 |
|---|---|---|
| Anomaly | 새로운 공격도 "평소와 다름"으로 잡을 수 있음 | 오탐이 많음 |
| Signature | 오탐이 적고 정확함 | 알려진 공격만 잡음 |

신종 웜이 퍼지는 상황에서는 anomaly가 먼저 반응한다. signature DB에 아직 없어서 패턴 매칭이 안 되지만, anomaly는 패턴을 몰라도 **행동이 평소와 다른 것**(갑자기 폭증하는 트래픽, 낯선 곳으로 퍼지는 스캔)을 보고 반응할 수 있기 때문이다. p.24에서도 worm, scanning, DoS를 anomaly에 적합한 공격으로 분류한다.

### Anomaly detection의 분류 접근법 *(p.13)*
- **Statistical**: 관찰한 지표(metrics)를 univariate, multivariate, time-series 모델로 통계 분석
- **Knowledge based**: **expert system**이 합법 행동을 모델링한 규칙 집합에 따라 관찰 행동을 분류
- **Machine-learning**: **data mining** 기법으로 학습 데이터에서 분류 모델을 **자동으로** 결정

규칙을 사람이 쓰면 knowledge based, 기계가 스스로 찾으면 machine-learning, 수치 분포로 판단하면 statistical이다.

### Signature/Heuristic detection *(p.14)*
- **Signature approaches**: 알려진 악성 패턴 대규모 모음을, 시스템에 저장된 데이터나 네트워크로 전송 중인 데이터와 매칭한다. signature는 false alarm rate를 최소화할 만큼 충분히 크면서 악성 데이터의 상당 부분을 탐지해야 한다. anti-virus 제품, network traffic scanning proxy, NIDS에서 널리 쓴다.
- **Rule-based heuristic identification**: 알려진 침투나 알려진 취약점을 악용하는 침투를 식별하는 규칙을 쓴다. 평소 사용 패턴의 범위 안에 있어도 **의심스러운 행동**을 식별하는 규칙을 정의할 수도 있다. 규칙은 보통 특정 상황에 특화돼 있고, **SNORT**가 rule-based NIDS의 대표 예이다.

### Signature의 예 *(p.15)*
- **HIDS**: root 로그인 시도 로그, 패스워드 파일 복제 시도 로그, 시스템 파일 변경 시도 로그
- **NIDS**: 인터넷 웜 XYZ의 악성코드 청크 패턴, APT 공격의 커맨드

HIDS는 호스트 안의 **행위 기록**을, NIDS는 네트워크를 지나는 **데이터 내용**을 signature로 삼는다.

## 10. Host-Based IDS *(p.16~20)*

**HIDS**: 취약하거나 민감한 시스템에 특화된 보안 소프트웨어 계층을 추가해서, 그 호스트 안의 활동을 모니터링하며 침입을 탐지하는 IDS.
- anomaly 방식과 signature·heuristic 방식 **둘 다** 쓸 수 있다.
- 주 목적은 침입 탐지, 의심 이벤트 로깅, 경고 전송이다.
- **외부 침입과 내부 침입을 모두** 탐지할 수 있다. 호스트 안에서 일어나는 일을 직접 보니까 내부자의 행위도 볼 수 있다는 게 장점이다.

### Data Sources and Sensors *(p.17)*
- **Log 파일**: 로그파일 분석기
- **System calls**: 시스템 콜 분석기
- **Registry access**: 레지스트리 분석기
- **System files integrity**: 시스템 파일 체크기(파일이 변조됐는지 확인)

### Table 8.2 *(p.18)*
HIDS가 모니터링하는 대상으로 Ubuntu Linux system call 목록과 Windows 핵심 DLL(kernel32, ntdll, ntoskrnl, user32, ws2_32 등)이 나열돼 있다. 전부 외울 필요는 없고, "시스템 콜과 핵심 DLL을 감시한다"는 사실만 알면 된다. 전체 목록은 정리 노트(`notes/기말고사/chapter-8.md`)에 있다.

### Distributed IDS 구조 (Figure 8.2) *(p.19)*
- **LAN Monitor**와 각 **Host**에 **Agent module**이 있다.
- 이 agent들이 수집한 정보를 **Central Manager**의 **Manager module**로 모아서 분석한다.
- 호스트 하나만 봐서는 안 보이는 공격(여러 호스트에 걸친 침입)을 중앙에서 연관 분석할 수 있다.

### Agent Architecture (Figure 8.3) *(p.20)*
OS audit information → **Filter for security interest** → **Reformat function** → **Host audit record(HAR)** → **Analysis module** → **Alerts** → **Central manager**

슬라이드에는 각 단계 설명이 없어서 교재 내용으로 보충한 것이다.
- **OS audit function**: OS가 자체적으로 남기는 감사 기록(audit information)을 만드는 단계. 로그인, 파일 접근, 프로세스 실행 같은 이벤트가 OS별 고유한 형식으로 쌓인다.
- **Filter for security interest**: audit 기록은 양이 엄청나니까, 보안과 관련 있는 이벤트만 남기고 나머지는 버린다. 분석 부담을 줄이려는 것이다.
- **Reformat function**: 거른 기록을 **표준화된 형식으로 변환**한다. OS마다 다른 형식을 하나로 맞추는 단계이다.
- **HAR(Host Audit Record)**: reformat의 **결과물**인 표준 레코드. 단계가 아니라 데이터 형식이다.
- **Analysis module**: HAR를 받아서 침입 여부를 판단한다. 이때 Logic module을 참조한다.
- **Logic module**: 판단 기준을 가진 곳. notable activity(보고할 만한 활동), signatures, noteworthy sessions(의심스러운 세션), templates를 갖고 있고, 분석 결과에 따라 이 기준이 **수정(Modifications)** 되기도 한다.
- **Alerts**: Analysis module이 의심 활동을 발견했을 때 Central manager로 보내는 경고. Central manager가 필요하면 agent에 Query/response로 추가 정보를 묻는다.

OS 차이를 흡수하는 단계는 **Reformat function**이고, HAR는 그 산출물이다.

## 11. Network-Based IDS *(p.21~25)*

**NIDS**: 네트워크의 선택된 지점에서 지나가는 트래픽을 패킷 단위로 실시간(또는 거의 실시간) 검사해서 침입을 탐지하는 IDS.

### 개요 *(p.21)*
- network, transport, application 계층의 프로토콜 활동을 검사할 수 있다.
- 구성: 여러 **sensor**, NIDS 관리 기능용 **server** 1개 이상, 사람이 쓰는 **management console** 1개 이상
- 트래픽 패턴 분석은 sensor에서 할 수도, management server에서 할 수도, 둘을 섞을 수도 있다.

### HIDS와 NIDS의 구조적 차이
- **HIDS**: 감시할 **호스트 안에** 설치된 소프트웨어(agent). 그 호스트의 로그, 시스템 콜, 파일을 직접 본다.
- **NIDS**: 호스트 안에 깔지 않고, **네트워크의 특정 지점에 따로 두는 sensor**. 그 지점을 지나가는 패킷을 엿본다. 감시 대상 호스트들은 NIDS가 있는지도 모른다.
- 슬라이드는 sensor가 하드웨어 장비인지 일반 서버에 소프트웨어를 깐 건지까지는 말하지 않는다. 보통은 전용 장비나 전용 서버에 sensor 소프트웨어를 올려서 쓰는데, 중요한 건 감시 대상 호스트와 **분리돼 있다**는 점이다. sensor가 트래픽을 받는 방법(스위치의 미러링 포트 등)도 슬라이드에는 없는 내용이다.

### Passive NIDS Sensor (Figure 8.4) *(p.22)*
- **Monitoring interface**: 네트워크 트래픽을 받아들이는 쪽. **IP가 없고 promiscuous mode**로 동작한다.
- **Management interface**: 관리용이고 **IP가 있다**.

monitoring interface에 IP가 없는 이유는 네트워크에서 **보이지 않게** 하려는 것이다. IP가 없으면 공격자가 그 sensor를 직접 공격하거나 존재를 알아내기 어렵다. 앞의 "attack-resistance" 요구사항과 연결된다. 이 sensor는 통신 당사자가 아니라 **지나가는 트래픽을 옆에서 구경하는 관찰자**라서 IP가 필요 없다. 자기한테 온 게 아닌 패킷도 전부 받아야 하니까 promiscuous mode가 쓰인다.

### NIDS Sensor 배치 예 (Figure 8.5) *(p.23)*
네트워크 구성은 Internet → **external firewall** → LAN switch/router → **internal firewall** → 내부망이다. external firewall 안쪽에는 **service network**(Web, Mail, DNS 등)가 붙어 있다.

| 번호 | 위치 | 보이는 것 |
|---|---|---|
| 1 | external firewall 안쪽, service network 쪽 | 방화벽을 **통과한** 공격과 service network로 가는 트래픽 |
| 2 | external firewall **바깥**(Internet 쪽) | 방화벽이 막기 전의 **모든 외부 트래픽** |
| 3 | internal server and data resource networks 앞 | 내부 서버 네트워크로 가는 트래픽 |
| 4 | workstation networks 앞 | 직원 PC 쪽 트래픽 |

**2번 (방화벽 바깥)**: 분석할 트래픽이 많고, 방화벽이 어차피 막을 트래픽까지 전부 경고로 올라온다. 방화벽이 처리할 공격까지 IDS가 전부 경고하면 **경고가 쏟아져서 노이즈가 커지고**, 진짜 중요한 경고가 묻힌다(기본율 오류와 같은 문제). 다만 방화벽에 막히는 공격 시도까지 보이니까 **어떤 공격이 얼마나 오는지 전체 현황**을 파악할 수 있다는 장점이 있다.

**1번 (방화벽 안쪽)**: 여기서 보이는 트래픽은 **방화벽이 이미 통과시킨 것**이라서, 거기서 공격이 탐지되면 "방화벽 규칙이 이 공격을 못 막았다"는 증거가 된다. 즉 방화벽 정책의 **구멍을 발견**하는 용도로 쓸 수 있고, 트래픽이 줄어서 분석 부담도 적다. IDS는 막지 않고 경고만 한다는 점에 주의한다.

**3, 4번**: 내부 네트워크 쪽이라 internal firewall을 통과한 트래픽을 본다. 내부 서버나 직원 PC로 향하는 트래픽을 따로 보니까 내부 구간의 이상도 잡을 수 있다.

### Intrusion Detection Techniques *(p.24)*

| Signature detection에 적합 | Anomaly detection에 적합 |
|---|---|
| Application layer attacks | **DoS** attacks |
| Transport layer attacks | **Scanning** |
| Network layer attacks | **Worms** |
| Unexpected application services | |
| Policy violations | |

계층별로 **패턴이 뚜렷한 공격**은 signature가 잘 잡고, **양이나 빈도, 행동의 이상**으로 드러나는 공격(DoS, scanning, worm)은 anomaly가 잘 잡는다.

### Logging of Alerts *(p.25)*
NIDS sensor가 경고와 함께 보통 기록하는 정보: Timestamp, Connection or session ID, Event or alert type, Rating, Network/transport/application layer protocols, Source/destination IP addresses, Source/destination TCP or UDP ports(또는 ICMP types and codes), 연결에서 전송된 bytes 수, Decoded payload data(application request/response 등), State-related information. 사고 분석할 때 필요한 정보를 다 남긴다고 보면 된다.

## 12. Honeypot *(p.26~28)*

**Honeypot**: 공격자를 유인하려고 일부러 만들어둔 미끼 시스템.

### 개요 *(p.26)*
- 목적: 공격자를 **중요 시스템에서 멀리 유인**, 공격자의 **활동 정보를 수집**, 관리자가 대응할 수 있을 만큼 공격자가 **오래 머물게** 유도
- 정상 사용자가 접근할 일이 없는 **조작된 정보**로 채워져 있다.
- **production value가 없는 자원**이다.

### production value가 없다는 것
production은 "실제 업무에 쓰인다"는 뜻이다. 웹서버는 고객이 접속하고, 메일 서버는 직원이 쓰고, 직원 PC는 직원이 쓴다. honeypot은 **아무 업무에도 안 쓰는 가짜 시스템**이라 직원도 고객도 접속할 이유가 없다. 그래서 이 시스템으로 들어오는 통신(inbound)은 정상일 수가 없고, **probe, scan, 공격 중 하나**일 가능성이 매우 높다. 일반 서버는 "정상 접속인지 공격인지" 판단하기 어려운데, honeypot은 **들어오는 건 전부 의심**하면 된다. 그래서 오탐이 거의 없고, 기본율 오류 문제를 구조적으로 피하는 방식이다.

### 먼저 밖으로 시작한 통신은 침해당한 것
honeypot은 사용자가 쓰지도 않고 업무 프로그램도 안 돌리므로 **스스로 밖으로 통신을 시작할 이유가 없다**. 정상이라면 바깥에서 들어온 요청에 응답하는 것까지만 하는 시스템이다. 먼저 외부로 연결을 시작했다면 누군가 이 시스템을 **장악해서 조종하고 있다**는 뜻이다. 예를 들어 공격자가 침투한 뒤 이 서버에서 다른 서버를 공격하거나, 악성코드를 내려받거나, 자기 서버(C2)에 접속하는 경우이다.
- **inbound**: 공격이 들어왔다는 신호(접속 시도)
- **먼저 시작한 outbound**: 이미 뚫렸다는 신호

### 분류 *(p.27)*

| | Low interaction | High interaction |
|---|---|---|
| 정의 | 특정 IT 서비스·시스템을 **에뮬레이션**하는 소프트웨어. 현실적인 초기 상호작용은 주지만 전체 서비스를 실제로 실행하지는 않음 | **실제 OS, 서비스, 애플리케이션**을 갖춘 진짜 시스템에 계측을 해서 공격자가 접근 가능한 곳에 배치 |
| 현실성 | 덜 현실적 | 더 현실적이라 공격자를 **오래 붙잡아 둘 수 있음** |
| 용도·특징 | 분산 IDS의 구성요소로 **임박한 공격을 경고**하는 용도로 충분한 경우가 많음 | 자원이 **훨씬 많이** 필요하고, **침해되면 다른 시스템 공격의 발판**이 될 수 있음 |

### 계측(instrument)은 모방이 아니다
모방(에뮬레이션)은 **low interaction** 쪽이다. 가짜 서비스를 흉내만 내는 소프트웨어이다. **high interaction**의 계측은 반대로, **진짜 시스템**(실제 OS, 서비스, 애플리케이션)을 그대로 쓰되 그 안에 **감시·기록 도구를 심어두는 것**이다. 공격자가 뭘 입력하는지, 어떤 파일을 건드리는지, 어디로 통신하는지를 전부 기록하게 만든다. 계기판을 단다고 생각하면 된다.

### 왜 high interaction이 발판이 되는가
"퀄리티가 좋아서"가 아니라 **진짜라서**이다.
- **low interaction**은 가짜 서비스를 흉내만 내는 프로그램이라, 공격자가 뚫어도 장악할 **진짜 OS가 없다**. 응답만 주는 껍데기라 그 안에서 할 수 있는 게 없다.
- **high interaction**은 진짜 OS와 서비스가 돌아간다. 공격자가 뚫으면 **실제 관리자 권한을 얻고 실제 프로그램을 실행**할 수 있다. 이 시스템도 네트워크에 연결돼 있으니, 그 서버를 **자기 공격 기지로 삼아** 다른 시스템을 공격할 수 있다(스캔, 악성코드 설치, 다른 서버 침투).
- 그래서 honeypot이 목적(공격 정보 수집)을 넘어서 **오히려 공격에 이용당할 수 있다**. 보통 high interaction은 외부로 나가는 통신을 강하게 통제하는 식으로 관리한다.

### Honeypot 배치 예 (Figure 8.8) *(p.28)*
1. **external firewall 바깥**(Internet 쪽)
2. **service network 안**
3. **internal network 안**

**3번(internal network 안)에 접속 시도가 들어오면 더 위험한 신호이다.**
- **외부 honeypot(1번)**: 인터넷에는 매일 스캔과 공격이 날아다니므로 접속 시도가 들어오는 건 **일상**이다.
- **내부 honeypot(3번)**: internal network는 방화벽 **안쪽**이라 원래 외부에서 직접 올 수 없다. 여기에 접속 시도가 들어왔다면 **이미 내부에 누군가 있다**는 뜻이다. 방화벽을 뚫고 들어온 공격자이거나, 이미 감염된 내부 PC이거나, 악의를 가진 내부자이다.
- 외부 honeypot은 "공격이 오고 있다"를, 내부 honeypot은 "**방어선이 이미 뚫렸을 수 있다**"를 알려준다. 후자가 훨씬 심각하다.
- 내부 honeypot 옆에는 진짜 내부 서버들이 있어서 "조금만 더 들어오면 진짜 시스템을 공격할 수 있다"는 것도 맞지만, 그건 결과이고 **원인은 이미 방화벽 안쪽에 침입자가 있다는 사실**이다.

## 13. Snort *(p.29~34)*

**Snort**: 오픈소스이고 설정 가능성이 높으며 이식성이 좋은 host-based 또는 network-based IDS. 규칙(rule)에 기반해서 다양한 공격을 탐지한다.

### 개요 *(p.29)*
- 실시간으로 **packet capture, protocol analysis, content searching & matching**을 수행한다.
- 앞에서 본 **signature/rule-based** 방식의 대표적인 예이다.
- 현재 버전은 3.0이다.

### Snort Architecture (Figure 8.9) *(p.30)*
**Packet → Decoder → Detection Engine → Log / Alert**
- **Decoder**: 캡처한 패킷의 헤더를 해석해서 구조를 파악한다.
- **Detection Engine**: 해석된 패킷을 규칙과 비교해서 일치하는지 판단한다.
- 일치하면 규칙에 정해진 대로 **Log**(기록)나 **Alert**(경고)로 보낸다.

### Snort Rule Format (Figure 8.10) *(p.31)*
- **(a) Rule Header**: `Action` `Protocol` `Source IP` `Source Port` `Direction` `Dest IP` `Dest Port` 순서로 7개 항목
- **(b) Options**: `Option Keyword`와 `Option Arguments`의 쌍을 여러 개 나열

헤더는 "어떤 패킷을 볼지(범위)"를 정하고, 옵션은 "그 안에서 무엇을 찾을지(내용)"를 정한다.

### Table 8.3: Rule Actions *(p.32)*

| Action | 동작 |
|---|---|
| **alert** | 경고를 만들고 패킷을 로그 |
| **log** | 패킷을 로그 |
| **pass** | 패킷을 무시 |
| **activate** | alert하고, 다른 dynamic rule을 켬 |
| **dynamic** | activate rule이 켤 때까지 대기하다가, 켜지면 log rule처럼 동작 |
| **drop** | iptables가 패킷을 drop하게 하고 로그 |
| **reject** | drop하고 로그한 뒤, TCP면 TCP reset, UDP면 ICMP port unreachable 전송 |
| **sdrop** | drop하되 로그는 남기지 않음 |

alert, log, pass는 "지켜보는" 동작이고, **drop, reject, sdrop은 패킷을 막는다**. Snort는 iptables와 연동하면 **IPS처럼도 동작**할 수 있다.

### Table 8.4: Rule Options *(p.33)*
분류 기준: **패킷 내용**(payload)을 보느냐, **헤더 같은 payload 이외 값**(non-payload)을 보느냐, **탐지 후 처리**(post-detection)냐, **설명용 정보**(meta-data)냐.

| 분류 | 옵션 | 설명 |
|---|---|---|
| **meta-data** | `msg` | 이벤트 발생 시 보낼 메시지 |
| | `reference` | 외부 공격 식별 시스템 링크 |
| | `classtype` | 시도된 공격 유형 |
| **payload** | `content` | payload에서 특정 내용을 **대소문자 구분**해 검색 |
| | `depth` | 패킷 안에서 얼마나 깊이까지 검색할지 (직전 content 수식) |
| | `offset` | 어디서부터 검색을 시작할지 (직전 content 수식) |
| | `nocase` | 대소문자 무시 (직전 content 수식) |
| **non-payload** | `ttl` | IP TTL 값 확인(traceroute 탐지) |
| | `id` | IP ID 필드 확인(일부 exploit이 31337 같은 값 사용) |
| | `dsize` | payload 크기 검사(비정상 크기, buffer overflow 탐지) |
| | `flags` | TCP flags 검사 |
| | `seq` | TCP sequence number 확인 |
| | `icmp-id` | ICMP ID 확인(covert channel, stacheldraht DDoS agent 탐지) |
| **post-detection** | `logto` | 매칭된 패킷을 지정 파일에 로그 |
| | `session` | TCP 세션에서 사용자 데이터 추출(telnet, ftp 등) |

외우기보다는 "이 공격을 잡으려면 어느 분류의 옵션이 필요하지?"를 추론하는 게 쓸모 있다.

### 규칙 예제 *(p.34)*

예제 1
```
alert tcp any 21 -> 10.199.12.8 any (msg: "TCP Packet is detected"; sid:1000010)
```
- Action = `alert`, Protocol = `tcp`, Source Address = `any`, Source Port = `21`, Direction = `->`, Dest Address = `10.199.12.8`, Dest Port = `any`
- Option = `msg`(경고 메시지), `sid`(규칙 번호)
- 해석: "모든 IP의 21번 포트에서 10.199.12.8의 모든 포트로 가는 TCP 패킷"이 탐지되면 경고를 낸다.

예제 2
```
alert tcp any any -> any 80 (msg: "Error Based SQL Injection Detected" ; content: "%27"; sid:100000011;)
```
- **헤더**: `alert`(경고+로그), `tcp`, 출발지 `any any`, 방향 `->`, 목적지 `any 80`. 즉 "어디서 오든 웹 서버(80번 포트)로 가는 TCP 패킷"이 대상이다.
- **옵션**: `content: "%27"`은 payload 안에 `%27`이 있는지 **대소문자 구분**해서 검색하고, `msg`는 일치 시 "Error Based SQL Injection Detected" 메시지를 내며, `sid`는 규칙 번호이다.
- **`%27`**: 작은따옴표 `'`를 **URL 인코딩**한 값(`'`의 ASCII 코드가 16진수로 27). SQL injection은 입력값에 `'`를 넣어서 쿼리 문자열을 깨뜨리는 게 시작점이다. 그러면 서버가 SQL 문법 에러를 내고, 공격자는 그 에러 메시지로 DB 구조를 알아낸다. 이게 "Error Based" SQL injection이다. URL로 전달될 때 `'`는 `%27`로 바뀌어 가니까 규칙이 `%27`을 찾는다.
- **한계**: 정상 요청에도 `%27`이 들어갈 수 있고(예: 이름에 `O'Brien`) 그러면 **오탐**이다. 공격자가 `%2527`처럼 이중 인코딩하거나 다른 방식으로 우회하면 **미탐**이다. signature 방식의 한계 그대로이다.

## 14. Summary *(p.35)*

슬라이드 Summary는 지금까지 다룬 내용의 목차 정리이다. 다만 "Intrusion detection exchange format"은 본문에 내용이 없어서 이번 수업 범위에서 다루지 않았다.

## 종료 점검 (Q&A)

- IDS: 시스템에서 침입 정황이 감지되면 경고하는 시스템
- 방화벽: 규칙에 맞지 않는 패킷들을 차단. 차이는 차단 vs 경고
- Anomaly: 이상행동을 기준으로 판단 / Signature: 알려진 악성행위를 기준으로 판단

## Self-study

- 선수 개념 확인 질문 5개 (방화벽이 뭘 하는 장비인가 / 패킷의 계층 구조, network·transport·application 계층이 뭔가 / promiscuous mode가 뭔가 / false positive와 false negative의 차이 / 시스템 콜이 뭔가)
- 호스트마다 OS가 다르면(Linux, Windows) audit 로그 형식도 달라진다. Agent architecture에서 이 차이를 흡수하는 단계는 어디인가?
- `alert tcp any any -> any 80 (msg: "Error Based SQL Injection Detected" ; content: "%27"; sid:100000011;)` 규칙은 어떤 패킷을 잡는가? 헤더와 옵션으로 나눠서 말하고, `%27`이 뭘 가리키는지 설명해보라.
