# 📚 복습 대시보드

## 🔴 미완료 대기 개수
```dataview
TABLE WITHOUT ID length(rows) AS "대기 중"
FROM #incomplete
GROUP BY "전체"
```

## 1️⃣ 이번 주 복습 (작성 3주 이내)
```dataview
TABLE created AS "작성일"
FROM #review
WHERE created >= date(today) - dur(3 weeks)
SORT created ASC
```

## 2️⃣ 졸업 심사 (3~4주차, 마지막 복습 → #completed / #incomplete 판정)
```dataview
TABLE created AS "작성일"
FROM #review
WHERE created < date(today) - dur(3 weeks) AND created >= date(today) - dur(4 weeks)
SORT created ASC
```

## ⚠️ 졸업 놓친 노트 (4주 초과 #review — 뒤늦게라도 심사)
```dataview
TABLE created AS "작성일", (date(today) - created).day AS "묵힌 일수"
FROM #review
WHERE created < date(today) - dur(4 weeks)
SORT created ASC
```

## 3️⃣ 대기 큐 (#incomplete, 묵힌 순)
```dataview
TABLE created AS "작성일", (date(today) - created).day AS "묵힌 일수"
FROM #incomplete
SORT created ASC
```

## 🏆 학습완료 (#completed)
```dataview
TABLE created AS "작성일"
FROM #completed
SORT file.mtime DESC
```

---

# 📈 활동 통계

## 📅 이번 달 작성한 노트
```dataview
TABLE created AS "작성일"
FROM #review or #incomplete or #completed
WHERE created.year = date(today).year AND created.month = date(today).month
SORT created DESC
```

## 🗓️ 월간 생성 횟수
```dataview
TABLE WITHOUT ID key AS "월", length(rows) AS "작성 수"
FROM #review or #incomplete or #completed
WHERE created
GROUP BY dateformat(created, "yyyy-MM")
SORT key DESC
```

## 📆 주간 생성 횟수 (ISO week)
```dataview
TABLE WITHOUT ID key AS "주", length(rows) AS "작성 수"
FROM #review or #incomplete or #completed
WHERE created
GROUP BY dateformat(created, "kkkk-'W'WW")
SORT key DESC
```
