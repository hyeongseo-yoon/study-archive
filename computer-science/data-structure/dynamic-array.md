---
created: 2026-08-05
tags:
  - review
---

# 동적 배열 (Dynamic Array)

## 정의

런타임에 크기를 늘릴 수 있는 배열. 힙에 할당한 버퍼 포인터를 들고 있다가, 필요하면 그 버퍼를 더 큰 것으로 재할당(`realloc`)하는 방식으로 동작함. 정적 배열(`int arr[10]`)은 컴파일 타임에 크기가 고정되어 런타임에 늘릴 수 없음.

## 원리 — capacity vs size

- `size`: 실제 채워진 원소 개수
- `capacity`: 지금 할당해둔 공간(여유분 포함)

이 둘을 분리해서 추적해야 `push_back` 시 매번 재할당할지 말지 판단 가능.

```c
void push_back(ArrayList *list, int value) {
    if (list->size == list->capacity) {
        resize(list, list->capacity * 2);
    }
    list->data[list->size++] = value;
}
```

## 이유 — 왜 2배 확장인가 (amortized O(1))

- 매번 1칸씩 늘리면: 재할당이 삽입마다 발생 → 총 비용 `1+2+...+n = O(n²)`
- 2배씩 늘리면: 재할당은 capacity가 1, 2, 4, 8, ...일 때만 발생. 총 복사 비용은 등비수열 합으로 `1+2+4+...+n ≈ 2n = O(n)` → 삽입 1회당 평균(amortized) O(1)
- amortized O(1)의 의미: 개별 연산 하나는 재할당 걸리면 O(n)이 될 수 있지만, 여러 번에 걸쳐 평균 내면 O(1). worst-case per-call 보장이 아니라 누적 총비용 기준.

## 핵심 포인트 — realloc 시 포인터 무효화

- `realloc`은 공간이 부족하면 기존 블록을 그대로 못 늘리고, 새 주소에 할당 후 데이터 복사, 원본은 free해버릴 수 있음 → 반환값이 원래 포인터와 다를 수 있음.
- 그래서 반드시 반환값을 다시 대입해야 함:

```c
int *new_data = realloc(list->data, new_cap * sizeof(int));
if (new_data == NULL) { /* 실패 처리, 기존 list->data는 아직 유효 */ }
list->data = new_data;
```

- `list->data = realloc(list->data, ...)`처럼 바로 덮어쓰면, realloc 실패 시 원래 포인터를 잃어버려 메모리 누수 + 기존 데이터 접근 불가.

## 실습

`~/sandbox/data-structure/1-arraylist/`에 `push_back`, `get`, `set`, `remove_at`, `resize` 구현. valgrind로 누수 없음 확인 완료.
