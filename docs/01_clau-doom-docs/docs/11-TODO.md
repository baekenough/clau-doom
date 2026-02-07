# 11 — 미결 사항

← [10-INFRA](10-INFRA.md) · [인덱스](../DOOM_ARENA_CLAUDE.md)

---

## 기술 탐색 필요

- [ ] Rust ↔ VizDoom 바인딩 방식 (Python FFI vs gRPC vs shared memory)
- [ ] ONNX 로컬 임베딩 vs Ollama 임베딩 성능 비교
- [ ] noVNC 멀티스트리밍 시 대역폭/성능 최적화
- [ ] DuckDB 스키마 상세 설계 (DOE 확장 테이블 포함)
- [ ] proto 파일 (agent.proto, orchestrator.proto) 상세 정의

## 알고리즘 설계 필요

- [ ] 세대 진화 시 교차/변이 구체적 알고리즘
- [ ] 베이지안 최적화 대리 모델 구현 방식 (GP vs RF)
- [ ] TOPSIS/AHP 가중치 초기값 및 동적 조정 정책
- [ ] FMEA의 빈도(O)/심각도(S)/검출난이도(D) 스코어링 기준 정의

## 파이프라인 설계 필요

- [ ] ANOVA/잔차 분석 자동화 (DuckDB + Python statsmodels? Rust?)
- [ ] Sub-agent 병렬 실행 시 작업 스케줄링 최적화
- [ ] SPC 관리도 자동 갱신 및 이상 신호 알림 파이프라인
- [ ] DOE 매트릭스 → 에이전트 MD 자동 주입 파이프라인

## 논문 관련

- [ ] 관련 연구 추가 서베이 (DOE + AI/ML 교차 분야)
- [ ] 베이스라인 정의 (순수 OFAT, 순수 랜덤, RL 기반 등)
- [ ] 통계적 유의성 검정 방법 최종 확정
- [ ] 실험 규모 결정 (세대 수, 에이전트 수, 에피소드 수)

## 의사결정 대기

- [ ] Agent Teams 기능 활용 범위 — 실행 레이어만? PI 레이어도?
- [ ] DOE Phase 전환을 PI가 완전 자율로 할지, 인간 승인 필요한지
- [ ] 논문 1편으로 갈지, DOE 파트와 LLM-as-PI 파트를 분리할지
