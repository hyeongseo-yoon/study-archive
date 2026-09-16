# Chapter 1: Algorithms and Problem Solving

*Introduction to Algorithms, 3rd Ed. (Cormen, Leiserson, Rivest, Stein)*

## 1. Problem과 Algorithm *(슬라이드 p.8)*

- **problem**: well-specified input과 output
- **algorithm**: problem을 푸는 well-defined procedure

예시 *(p.9~10)*: 라면 끓이기
- input: 면, 스프, 계란, 파 등 / output: 조리된 라면
- algorithm: "물 500cc 끓인다 → 면·스프 투입 → 5분 끓인다 → 계란·파 투입 → 1분 끓인다"처럼 단계별 절차로 표현

## 2. Computer Algorithm *(슬라이드 p.11)*

- **computer algorithm**: well-defined *computational* procedure to solve a *computational* problem
- computational problem 예시: 1부터 n까지 정수의 합 구하기 (S = 1 + 2 + ... + n)

## 3. Algorithm의 correctness *(슬라이드 p.12~13)*

같은 문제도 여러 알고리즘으로 풀 수 있음 — 초등학교식(왼쪽부터 하나씩 더하기)과 고등학교식(공식 S = n(n+1)/2) 비교.

- 초등학교식: 정의상 자명하게 correct
- 고등학교식: 증명 필요
  - 2S = (1+2+...+n) + (n+n-1+...+1) = n(n+1)
  - S = n(n+1)/2

## 4. Algorithm의 performance *(슬라이드 p.15~16)*

두 알고리즘이 모두 correct해도 성능 비교가 필요함. 성능의 두 축:
- **running time**
- **space consumption**

앞의 두 합 구하기 알고리즘을 예로 들면, 고등학교식(공식 한 번 계산)이 초등학교식(n번 덧셈)보다 running time이 빠름.

## 5. Problem instance *(슬라이드 p.17)*

- **problem**: 일반화된 형태 (예: 1부터 n까지 정수의 합, S = 1+2+...+n)
- **problem instance**: 구체적인 입력이 주어진 형태 (예: 1부터 100까지의 합, 1+2+...+100)

## Chapter 1 핵심 요약 *(슬라이드 p.18)*

- Problem: 문제를 왜 정의하는지, problem definition
- Algorithm: description(기술) / correctness(정확성 증명) / performance(running time, space consumption)

이 세 가지 관점(기술·정확성·성능)이 이후 모든 알고리즘을 배울 때 반복되는 틀이다.
