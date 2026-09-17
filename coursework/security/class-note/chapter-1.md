# Chapter 1 수업노트

*(수업일: 2026-09-17, 참조 노트: `notes/chapter-1.md`)*

## 1. Introduction

### 보안의 세 범주

보안이라고 뭉뚱그려 말하지만 사실 범위에 따라 세 가지로 나뉘어:

- **Information security**: 전자 형태가 아니어도 모든 종류의 데이터를 보호 (예: 민감정보 보관용 캐비닛의 자물쇠)
- **Computer security**: 컴퓨터에 저장된 데이터 보호
- **Network security / Internet security**: 상호연결된 네트워크를 통해 전송되는 데이터 보호

즉 셋은 서로 배타적인 범주가 아니라 **Information security ⊃ Computer security**, 그리고 Network security는 Computer security의 하위 영역 중 "전송 중" 상황에 특화된 부분이라고 보면 돼.

### Computer security 정의 — 왜 이렇게 정의하나

NIST가 내리는 정의:

> 정보시스템 자원(H/W, S/W, 데이터, 통신 등)의 **integrity, availability, confidentiality**를 지키기 위해 자동화된 정보시스템에 제공되는 보호

여기서 핵심은 "보호"의 목표가 뭔지를 세 가지로 쪼갠 거야. 이게 바로 **CIA triad**:

- **Confidentiality (기밀성)**: 비인가자에게 정보가 노출되면 안 됨. "누가 봐도 되는가"의 문제.
- **Integrity (무결성)**: 정보/프로그램이 인가된 방식으로만 변경돼야 함. "누가 바꿔도 되는가"의 문제.
- **Availability (가용성)**: 인가된 사용자가 필요할 때 서비스를 못 받는 일이 없어야 함. "제때 쓸 수 있는가"의 문제.

**포인트**: 이 셋은 서로 트레이드오프 관계일 때가 많아. 예를 들어 보안을 너무 강하게 걸면(암호화, 다단계 인증 등) confidentiality/integrity는 올라가지만 availability(접근 편의성)는 떨어지는 경우가 흔해. 그래서 "보안 = 무조건 세게" 가 아니라 이 세 축의 **균형**을 맞추는 문제로 봐야 해.

맞아, 정확해. 서비스 자체를 못 쓰게 만드는 거니까 **Availability** 침해지.

---

## 2. Key Security Concepts

### CIA 삼각형

CIA를 그림으로 표현할 때는 삼각형을 써. 가운데에 보호 대상인 **Data and services**가 있고, 그걸 세 변(Confidentiality, Integrity, Availability)이 감싸는 구조야. "이 세 속성이 있어야 데이터/서비스가 안전하다"는 걸 시각화한 거지.

### 보안 침해 시 3단계 영향 수준 — FIPS 199

보안 침해가 발생했을 때, 그 피해가 얼마나 심각한지를 3단계로 나눠:

| 수준 | 정의 |
|---|---|
| **Low** | 조직 운영/자산/개인에 **제한적(limited)** 악영향 |
| **Moderate** | **심각한(serious)** 악영향 |
| **High** | **심각하거나 파국적인(severe or catastrophic)** 악영향 |

**왜 이런 등급이 필요하냐면**: 모든 보안 침해를 똑같이 취급하면 자원(예산, 인력)을 효율적으로 못 써. 사소한 정보 유출이랑 전체 시스템 마비를 같은 강도로 대응할 필요는 없으니까, 위협의 심각도에 따라 대응 수준을 다르게 가져가기 위한 기준이야.

### Computer security가 왜 어려운가 (Challenges)

여기서 제일 핵심적인 포인트 하나: **공격자는 단 하나의 약점만 찾으면 되지만, 방어자(개발자)는 모든 약점을 찾아야 한다**는 비대칭성이야. 이게 보안이 구조적으로 어려운 근본 이유고, 나머지 특징들(직관에 반하는 절차, 평소엔 체감 안 되는 보안 효과, 설계 끝난 뒤 나중에 끼워 넣는 후속조치 취급 등)은 다 이 비대칭성에서 파생되는 현실적인 문제들이라고 보면 돼.

맞아, 발생 빈도가 아니라 **악영향의 심각도**가 기준이야.

