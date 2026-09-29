# Chapter 0: Course Intro

*Computer Networking: A Top-Down Approach, 8th ed. (Kurose & Ross)*

> 이 PDF는 대부분 강의계획서(강사 정보, 교재, 주차별 일정, 성적 평가, 수업 정책) 내용이라 개념적으로 정리할 내용은 아래 TCP/IP 프로토콜 스택 다이어그램뿐이다.

## 1. TCP/IP and OSI Model *(슬라이드 p.5)*

OSI의 7계층을 TCP/IP 스택에 대응시킨 다이어그램:

- **Application / Presentation / Session** → TCP/IP의 **Application** 계층: SMTP, FTP, HTTP, DNS, SNMP, TELNET 등
- **Transport** 계층: SCTP, **TCP**, **UDP**
- **Network(internet)** 계층: **IP**가 중심이며, 보조 프로토콜로 ICMP·IGMP(제어용), ARP·RARP(주소 변환용)가 포함
- **Data link / Physical** 계층: 하부 네트워크가 정의하는 프로토콜(host-to-network) — TCP/IP 스택 자체는 이 계층의 프로토콜을 규정하지 않음
