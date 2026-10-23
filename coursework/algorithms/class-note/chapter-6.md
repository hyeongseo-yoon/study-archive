# Chapter 6: Heapsort (수업노트)

```dataviewjs
await dv.view("02.Area/study-archive/coursework/_nav")
```

**수업 목표**: heap 구조를 이해하고, MAX-HEAPIFY / BUILD-MAX-HEAP / HEAPSORT가 어떻게 동작하고 왜 그 시간복잡도가 나오는지 설명할 수 있게 된다.

---

## 0. 선수 지식 정리

- **internal node**: 자식이 하나라도 있는 node. root도 자식이 있으면 internal이다.
- **depth**: root에서 그 node까지 내려오는 edge 수. root가 0.
- **height**: 그 node에서 가장 먼 leaf까지 내려가는 edge 수. leaf가 0.
- **complete binary tree** (슬라이드 p.4): 모든 leaf가 같은 depth고 internal node가 전부 자식 2개인 꽉 찬 트리. "마지막 층만 빼고 가득 차고 마지막 층은 왼쪽부터 채운" 모양은 **nearly complete**이고, heap이 이 모양이다.
- **in-place**: 입력 배열 바깥에 상수 개(O(1))의 원소만 추가로 쓴다.

---

## 1. Heapsort 개요 *(p.3)*

Heapsort는 두 정렬의 장점을 합친 정렬이다.
- merge sort처럼 시간이 **O(n lg n)** (insertion sort는 O(n²))
- insertion sort처럼 **in-place** (merge sort는 병합용 추가 배열 필요)

이를 가능하게 하는 도구가 **heap**이다.

---

## 2. Heap *(p.4~11)*

**heap**: nearly complete binary tree 모양이면서 모든 node가 부모-자식 간 크기 규칙(heap property)을 지키는 자료구조.

### Heap property *(p.5~7)*

- **max-heap property**: 모든 node i에 대해 A[PARENT(i)] ≥ A[i]
- **min-heap property**: A[PARENT(i)] ≤ A[i]

max-heap에서는 부모 ≥ 자식이 위로 이어지므로 **root가 전체 최댓값**이고, 모든 subtree의 root도 그 subtree 안의 최댓값이다. Heapsort는 max-heap을 쓴다.

이진 탐색 트리와 달리 **형제 사이의 크기 순서는 규칙이 없다.** 규칙은 부모-자식 사이에만 있다.

```
                 16 [1]
             /           \
        14 [2]            10 [3]
        /    \            /    \
     8 [4]   7 [5]     9 [6]   3 [7]
     /  \              /
  2 [8]  4 [9]      1 [10]

배열 A:  인덱스  1   2   3  4  5  6  7  8  9  10
         값     16  14  10  8  7  9  3  2  4  1
```

### 배열 표현 *(p.8~9)*

heap은 포인터 없이 배열 하나에 level order(위층부터 왼쪽→오른쪽)로 저장한다. 인덱스는 1부터 시작.

```
PARENT(i)   return ⌊i/2⌋
LEFT(i)     return 2i
RIGHT(i)    return 2i+1
```

- 파라미터 i: node의 배열 인덱스. 반환값: 해당 관계 node의 인덱스. ⌊ ⌋는 floor.
- 예: i=3(값 10) → LEFT=6(값 9), RIGHT=7(값 3), PARENT=1(값 16)
- **주의**: 공식은 항상 숫자를 내놓지만 그 인덱스가 heap 안에 있다는 보장은 없다. 예를 들어 i=5(값 7)의 PARENT=2, LEFT=10(값 1), RIGHT=11인데, 원소가 10개이므로 **11은 존재하지 않는다**. 즉 node 5는 왼쪽 자식만 있다.
- 일반화: **2i > n이면 leaf**, 2i = n이면 왼쪽 자식만 있다. 그래서 `A.heap-size`와 비교해 자식이 실제로 있는지 확인해야 한다.
- **A.length**(배열 전체 길이)와 **A.heap-size**(heap으로 쓰는 구간 크기)는 다를 수 있고, 이 차이가 heapsort에서 핵심으로 쓰인다.

