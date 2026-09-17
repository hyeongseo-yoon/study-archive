# Chapter 1: Introduction

*Hanyang University, Division of Computer Science and Engineering*

## 1. Introduction *(슬라이드 p.3~4)*

### 보안의 세 범주 *(슬라이드 p.3)*
- **Information security**: 전자 형태가 아니어도 모든 종류의 데이터를 보호 (예: 민감정보 보관용 캐비닛의 자물쇠)
- **Computer security**: 컴퓨터에 저장된 데이터 보호
- **Network security / Internet security**: 상호연결된 네트워크를 통해 전송되는 데이터 보호

### Computer security 정의 (NIST Computer Security Handbook) *(슬라이드 p.4)*
> The protection afforded to an automated information system in order to attain the applicable objectives of preserving the **integrity, availability, and confidentiality** of information system resources (including H/W, S/W, firmware, information/data, and telecommunications)

- **Confidentiality**: 비공개/기밀 정보가 비인가자에게 노출·공개되지 않도록 보장
- **Integrity**: 정보와 프로그램이 지정되고 인가된 방식으로만 변경되도록 보장
- **Availability**: 시스템이 신속하게 동작하고, 인가된 사용자에게 서비스 거부가 발생하지 않도록 보장

---

## 2. Key Security Concepts *(슬라이드 p.5)*

CIA는 하나의 삼각형으로 표현되며, 보호 대상인 **Data and services**를 중심으로 세 변(Confidentiality, Integrity, Availability)이 감싸는 구조.

### 보안 침해 시 3단계 영향 수준 (FIPS 199) *(슬라이드 p.6)*
| 수준 | 정의 |
|---|---|
| **Low** | 조직 운영/자산/개인에 제한적(limited) 악영향 |
| **Moderate** | 조직 운영/자산/개인에 심각한(serious) 악영향 |
| **High** | 조직 운영/자산/개인에 심각하거나 파국적인(severe or catastrophic) 악영향 |

### Computer security challenges *(슬라이드 p.7~8)*
- 초보자가 생각하는 것만큼 단순하지 않음
- 보안 기능에 대한 잠재적 공격을 고려해야 함
- 특정 서비스를 제공하는 절차가 종종 직관에 반함(counterintuitive)
- 물리적/논리적 배치를 결정해야 함
- 추가적인 알고리즘이나 프로토콜이 관련될 수 있음
- **공격자는 단 하나의 약점만 찾으면 되지만, 개발자는 모든 약점을 찾아야 함** (비대칭성)
- 사용자와 시스템 관리자는 장애가 발생하기 전까지 보안의 이점을 체감하지 못하는 경향
- 보안은 정기적이고 지속적인 모니터링을 요구함
- 흔히 설계가 끝난 뒤에 시스템에 끼워 넣는 후속 조치(afterthought)로 취급됨
- 효율적이고 사용자 친화적인 운영에 대한 걸림돌로 여겨짐

---

## 3. Security Trends *(슬라이드 p.9~11)*

- Internet-related vulnerabilities: 1995~2002년 급격히 증가 후 2002년 이후 소폭 감소/정체
- Security-related incidents: 1995~2003년 지속적으로 기하급수적 증가
- Attack sophistication vs. intruder knowledge: 시간이 지날수록 **공격 정교화(attack sophistication)는 상승**하지만 **공격에 필요한 침입자 지식(intruder knowledge)은 하락** — 공격 도구가 자동화·고도화되면서 지식이 부족한 공격자도 정교한 공격을 수행 가능해짐

---

## 4. Computer Security Terminology *(슬라이드 p.12)*

- **Adversary**: 공격자/위협 주체
- **Attack**: 공격 행위
- **Countermeasure**: 대응책
- **Risk**: 위험
- **Security Policy**: 보안 정책
- **System Resource (Asset)**: 보호 대상 자원
- **Threat**: 위협
- **Vulnerability**: 취약점

---

## 5. The OSI Security Architecture *(슬라이드 p.13)*

ITU-T Recommendation X.800, *Security Architecture for OSI* 에서 정의하는 세 요소:

- **Security attack**: 정보의 보안을 침해하는 모든 행위
- **Security service**: security mechanism을 활용해 security attack에 대응하는 서비스
- **Security mechanism**: security attack을 탐지(detect)·예방(prevent)·복구(recover)하도록 설계된 프로세스

---

## 6. Security Attacks *(슬라이드 p.14~24)*

Security Attacks는 크게 **Passive Attacks**와 **Active Attacks**로 나뉜다 *(슬라이드 p.14)*.

