# Chapter 4: Divide-and-Conquer

*Introduction to Algorithms, 3rd Ed. (Cormen, Leiserson, Rivest, Stein)*

## 1. Recurrence 개념 *(슬라이드 p.3~4)*

- 알고리즘이 자기 자신을 재귀 호출하면, running time을 **recurrence**(점화식)로 표현할 수 있음
- **recurrence**: 어떤 함수를 더 작은 입력에서의 자기 자신의 값으로 정의하는 방정식/부등식
  - 예: T(n) = Θ(1) (n=1), 2T(n/2) + Θ(n) (n>1)
- recurrence를 푸는 것 = 해에 대한 asymptotic한 Θ, O bound를 구하는 것
- 이 강의에서 다루는 두 가지 방법: **substitution method**, **recursion-tree method**

---

## 2. Substitution method *(슬라이드 p.5~12)*

두 단계로 구성:
1. 해를 **guess**한다
2. **mathematical induction**으로 그 guess가 맞음을 증명한다 (basis/boundary condition + inductive step)

### 예제: T(n) = 2T(⌊n/2⌋) + n *(p.6~11)*

- Guess: T(n) = O(n lg n), 즉 T(n) ≤ cn lg n을 증명하면 됨
- **Inductive step**: ⌊n/2⌋에 대해 bound가 성립한다고 가정(T(⌊n/2⌋) ≤ c⌊n/2⌋lg(⌊n/2⌋))하고 전개
  ```
  T(n) = 2T(⌊n/2⌋) + n
       ≤ 2(c⌊n/2⌋lg(⌊n/2⌋)) + n
       ≤ cn lg(n/2) + n
       = cn lg n - cn lg 2 + n
       = cn lg n - cn + n
       ≤ cn lg n   (c ≥ 1일 때)
  ```
- **Boundary condition**: n=1에서 T(n) ≤ cn lg n은 불가능(T(1)=1이지만 c·1·lg1=0). 하지만 **모든 n에 대해 증명할 필요는 없고, 어떤 n₀ 이상에서만** 성립하면 됨
  - n₀=2로 두고 T(1)=1 → T(2)=2T(1)+2=4 ≤ c·2·lg2 → c≥2로 만족
  - 그 사이의 boundary는 재귀적으로 연결됨 (예: T(3)=2T(1)+3=5, c≥2로 T(3)≤c·3·lg3 만족)

### 흔한 실수 *(p.12)*

- 느슨한 guess로 증명해도 tight bound가 되지 않는 경우 — 예를 들어 T(n) ≤ 2T(⌊n/2⌋) + n에서 O(n)을 guess해 T(n) ≤ cn을 증명하려 하면, T(n) ≤ 2c⌊n/2⌋ + n ≤ cn + n = O(n)처럼 **induction 자체는 성립하는 것처럼 보여도** 실제로는 추가 항(+n)이 누적돼 tight bound가 아님에 주의해야 함

---

## 3. Recursion-tree method *(슬라이드 p.13~20, 22~25)*

- Substitution method는 correct한 guess가 필요한데, **좋은 guess를 만드는 도구**가 recursion-tree method
- 절차: recursion-tree로 **guess**를 만든 뒤, **substitution method로 증명**

### 예제 1: T(n) = 3T(⌊n/4⌋) + Θ(n²) *(p.14~20)*

목표: T(n) = Θ(n²) 증명
- **Ω(n²)**: 자명 (recurrence의 두 번째 항이 이미 n²이므로)
- **O(n²)**: recursion-tree로 guess

recursion tree 구조 (n = 4ᵏ로 가정, T(n) = 3T(n/4) + cn²):
- depth i에서 subproblem 크기: n/4ⁱ
- depth i에서 노드 개수: 3ⁱ
- 레벨 수: log₄n + 1 (n/4ⁱ = 1일 때, 즉 i = log₄n에서 종료)
- depth i의 (last level 제외) 총 cost: 3ⁱ·c(n/4ⁱ)² = (3/16)ⁱ·cn²
- last level의 총 cost: Θ(3^(log₄n)) = Θ(n^(log₄3))

전체 cost 합산 (등비급수):
```
T(n) = Σ(i=0 to log₄n-1) (3/16)ⁱ cn² + Θ(n^(log₄3))
     < Σ(i=0 to ∞) (3/16)ⁱ cn² + Θ(n^(log₄3))
     = 16/13 cn² + Θ(n^(log₄3))
     = O(n²)
```

→ guess: T(n) = O(n²). 이를 substitution method로 증명(T(n) ≤ dn²라고 가정하고 전개):
```
T(n) = 3T(⌊n/4⌋) + cn²
     ≤ 3d(n/4)² + cn²
     = 3/16 dn² + cn²
     ≤ dn²   (d ≥ (16/13)c일 때)
```
Ω(n²)와 O(n²) 모두 성립하므로 **T(n) = Θ(n²)**

### 예제 2: T(n) = T(n/3) + T(2n/3) + O(n) *(p.22~25)*

목표: T(n) = O(n lg n) 증명. 두 subtree의 크기가 다르므로(n/3, 2n/3) recursion tree가 비대칭.
- 각 레벨의 cost 합은 항상 cn (한 레벨 안의 모든 노드 cost를 더하면 상수배로 유지됨)
- tree의 height: 가장 느리게 줄어드는 2n/3 쪽 경로 기준, (2/3)ᵏn = 1일 때 k = log_(3/2) n
- Total = 레벨당 cost × (height+1) = O(cn·log_(3/2)n) = O(n lg n) → guess

substitution method로 증명(T(n) ≤ dn lg n 가정):
```
T(n) ≤ T(n/3) + T(2n/3) + cn
     ≤ d(n/3)lg(n/3) + d(2n/3)lg(2n/3) + cn
     = dn lg n + dn(-lg3 + 2/3) + cn
     ≤ dn lg n   (d ≥ c/(lg3 - 2/3)일 때)
```
→ **T(n) = O(n lg n)**
