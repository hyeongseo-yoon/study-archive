# Chapter 22-2: Elementary Graph Algorithms — Searching a Graph (BFS, DFS)

```dataviewjs
await dv.view("02.Area/archive/coursework/_nav")
```

*Slides from Heejin Park, Hanyang Univ. / 파일: `22_Elementary Graph Algorithms_2.pdf` (슬라이드 p.36~146)*

## 0. 개요 *(슬라이드 p.36, p.127)*
- Graphs: Graph basics, Graph representation
- Searching a graph: **Breadth-first search**, **Depth-first search** ← 이번 파일
- Applications of depth-first search: Topological sort

## 1. Searching a tree *(p.37)*
- 트리 예시: 1의 자식 2, 3 / 2의 자식 4, 5 / 3의 자식 6, 7
- 두 가지 탐색 방식: **Breadth-first search**, **Depth-first search**

## 2. Breadth-first search (BFS)

### 2.1 Distance *(p.38)*
- **Distance from u to v**: u에서 v까지의 shortest path에 있는 간선의 수.
- 예시 그래프(정점 r, s, t, u / v, w, x, y)에서 s에서 v까지의 distance는 2.

### 2.2 BFS의 정의 *(p.39~42)*
- 그래프 G = (V, E)와 **source vertex s**가 주어지면, G의 간선을 탐색해서 s에서 reachable한 모든 정점을 "discover"한다.
- 정점을 source로부터의 **distance가 증가하는 순서**로 discover한다. distance 1인 정점을 모두 찾고, 그다음 2, …
- 예시 진행 *(p.39~42)*: s = 0 → r, w = 1 → v, t, x = 2 → u, y = 3

### 2.3 BFS가 계산하는 것 *(p.43)*
- 각 정점의 source로부터의 **distance**: 예) u.d = 3
- 각 정점의 **predecessor**: 예) u.π = t

### 2.4 Predecessor subgraph와 breadth-first tree *(p.44~45)*
- G의 **predecessor subgraph** Gπ = (Vπ, Eπ) *(p.44)*
    - Vπ = {v ∈ V | v.π ≠ NIL} ∪ {s}
    - Eπ = {(v.π, v) | v ∈ Vπ − {s}}
- Gπ는 **breadth-first tree**다 *(p.45)*
    - connected이고 |Eπ| = |Vπ| − 1 이기 때문 (22-1의 tree 동치 조건).
    - Eπ의 간선들을 **tree edges**라고 부른다.

### 2.5 BFS 의사코드 *(p.46)*
```
BFS(G, s)
1  for each vertex u ∈ G.V − {s}
2      u.color = WHITE
3      u.d = ∞
4      u.π = NIL
5  s.color = GRAY
6  s.d = 0
7  s.π = NIL
8  Q = Ø
9  ENQUEUE(Q, s)
10 while Q ≠ Ø
11     u = DEQUEUE(Q)
12     for each v ∈ G.Adj[u]
13         if v.color == WHITE
14             v.color = GRAY
15             v.d = u.d + 1
16             v.π = u
17             ENQUEUE(Q, v)
18     u.color = BLACK
```

### 2.6 정점의 색 *(p.47)*
- **white**: not discovered (아직 Q에 들어간 적 없음)
- **gray**: discovered (Q 안에 있음)
- **black**: finished (Q에서 나옴)

### 2.7 BFS 예제 진행 *(p.47~123)*
- 예시 그래프 (undirected) 인접 리스트 *(p.47)*

```
r: s → v
s: r → w
t: u → w → x
u: t → x → y
v: r
w: s → t → x
x: t → u → w → y
y: u → x
```

- 진행 (각 단계 끝의 Q 상태, 숫자는 d 값)

| 단계 | DEQUEUE | 새로 discover (d, π) | Q | 슬라이드 |
|---|---|---|---|---|
| 초기화 | — | s (0, NIL) | s(0) | p.47~49 |
| 1 | s | r (1, s), w (1, s) | r(1) w(1) | p.50~66 |
| 2 | r | v (2, r) | w(1) v(2) | p.67~79 |
| 3 | w | t (2, w), x (2, w) | v(2) t(2) x(2) | p.80~98 |
| 4 | v | 없음 (r는 이미 discover됨) | t(2) x(2) | p.99~102 |
| 5 | t | u (3, t) | x(2) u(3) | p.103~109 |
| 6 | x | y (3, x) | u(3) y(3) | p.110~118 |
| 7 | u | 없음 | y(3) | p.119~121 |
| 8 | y | 없음 | Ø | p.122~123 |

- 최종 결과: s = 0, r = 1, w = 1, v = 2, t = 2, x = 2, u = 3, y = 3
- Q에 들어가는 d 값은 항상 비감소 순서 (0 → 1 1 → 2 2 2 → 3 3).

### 2.8 Running time *(p.124~125)*
- 의사코드 구간별 *(p.124)*
    - line 1~9 **Initialization**: Θ(V)
    - line 10~18 **Graph Exploration**: O(V + E)
- *(p.125)*
    - Initialization: Θ(V)
    - Exploring the graph: O(V + E)
        - 각 정점은 최대 한 번 examine된다.
        - 각 간선은 최대 두 번 explore된다 (undirected에서 양 끝 정점의 인접 리스트에 한 번씩).
    - **Overall: O(V + E)**

### 2.9 Self-study *(p.126)*
- Exercise 22.2-4 (2판 22.2-3): adjacency matrix 표현일 때 BFS의 running time
- Exercise 22.2-6 (2판 22.2-5): 불가능한 breadth-first tree
- Exercise 22.2-7 (2판 22.2-6): Rivalry

