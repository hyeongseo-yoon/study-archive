# Chapter 8: Sorting in Linear Time

*Introduction to Algorithms, 3rd Ed. (Cormen, Leiserson, Rivest, Stein)*

## 1. Lower Bounds for Sorting *(슬라이드 p.4~10)*

### Comparison Sort의 정의 *(p.4)*
- **Comparison sort**: 입력 원소들의 정렬 순서를 오직 **비교(comparison)**만으로 결정하는 정렬 알고리즘
- `a_i < a_j`, `a_i ≤ a_j`, `a_i = a_j`, `a_i ≥ a_j`, `a_i > a_j` 같은 test를 사용
- Heapsort, Mergesort, Insertion sort, Selection sort, Quicksort가 모두 comparison sort
- **Lower bound**: 어떤 comparison sort든 n개의 원소를 정렬하려면 최악의 경우 **Ω(n lg n)**번의 비교가 필요함

### 비교 형태의 단순화 *(p.5)*
- 일반성을 잃지 않고 입력 원소가 모두 서로 다르다고 가정 가능
- `a_i ≤ a_j`, `a_i ≥ a_j`, `a_i > a_j`, `a_i < a_j`는 서로 동치이므로, 모든 비교는 `a_i ≤ a_j` 형태로 가정

### Decision-tree 모델 *(p.6~10)*
- Comparison sort는 **decision tree**(full binary tree)로 표현 가능
  - 각 **leaf**는 입력 원소들의 한 permutation
  - 각 **internal node** `i:j`는 비교 `a_i ≤ a_j`를 나타냄
  - node `i:j`의 **왼쪽 subtree**는 `a_i ≤ a_j`인 경우의 모든 permutation, **오른쪽 subtree**는 `a_i > a_j`인 경우의 모든 permutation을 포함 *(p.6~7)*
  - 정렬 알고리즘의 실행은 root에서 leaf까지의 경로를 따라가는 것에 대응 *(p.8)*
  - **최악의 경우 비교 횟수 = decision tree의 height** *(p.9)*
- **Theorem 8.1**: 어떤 comparison sort 알고리즘이든 최악의 경우 Ω(n lg n)번의 비교가 필요함 *(p.10)*
  - **증명**: height h, 원소 개수 n인 decision tree에서, n개 입력의 모든 permutation(n!개)이 leaf로 나타나야 함
  - `n! ≤ 2^h` (full binary tree의 leaf 개수는 2^h 이하)
  - `lg(n!) ≤ h`
  - 식 (3.18) `lg(n!) = Θ(n lg n)`에 의해 `h = Ω(n lg n)`

### Self-study *(p.11)*
- Exercise 8.1-1: decision tree에서 leaf의 최소 depth
- Exercise 8.1-3: decision tree의 존재 여부
- Exercise 8.1-4: decision tree의 lower bound

---

## 2. Counting Sort *(슬라이드 p.12~19)*

### 개념 *(p.12)*
- **counting**을 이용하는 정렬 알고리즘 (comparison을 사용하지 않음)
- 입력 원소 x가, x보다 작은 원소의 개수가 i-1개라면 정렬 후 배열에서 **i번째 자리**에 위치해야 한다는 아이디어

### 동작 예시 *(p.13~16)*
- 입력 A = [2,5,3,0,2,3,0,3] (인덱스 1~8)에 대해:
  1. **C[0..k]**: 값 i가 A에 등장하는 횟수를 세는 카운트 배열 → C = [2,0,2,3,0,1] (0이 2개, 2가 2개, 3이 3개, 5가 1개) *(p.13, p.15)*
  2. **누적합**: C[i] += C[i-1]을 적용해 C[i]가 "i 이하인 원소의 개수"가 되도록 변환 → C' = [2,2,4,7,7,8] *(p.15)*
  3. A를 뒤에서부터(j = A.length downto 1) 순회하며, `B[C[A[j]]] = A[j]`로 B에 배치하고 `C[A[j]]`를 1 감소시킴 — 이렇게 뒤에서부터 채우면 같은 값의 상대적 순서가 유지됨 *(p.16)*
  - 예시 진행: A[8]=3 → C[3]=7이므로 B[7]=3, C[3]을 6으로 감소 / A[7]=0 → C[0]=2이므로 B[2]=0, C[0]을 1로 감소 / A[6]=3 → C[3]=6이므로 B[6]=3, C[3]을 5로 감소 … *(p.16)*
- **Stable**: 입력 배열에서 값이 같은 원소들은 출력 배열에서도 같은 순서로 나타남 *(p.14)*