그리고 "주관적이다"라는 지적은 맞는 말이야. FIPS 199 자체가 "limited / serious / severe" 같은 정성적 표현을 쓰고, 정량적인 임계값을 딱 정해주지 않거든. 실제로는 조직이 자체적으로 영향 평가 기준(예: 피해 금액, 영향받는 사용자 수, 법적 책임 등)을 세워서 이 등급에 매핑하는 방식으로 운영돼. 이 "주관성/신뢰도"에 관한 문제는 뒤에 10번 섹션 **Assurance**에서 다시 나와 — 엄밀한 수학적 증명 대신 high/mid/low 같은 신뢰도 등급으로 표현할 수밖에 없다는 얘기랑 같은 맥락이야. 지금은 그런 구조가 있다는 것만 기억해두면 돼.

---

## 3. Security Trends

이 섹션은 개념이라기보다 "역사적 추세"를 보여주는 데이터 얘기야.

- 1995~2002년: **인터넷 관련 취약점(vulnerabilities)**이 급격히 증가했다가, 2002년 이후로는 소폭 감소하거나 정체.
- 1995~2003년: **보안 관련 사고(incidents)** 자체는 계속 기하급수적으로 증가.
- 시간에 따른 두 그래프의 대비가 핵심 포인트: **공격 정교화(attack sophistication)는 계속 올라가는데, 공격에 필요한 침입자 지식(intruder knowledge)은 오히려 내려간다**.

**왜 이런 현상이 생기냐**: 공격 도구가 점점 자동화·패키지화되면서, 예전엔 전문 지식이 있어야 가능했던 정교한 공격을 이제는 도구만 다운받아서 지식이 부족한 사람도 실행할 수 있게 됐기 때문이야. (이른바 "script kiddie" 현상의 배경이 되는 트렌드지.)

오케이, 정확해. 자동화된 공격 도구 덕분에 진입장벽이 낮아지고 있다는 거지.

---

## 4. Computer Security Terminology

이 섹션은 앞으로 계속 쓸 용어들을 정리하는 거야.

- **Vulnerability (취약점)**: 시스템 자체에 존재하는 약점. 공격당하기 전부터 이미 거기 있는 "구멍".
- **Threat (위협)**: 그 취약점을 이용해서 피해를 입힐 **가능성/잠재력**. 아직 실제로 벌어진 건 아님.
- **Attack (공격)**: 그 위협이 **실제로 실행**된 것. 취약점을 노려서 벌어진 구체적인 행위.

비유하면: 창문 자물쇠가 고장 난 게 **vulnerability**, "저 집은 자물쇠가 고장 나서 누가 침입할 수도 있겠다"는 게 **threat**, 실제로 누가 그 창문으로 침입한 게 **attack**이야.

나머지 용어들은 이 셋과 엮여서 쓰이는 관련 개념들이야:

- **Adversary**: 공격을 실행하는 주체 (공격자)
- **Countermeasure**: 취약점/위협/공격에 대응하기 위한 조치
- **Risk**: 특정 위협이 실제로 발생해서 피해를 줄 가능성과 그 피해 크기를 종합한 개념
- **Security Policy**: 보안을 어떻게 운영할지에 대한 규칙 (뒤 10번 섹션에서 자세히 다룸)
- **System Resource (Asset)**: 보호해야 할 대상 자체 (하드웨어, 소프트웨어, 데이터 등)

정확해. 취약점(vulnerability)은 확정적으로 존재하고, 그걸 누군가 악용할 가능성(threat)도 동시에 존재하는 상태야. 여기서 실제로 누가 그 CVE를 찔러서 침투를 시도하면 그때 비로소 attack이 되는 거고.

---

## 5. The OSI Security Architecture

앞으로 보안 메커니즘/서비스를 설명할 때 쓸 **공용 프레임워크**를 하나 소개하는 섹션이야. ITU-T의 X.800 표준에서 정의한 건데, 보안을 세 가지 요소로 나눠서 봐:

- **Security attack**: 정보의 보안을 침해하는 모든 행위 — 앞에서 배운 "attack"과 같은 개념.
- **Security service**: **security mechanism을 활용해서** security attack에 대응하는 서비스.
- **Security mechanism**: security attack을 **탐지(detect)·예방(prevent)·복구(recover)**하도록 설계된 구체적인 프로세스.

**핵심은 이 셋의 관계**: mechanism은 실제로 동작하는 "도구/기법"이고, service는 그 mechanism을 활용해서 제공되는 "기능/목적"이야. 즉 mechanism이 더 하위 레벨, service가 더 상위(목적) 레벨 개념이라고 보면 돼.