### Height *(p.10~11)*

- heap의 height = root의 height
- 층마다 node 수가 2배(1, 2, 4, 8, …)로 늘어나므로 n개 원소 heap의 height는 **⌊lg n⌋ = Θ(lg n)**
- 예: 원소 16개 → 층이 1+2+4+8+1 = 5층, depth 0~4, height 4 (마지막 층에 node가 하나뿐이어도 height는 한 칸 오른다)
- heap 연산은 root-leaf를 잇는 한 줄만 오르내리므로 시간이 height에 비례해 **O(lg n)**

---

## 3. MAX-HEAPIFY *(p.12~14)*

**MAX-HEAPIFY**: 자식 쪽 두 subtree는 이미 max-heap인데 node i만 규칙을 깨고 있을 때, i의 값을 아래로 "float down"시켜 i를 root로 하는 subtree를 max-heap으로 복원하는 연산.

### 예제 *(p.12~13)*

배열 [16, 4, 10, 14, 7, 9, 3, 2, 8, 1], 인덱스 2(값 4)만 위반 (두 subtree는 max-heap).

```
                 16 [1]
             /           \
        4 [2]  ←문제       10 [3]
        /    \            /    \
    14 [4]   7 [5]     9 [6]   3 [7]
     /  \      /
  2 [8] 8 [9] 1 [10]
```

- **큰 쪽 자식과 교환**해야 한다. 작은 쪽과 바꾸면 올라온 값이 다른 큰 자식보다 작아져 새 위반이 생긴다.
- 값이 내려간 자리에서 다시 확인해야 한다 (교환 후 그 아래 subtree가 다시 깨질 수 있음).

```
1단계: 4 ↔ 14 (자식 14, 7 중 큰 쪽)          2단계: 4 ↔ 8 (자식 2, 8 중 큰 쪽)

            16                                      16
         /      \                                /      \
      14         10                           14         10
     /   \      /   \                        /   \      /   \
    4     7    9     3                      8     7    9     3
   / \   /                                 / \   /
  2   8 1                                 2   4 1

3단계: 4는 인덱스 9의 leaf → 자식 없음 → 종료
최종 배열: [16, 14, 10, 8, 7, 9, 3, 2, 4, 1]
```

### Running time *(p.14)*

- 한 층에서 하는 일(자신과 두 자식 비교, 교환)은 Θ(1)
- 값이 내려갈 수 있는 최대 층 수는 subtree의 height h = ⌊lg n⌋
- 따라서 Θ(1) × h = **O(h) = O(lg n)**

*(참고: 수업 중 내가 교재 기준으로 의사코드를 보여줬지만 슬라이드에는 MAX-HEAPIFY 의사코드가 없다. 슬라이드는 동작 설명, 예제 그림, running time만 제시한다.)*

---

## 4. BUILD-MAX-HEAP *(p.15~23)*

임의의 배열을 통째로 max-heap으로 만드는 연산. MAX-HEAPIFY는 두 subtree가 heap일 때만 쓸 수 있다는 제약을 어떻게 만족시키는가가 핵심.

```
BUILD-MAX-HEAP(A)
1. A.heap-size = A.length
2. for i = ⌊A.length / 2⌋ downto 1
3.     MAX-HEAPIFY(A, i)
```

