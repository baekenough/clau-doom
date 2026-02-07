# 실행 계획: 4세션 × Agent Teams × Sub-agents

---

## 실행 구조 개요

```
┌─────────────────────────────────────────────────────────────┐
│                    clau-doom 연구 설계 점검                    │
│                                                              │
│  Session 1 (문헌 수집)      Session 2 (연구 설계 보강)         │
│  ┌─ Lead ──────────────┐   ┌─ Lead ──────────────┐          │
│  │ Sub: QD/MAP-Elites  │   │ Sub: 랜덤 베이스라인  │          │
│  │ Sub: LLM 진화 최적화 │   │ Sub: RL 베이스라인   │          │
│  │ Sub: MARL 협업/경쟁  │   │ Sub: QD 지표 추출   │          │
│  │ Sub: RAG Decision   │   │ Sub: DuckDB 매핑    │          │
│  │ Sub: LLM-as-Sci     │   │ Sub: 세션-팀 역할    │          │
│  │ Sub: VizDoom Comp   │   │ Sub: 파일 소유권     │          │
│  └─────────────────────┘   └─────────────────────┘          │
│           │                          │                       │
│  Session 3 (기술 검증)      ─────────┘                       │
│  ┌─ Lead ──────────────┐        │                            │
│  │ Sub: Dockerfile     │        │                            │
│  │ Sub: noVNC 테스트    │        │                            │
│  │ Sub: FFI PoC        │        ▼                            │
│  │ Sub: gRPC PoC       │   Session 4 (문서 통합)              │
│  │ Sub: OpenSearch 구성 │   ┌─ Lead ──────────────┐          │
│  │ Sub: 임베딩 벤치마크  │   │ Sub: 문헌 정리/포맷  │          │
│  └─────────────────────┘   │ Sub: 기술 결정 정리   │          │
│                             │ Sub: 설계 섹션 확장   │          │
│                             │ Sub: CLAUDE.md 작성  │          │
│                             └─────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 세션별 상세

### Session 1 — 문헌 수집

**목적**: 현재 편중된 문헌 커버리지를 4개 축으로 확장

**Agent Teams 구성**:

| 역할 | 담당 | 출력물 |
|------|------|--------|
| Lead | 문헌 탐색 총괄, 중복 제거, 품질 필터링 | 각 태스크 MD 최종 검수 |
| Sub-agent A | QD/MAP-Elites, EvoPrompting, FunSearch 서치 | S1-01 초안 |
| Sub-agent B | LLM 진화 최적화, MARL 협업/경쟁 서치 | S1-01 보충 |
| Sub-agent C | RAG + RL/Decision, kNN 정책 검색 서치 | S1-02 초안 |
| Sub-agent D | LLM-as-Scientist, 자율 실험 설계 서치 | S1-03 초안 |
| Sub-agent E | VizDoom Competition, FPS RL agent 서치 | S1-04 초안 |

**파일 소유권 규칙**:
- 각 Sub-agent는 자신의 담당 MD 파일만 수정
- Lead만 최종 검수 후 완료 표시

**병렬 실행**: S1 내 4개 태스크 모두 독립적 → 전원 동시 실행

---

### Session 2 — 연구 설계 보강

**목적**: 평가 프레임워크, ablation 계획, 다양성 지표, Agent Teams 워크플로 확정

**Agent Teams 구성**:

| 역할 | 담당 | 출력물 |
|------|------|--------|
| Lead | 설계 일관성 검수, 기존 설계 문서와 정합성 확인 | 각 태스크 MD 최종 검수 |
| Sub-agent A | 랜덤/룰 전용 베이스라인 정의 | S2-01 일부 |
| Sub-agent B | RL 베이스라인 조사 (VizDoom 기존 성과) | S2-01 일부 |
| Sub-agent C | 문서 품질 변수 조작 방안 | S2-02 일부 |
| Sub-agent D | 스코어링 가중치 변수 조작 방안 | S2-02 일부 |
| Sub-agent E | QD 문헌에서 다양성 지표 추출 | S2-03 일부 |
| Sub-agent F | DuckDB 스키마에 지표 매핑 | S2-03 일부 |
| Sub-agent G | 세션-팀-서브 역할 매핑 | S2-04 일부 |
| Sub-agent H | 파일 소유권/충돌 방지 규칙 | S2-04 일부 |

**의존성**: S2-01(베이스라인)은 S1-04(Doom RL 문헌)의 결과가 있으면 더 좋지만, 없어도 독립 실행 가능. 병렬 진행 후 S4에서 통합.

---

### Session 3 — 기술 검증

**목적**: DOOM_ARENA_CLAUDE.md 미결 사항 4건 해소

**Agent Teams 구성**:

| 역할 | 담당 | 출력물 |
|------|------|--------|
| Lead | PoC 총괄, 벤치마크 설계, 결과 비교 | 각 태스크 MD 최종 검수 |
| Sub-agent A | Dockerfile 작성 (VizDoom + Xvfb) | S3-01 일부 |
| Sub-agent B | noVNC 스트리밍 테스트 | S3-01 일부 |
| Sub-agent C | Python FFI PoC | S3-02 일부 |
| Sub-agent D | gRPC PoC | S3-02 일부 |
| Sub-agent E | shared memory PoC | S3-02 일부 |
| Sub-agent F | OpenSearch 컨테이너 구성 | S3-03 일부 |
| Sub-agent G | 임베딩 + 검색 테스트 | S3-03 + S3-04 |

**파일 소유권 규칙**:
- Dockerfile → Sub-A 전담
- docker-compose.yml → Lead만 수정
- PoC 코드 → 각 Sub가 별도 디렉토리에서 작업

---

### Session 4 — 문서 통합

**목적**: S1~S3 결과를 기존 설계 문서에 반영, CLAUDE.md 신규 작성

**선행 조건**: S1, S2, S3 전체 완료

**Agent Teams 구성**:

| 역할 | 담당 | 출력물 |
|------|------|--------|
| Lead | 문서 일관성 검수, 최종 머지 | 통합 완료 확인 |
| Sub-agent A | S1 문헌 → DESIGN.md 관련 연구 섹션 업데이트 | S4-01 |
| Sub-agent B | S3 기술 검증 → CLAUDE.md 미결사항 갱신 | S4-02 |
| Sub-agent C | S2 설계 보강 → DESIGN.md 실험/평가 섹션 확장 | S4-03 |
| Sub-agent D | S4-02, S4-03 결과 → CLAUDE.md 작성 | S4-04 |

**내부 의존성**: S4-04는 S4-02, S4-03 완료 후 시작

---

## 동시성/순서 요약

```
Phase 1 (병렬): S1 + S2 + S3 동시 시작
Phase 2 (순차): S4 — S1~S3 완료 대기 후 시작
  S4 내부: S4-01, S4-02, S4-03 병렬 → S4-04 순차
```

---

## 토큰 비용 고려

- Session당 Lead 1 + Sub-agents 5~8개 = 컨텍스트 윈도우 6~9개
- 4세션 동시 시 최대 ~32개 컨텍스트 윈도우
- **비용 절감 전략**: Sub-agent에는 Sonnet 사용, Lead만 Opus 사용
- 문헌 서치(S1)처럼 독립적 작업은 Sub-agent 효율이 높음
- 기술 검증(S3)은 실제 코드 실행이 필요해 Sub-agent당 시간이 길 수 있음

---

## 폴백 전략

Agent Teams가 실험적 기능이므로, 장애 시 폴백:

1. **팀 내 Sub-agent 실패**: Lead가 해당 태스크를 직접 처리하거나 새 Sub-agent spawn
2. **세션 전체 장애**: 단일 Claude Code 세션에서 순차 실행으로 전환
3. **세션 간 결과 전달 실패**: MD 파일이 바인드 마운트에 있으므로 파일 시스템 레벨에서 복구 가능

핵심: **MD 파일 기반 소통이므로 어떤 실행 구조에서든 결과물은 동일한 MD 파일**. 실행 방식만 병렬 → 순차로 바뀔 뿐.