### Passive Attacks *(슬라이드 p.14~17)*
시스템에 영향을 주지 않고(without affecting system resources) 정보를 관찰(observe)하는 공격.

- **Release of message contents**: 통신 내용 자체를 도청해서 읽음 *(슬라이드 p.15)*
- **Traffic analysis**: 메시지 내용을 몰라도 메시지 송수신 패턴(트래픽 흐름)을 관찰·분석함 *(슬라이드 p.16)*
- 특징 *(슬라이드 p.17)*:
  - 데이터 변경이 없기 때문에 발생 후 **탐지(detect)가 어려움**
  - 따라서 탐지보다는 **예방(prevented)**을 목표로 해야 함

### Active Attacks *(슬라이드 p.18~24)*
시스템 자원을 변경하거나 그 동작에 영향을 주려는(alter/affect) 공격.

분류 *(슬라이드 p.18)*:
- **Creating illegitimate messages** (불법적인 메시지 생성)
  - **Masquerade (who)**: 한 개체가 다른 개체인 척 위장 *(슬라이드 p.19)*
  - **Replay (when)**: 메시지를 캡처해서 나중에 재전송 *(슬라이드 p.20)*
  - **Modification of messages (what)**: 메시지를 캡처, 변조 후 전송 *(슬라이드 p.21)*
- **Denying legitimate messages** (정당한 메시지 부인)
  - **Repudiation**: 메시지를 보내거나 받은 사실 자체를 부인 *(슬라이드 p.22)*
- **Making system facilities unavailable**
  - **Denial of service (DoS)**: 시스템 서비스를 이용 불가능하게 만듦 *(슬라이드 p.23)*

특징 *(슬라이드 p.24)*:
- 새로운 취약점과 다양한 공격 기법 때문에 **예방(prevent)이 어려움**
- 따라서 목표는 능동적 공격을 최대한 빨리 **탐지(detect)하고 복구(recover)**하는 것

> Passive attack은 "예방" 중심, Active attack은 "탐지+복구" 중심이라는 대비가 핵심.

---

## 7. Assets of the Computer System & Threats *(슬라이드 p.25~26)*

### Computer System의 자산 보호 흐름 (Figure 1.2) *(슬라이드 p.25)*
1. 컴퓨터 시설에 대한 접근은 통제되어야 함 (**user authentication**)
2. 데이터에 대한 접근은 통제되어야 함 (**protection**)
3. 데이터는 네트워크를 통해 안전하게 전송되어야 함 (**network security**)
4. 민감한 파일은 안전하게 보호되어야 함 (**file security**)

### Table 1.3 — Computer and Network Assets, with Examples of Threats *(슬라이드 p.26)*
자산 종류(Hardware / Software / Data / Communication Lines and Networks) × CIA 세 속성에 대한 위협 예시:

| 자산 | Availability | Confidentiality | Integrity |
|---|---|---|---|
| **Hardware** | 장비가 도난되거나 무력화되어 서비스가 거부됨 | 암호화되지 않은 CD-ROM/DVD가 도난됨 | - |
| **Software** | 프로그램이 삭제되어 사용자 접근이 거부됨 | 소프트웨어가 비인가 복제됨 | 동작 중인 프로그램이 변조되어 실행 중 실패하거나 의도치 않은 동작을 하게 됨 |
| **Data** | 파일이 삭제되어 사용자 접근이 거부됨 | 데이터가 비인가 읽기됨, 통계 데이터 분석으로 기반 데이터가 노출됨 | 기존 파일이 변조되거나 새 파일이 위조됨 |
| **Communication Lines and Networks** | 메시지가 파괴/삭제됨, 통신선/네트워크가 사용 불가능해짐 | 메시지가 읽힘, 메시지의 트래픽 패턴이 관찰됨 | 메시지가 변조·지연·재정렬·중복되거나 허위 메시지가 위조됨 |

---

## 8. Security Requirements (FIPS 200) *(슬라이드 p.27)*

FIPS 200이 정의하는 17개 보안 요구사항 영역:

Access Control, Awareness and Training, Audit and Accountability, Certification·Accreditation·Security Assessments, Configuration Management, Contingency Planning, Identification and Authentication, Incident Response, Maintenance, Media Protection, Physical and Environmental Protection, Planning, Personnel Security, Risk Assessment, System and Services Acquisition, System and Communications Plan, System and Information Integrity

---

## 9. Fundamental Security Design Principles *(슬라이드 p.28)*

