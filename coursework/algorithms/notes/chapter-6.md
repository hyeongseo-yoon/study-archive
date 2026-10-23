# Chapter 6: Heapsort

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

*Introduction to Algorithms, 3rd Ed. (Cormen, Leiserson, Rivest, Stein)*

## 1. Heapsort 개요 *(슬라이드 p.3)*

- merge sort처럼 running time이 **O(n lg n)**
- insertion sort처럼 **in place** 정렬 (in-place: 한 번에 O(1)개 이상의 배열 원소가 정렬 대상 배열 바깥에 있지 않음)

---

## 2. Heap *(슬라이드 p.4~11)*

### 구조 *(p.4)*

- (binary) heap의 모양: **nearly complete binary tree**
- complete binary tree: 모든 leaf가 같은 depth를 가지고 모든 internal node가 degree 2를 가지는 트리
- 예시 heap (원소 10개): 마지막 층(2, 4, 1)이 왼쪽부터 채워진 모양
  ```
            16
         /      \
       14        10
      /  \      /  \
     8    7    9    3
    / \  /
   2  4 1
  ```

### Heap property *(p.5~7)*

두 종류의 binary heap이 있음:
- **max-heap property**: A[PARENT(i)] ≥ A[i] — 부모가 자식보다 크거나 같음. root가 최댓값을 가지며, 모든 subtree의 root도 그 subtree 내 최댓값을 가짐
- **min-heap property**: A[PARENT(i)] ≤ A[i] — 자식이 부모보다 크거나 같음. root가 최솟값

### 배열 표현 *(p.8~9)*

- heap은 배열에 저장 가능: root는 A[1], 나머지는 level order로 저장
- 인덱스 관계:
  ```
  PARENT(i)  return ⌊i/2⌋
  LEFT(i)    return 2i
  RIGHT(i)   return 2i+1
  ```
- 예시 (p.8~9): 위 트리를 level order로 저장한 배열
  ```
  인덱스:  1   2   3  4  5  6  7  8  9  10
  값:     16  14  10  8  7  9  3  2  4  1
  ```
  - i=3(값 10)이면 LEFT=6(값 9), RIGHT=7(값 3), PARENT=⌊3/2⌋=1(값 16)

### Height *(p.10~11)*

- **node의 height**: 그 node에서 leaf까지의 longest simple downward path에 있는 edge 개수
- **heap의 height** = root의 height = **Θ(lg n)** (n개 원소의 heap은 complete binary tree 기반이므로). 정확히는 n개 원소 heap의 height = ⌊lg n⌋ *(p.21)*

---

## 3. Heap property 유지 — MAX-HEAPIFY *(슬라이드 p.12~14)*

- **input**: 왼쪽·오른쪽 subtree는 이미 max-heap이지만, 그 node 자신의 값이 자식보다 작아서 max-heap property가 깨진 상태의 node
- **동작**: 그 node의 값을 max-heap 안에서 아래로 "float down"시켜, 그 node를 root로 하는 subtree가 max-heap이 되도록 함 — 자신과 두 자식 중 최댓값을 찾아 더 큰 자식과 교환하고, 교환된 위치에서 재귀적으로 반복
- **running time**: T(n) (n = subtree의 노드 수)
  - 값 교환 자체는 Θ(1)
  - 전체는 O(h) = O(lg n) (h는 그 subtree의 height)

### 예제 *(p.12~13)*

배열 [16, 4, 10, 14, 7, 9, 3, 2, 8, 1]에서 인덱스 2(값 4)가 max-heap property를 깨고 있음 (두 subtree는 max-heap).

```
1) i=2 (값 4): 자식 14(idx4), 7(idx5) → 최대 14 → 교환
   [16, 14, 10, 4, 7, 9, 3, 2, 8, 1]
2) i=4 (값 4): 자식 2(idx8), 8(idx9) → 최대 8 → 교환
   [16, 14, 10, 8, 7, 9, 3, 2, 4, 1]
3) i=9: 자식 없음 → 종료 (max-heap 복원)
```

