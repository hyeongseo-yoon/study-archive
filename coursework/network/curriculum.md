# 컴퓨터 네트워크 커리큘럼 (2026-2)

## 진행상황
- [ ] Level 1 — Chapter 1: Introduction (진행 중)
- [ ] Level 2 — Chapter 2: (추후 진행하며 추가)

## 소스 등급 (0단계)
**Tier 1** — Kurose & Ross, *Computer Networking: A Top-Down Approach* (8th ed.) 기반 정규 강의 슬라이드. 이미 검증된 교재/강의 순서를 그대로 따라가며, **챕터 = 커리큘럼 레벨**로 1:1 매핑한다. 따로 순서를 합성하지 않는다.

---

## Level 1 — Chapter 1: Introduction

- 수업 자료: `materials/Chapter_1_v8.2.pdf`, 정리 노트 [[02.Area/study-archive/coursework/network/notes/chapter-1]] .수업을 진행할 때 해당 위치에 있는 정리노트의 내용들을 상세하게 설명해야한다.(노트 내용을 그대로 가져오지 말고 이해가기 쉽게 수업을 진행한다). 수업하면서 수업 내용에 해당하는 슬라이드를 알려준다.
- 선수지식: 없음 (챕터 1은 사전 네트워크 지식을 가정하지 않는 개론)

**개념:**
- **Internet 개관**: nuts-and-bolts view(host/packet switch/link/network) vs services view(infrastructure로서의 인터넷), protocol의 정의(format/order/action)
- **Network edge**: host(client/server), access network 종류별 특징(cable-HFC, DSL, WiFi/4G-5G, enterprise, datacenter), physical media(twisted pair/coax/fiber/radio)
- **Network core**: packet switching(store-and-forward, forwarding vs routing, queueing/loss) vs circuit switching(FDM/TDM, 전용자원), Internet 구조가 단계적으로 진화한 이유(access ISP → IXP/peering → regional ISP → tier-1/content provider)
- **Performance**: packet delay 4요소(d_proc/d_queue/d_trans/d_prop) 계산, traffic intensity(La/R)와 큐잉 지연의 관계, packet loss 발생 조건, throughput과 bottleneck link
- **Security 개요**: packet sniffing, IP spoofing, DoS의 동작 방식, 방어선(authentication/confidentiality/integrity check/firewall)
- **Protocol layering**: 5-layer Internet stack(app/transport/network/link/physical) vs OSI 7-layer(+presentation/session), TCP/IP 계층별 실제 프로토콜 매핑(HTTP/TCP/IP/Ethernet 등), encapsulation 구조(message→segment→datagram→frame)
- **Internet 역사**: 1961~현재 주요 타임라인(ARPAnet → TCP/IP 표준화 → Web 상용화 → SDN/모바일/클라우드)

**실습:** 순수 개념·배경지식 위주 챕터라 실습 비중이 낮음 — 수업 진행하면서 생략 여부 확정 (계산 문제(delay, throughput)만 필요시 별도 진행)

**검증:** 위 7개 개념을 자기 말로 설명 가능한지 + 핵심 확인 질문 통과
- packet switching과 circuit switching의 차이를 자원 할당 관점에서 설명할 수 있는가?
- packet delay 4요소 각각이 무엇에 의해 결정되는지 구분할 수 있는가?
- 5-layer 모델에서 각 계층의 역할과 캡슐화가 어떻게 이뤄지는지 설명할 수 있는가?
- ISP 계층 구조(access → regional → tier-1)와 IXP/peering의 역할을 설명할 수 있는가?

---

## Level 2 이후
챕터 2(Application Layer)부터는 진행하면서 이 문서에 레벨을 추가한다.
