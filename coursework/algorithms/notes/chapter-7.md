# Chapter 7: Quicksort

*Introduction to Algorithms, 3rd Ed. (Cormen, Leiserson, Rivest, Stein)*

## 1. Quicksort 알고리즘 *(슬라이드 p.3~6)*

### Divide-and-Conquer 구조 *(p.3)*
```
QUICKSORT(A, p, r)
 if p < r
     q = PARTITION(A, p, r)
     QUICKSORT(A, p, q-1)
     QUICKSORT(A, q+1, r)
```

### Partition 아이디어 *(p.4~5)*
- 배열의 마지막 원소 x를 **pivot**으로 삼아, 배열을 `≤ x`인 부분과 `≥ x`인 부분으로 나눔
- 예시: `[2,8,7,1,3,5,6,4]`에서 pivot=4일 때, 파티션 후 `[2,1,3,4,7,5,6,8]`로 재배열됨 (4를 기준으로 왼쪽은 4 이하, 오른쪽은 4 이상)
- 슬라이드 5는 이 과정을 j가 배열을 한 칸씩 스캔하면서 i(≤x 영역의 경계)를 갱신해가는 단계별 스냅샷으로 보여줌

### PARTITION 의사코드 *(p.6)*
```
PARTITION(A, p, r)
1  x = A[r]
2  i = p - 1
3  for j = p to r-1
4      do if A[j] ≤ x
5          then i = i + 1
6              exchange A[i] ↔ A[j]
7  exchange A[i+1] ↔ A[r]
8  return i + 1
```
- `x`는 pivot(마지막 원소), `i`는 지금까지 확인한 원소 중 pivot 이하인 부분의 마지막 인덱스
- j로 배열을 순회하며 `A[j] ≤ x`일 때만 i를 늘리고 A[i]와 A[j]를 교환 → 결국 pivot을 A[i+1] 위치로 옮기고 그 인덱스를 반환

---

## 2. Quicksort 성능 *(슬라이드 p.7~15)*

### Partition의 비용 *(p.7)*
PARTITION 한 번은 **Θ(n)** — 이후 성능은 partition이 얼마나 균형 있게 나뉘는지에 좌우됨 (**balanced** vs **unbalanced partitioning**)

### Balanced partitioning *(p.8~9)*
- PARTITION이 크기 ⌊n/2⌋와 ⌈n/2⌉-1인 두 부분문제로 나누는 이상적인 경우
- 재귀식: `T(n) ≤ 2T(n/2) + Θ(n) = O(n lg n)`
- recursion tree로 보면 각 레벨의 합이 n이고 트리의 깊이가 lg n → 전체 **Θ(n lg n)**

### Unbalanced partitioning *(p.10~11)*
- 한쪽이 크기 0, 다른 쪽이 n-1인 극단적으로 불균형한 경우 (트리가 사선으로 계속 이어지는 형태)
- 재귀식: `T(n) = T(n-1) + Θ(n) = Σ(k=1 to n) Θ(k) = Θ(n²)`

### Worst-case Analysis *(p.12~14)*
- Quicksort는 최악의 경우 **Ω(n²)** 시간이 걸림 (unbalanced partitioning이 발생하는 경우)
- substitution method로 `T(n) = O(n²)` 증명 *(p.13~14)*:
  - `T(n) = max_{0≤q≤n-1}(T(q) + T(n-q-1)) + Θ(n)`
  - `T(n) ≤ cn²`라고 가정하고 전개하면, 내부 max 식은 `q=0` 또는 `q=n-1`일 때 최대가 됨
  - 정리하면 `T(n) ≤ c·(n-1)² + Θ(n) = cn² - c(2n-1) + Θ(n) ≤ cn²` (c를 Θ(n) 항을 압도할 만큼 충분히 크게 선택)
  - 따라서 **T(n) = O(n²)**

### Average-case Analysis *(p.15)*
- `E[T(n)] = (1/n)·Σ_{q=1}^{n}(E[T(q-1)] + E[T(n-q)]) + Θ(n) = (2/n)·Σ_{q=0}^{n-1} E[T(q)] + Θ(n)`
- substitution method로 `T(n) ≤ cn lg n`임을 보일 수 있음 (교재 Problem 7-3에서 다룸)

---

## 3. Randomized Quicksort *(슬라이드 p.16~17)*

### RANDOMIZED-PARTITION *(p.16)*
```
RANDOMIZED-PARTITION(A, p, r)
1. i = RANDOM(p, r)
2. exchange A[r] with A[i]
3. return PARTITION(A, p, r)
```
pivot으로 쓸 원소를 매번 `[p, r]` 범위에서 무작위로 골라 마지막 자리(A[r])와 교환한 뒤 기존 PARTITION을 그대로 수행 — 특정 입력(이미 정렬된 배열 등)에 대해 항상 worst case가 발생하는 것을 방지

### RANDOMIZED-QUICKSORT *(p.17)*
```
RANDOMIZED-QUICKSORT(A, p, r)
1 if p < r
2   q = RANDOMIZED-PARTITION(A, p, r)
3     RANDOMIZED-QUICKSORT(A, p, q-1)
4     RANDOMIZED-QUICKSORT(A, q+1, r)
```
PARTITION 대신 RANDOMIZED-PARTITION을 사용한다는 점만 다름

---

## 4. Self-study 문제 *(슬라이드 p.18)*
- Exercise 7.1-2: 모든 원소가 같은 값일 때도 balanced partition이 되는지
- Exercise 7.2-4: 거의 정렬된(almost-sorted) 입력을 정렬하는 경우