Economy of mechanism, Fail-safe defaults, Complete mediation, Open design, Separation of privilege, Least privilege, Least common mechanism, Psychological acceptability, Isolation, Encapsulation, Modularity, Layering, Least astonishment

---

## 10. Computer Security Strategy *(슬라이드 p.29~33)*

Security policy → Security implementation → Assurance → Evaluation 의 4단계로 구성 *(슬라이드 p.29)*.

### Security policy *(슬라이드 p.30)*
보안 서비스를 어떻게 제공할지, 데이터를 어떻게 보호할지에 대한 **formal security rule**을 수립함.
- 예: 사원만 사내 데이터를 읽을 수 있다 (data confidentiality)
- 예: 모든 사내 데이터는 외부 유출이 금지된다 (data confidentiality)
- 예: 홍보용 web server에는 security level 1의 데이터밖에 있을 수 없다
- 예: level 3 이상의 데이터는 단일 공격에 대해 훼손되어도 복구 가능해야 한다

### Security implementation *(슬라이드 p.31)*
Security policy를 효율적·효과적으로 구현함:
- **Prevention**: 모든 사내 데이터를 암호화 → 유출을 1차적으로 막음
- **Detection**: 침입탐지시스템이 네트워크를 모니터링 → 데이터유출 및 사이버공격을 감지
- **Response**: 침입으로부터의 연결 차단, 서비스 중단 등
- **Recovery**: 백업데이터로부터 복구

### Assurance *(슬라이드 p.32)*
"보안 시스템 설계가 요구사항을 충족하는가?"에 대한 신뢰의 정도(degree of confidence)로 표현됨.
- 엄격한 수학적 증명(mathematical proof)은 현실적으로 어려워서, 보통 high/mid/low 같은 정도로 표현됨
- 이 신뢰는 통상 **evaluation**을 통해 근거를 얻음

### Evaluation *(슬라이드 p.33)*
특정 기준에 따라 컴퓨터 제품이나 시스템을 검토하는 과정.
- **Security hardening**: 예 — 모든 데이터의 저장 시·통신 시 암호화 제공 → 불특정 다수가 해독할 확률이 낮아짐 (confidentiality 제공)
- **Security testing & vulnerability management**: 예 — web server에 대한 침투테스트 수행 결과 level 2 데이터 유출 가능성 발견 → vulnerability 경로 조사 후 조치

---

## 11. A Model for Network Security *(슬라이드 p.34~35)*

Figure 1.5 — 통신을 상대(opponent)로부터 보호하는 모델.

- **Sender**가 메시지에 secret information을 이용한 **security-related transformation**을 적용해 secure message로 만들고, Information Channel을 통해 **Recipient**에게 전달
- Recipient는 secret information을 이용해 역으로 security-related transformation을 적용해 원래 message를 복원
- **Trusted third party** (예: arbiter, secret information의 배포자)가 Sender/Recipient 양쪽과 관여할 수 있음
- **Opponent**가 Information Channel에 개입할 수 있음

---

## 12. A Model for Computer Security *(슬라이드 p.36~38)*

Figure 1.6 — 시스템을 비인가 접근(unwanted access)으로부터 보호하는 모델 *(슬라이드 p.36)*.

- **Opponent**: human(예: hacker) 또는 software(예: virus, worm)
- Opponent는 **Access Channel**을 통해 Information System에 접근을 시도
- **Gatekeeper function**이 Access Channel과 Information System 사이에서 접근을 통제
- Information System 내부에는 computing resources(processor, memory, I/O), data, processes, software, 그리고 **internal security controls**가 있음

### 두 가지 위협 유형 *(슬라이드 p.37)*
- **Information access threat**: 시스템 내 데이터를 보거나 변경하려는 위협
- **Service threat**: 정당한 사용자가 시스템 서비스를 이용하지 못하게 막으려는 위협

### 비인가 접근에 대한 보안 메커니즘 분류 *(슬라이드 p.38)*
- **Gatekeeper function (prevention)**
  - 비인가 사용자의 접근을 거부하는 password 기반 로그인 절차
  - worm, virus를 탐지·거부하는 screening logic
- **Monitoring activity (detection)**
  - 비정상 활동을 모니터링해 비인가 침입자를 탐지

---

## 수업 진행 섹션

1. Introduction
2. Key Security Concepts
3. Security Trends
4. Computer Security Terminology
5. The OSI Security Architecture
6. Security Attacks
7. Assets of the Computer System & Threats
8. Security Requirements (FIPS 200)
9. Fundamental Security Design Principles
10. Computer Security Strategy
11. A Model for Network Security
12. A Model for Computer Security