---

## 4. Heap 만들기 — BUILD-MAX-HEAP *(슬라이드 p.15~23)*

```
BUILD-MAX-HEAP(A)
1  A.heap-size = A.length
2  for i = ⌊A.length/2⌋ downto 1
3      MAX-HEAPIFY(A, i)
```

- 배열의 뒤쪽 절반(⌊n/2⌋+1 ... n)은 모두 leaf이므로 그 자체로 1-원소 max-heap
- 자식을 가진 가장 오른쪽 node(i = ⌊A.length/2⌋)부터 거꾸로 root까지 MAX-HEAPIFY를 호출하며 올라가면, 매 호출 시점에 그 node의 두 subtree는 이미 max-heap이 되어 있어 MAX-HEAPIFY의 input 조건을 만족

### 예제 *(p.16~19)*

입력 배열 [4, 1, 3, 2, 16, 9, 10, 14, 8, 7] (원소 10개, i = 5부터 1까지)

```
i=5 (16): 자식 7 → 이미 OK, 변화 없음
i=4 (2):  자식 14, 8 → 14와 교환
          [4, 1, 3, 14, 16, 9, 10, 2, 8, 7]
i=3 (3):  자식 9, 10 → 10과 교환
          [4, 1, 10, 14, 16, 9, 3, 2, 8, 7]
i=2 (1):  자식 14, 16 → 16과 교환, idx5에서 자식 7과 교환
          [4, 16, 10, 14, 7, 9, 3, 2, 8, 1]
i=1 (4):  자식 16, 10 → 16과 교환, idx2에서 14와, idx4에서 8과 교환
          [16, 14, 10, 8, 7, 9, 3, 2, 4, 1]   ← max-heap 완성
```

### Running time *(p.20~23)*

- **Upper bound (느슨한 분석)**: MAX-HEAPIFY 한 번이 O(lg n), 호출이 Θ(n)번 → O(n lg n)
- **Tighter bound**: 실제로는 대부분의 node가 height가 작음(leaf에 가까울수록 많음)을 이용
  - height h인 node는 최대 ⌈n/2^(h+1)⌉개, MAX-HEAPIFY의 cost는 O(h)
  - 전체 cost = Σ(h=0 to ⌊lg n⌋) ⌈n/2^(h+1)⌉·O(h) = O(n·Σh/2^h)
  - Σ(h=0 to ∞) h/2^h = 2 (수렴하는 등비 계열) → 전체는 **O(n)**
- 따라서 **BUILD-MAX-HEAP은 linear time(O(n))에 가능**

---

## 5. Heapsort 알고리즘 *(슬라이드 p.24~31)*

### Extract-Max 아이디어 *(p.24~25)*

max-heap에서 최댓값(root)을 꺼낸 뒤 heap 구조를 복원하는 절차:
1. root(최댓값)를 마지막 원소와 교환
2. heap 크기를 1 줄임 (마지막 원소를 heap에서 제외 → 정렬된 영역으로 편입)
3. 새 root에 대해 MAX-HEAPIFY 호출 (O(lg n))

예시 (p.24~25): max-heap [16, 14, 10, 8, 7, 9, 3, 2, 4, 1]에서 최댓값 16을 제거
```
root 16 제거, 마지막 원소 1을 root로 → [1, 14, 10, 8, 7, 9, 3, 2, 4]
MAX-HEAPIFY: 1 ↔ 14, 1 ↔ 8, 1 ↔ 4 순서로 내려감
→ [14, 8, 10, 4, 7, 9, 3, 2, 1]   (새 root = 14, O(lg n))
```

### Heapsort 개요 *(p.26)*

- BUILD-MAX-HEAP on A[1..n]: O(n)
- Extract-Max를 n번: O(n lg n)

### HEAPSORT *(p.30)*

```
HEAPSORT(A)
1  BUILD-MAX-HEAP(A)
2  for i = A.length downto 2
3      exchange A[1] with A[i]
4      A.heap-size = A.heap-size - 1
5      MAX-HEAPIFY(A, 1)
```