### COUNTING-SORT 의사코드 *(p.17)*
```
COUNTING-SORT(A, B, k)
1  for i = 0 to k
2      C[i] = 0
3  for j = 1 to A.length
4      C[A[j]] = C[A[j]] + 1
5      // C[i] contains the number of elements equal to i.
6  for i = 1 to k
7      C[i] = C[i] + C[i-1]
8      // C[i] contains the number of elements less than or equal to i.
9  for j = A.length downto 1
10     B[C[A[j]]] = A[j]
11     C[A[j]] = C[A[j]] - 1
```
- 줄 1~2: Θ(k) / 줄 3~4: Θ(n) / 줄 6~7: Θ(k) / 줄 9~11: Θ(n)

### Running time *(p.18)*
- 전체 시간: **Θ(k+n)**, k는 입력 정수의 범위(range)
- **k = O(n)**이면 running time은 **Θ(n)** — comparison sort의 Ω(n lg n) 하한을 우회하는 linear time 정렬이 가능

### Self-study *(p.19)*
- Exercise 8.2-1: counting sort 예제
- Exercise 8.2-3: counting sort의 안정성(stability)
- Exercise 8.2-4: counting sort 응용

---

## 3. Radix Sort *(슬라이드 p.20~29)*

### 개념과 동작 방식 *(p.20~21)*
- 여러 자릿수(digit)로 이루어진 키를 정렬할 때, **자릿수 단위로 여러 번 정렬**하는 방식
- 반드시 **LSD(Least Significant Digit)부터 MSD(Most Significant Digit) 방향**으로 각 자릿수에 대해 **stable sort**를 적용해야 올바르게 동작함
  - 예: [326,453,608,835,751,435,704,690]을 1의 자리 → 10의 자리 → 100의 자리 순으로 stable sort하면 최종적으로 [326,435,453,608,690,704,751,835]로 정렬됨 *(p.20~21)*

### RADIX-SORT 의사코드와 running time *(p.22)*
```
RADIX-SORT(A, d)
1 for i = 1 to d
2     use a stable sort to sort array A on digit i
```
- n개의 d-digit 숫자가 있고 각 digit이 최대 k개의 값을 가질 수 있을 때, RADIX-SORT는 **Θ(d(n+k))** 시간에 정렬함 (각 digit에 대해 counting sort 등 stable sort를 한 번씩 적용 → Θ(n+k)를 d번 반복)
- d가 상수이고 k = O(n)이면 radix sort는 **linear time**

### d와 k를 조정하는 관점 *(p.23~26)*
- 숫자를 몇 bit씩 묶어서 하나의 "digit"으로 볼지(r bit 단위)에 따라 d와 k가 달라짐 — d와 k 사이에는 trade-off가 있음 *(p.23)*
- **Lemma 8.4** (self-study): n개의 b-bit 숫자와 임의의 양의 정수 r ≤ b가 주어지면, RADIX-SORT는 이 숫자들을 **Θ((b/r)(n+2^r))** 시간에 올바르게 정렬함 — b bit를 r bit씩 묶어 digit으로 삼으면 총 (b/r)개의 digit이 생기고, 각 digit은 0~2^r-1의 값을 가짐 *(p.24)*
- **최적의 r 구하기** — `(b/r)(n+2^r)`을 최소화 *(p.25~26)*:
  1. `b < ⌊lg n⌋`인 경우: 어떤 r을 고르든 `r ≤ b`이므로 `(n+2^r) = Θ(n)`. 따라서 `r = b`로 선택하면 `(b/b)(n+2^b) = Θ(n)`으로, 점근적으로 최적
  2. `b ≥ ⌊lg n⌋`인 경우: `r = ⌊lg n⌋`으로 선택하면 상수 배 이내에서 최선의 시간 `(b/lg n)(n+2^lg n) = (b/lg n)(2n) = Θ(bn/lg n)`을 얻음
  - r을 ⌊lg n⌋보다 키우면 분자의 2^r이 분모의 r보다 더 빠르게 증가해서 불리해지고, r을 ⌊lg n⌋보다 줄이면 b/r 항이 커지는 반면 n+2^r 항은 여전히 Θ(n)에 머물러 역시 불리해짐

### Radix sort vs Quicksort 비교 *(p.27~28)*
- `b = O(lg n)`이면 `r ≈ lg n`을 선택 → **Radix sort: Θ(n)** vs **Quicksort: Θ(n lg n)** *(p.27)*
- 다만 Θ-notation에 숨겨진 상수 배수(constant factor)가 서로 다름을 유의해야 함 *(p.28)*:
  1. radix sort는 quicksort보다 n개의 key에 대한 pass 횟수가 적을 수 있지만, radix sort의 각 pass가 훨씬 오래 걸릴 수 있음
  2. **radix sort는 in-place로 정렬하지 않음** (counting sort 기반이라 추가 배열 필요)

### Self-study *(p.29)*
- Exercise 8.3-1: radix sort 예제
- Exercise 8.3-2: 안정성(stability)
- Exercise 8.3-4: radix sort 응용
