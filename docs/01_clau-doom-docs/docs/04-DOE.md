# 04 — 실험계획법(DOE) 프레임워크

← [03-EXPERIMENT](03-EXPERIMENT.md) · [인덱스](../DOOM_ARENA_CLAUDE.md) · 다음 → [05-QUALITY](05-QUALITY.md)

---

## 설계 철학

기존 OFAT(One-Factor-At-A-Time) 방식에서 벗어나 산업공학의 체계적 실험계획법을 적용한다. 다변수 동시 최적화, 교호작용 검출, 실험 효율 극대화를 달성한다. 논문에서는 이 접근이 LLM 에이전트 연구에 DOE를 최초로 체계적으로 적용한 사례임을 주장한다.

## 단계적 도입 로드맵

PI(Opus)가 도입 시점을 자율적으로 판단한다.

```
Phase 0: 기초 탐색 (세대 1~2)
  ├─ OFAT으로 개별 변수 효과 크기와 분산 추정
  ├─ SPC 관리도 기선(baseline) 수립
  └─ 목적: Phase 1 DOE 설계를 위한 사전 정보 확보

Phase 1: 스크리닝 (세대 3~5)
  ├─ 부분요인배치(2^(k-p))로 유의변수 선별
  ├─ 타구치 직교배열로 강건 설계 병행
  └─ 목적: 5~8개 변수 중 핵심 2~3개 식별

Phase 2: 최적화 (세대 6~10)
  ├─ RSM(반응표면법)으로 연속 최적화
  ├─ CCD(Central Composite Design)로 최적 영역 탐색
  └─ 목적: 핵심 변수의 최적값 수렴

Phase 3: 강건 설계 (세대 11+)
  ├─ 타구치 SN비로 잡음에 강건한 전략 조합
  ├─ 확인 실험(confirmation run)으로 최적 조건 검증
  └─ 목적: 맵/적 변동에도 안정적인 성과 보장
```

## 요인 배치법 (Factorial Design)

전략 파라미터를 동시에 변경하여 주효과와 교호작용을 추정한다.

```
예시: 2³ 완전요인배치 (3개 변수, 각 2수준)

인자 A: retreat_threshold  (0.30 / 0.45)
인자 B: ammo_conservation  (low / high)
인자 C: exploration_priority (low / high)

실험 매트릭스:
  Run | A    | B    | C    | 에이전트 배정
  1   | 0.30 | low  | low  | PLAYER_001
  2   | 0.45 | low  | low  | PLAYER_002
  3   | 0.30 | high | low  | PLAYER_003
  4   | 0.45 | high | low  | PLAYER_004
  5   | 0.30 | low  | high | PLAYER_005
  6   | 0.45 | low  | high | PLAYER_006
  7   | 0.30 | high | high | PLAYER_007
  8   | 0.45 | high | high | PLAYER_008

→ Sub-agent 4개가 2 run씩 병렬 실행
→ ANOVA로 주효과(A, B, C) + 교호작용(AB, AC, BC, ABC) 분석
→ OFAT 대비: 동일 표본으로 교호작용 정보 추가 확보
```

## 부분요인배치 (Fractional Factorial Design)

변수 5개 이상일 때 실험 수를 줄인다. 고차 교호작용을 혼입(confounding)시켜 주효과와 2차 교호작용에 집중한다.

```
예시: 2^(5-2) Resolution III

5개 인자를 8회 실험으로 스크리닝:
  A: retreat_threshold
  B: ammo_conservation
  C: exploration_priority
  D: weapon_switch_speed     (= AB 생성자)
  E: enemy_priority_method   (= AC 생성자)

→ 주효과는 2차 교호작용과 혼입되므로 주의
→ 유의한 주효과 2~3개 식별 후 Phase 2(RSM)로 이관
→ 완전요인배치(32회) 대비 75% 실험 절감
```

## 타구치 방법 (Taguchi Robust Design)

잡음인자(통제 불가 변수)에 강건한 최적 조건을 찾는다.

```
제어인자 (내측 직교배열, L9):
  A: retreat_threshold    (3수준: 0.25, 0.35, 0.45)
  B: ammo_conservation    (3수준: low, medium, high)
  C: exploration_priority (3수준: low, medium, high)
  D: weapon_preference    (3수준: shotgun, chaingun, balanced)

잡음인자 (외측 직교배열, L4):
  N1: 맵 난이도 (easy / hard)
  N2: 적 밀도   (sparse / dense)

→ 9 × 4 = 36회 실험
→ 각 제어인자 조합에서 SN비(Signal-to-Noise ratio) 산출
  - 망대특성(larger-is-better): kill rate → SN = -10·log(Σ(1/y²)/n)
  - 망소특성(smaller-is-better): damage_taken → SN = -10·log(Σy²/n)
→ SN비가 높은 조합 = 맵/적 변동에 강건한 전략
→ 부모 선택 기준: 평균 kill rate → SN비 기반으로 전환
```

## 반응표면법 (RSM)

스크리닝에서 유의미한 변수를 식별한 후, 연속 공간에서 최적점을 탐색한다.

```
단계 1: 최급경사법 (Steepest Ascent)
  스크리닝 결과의 1차 모델 기울기 방향으로 탐색점 이동
  → kill rate가 증가하지 않는 지점에서 정지

단계 2: CCD (Central Composite Design)
  정지점 근방에서 2차 모델 피팅
  → 2개 인자 기준: 중심점 + 축점(α) + 요인점 = 13회 실험
  → y = β₀ + β₁x₁ + β₂x₂ + β₁₂x₁x₂ + β₁₁x₁² + β₂₂x₂²

단계 3: 정상점 분석
  ∂y/∂x₁ = 0, ∂y/∂x₂ = 0 → 최적점 (안장점이면 능선 분석)
  → 최적 파라미터 값 도출, 확인 실험으로 검증
```

## 분할구 배치법 (Split-Plot Design)

변경 난이도가 다른 변수를 효율적으로 배치한다.

```
Hard-to-change (whole-plot): 에이전트 재시작 필요한 변수
  - 맵 시드, 에이전트 기본 아키텍처

Easy-to-change (sub-plot): MD 파라미터 수정만으로 가능한 변수
  - retreat_threshold, ammo_conservation, exploration_priority

→ whole-plot 변수를 고정한 채 sub-plot 변수를 여러 수준 실행
→ 에이전트 재시작 횟수 최소화 → 실험 시간 절감
→ REML(제한최대우도법)로 분석
```

## 순차적/적응적 설계 (Sequential & Adaptive Design)

이전 실험 결과를 반영하여 다음 실험 조건을 동적으로 결정한다.

```
베이지안 최적화 통합:
  1. 초기 DOE(LHS 또는 직교배열)로 사전 데이터 확보
  2. 가우시안 프로세스(GP)로 대리 모델(surrogate) 구축
  3. 획득 함수(Expected Improvement)로 다음 탐색점 선택
  4. 반복 → 글로벌 최적에 수렴

장점: 고차원 파라미터 공간에서 RSM보다 효율적
적용 시점: Phase 2 이후, 파라미터 공간이 넓을 때
PI가 GP 대리 모델의 불확실성을 보고 추가 탐색 여부 결정
```
