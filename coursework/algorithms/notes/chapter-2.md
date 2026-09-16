# Chapter 2: Getting Started

*Introduction to Algorithms, 3rd Ed. (Cormen, Leiserson, Rivest, Stein)*

## 1. Sorting problem *(슬라이드 p.7)*

- **input**: n개의 수로 이뤄진 수열 &lt;a₁, a₂, ..., aₙ&gt; (각 수는 **key**라고 부름)
- **output**: 입력 수열의 permutation(재배열) &lt;a'₁, a'₂, ..., a'ₙ&gt;이면서 a'₁ ≤ a'₂ ≤ ... ≤ a'ₙ을 만족
- 예: input &lt;5, 2, 4, 6, 1, 3&gt; → output &lt;1, 2, 3, 4, 5, 6&gt;

---

## 2. Insertion sort *(슬라이드 p.8~24)*

### Description *(p.9~12)*

- **insertion**: key 하나와 sorted list가 주어졌을 때, sorted 순서를 유지하며 그 key를 list에 삽입하는 것
- **insertion sort**: insertion을 incremental하게 반복 적용하는 정렬 알고리즘
  - A[2]를 A[1]에 삽입 → A[3]을 A[1..2]에 삽입 → ... → A[n]을 A[1..n-1]에 삽입

```
INSERTION-SORT(A)
1  for j = 2 to A.length
2      key = A[j]
3      // Insert A[j] into the sorted sequence A[1..j-1].
4      i = j - 1
5      while i > 0 and A[i] > key
6          A[i+1] = A[i]
7          i = i - 1
8      A[i+1] = key
```

- 전체 구조: n-1번의 insertion 반복
- 매 반복: `A[j]`를 넣을 자리를 찾은 뒤(5~7행) 그 자리에 넣음(8행)

### Performance — Running time *(p.14~23)*

- 알고리즘의 running time은 특정 머신에서 실측하는 대신, **알고리즘이 수행하는 instruction의 개수**를 세어 분석한다 (머신마다 실측값이 달라 비교가 불가능하기 때문).
- Instruction 종류: arithmetic(사칙연산 등), data movement(load/store/copy), control(분기, 서브루틴 호출 등)
- running time은 입력 크기 n에 대한 함수 T(n)으로 표현

**각 줄의 cost × 실행 횟수(times)를 합산**해 T(n)을 구한다. tⱼ는 j에 대해 while 검사가 실행된 횟수 (for, while 검사는 loop body보다 1번 더 실행됨에 유의).

```
T(n) = c₁n + c₂(n-1) + c₄(n-1) + c₅Σtⱼ + c₆Σ(tⱼ-1) + c₇Σ(tⱼ-1) + c₈(n-1)
```

- **Best case**: 이미 정렬된 입력 → tⱼ = 1 (모든 j) → T(n) = an + b, **linear function**
- **Worst case**: 역순 정렬된 입력 → tⱼ = j (모든 j) → T(n) = an² + bn + c, **quadratic function**
- leading term의 차수만 중요(rate of growth 관점) → Θ-notation으로 표현하면 worst-case running time은 **Θ(n²)**

### Performance — Space consumption *(p.24)*

- Θ(n) space. 입력을 **sorted in place**하므로 실제로는 n + c (상수 c는 임시 변수용)

---

## 3. Merge sort *(슬라이드 p.26~41)*

### Merge *(p.27~30)*

- **merge**: 정렬된 두 리스트가 주어졌을 때, 그 안의 모든 key를 담은 하나의 정렬된 리스트를 만드는 것
- 예: &lt;1,5,6,8&gt;, &lt;2,4,7,9&gt; → &lt;1,2,4,5,6,7,8,9&gt;

```
MERGE(A, p, q, r)
1   n₁ = q - p + 1
2   n₂ = r - q
3   let L[1..n₁+1]과 R[1..n₂+1]을 새 배열로 선언
4   for i = 1 to n₁
5       L[i] = A[p+i-1]
6   for j = 1 to n₂
7       R[j] = A[q+j]
8   L[n₁+1] = ∞
9   R[n₂+1] = ∞
10  i = 1
11  j = 1
12  for k = p to r
13      if L[i] ≤ R[j]
14          A[k] = L[i]; i = i+1
15      else A[k] = R[j]; j = j+1
```

- 두 리스트의 끝에 ∞ sentinel을 둬서 한쪽이 먼저 소진돼도 비교 로직을 단순하게 유지
- 핵심 연산은 compare와 move. #comparison ≤ #movement = 2(n₁+n₂) → merge의 running time은 **Θ(n₁+n₂)**

### Merge sort — divide-and-conquer *(p.31~34)*

- **Divide**: n개의 key를 n/2개씩 두 리스트로 나눔
- **Conquer**: 두 리스트를 merge sort로 재귀 정렬
- **Combine**: 정렬된 두 리스트를 merge

```
MERGE-SORT(A, p, r)
1  if p < r
2      q = ⌊(p+r)/2⌋
3      MERGE-SORT(A, p, q)
4      MERGE-SORT(A, q+1, r)
5      MERGE(A, p, q, r)
```

### Running time *(p.35~41)*

- Divide: Θ(1) (중간 인덱스 계산만)
- Conquer: 2T(n/2) (크기 ~n/2인 subproblem 2개를 재귀적으로 풂)
- Combine: Θ(n) (n/2 크기 두 리스트를 merge)

```
T(n) = Θ(1)              if n = 1,
     = 2T(n/2) + Θ(n)    if n > 1
     → T(n) = c (n=1), 2T(n/2) + cn (n>1)
```

**Recursion tree**로 분석: 각 depth(레벨)의 총 cost는 cn으로 동일하고, 레벨 수는 lg n + 1개.

```
Total = cn·lg n + cn = Θ(n lg n)
```

→ merge sort의 running time은 **Θ(n lg n)**, insertion sort의 Θ(n²)보다 점근적으로 빠름.
