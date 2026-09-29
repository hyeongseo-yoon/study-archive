# Chapter 0: Class Intro

*2026 Fall, Hunjun Lee*

> 이 자료는 슬라이드에 쪽번호가 인쇄되어 있지 않아서, 아래 `p.N`은 PDF 파일 자체의 페이지 순서(1부터 시작)를 가리킨다. 이 PDF는 대부분 강의계획서(수강 규칙·성적·연락처 등) 내용이라 개념적으로 정리할 내용은 아래 두 섹션(compiler의 정의와 중요성)뿐이다.

## 1. What is a Compiler? *(p.3)*

- 전체 compilation toolchain은 사람이 작성한 프로그램(human-understandable language)을 컴퓨터가 실행 가능한 형태(binary instruction)로 번역함
- 컴퓨터는 binary instruction만 실행할 수 있고, 사람이 이해하기 쉬운 언어와 컴퓨터가 이해하는 언어 사이의 간극을 **compiler**가 메움
- 예: `int sum; int a = 1; int b = 3; sum = a + b;` (Program, 사람이 이해하는 서술) → Compiler → `0100010000101...` (Executable, 컴퓨터가 이해하는 형태)

## 2. Why is a Compiler Important? *(p.4~6)*

- Compiler는 hardware와 user 사이의 간극을 이어주는 역할 — compiler가 없으면 hardware를 활용할 수 없음
- computing stack에서 compiler는 System Software 계층에 속하며, Algorithm/Programming과 SW/HW Interface·Microarchitecture·Logic·Devices 사이를 연결함 *(p.4)*
  ```
  Algorithm
  Programming
  System Software   ← compiler가 속한 계층
  SW/HW Interface
  Microarchitecture
  Logic
  Devices
  ```
- ChatGPT, Human Genome Project, Human Brain Project, Neuralink 같은 다양한 신흥 응용 분야와, NVIDIA GPU/IBM Q/UPMEM/PIM 같은 혁신적 컴퓨팅 하드웨어들이 계속 등장하고 있음 — 이런 응용과 하드웨어를 실제로 활용하려면 그 사이를 잇는 compiler 기술이 중요함 *(p.5)*
- 예시: AMD MI300X는 NVIDIA H200 대비 가격 대비 스펙(메모리 용량·대역폭)이 경쟁력 있지만($15,000 vs $30,000), NVIDIA는 CUDA·NVSwitch 등 소프트웨어/네트워크 생태계를 지배하고 있어 실사용에서 격차가 발생함 — 하드웨어 성능 자체보다 이를 뒷받침하는 소프트웨어 도구체인(compiler 포함)의 성숙도가 실질적 경쟁력을 좌우하는 사례 *(p.6)*