- **A.length는 배열의 원소 개수**다 (예제에서 10). ⌊10/2⌋ = 5가 자식이 있는 마지막 node. leaf는 6~10번 (2i > 10).
- leaf는 이미 1-원소 max-heap이라 MAX-HEAPIFY를 불러도 아무 일도 없다. 호출해야 하는 건 leaf가 아닌 **1~5번 전부**다 (3, 4, 5만이 아님).
- **거꾸로(5 → 1) 호출하는 이유**: 낮은 node부터 처리해야 i번을 처리할 때 그 아래 subtree들이 이미 max-heap이라서 MAX-HEAPIFY의 전제 조건이 매번 성립한다. 1 → 5 순서면 root를 처리할 때 아래가 heap이 아니라 제대로 자리를 못 찾는다.

### 예제 *(p.16~19)*

입력 [4, 1, 3, 2, 16, 9, 10, 14, 8, 7]

```
                  4 [1]
             /           \
         1 [2]            3 [3]
        /     \          /     \
     2 [4]   16 [5]   9 [6]   10 [7]
     /  \      /
 14 [8] 8 [9] 7 [10]

i=5 (16): 자식 7 → 이미 OK, 변화 없음
i=4 (2):  자식 14, 8 → 14와 교환  → [4, 1, 3, 14, 16, 9, 10, 2, 8, 7]
i=3 (3):  자식 9, 10 → 10과 교환  → [4, 1, 10, 14, 16, 9, 3, 2, 8, 7]
```

i=2 처리 전후 (1이 16과 교환해 5번 자리로 내려간 뒤, 자식 7과 다시 교환 — 값이 여러 층을 연속해서 내려갈 수도 있다):

```
i=2 처리 전                           i=2 처리 후

         4                                     4
       /   \                                 /   \
     1      10                             16     10
    / \     / \                           /  \    / \
  14   16  9   3                        14    7  9   3
  / \  /                                / \   /
 2  8 7                                2  8  1

i=2 후: [4, 16, 10, 14, 7, 9, 3, 2, 8, 1]
i=1 (4): 16과 교환 → idx2에서 14와 교환 → idx4에서 8과 교환
최종:   [16, 14, 10, 8, 7, 9, 3, 2, 4, 1]   ← max-heap 완성
```

### Running time *(p.20~23)*

**느슨한 분석**: 호출 Θ(n)번 × 한 번 O(lg n) = O(n lg n). 틀린 건 아니지만 너무 느슨하다.

**tighter bound**: 비싼 호출(위쪽 node)은 소수고, 싼 호출(아래쪽 node)이 다수다.

```
height 3:  1개 (root)       → 최대 3번 내려감
height 2:  1개              → 최대 2번
height 1:  3개              → 최대 1번
height 0:  5개 (leaf)       → 0번 (호출도 안 함)
```

- height가 h인 node는 최대 ⌈n/2^(h+1)⌉개, MAX-HEAPIFY 비용은 O(h)
- 전체 = Σ(h=0~⌊lg n⌋) ⌈n/2^(h+1)⌉·O(h) = O(n · Σ h/2^h)
- 슬라이드: Σ(h=0~∞) h/2^h = **2** (상수로 수렴)
- 따라서 **BUILD-MAX-HEAP = O(n)**

수렴하는 이유: height가 한 칸 오를 때 node 수는 **절반**으로 줄고 비용은 h만큼 **선형으로** 늘어서, 줄어드는 속도가 이긴다. "위쪽 node가 적어서 O(n)"이 아니라 **전체 합**이 n × 상수가 되는 것이다.

---

## 5. Heapsort 알고리즘 *(p.24~31)*

### Extract-Max 아이디어 *(p.24~25)*

max-heap에서 최댓값을 꺼내 정렬 영역으로 보내는 절차:
1. root(최댓값)를 마지막 원소와 교환 — 최댓값은 오름차순 정렬의 맨 끝 자리 몫
2. heap-size를 1 줄임 — 16은 제자리를 찾았으므로 heap에서 제외 (배열에서 지우는 게 아니라 heap-size만 줄임)
3. 새 root에 MAX-HEAPIFY(A, 1) — root만 바뀌었고 두 subtree는 여전히 max-heap이라 전제 조건이 성립

