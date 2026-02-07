# S2-04: Agent Teams 워크플로 설계

> **세션**: S2 (연구 설계 보강)
> **우선순위**: 🟠 high
> **의존성**: 없음
> **상태**: ⬜ 미시작

---

## 목적

4세션 × Agent Teams 병렬 × Sub-agents 구조를 연구 프로세스에 공식 반영한다. Claude Code Agent Teams의 실험적 기능 특성을 고려한 운용 규칙, 파일 소유권, 폴백 전략을 확정한다.

---

## 세션-팀-서브 역할 매핑

### 연구 프로세스에서의 위치

```
Opus PI (Cowork)
  │
  │  EXPERIMENT_ORDER.MD
  ▼
Claude Code (4세션 병렬)
  ├─ Session 1: Lead + Sub-agents → 문헌 수집
  ├─ Session 2: Lead + Sub-agents → 연구 설계 보강
  ├─ Session 3: Lead + Sub-agents → 기술 검증
  └─ Session 4: Lead + Sub-agents → 문서 통합
  │
  │  EXPERIMENT_REPORT.MD
  ▼
Opus PI (Cowork)
```

### 세션별 역할

| 세션 | Lead 역할 | Sub-agent 역할 | 모델 권장 |
|------|----------|---------------|----------|
| S1 | 문헌 품질 필터링, 중복 제거 | 개별 카테고리 서치 | Lead: Opus, Sub: Sonnet |
| S2 | 설계 일관성 검수 | 개별 설계 항목 작성 | Lead: Opus, Sub: Sonnet |
| S3 | PoC 총괄, 벤치마크 설계 | 개별 PoC 구현/테스트 | Lead: Opus, Sub: Opus |
| S4 | 문서 머지 최종 검수 | 개별 섹션 업데이트 | Lead: Opus, Sub: Sonnet |

S3만 Sub-agent에도 Opus 권장 — 코드 구현/디버깅 품질이 중요하므로.

---

## 파일 소유권 규칙

### 원칙: 하나의 파일을 동시에 두 팀원이 수정하지 않는다

```
volumes/agents/active/DOOM_PLAYER_{SEQ}.MD  → 해당 SEQ 담당 팀원만
volumes/data/player-{SEQ}/                  → 해당 SEQ 담당 팀원만
volumes/research/reports/                   → Lead만 최종 작성
volumes/research/orders/                    → Opus PI만 (읽기 전용)
```

### 세션 간 파일 충돌 방지

| 파일 | S1 | S2 | S3 | S4 |
|------|----|----|----|----|
| DOOM_ARENA_DESIGN.md | 읽기 | 읽기 | 읽기 | **쓰기** |
| DOOM_ARENA_CLAUDE.md | 읽기 | 읽기 | 읽기 | **쓰기** |
| sessions/S1-*/*.md | **쓰기** | — | — | 읽기 |
| sessions/S2-*/*.md | — | **쓰기** | — | 읽기 |
| sessions/S3-*/*.md | — | — | **쓰기** | 읽기 |
| sessions/S4-*/*.md | — | — | — | **쓰기** |

S4는 다른 세션 결과를 읽기만 하고 최종 통합 문서만 쓴다.

---

## CLAUDE.md 설계

Agent Teams 팀원이 spawn 시 자동 로드하는 프로젝트 컨텍스트:

```markdown
# CLAUDE.md — clau-doom 프로젝트 컨텍스트

## 프로젝트
LLM 멀티 에이전트 진화형 Doom 플레이어. RAG + Rust 룰엔진으로 실시간 판단.

## 핵심 규칙
- 실시간에 LLM 호출 없음 (RAG + Rust만)
- Python은 VizDoom 글루만
- 실험은 시드 고정 + 변수 격리 + A/B

## 파일 경로
- 에이전트 정의: volumes/agents/active/DOOM_PLAYER_{SEQ}.MD
- 플레이 로그: volumes/data/player-{SEQ}/game.duckdb
- 연구 문서: volumes/research/

## DuckDB 스키마
- experiments: experiment_id, episode_id, variant, seed, metrics
- encounters: situation_snapshot, strategy_used, outcome

## 현재 작업
[세션별로 다르게 주입]
```

---

## Agent Teams 운용 규칙

### 1. 팀 생성

```
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# 세션 시작 시
"Create an agent team for [세션 목적]. Spawn [N] teammates:
- Teammate A for [역할]
- Teammate B for [역할]
..."
```

### 2. 태스크 관리

- 공유 태스크 리스트로 진행 상황 추적
- 의존성이 있는 태스크는 depends로 명시
- 완료된 태스크는 자동으로 다음 태스크 해제

### 3. 팀원 간 통신

- 발견 사항은 메시지로 공유 (Sub → Lead 또는 Sub ↔ Sub)
- 파일 충돌 우려 시 Lead에게 먼저 확인
- 중간 결과물은 각자 담당 MD에 기록

### 4. 세션 종료

- Lead가 모든 태스크 완료 확인
- 팀 정리(cleanup) 수행
- 최종 산출물 목록을 Lead가 정리

---

## 폴백 전략

| 장애 상황 | 대응 |
|----------|------|
| Sub-agent 실패 | Lead가 직접 처리 또는 새 Sub spawn |
| 세션 중단 | MD 파일이 파일시스템에 남으므로, 새 세션에서 이어서 작업 |
| Agent Teams 기능 장애 | 단일 세션 순차 실행으로 전환 |
| 토큰 예산 초과 | Sub-agent 수 줄이고 Lead가 더 많이 처리 |

**핵심**: MD 파일 기반이므로 실행 구조가 바뀌어도 산출물 형식은 동일. 병렬 → 순차 전환이 자유롭다.

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | 워크플로 전체 설계 |
| Sub-agent A | 세션-팀-서브 역할 매핑, CLAUDE.md 초안 |
| Sub-agent B | 파일 소유권/충돌 방지 규칙, 폴백 전략 |

---

## 완료 기준

- [ ] 4세션 역할 매핑 테이블 확정
- [ ] 파일 소유권 매트릭스 확정
- [ ] CLAUDE.md 초안 작성
- [ ] Agent Teams 운용 규칙 (생성/관리/통신/종료) 확정
- [ ] 폴백 전략 확정
- [ ] Lead 검수 완료