- BUILD-MAX-HEAP으로 전체를 max-heap으로 만든 뒤, root(최댓값)를 배열 끝으로 보내고 heap 크기를 줄이는 과정을 반복 — 매번 남은 heap 중 최댓값이 정렬된 영역의 맨 앞에 쌓임

### 예제 *(p.27~29)*

max-heap [16, 14, 10, 8, 7, 9, 3, 2, 4, 1]에서 시작 (`|` 뒤는 정렬 완료 영역)

```
i=10: A[1]↔A[10], heap-size 9, MAX-HEAPIFY
      [14, 8, 10, 4, 7, 9, 3, 2, 1 | 16]
i=9:  A[1]↔A[9], heap-size 8, MAX-HEAPIFY
      [10, 8, 9, 4, 7, 1, 3, 2 | 14, 16]
i=8:  [9, 8, 3, 4, 7, 1, 2 | 10, 14, 16]
 ...  (i=2까지 반복, 마지막 원소 1개는 저절로 제자리)
최종: [1, 2, 3, 4, 7, 8, 9, 10, 14, 16]
```

### Running time *(p.31)*

- BUILD-MAX-HEAP: O(n)
- MAX-HEAPIFY를 n-1번 반복: 매번 O(lg n) → O(n lg n)
- 전체: **O(n lg n)**

---

## 6. Priority Queue *(슬라이드 p.32~37)*

- **priority queue**: 각 원소가 key라는 연관값을 가지는 집합 S를 관리하는 자료구조. heap으로 구현 가능
- **max-priority queue**의 연산:
  - `INSERT(S, x)`: 원소 x를 S에 삽입
  - `MAXIMUM(S)`: S에서 가장 큰 key를 가진 원소를 반환
  - `EXTRACT-MAX(S)`: S에서 가장 큰 key를 가진 원소를 제거하며 반환
  - `INCREASE-KEY(S, x, k)`: 원소 x의 key값을 새 값 k로 증가

### 각 연산의 구현과 running time *(p.33~37)*

- **MAXIMUM**: root값을 그냥 읽음 → **O(1)**
- **EXTRACT-MAX**: root 제거 + MAX-HEAPIFY → **O(lg n)**
- **INCREASE-KEY (HEAP-INCREASE-KEY)**: key를 증가시킨 뒤, 그 node를 부모와 비교하며 **위로** 이동(bubble up)시켜 max-heap property 복원 → **O(lg n)**
  - 예시 (p.34~35): idx 9의 값 4를 15로 증가 → 부모 8과 교환 → 부모 14와 교환 → 부모 16보다 작아 멈춤
    ```
    [16, 14, 10, 8, 7, 9, 3, 2, 4, 1]  (4 → 15)
    [16, 14, 10, 8, 7, 9, 3, 2, 15, 1]
    [16, 14, 10, 15, 7, 9, 3, 2, 8, 1]
    [16, 15, 10, 14, 7, 9, 3, 2, 8, 1]
    ```
- **INSERT (MAX-HEAP-INSERT)**: heap 크기를 늘리고 새 자리에 -∞를 넣은 뒤, HEAP-INCREASE-KEY로 원하는 key값까지 올림 → **O(lg n)**
  ```
  MAX-HEAP-INSERT(A, key)
  1  A.heap-size = A.heap-size + 1
  2  A[A.heap-size] = -∞
  3  HEAP-INCREASE-KEY(A, A.heap-size, key)
  ```

---

## 수업에서 다룬 섹션

1. Heapsort 개요
2. Heap (구조, heap property, 배열 표현, height)
3. MAX-HEAPIFY (예제, running time)
4. BUILD-MAX-HEAP (예제, running time: 느슨한 O(n lg n) vs tight O(n))
5. Heapsort 알고리즘 (Extract-Max 아이디어, 예제, running time)
6. Priority Queue (MAXIMUM, EXTRACT-MAX, INCREASE-KEY, INSERT)