```
1) 16 ↔ 1 교환, heap-size 10 → 9
   [1, 14, 10, 8, 7, 9, 3, 2, 4 | 16]        (| 오른쪽은 heap 밖, 정렬 끝난 영역)

2) MAX-HEAPIFY(A, 1): 1 ↔ 14, 1 ↔ 8, 1 ↔ 4 순으로 내려감
   [14, 8, 10, 4, 7, 9, 3, 2, 1 | 16]

            14
         /      \
        8        10
       / \      /  \
      4   7    9    3          정렬 끝: 16
     / \
    2   1
```

### HEAPSORT *(p.26~30)*

```
HEAPSORT(A)
1  BUILD-MAX-HEAP(A)
2  for i = A.length downto 2
3      exchange A[1] with A[i]
4      A.heap-size = A.heap-size - 1
5      MAX-HEAPIFY(A, 1)
```

**HEAPSORT**: max-heap을 만든 뒤 root(현재 최댓값)를 heap 끝으로 보내고 heap 크기를 줄이는 과정을 반복해 정렬하는 알고리즘. 배열 안에서 끝나므로 in-place.

- 반복문이 i=2까지만 도는 이유: 원소가 하나 남으면 그게 남은 중 최솟값이고 이미 맨 앞 제자리라서 교환할 필요가 없다.

### 예제 *(p.27~29)*

```
i=10: [14, 8, 10, 4, 7, 9, 3, 2, 1 | 16]
i=9:  [10, 8, 9, 4, 7, 1, 3, 2 | 14, 16]
i=8:  [9, 8, 3, 4, 7, 1, 2 | 10, 14, 16]
 ...  (i=2까지 반복)
최종: [1, 2, 3, 4, 7, 8, 9, 10, 14, 16]
```

### Running time *(p.31)*

- BUILD-MAX-HEAP: O(n)
- 반복 n-1번 × MAX-HEAPIFY O(lg n) = O(n lg n)
- 전체는 두 단계의 **합**이므로 큰 쪽이 결정 → **O(n lg n)**
- BUILD-MAX-HEAP을 정교하게 분석해 O(n)을 얻은 건 그 부분만으로는 의미 있지만 heapsort 전체 big-O는 바뀌지 않는다. 느슨한 O(n lg n)이었어도 O(n lg n) + O(n lg n) = O(n lg n)이다. (O(n²)이 되려면 한 단계가 n번 반복되고 각 반복이 n번을 도는 식의 **중첩**이어야 한다. 합이 곱이 되는 게 아님)
- 반복문 부분은 실제로 n lg n이 걸린다. root로 올라온 값이 원래 맨 끝에 있던 작은 값이라 보통 아래로 한참 내려가기 때문이다.

### 면접식 한 번에 설명

**Heap**은 nearly complete binary tree 모양에서 모든 node가 부모 ≥ 자식(max-heap)을 지키는 구조라서 root가 항상 최댓값이고, 배열 하나로 저장된다(PARENT = ⌊i/2⌋, LEFT = 2i, RIGHT = 2i+1). **Heapsort**는 먼저 BUILD-MAX-HEAP으로 배열 전체를 max-heap으로 만든 뒤, root를 heap의 마지막 원소와 교환하고 heap-size를 1 줄여 그 값을 정렬 영역에 편입시키고, MAX-HEAPIFY로 root를 복원하는 걸 반복한다. 전부 한 배열 안에서 일어나므로 in-place다. 시간은 BUILD-MAX-HEAP이 O(n)(height가 작은 node가 압도적으로 많음), 반복문이 n-1번 × O(lg n)이라 합쳐서 **O(n lg n)**이다.

---

## 6. Priority Queue *(p.32~37)*

**priority queue**: 각 원소가 key라는 값을 갖는 집합 S를 관리하면서 key가 가장 큰(또는 작은) 원소를 빠르게 꺼낼 수 있게 해주는 자료구조. heap으로 구현한다.