정확해, 그리고 "mechanism = 구현 방법, service = 구현 목표"라는 일반화도 정확하게 잡았어. 앞으로 나올 구체적인 보안 기법들을 볼 때 이 프레임으로 분류하면 헷갈릴 일이 없을 거야.

---

## 6. Security Attacks

Security attack은 크게 두 가지로 나뉘어: **Passive Attacks**와 **Active Attacks**. 이 둘을 나누는 기준은 "시스템 자원에 영향을 주느냐 안 주느냐"야.

### Passive Attacks

시스템 자원에 **영향을 주지 않고**, 그냥 정보를 몰래 관찰(observe)하는 공격.

- **Release of message contents**: 통신 내용 자체를 도청해서 읽는 것.
- **Traffic analysis**: 메시지 내용은 몰라도, 누가 누구한테 얼마나 자주/많이 통신하는지 같은 **패턴**을 분석하는 것. (내용을 암호화해도 이건 막기 어려움)

**특징**: 데이터를 변경하지 않으니까 발생한 뒤에 **탐지(detect)가 거의 불가능**해. 그래서 대응 전략도 "탐지해서 잡자"가 아니라 애초에 **예방(prevention)** 중심이야.

### Active Attacks

시스템 자원을 **변경하거나 동작에 영향을 주는** 공격. 세 부류로 나뉘어:

1. **불법적인 메시지 생성** (Creating illegitimate messages)
   - **Masquerade** — "누가(who)" 위장했는가: 다른 개체인 척 행세
   - **Replay** — "언제(when)" 문제: 정상 메시지를 캡처해서 나중에 재전송
   - **Modification of messages** — "무엇을(what)" 변조했는가: 메시지를 가로채서 내용을 바꿔 전송
2. **정당한 메시지 부인** (Denying legitimate messages)
   - **Repudiation**: 메시지를 보내거나 받은 사실 자체를 부인
3. **시스템 기능 마비** (Making system facilities unavailable)
   - **Denial of service (DoS)**: 서비스를 못 쓰게 만듦

**특징**: 새로운 취약점/기법이 계속 나오기 때문에 **예방이 어려워**. 그래서 목표가 Passive와 정반대로, 최대한 빨리 **탐지(detect)하고 복구(recover)**하는 쪽으로 바뀌어.

> 결국 이 섹션의 핵심 대비: **Passive = 예방 중심 / Active = 탐지+복구 중심**. 이게 왜 그런지는 위에서 설명한 "탐지 가능 여부" 차이에서 나오는 자연스러운 결론이야.

둘 다 정확해.

1. DDoS는 시스템 자원(가용성)에 실제 영향을 주니까 **active**.
2. 캡처한 패킷을 **내용은 그대로** 나중에 재전송한 거니까 **replay**가 맞아. (참고로 그 과정에서 내용을 바꿔치기했다면 modification, 남의 신원으로 아예 새로 위장했다면 masquerade가 됐을 거야 — 셋의 구분 기준을 잘 잡았어)

---

## 7. Assets of the Computer System & Threats

이 섹션은 "보호해야 할 자산이 뭐가 있고, 각 자산이 CIA 세 속성에 대해 어떤 위협을 받는지"를 정리해.

### 자산 보호 흐름 (Figure 1.2)

컴퓨터 시스템의 자산을 지키려면 순서대로 이런 통제가 필요해:

1. 컴퓨터 시설 자체에 대한 접근 통제 → **user authentication**
2. 데이터에 대한 접근 통제 → **protection**
3. 네트워크를 통한 데이터 전송 보호 → **network security**
4. 민감한 파일 보호 → **file security**

### 자산 × CIA 위협 매트릭스 (Table 1.3)

자산을 네 종류(Hardware / Software / Data / Communication Lines and Networks)로 나누고, 각각이 Availability/Confidentiality/Integrity 측면에서 어떤 위협을 받는지 정리한 표야. 예시 몇 개만 감 잡고 가자:

| 자산 | Availability 위협 | Confidentiality 위협 | Integrity 위협 |
|---|---|---|---|
| Hardware | 장비 도난/파괴로 서비스 거부 | 암호화 안 된 저장매체 도난 | - |
| Software | 프로그램 삭제로 접근 거부 | 비인가 복제(불법 복제) | 실행 중 프로그램 변조 |
| Data | 파일 삭제로 접근 거부 | 비인가 읽기, 통계 분석으로 원본 노출 | 파일 변조/위조 |
| Communication Lines/Networks | 메시지 파괴, 통신선 불능 | 메시지 도청, 트래픽 패턴 관찰 | 메시지 변조·지연·재정렬·중복, 허위 메시지 위조 |

**포인트**: 이 표 자체를 암기하기보다, "자산 종류마다 CIA 세 축에서 각각 다른 방식의 위협이 존재한다"는 **틀(프레임)**을 이해하는 게 중요해. 표에 나온 예시들은 사실 앞에서 배운 개념들(도청=confidentiality 침해, DoS류=availability 침해, 변조=integrity 침해)의 구체적인 적용 사례일 뿐이야.

좋은 지적이야, 실제로 맞는 말이야. 하드웨어를 파괴/탈취하는 것과 달리, **하드웨어 자체를 조작된 것으로 바꿔치기**(supply chain attack, hardware trojan/implant 같은 것들)하는 건 명백히 integrity 위협이 맞아 — "인가되지 않은 방식으로 자산이 변경됐다"는 정의에 정확히 부합하거든.

표에 "-"로 비어있는 건 "그런 위협이 존재하지 않는다"는 뜻이라기보다, 이 교재가 대표 예시를 하나씩 들 때 하드웨어는 물리적 실체라서 소프트웨어/데이터처럼 "내용이 슬쩍 바뀌는" 형태의 공격이 상대적으로 덜 일반적이고 예시로 들기 애매해서 생략한 것에 가까워. 실제로는 네가 말한 하드웨어 변조/바꿔치기 공격이 엄연히 존재하는 위협 범주야. 좋은 반례 짚었어.

---

## 8. Security Requirements (FIPS 200)

FIPS 200이 정의하는 **17개 보안 요구사항 영역**이야:

Access Control, Awareness and Training, Audit and Accountability, Certification·Accreditation·Security Assessments, Configuration Management, Contingency Planning, Identification and Authentication, Incident Response, Maintenance, Media Protection, Physical and Environmental Protection, Planning, Personnel Security, Risk Assessment, System and Services Acquisition, System and Communications Plan, System and Information Integrity

이건 암기 대상이라기보다, **"보안이 기술적인 영역(access control, 암호화 등)에만 국한되지 않는다"**는 걸 보여주는 리스트야. 자세히 보면 Awareness and Training(교육), Personnel Security(인사 보안), Physical and Environmental Protection(물리 보안), Planning처럼 기술과 무관해 보이는 항목들도 섞여 있지. 즉 보안은 기술 + 조직 운영 + 사람까지 아우르는 종합적인 관리 영역이라는 게 이 섹션의 요지야.

맞아, 정확히 그 취지야. 조금 더 구체적으로 말하면 — 아무리 기술적으로 완벽한 시스템을 만들어도, 사용자가 피싱 메일에 속아서 비밀번호를 넘겨주거나(social engineering), 실수로 민감 파일을 잘못된 곳에 올리면 그 순간 기술적 방어는 다 무의미해지거든. 그래서 "사람"이 보안 체인에서 가장 약한 고리가 되는 경우가 많고, FIPS 200이 그걸 공식 요구사항으로 못 박아둔 거야.

---

## 9. Fundamental Security Design Principles

시스템을 **설계할 때부터** 지켜야 할 보안 원칙들이야:

Economy of mechanism, Fail-safe defaults, Complete mediation, Open design, Separation of privilege, Least privilege, Least common mechanism, Psychological acceptability, Isolation, Encapsulation, Modularity, Layering, Least astonishment

이것도 노트에는 이름만 나열돼 있는데, 몇 개는 뜻을 짚고 가는 게 좋을 것 같아 — 특히 자주 언급되는 것들:

- **Least privilege (최소 권한)**: 각 주체(사용자/프로세스)는 자기 임무 수행에 **필요한 최소한의 권한**만 가져야 함.
- **Fail-safe defaults**: 기본값은 "거부(deny)"로 설정하고, 명시적으로 허용된 경우에만 접근을 허용. (반대로 기본이 "허용"이면 뭘 막아야 할지 일일이 다 나열해야 하는데, 빠뜨리는 순간 구멍이 생김)
- **Complete mediation**: 모든 접근 시도를 **매번 빠짐없이** 검사. 한 번 인증됐다고 이후 검사를 생략하면 안 됨.
- **Separation of privilege**: 하나의 권한을 얻는 데 **여러 조건**이 동시에 충족되도록 요구 (예: 2단계 인증)
- **Least common mechanism**: 여러 사용자가 공유하는 메커니즘/자원을 최소화 — 공유가 많을수록 한쪽의 침해가 다른 쪽에도 영향을 줄 경로가 생김.
- **Layering (Defense in depth)**: 단일 방어선에 의존하지 않고 여러 겹의 방어 장치를 둠.
- **Psychological acceptability**: 보안 메커니즘이 사용자에게 과도한 불편을 주면 안 됨 (그렇지 않으면 사용자가 우회하려 함).

**포인트**: 이 원칙들 전체를 관통하는 철학은 **"방어자가 실수해도 시스템이 안전한 쪽으로 무너지게 만들자"**야. 완벽한 구현을 가정하지 않고, 어딘가는 반드시 실수가 나온다는 전제 하에 설계하는 게 핵심 사고방식이지.

음, "least privilege"라고 보긴 좀 억지야 — least privilege는 원래 **권한(할 수 있는 행위의 범위)**에 관한 원칙이지, 정보 노출량에 관한 원칙은 아니거든. 정직하게 말하면 이 예시는 지금 나열된 13개 원칙 중 **어느 하나에 깔끔하게 딱 들어맞지는 않아** — 질문을 만들 때 살짝 애매한 예시를 골랐어.

이 케이스의 진짜 요지는: **에러 메시지가 공격자에게 유용한 정보(이 아이디가 존재하는지 여부)를 흘려주면, 공격자가 계정 존재 여부를 하나씩 확인하는 "user enumeration" 공격을 훨씬 쉽게 할 수 있다**는 거야. 굳이 13개 원칙 중 하나에 억지로 연결하자면 **Economy of mechanism**(시스템이 노출하는 정보/기능을 최소화해서 공격 표면 자체를 줄인다)에 가장 가깝다고 볼 수 있지만, 사실 이건 "공격자에게 불필요한 정보를 주지 않는다"는 별도의 보안 관행에 더 가까워.

---

## 10. Computer Security Strategy

보안을 실제로 운영하는 전략은 4단계로 구성돼: **Security policy → Security implementation → Assurance → Evaluation**

### Security policy
"뭘, 어떻게 보호할지"에 대한 **formal한 규칙**을 세우는 단계. 예:
- 사원만 사내 데이터를 읽을 수 있다 (confidentiality)
- 홍보용 웹서버엔 security level 1 데이터만 있을 수 있다

### Security implementation
정책을 실제로 구현하는 단계. 네 가지 수단으로:
- **Prevention**: 데이터 암호화 → 애초에 유출을 막음
- **Detection**: 침입탐지시스템으로 이상 징후 모니터링
- **Response**: 침입 연결 차단, 서비스 중단
- **Recovery**: 백업으로 복구

### Assurance
"이 시스템이 요구사항을 제대로 충족하는가"에 대한 **신뢰의 정도**. 완벽한 수학적 증명은 현실적으로 어려워서 보통 high/mid/low 같은 정도로 표현하고, 이 신뢰는 **evaluation**을 통해 근거를 얻어.

### Evaluation
특정 기준에 따라 실제로 제품/시스템을 검토하는 과정. 예:
- **Security hardening**: 저장/통신 시 암호화 적용 → 해독 확률을 낮춤
- **Security testing**: 침투테스트로 실제 취약점을 찾아냄

**포인트**: 이 네 단계가 **한 방향 순환 구조**라는 걸 기억해. 정책을 세우고(policy) → 구현하고(implementation) → 그게 잘 됐는지 신뢰도를 판단하는데(assurance) → 그 신뢰도의 근거는 실제 검증(evaluation)에서 나와. 즉 evaluation 결과가 다시 assurance를 뒷받침하는 순환이야.

맞아, 실제로 검증해본 거니까 **Evaluation**. 이 결과는 다시 assurance(신뢰도 판단)의 근거가 되고, 발견된 취약점을 고치면 그게 다시 security implementation으로 피드백되는 식으로 순환하는 거지.

---

## 11. A Model for Network Security

이건 **통신을 보호하는 구조**를 일반화한 모델이야 (Figure 1.5). 구성 요소:

- **Sender**가 메시지에 secret information(예: 암호화 키)을 이용한 **security-related transformation**(예: 암호화)을 적용해서 secure message로 만듦
- 그걸 **Information Channel**을 통해 **Recipient**에게 전달
- Recipient는 자신이 가진 secret information으로 역변환(예: 복호화)을 적용해서 원래 메시지를 복원
- **Trusted third party**(예: 키를 배포하는 중재자)가 양쪽에 관여할 수 있음
- **Opponent**(공격자)가 이 Information Channel에 개입을 시도할 수 있음

**포인트**: 이 모델이 말하는 건 결국 "네트워크 보안을 설계하려면 네 가지를 결정해야 한다"는 거야 — ① 어떤 transformation(암호화 알고리즘 등)을 쓸지, ② secret information(키)을 어떻게 만들고, ③ 그걸 어떻게 배포/공유할지(Trusted third party 역할), ④ 통신 당사자들이 이 알고리즘/프로토콜을 어떻게 사용할지. 즉 이 모델은 앞으로 배울 암호학/프로토콜 내용 전체를 담는 **뼈대(틀)** 역할을 해.

답은 맞아: HTTPS에서 **TLS 암호화가 하는 일이 바로 transformation**이야. 평문 HTTP 메시지를 암호화해서 secure message로 바꾸는 역할. 이때 쓰이는 세션 키가 secret information이고, 그 키를 안전하게 협상하는 과정(인증서 검증 등)에 CA(Certificate Authority) 같은 게 trusted third party 역할을 해.

---

## 12. A Model for Computer Security

11번이 "네트워크로 전송 중인 데이터"를 지키는 모델이었다면, 이건 **시스템 자체를 비인가 접근으로부터 지키는 모델**이야 (Figure 1.6).

- **Opponent**: human(해커)이거나 software(바이러스, 웜)일 수 있음
- Opponent는 **Access Channel**을 통해 Information System에 접근을 시도
- **Gatekeeper function**이 Access Channel과 Information System 사이에서 접근을 통제
- Information System 내부엔 computing resources(processor, memory, I/O), data, processes, software, 그리고 **internal security controls**가 있음

### 두 가지 위협 유형
- **Information access threat**: 시스템 내 데이터를 보거나 바꾸려는 위협
- **Service threat**: 정당한 사용자가 서비스를 못 쓰게 막으려는 위협

### 방어 메커니즘 분류
- **Gatekeeper function (prevention)**: 비밀번호 기반 로그인, 바이러스/웜을 걸러내는 screening logic
- **Monitoring activity (detection)**: 비정상 활동을 모니터링해서 침입자를 탐지

**포인트**: 11번 모델과 비교해보면 구조가 거의 대칭이야 — **11번은 "채널을 지나는 데이터"**, **12번은 "시스템 자체로 들어오는 접근"**을 지키는 모델. 둘 다 "Opponent가 있고, 그 사이에 방어 계층(transformation vs. gatekeeper)이 있다"는 같은 패턴을 반복하는 거지. 그리고 두 가지 위협 유형(information access / service)은 사실 CIA의 confidentiality+integrity(정보 접근) / availability(서비스)를 그대로 재구성한 거야.

맞아, **Gatekeeper function**이야. "worm, virus를 탐지·거부하는 screening logic"을 정확히 gatekeeper(prevention) 사례로 들고 있어. 이유는 침입이 일어난 *후에* 잡아내는 게 아니라, 접근/실행 자체를 사전에 막아버리는 방식이라서 prevention 계열인 거지. (참고로 만약 이미 실행된 뒤에 "이상 행동 패턴"을 보고 사후 탐지하는 거였다면 monitoring activity 쪽에 더 가까웠을 거야.)

---

## 강의 마무리

1강 노트 12개 섹션 전부 다뤘는지 다시 확인해봤는데, 빠진 내용 없이 다 짚었어. 특히 이번 강의에서 반복해서 나온 핵심 축은:

- **CIA triad** (1, 2, 7번 섹션에서 반복 등장)
- **예방 vs 탐지+복구** 대비 (Passive/Active attack, Gatekeeper/Monitoring 양쪽에서 같은 패턴 반복)
- **threat/vulnerability/attack** 용어 구분 (4번 섹션, 이후 전체에서 계속 쓰임)

이 정도면 챕터 1을 관통하는 핵심 개념 다 짚은 걸로 보여.
