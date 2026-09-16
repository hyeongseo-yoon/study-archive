# Chapter 3: Growth of Functions

*Introduction to Algorithms, 3rd Ed. (Cormen, Leiserson, Rivest, Stein)*

## 1. Asymptotic notation 개요 *(슬라이드 p.2~4)*

세 가지 기본 notation: **Θ**(tight bound), **O**(upper bound), **Ω**(lower bound)

부등호에 빗댄 직관 *(p.4, p.15)*:
| notation | 부등호 유비 |
|---|---|
| f(n) = Θ(g(n)) | f(n) = g(n) (degree 기준) |
| f(n) = O(g(n)) | f(n) ≤ g(n) |
| f(n) = Ω(g(n)) | f(n) ≥ g(n) |
| f(n) = o(g(n)) | f(n) < g(n) |
| f(n) = ω(g(n)) | f(n) > g(n) |

예 *(p.3)*: Θ(n²) = 3n²+2n-1 (O)  /  Θ(n²) ≠ 3n-1 (X, degree가 다름)  /  O(n²) = 3n-1 (O, upper bound는 더 높아도 됨)  /  Ω(n) = 3n²-1 (O, lower bound는 더 낮아도 됨)

---

## 2. O-notation — asymptotic upper bound *(슬라이드 p.5~7)*

**정의**: 양의 상수 c, n₀가 존재해서 모든 n ≥ n₀에 대해 0 ≤ f(n) ≤ c·g(n)이면 f(n) = O(g(n))

**예제**: 3n+1 = O(n²) 증명
- 3n+1 ≤ cn²을 만족하는 c, n₀를 찾으면 됨
- n²으로 나누면 3/n + 1/n² ≤ c
- n ≥ 1(n₀=1)일 때 c=4로 성립

## 3. Ω-notation — asymptotic lower bound *(슬라이드 p.8~9)*

**정의**: 양의 상수 c, n₀가 존재해서 모든 n ≥ n₀에 대해 0 ≤ c·g(n) ≤ f(n)이면 f(n) = Ω(g(n))

**예제**: 3n²-4n+1 = Ω(n) 증명
- 3n²-4n+1 ≥ cn을 만족하는 c, n₀를 찾으면 됨
- n으로 나누면 3n-4+1/n ≥ c
- n ≥ 2(n₀=2)일 때 c=2로 성립

## 4. Θ-notation — asymptotically tight bound *(슬라이드 p.10~13)*

**정의**: 양의 상수 c₁, c₂, n₀가 존재해서 모든 n ≥ n₀에 대해 0 ≤ c₁g(n) ≤ f(n) ≤ c₂g(n)이면 f(n) = Θ(g(n))

**예제**: (1/2)n²-3n = Θ(n²) 증명
- c₁n² ≤ (1/2)n²-3n ≤ c₂n²을 만족하는 c₁, c₂, n₀를 찾으면 됨
- n²으로 나누면 c₁ ≤ 1/2 - 3/n ≤ c₂
- 우변: n≥1이면 c₂≥1/2로 성립 / 좌변: n≥7이면 c₁≤1/14로 성립
- 따라서 c₁=1/14, c₂=1/2, n₀=7로 Θ(n²) 성립

**일반화**: 임의의 다항식 p(n) = Σᵢaᵢnⁱ (aₐ > 0)에 대해 p(n) = Θ(nᵈ) — **최고차항의 차수만 남기고 나머지는 버림**

## 5. 정렬/탐색 알고리즘의 복잡도 정리 *(슬라이드 p.14)*

| 알고리즘 | 복잡도 |
|---|---|
| Insertion sort | O(n²), Ω(n) |
| Selection sort | Θ(n²) |
| Merge sort | Θ(n lg n) |
| Binary search | O(lg n), Ω(1) |

---

## 6. 함수 비교의 성질 *(슬라이드 p.16~20)*

부등호와 마찬가지로 함수 비교도 아래 성질들을 만족한다.

- **Transitivity** (=, ≤, ≥, <, > 모두 성립): f(n)=Θ(g(n)) ∧ g(n)=Θ(h(n)) ⟹ f(n)=Θ(h(n)) (O, Ω, o, ω도 동일)
- **Reflexivity** (=, ≤, ≥): f(n)=Θ(f(n)), f(n)=O(f(n)), f(n)=Ω(f(n))
- **Symmetry** (=): f(n)=Θ(g(n)) ⟺ g(n)=Θ(f(n))
- **Transpose symmetry** (≤↔≥, <↔>): f(n)=O(g(n)) ⟺ g(n)=Ω(f(n)) / f(n)=o(g(n)) ⟺ g(n)=ω(f(n))

## 7. Trichotomy — 함수는 항상 비교 가능한가? *(슬라이드 p.21)*

- 실수는 trichotomy를 만족: 임의의 a, b에 대해 a<b, a=b, a>b 중 정확히 하나가 성립 (항상 비교 가능)
- **함수는 trichotomy를 만족하지 않음** — f(n) ≠ O(g(n))이면서 f(n) ≠ Ω(g(n))인 경우가 존재
  - 예: n과 n^(1+sin n) — sin n이 진동하므로 두 함수는 asymptotic하게 비교 불가능