## 3. Depth-first search (DFS)

### 3.1 정점의 색 *(p.128)*
- 모든 정점은 처음에 **white** (not discovered).
- **discover**되면 **gray**가 된다.
- **finish**되면, 즉 인접 리스트를 전부 다 examine하면 **black**이 된다.
- 예시 그래프 (directed): u→v, u→x, v→y, w→y, w→z, x→v, y→x, z→z (self-loop)

### 3.2 Timestamps *(p.129)*
- 각 정점 v는 timestamp 두 개를 가진다.
    - **v.d**: discovery time (gray가 될 때)
    - **v.f**: finishing time (black이 될 때)
- 예) u = 1/, v = 2/, y = 3/, x = 4/5 (d/f 표기)

### 3.3 DFS 예제 진행 *(p.130~133)*
| 그림 | 상태 |
|---|---|
| (a) | u discover: u = 1/ |
| (b) | u→v, v = 2/ |
| (c) | v→y, y = 3/ |
| (d) | y→x, x = 4/ |
| (e) | x→v 확인 (v는 gray) |
| (f) | x finish: x = 4/5 |
| (g) | y finish: y = 3/6 |
| (h) | v finish: v = 2/7 |
| (i) | u→x 확인 (x는 black) |
| (j) | u finish: u = 1/8 |
| (k) | 새 시작점 w discover: w = 9/ |
| (l) | w→y 확인 (y는 black) |
| (m) | w→z, z = 10/ |
| (n) | z→z 확인 (self-loop, z는 gray) |
| (o) | z finish: z = 10/11 |
| (p) | w finish: w = 9/12 |

- 최종: u 1/8, v 2/7, y 3/6, x 4/5, w 9/12, z 10/11

### 3.4 DFS 의사코드 *(p.134)*
```
DFS(G)
1  for each vertex u ∈ G.V
2      u.color = WHITE
3      u.π = NIL
4  time = 0
5  for each vertex u ∈ G.V
6      if u.color == WHITE
7          DFS-VISIT(G, u)

DFS-VISIT(G, u)
1  time = time + 1
2  u.d = time
3  u.color = GRAY
4  for each v ∈ G.Adj[u]
5      if v.color == WHITE
6          v.π = u
7          DFS-VISIT(G, v)
8  u.color = BLACK
9  time = time + 1
10 u.f = time
```

### 3.5 Running time 구간별 *(p.135)*
- DFS line 1~3 **Initialization**: Θ(V)
- DFS line 4~7 **Graph Exploration**: Θ(V + E)
- **DFS-VISIT** 전체: Θ(E) (모든 인접 리스트 길이의 합)

### 3.6 Depth-first forest *(p.136)*
- DFS의 predecessor subgraph는 **depth-first forest**다.
- 예시: 트리 u → v → y → x, 트리 w → z (두 개의 트리로 된 forest)

### 3.7 Parenthesis theorem *(p.137)*
- 각 정점의 **gray interval** [v.d, v.f]에 대해
    - **Inclusion**: ancestor의 interval은 descendant의 interval을 포함한다.
    - **Disjoint**: 그 외에는 서로 겹치지 않는다.
- 예시 (시간축 1~12)
    - u [1, 8] ⊃ v [2, 7] ⊃ y [3, 6] ⊃ x [4, 5]
    - w [9, 12] ⊃ z [10, 11]
    - u 쪽 interval과 w 쪽 interval은 disjoint

### 3.8 Classification of edges *(p.138~139)*
- 예시 그래프의 분류 *(p.138)*: Tree edges (u→v, v→y, y→x, w→z), **B** x→v, **B** z→z, **F** u→x, **C** w→y
- 정의 *(p.139)*
    - **Tree edges**: depth-first tree에 속한 간선
    - **Back edges** (cycle): descendant에서 ancestor로 가는 간선, 또는 self-loop
    - **Forward edges**: ancestor에서 descendant로 가는 non-tree 간선
    - **Cross edges**: 나머지 전부. 한 정점이 다른 정점의 ancestor가 아닌 두 정점 사이의 간선

### 3.9 DFS 알고리즘으로 간선 분류하기 *(p.140~144)*
- 간선 (u, v)를 **처음 explore할 때 도달한 v의 색**으로 분류한다 *(p.140)*
    - **white** → tree edge
    - **gray** → back edge
    - **black** → forward edge 또는 cross edge
- Forward와 cross는 u와 v의 **gray interval 포함 관계**로 구분한다 *(p.140)*
    - u의 interval이 v의 interval을 포함 (u.d < v.d) → forward
    - disjoint (v.d < u.d) → cross
- 예시 *(p.141)*: interval 그림과 분류된 그래프를 함께 보면
    - x→v: v는 gray → back
    - u→x: x는 black, [1,8] ⊃ [4,5] → forward
    - w→y: y는 black, [9,12]와 [3,6] disjoint → cross
    - z→z: self-loop → back
- 예제 진행에 분류 표시 *(p.142~144)*: (e) x→v에서 B, (i) u→x에서 F, (l) w→y에서 C, (n) z→z에서 B

### 3.10 Undirected graph의 DFS와 running time *(p.145)*
- Undirected graph를 DFS하면 모든 간선은 **tree edge 또는 back edge** 중 하나다.
    - Forward edge? Cross edge? → 생기지 않는다 (왜 그런지 생각해볼 것)
- **Running time: Θ(V + E)**

### 3.11 Self-study *(p.146)*
- Exercise 22.3-5 (2판 22.3-4): Edge classification
- Problem 22-2 a-d: Articulation points