**max-priority queue**의 연산:
- `INSERT(S, x)`: 원소 x를 S에 삽입
- `MAXIMUM(S)`: key가 가장 큰 원소 반환 (제거하지 않음)
- `EXTRACT-MAX(S)`: key가 가장 큰 원소를 제거하며 반환
- `INCREASE-KEY(S, x, k)`: 원소 x의 key를 새 값 k로 증가

### 각 연산의 구현과 running time *(p.33~37)*

- **MAXIMUM**: root를 읽기만 하면 됨 → **O(1)**
- **EXTRACT-MAX**: heapsort의 한 단계와 같음. root와 마지막 원소 교환, heap-size 감소, MAX-HEAPIFY(A, 1) → **O(lg n)**
- **INCREASE-KEY (HEAP-INCREASE-KEY)**: key를 올린 뒤 부모와 비교하며 **위로(bubble up)** 올림 → **O(lg n)**
  - 증가시키면 깨지는 건 **부모와의 관계**다 (자식과의 관계는 문제없음). MAX-HEAPIFY가 위→아래라면 이건 아래→위, 반대 방향.
  - 예 (p.34~35): 인덱스 9의 값 4를 15로 증가. 부모 8(idx4)과 교환 → 부모 14(idx2)와 교환 → 부모 16이 더 크므로 멈춤.

```
시작:         [16, 14, 10,  8,  7, 9, 3, 2, 15, 1]   (인덱스 9: 4 → 15)
15 ↔ 8:       [16, 14, 10, 15,  7, 9, 3, 2,  8, 1]
15 ↔ 14:      [16, 15, 10, 14,  7, 9, 3, 2,  8, 1]
15 vs 16:     16이 더 큼 → 멈춤 (max-heap 복원)

             16                              16
          /      \                        /      \
       14         10                   15         10
      /  \       /  \                 /  \       /  \
     8    7     9    3     →        14    7     9    3
    / \  /                          / \  /
   2  15 1                         2   8 1
```

- **INSERT (MAX-HEAP-INSERT)**: heap 크기를 늘리고 새 자리에 -∞를 넣은 뒤 HEAP-INCREASE-KEY로 key까지 올림 → **O(lg n)**

```
MAX-HEAP-INSERT(A, key)
1  A.heap-size = A.heap-size + 1
2  A[A.heap-size] = -∞
3  HEAP-INCREASE-KEY(A, A.heap-size, key)
```

  - -∞는 어떤 값보다 작아서 부모 ≥ 자식이 항상 성립하므로 추가 직후에도 heap이 멀쩡하다. "-∞에서 key로 증가"로 바꿔 INCREASE-KEY를 그대로 재활용하는 것이다.
  - O(lg n)인 이유: 깨진 곳은 새 node 하나뿐이고, 그 node가 맨 끝 leaf에서 부모를 따라 위로 한 줄을 오른다. 한 층의 일은 Θ(1)이고 최대 층 수는 height ⌊lg n⌋이므로 Θ(1) × lg n = O(lg n). (BUILD-MAX-HEAP처럼 전체를 다시 만드는 것이 아님)

| 연산 | 시간 |
|---|---|
| MAXIMUM | O(1) |
| EXTRACT-MAX | O(lg n) |
| INCREASE-KEY | O(lg n) |
| INSERT | O(lg n) |

---

## 수업에서 다룬 섹션

1. Heapsort 개요
2. Heap (구조, heap property, 배열 표현, height)
3. MAX-HEAPIFY (예제, running time)
4. BUILD-MAX-HEAP (예제, running time: 느슨한 O(n lg n) vs tight O(n))
5. Heapsort 알고리즘 (Extract-Max 아이디어, 예제, running time)
6. Priority Queue (MAXIMUM, EXTRACT-MAX, INCREASE-KEY, INSERT)
