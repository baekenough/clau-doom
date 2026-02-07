# 02 — 에이전트

← [01-ARCHITECTURE](01-ARCHITECTURE.md) · [인덱스](../DOOM_ARENA_CLAUDE.md) · 다음 → [03-EXPERIMENT](03-EXPERIMENT.md)

---

## 에이전트 정의: DOOM_PLAYER_{SEQ}.MD

각 에이전트의 DNA이자 프롬프트:

```markdown
# DOOM_PLAYER_007.MD

## Identity
- Generation: 3
- Parent: PLAYER_003 (Kill Rate 72%)
- Mutation: aggressive_push 전략 강화

## Strategy Profile
- play_style: aggressive
- retreat_threshold: health < 40%
- ammo_conservation: low
- exploration_priority: medium

## Learned Rules
- 좁은 복도에서는 shotgun 우선
- 체력 30% 이하시 아이템 탐색 모드 전환
- imp 2마리 이상 동시 출현 시 후퇴 후 각개격파

## Active Experiments
### EXP-007-012
- hypothesis: "retreat_threshold를 40%로 올리면 생존시간 20% 증가"
- variable: retreat_threshold
- control: 0.30 / treatment: 0.40
- min_episodes: 30
- status: running

## Performance History
- gen1_avg_kill: 3.2
- gen2_avg_kill: 5.8
- gen3_avg_kill: 7.1
```

## 의사결정 계층

### 실시간 (< 100ms) — LLM 호출 없음

```
게임 틱
  → Rust: 상황 피처 추출 (~2ms)
  → Rust: 로컬 룰 매칭 (MD 하드코딩 규칙)
    ├─ 매칭됨 → 즉시 액션
    └─ 매칭 안됨 ↓
  → OpenSearch kNN 검색 (~20ms)
  → Rust: Top-K 결과 스코어링 + 액션 선택 (~5ms)
  → 액션 실행
```

실시간 판단은 전적으로 RAG 검색 + Rust 룰엔진이 담당한다.

### 비동기 정제 (수백ms, 백그라운드)

```
매 N틱 스냅샷 → NATS 큐
  → Ollama (경량 LLM)
    ├─ 상황 분류 태그 보강
    ├─ 놓친 패턴 감지
    └─ OpenSearch 문서 품질 개선
  → 결과를 에이전트 로컬 캐시에 push
```

### 에피소드 간 학습 (수초~수분)

```
에피소드 종료
  → Claude Code
    ├─ 전체 에피소드 회고
    ├─ DuckDB 집계 분석
    ├─ 새 전략 문서 생성 → OpenSearch 색인
    └─ DOOM_PLAYER_{SEQ}.MD 업데이트
```

### 세대 진화 (수분)

```
세대 종료
  → Claude Code (Opus 지시에 따라)
    ├─ 상위 에이전트 MD 교차/변이
    ├─ 전략 풀 정리 (저성과 문서 퇴출)
    └─ 다음 세대 MD 생성
```

## RAG 파이프라인

### 계층적 검색

```
Level 0 — 로컬 룩업 (< 1ms)
  MD에 하드코딩된 규칙, Rust에서 바로 처리

Level 1 — DuckDB 캐시 (< 10ms)
  자기 경험에서 SQL 검색

Level 2 — OpenSearch kNN (< 100ms)
  전체 에이전트 풀의 지식에서 벡터 검색

Level 3 — Claude Code CLI (수초, 비동기)
  프로젝트 컨텍스트를 아는 상태에서 추론
  MD 파일 직접 읽기/수정 가능
```

### 전략 문서 구조

```json
{
  "doc_id": "tactic_007_042",
  "agent_id": "PLAYER_007",
  "generation": 3,
  "situation_embedding": [0.12, -0.34, ...],
  "situation_tags": ["narrow_corridor", "multi_enemy", "low_health"],
  "decision": {
    "tactic": "retreat_and_funnel",
    "weapon": "shotgun"
  },
  "quality": {
    "success_rate": 0.84,
    "sample_size": 47,
    "last_validated": "2026-02-07T...",
    "confidence_tier": "high"
  }
}
```

### 문서 생명주기

생성(LLM 제안) → 검증(실전 사용, 성공률 집계) → 승격/퇴화(메타 변화 감지)

### Rust 스코어링

kNN Top-K 결과에 대해 유사도(0.4) + 신뢰도(0.4) + 최신성(0.2) 가중 스코어링. 신뢰도는 윌슨 스코어 구간 하한을 적용하여 표본 적은 문서를 보수적으로 평가.
