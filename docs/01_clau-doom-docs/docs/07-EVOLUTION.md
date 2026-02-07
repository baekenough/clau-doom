# 07 — 진화 메커니즘

← [06-ANALYTICS](06-ANALYTICS.md) · [인덱스](../DOOM_ARENA_CLAUDE.md) · 다음 → [08-DASHBOARD](08-DASHBOARD.md)

---

## 세대 진화 흐름

```
세대 N 에이전트들 플레이 완료
  → [SPC] 관리도 갱신, 이상 신호 확인
  → [FMEA] 실패 모드 분석, RPN 갱신
  → [공정능력] Cp/Cpk 산출
  → [TOPSIS/AHP] 다기준 종합 평가로 부모 선택
    ├─ 교차: 상위 2개 에이전트의 전략 조합
    ├─ 변이: DOE 결과 기반 유의변수 방향으로 조정
    └─ 엘리트: Cpk > 1.33 최고 성과자 그대로 유지
  → [DOE] 다음 세대 실험 매트릭스 설계
  → 새 DOOM_PLAYER_{SEQ}.MD 배포
  → 세대 N+1 시작
```

## 부모 선택 기준의 진화

```
Phase 0: 평균 kill rate 단순 순위
Phase 1: 평균 × Cpk 가중 (안정성 반영)
Phase 2: TOPSIS 다기준 종합 (공격력, 생존력, 안정성, 혁신, 효율)
Phase 3: 타구치 SN비 기반 (잡음 강건성)
```

PI가 세대 전략 방향에 따라 TOPSIS 가중치를 동적으로 조정한다.

## 교차 (Crossover)

상위 2개 에이전트의 MD를 기반으로 새 에이전트 생성:
- Strategy Profile의 파라미터를 부모 간 조합
- Learned Rules는 두 부모의 합집합에서 성공률 기반 선택
- Active Experiments는 초기화

## 변이 (Mutation)

- DOE에서 유의미한 변수: 효과 방향으로 조정 (exploitation)
- 비유의 변수: 랜덤 perturbation (exploration)
- exploration 비율: 전체의 30% — PI가 동적 조정

## 엘리트 보존 (Elitism)

- Cpk > 1.33이면서 TOPSIS 상위: 그대로 다음 세대에 복사
- 엘리트 비율: 전체 에이전트의 10~20%

## 실험 채택률과 진화의 연결

실험을 많이 하고 채택률이 높은 에이전트가 다음 세대의 부모가 될 확률이 높아진다. TOPSIS의 experiment_adopt(w4=0.15) 기준으로 반영.
