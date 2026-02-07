# T-01: VizDoom 플랫폼

## 기본 정보
| 항목 | 내용 |
|------|------|
| 공식 사이트 | [vizdoom.cs.put.edu.pl](https://vizdoom.cs.put.edu.pl/) |
| GitHub | [Farama-Foundation/ViZDoom](https://github.com/Farama-Foundation/ViZDoom) |
| 원논문 | Kempka et al., "ViZDoom: A Doom-based AI Research Platform for Visual Reinforcement Learning," IEEE CIG 2016 |
| 인용 | 666+ 논문 |
| 관리 | Farama Foundation (2022~) — Gymnasium/PettingZoo와 동일 재단 |

## 핵심 기능
- Doom 엔진 기반 AI 연구 플랫폼
- Python/C++ API 제공
- 커스텀 시나리오(.cfg + .wad) 지원
- 스크린 버퍼 (RGB, depth, labels, automap) 접근
- 게임 변수 (health, ammo, kills 등) 직접 접근
- 멀티플레이어 지원 (CIG 대회)

## clau-doom에서의 역할
- 게임 환경 자체
- Python 글루를 통해 Rust 에이전트와 연결
- Xvfb(가상 디스플레이) + x11vnc + noVNC로 브라우저 스트리밍
- 컨테이너 내부에서 실행 (OS 의존성 격리)

## 미결 사항
- Rust ↔ VizDoom 바인딩 방식: Python FFI vs gRPC vs shared memory
- 멀티 인스턴스 실행 시 성능 최적화

---

# T-02: VizDoom RL 베이스라인

clau-doom의 RAG 기반 에이전트 성능을 비교할 RL 베이스라인.

## Arnold Agent
| 항목 | 내용 |
|------|------|
| 저자 | Lample & Chaplot |
| 발표 | AAAI 2017 |
| 성과 | **VizDoom Competition 2017 Track 2 우승** |
| 방법 | DRQN + game features network |

## F1 Agent
| 항목 | 내용 |
|------|------|
| 저자 | Wu & Tian |
| 발표 | ICLR 2017 |
| 성과 | **VizDoom Competition 2016 Track 1 우승** |
| 방법 | A3C + reward shaping + curriculum design |

## Gunner
| 항목 | 내용 |
|------|------|
| 발표 | PeerJ Computer Science, 2025.12 |
| 방법 | 모델 프리 RL 알고리즘으로 deathmatch 시나리오 훈련 |
| 의의 | 최신 DRL 알고리즘 비교 벤치마크 |

## Khan et al. PPO Study
| 항목 | 내용 |
|------|------|
| 발표 | Computer Animation and Virtual Worlds (CAVW), 2025 |
| 방법 | PPO + reward shaping + curriculum learning |
| 환경 | VizDoom Deadly Corridor |

## clau-doom 비교 전략
- 동일 시나리오(E1M1, Deadly Corridor 등)에서 RAG 에이전트 vs RL 에이전트 비교
- RAG 에이전트의 장점: 학습 시간 0, 해석 가능성, 새 전략 즉시 적용
- RAG 에이전트의 단점 (예상): 실시간 반응 속도, 미세 조정 정밀도
- 세대 진화 후 RAG 에이전트가 RL 에이전트 수준에 근접하는지 관찰

---

# T-03: OpenSearch kNN 벡터 검색

## 기술 개요
| 항목 | 내용 |
|------|------|
| 문서 | [docs.opensearch.org/latest/vector-search/](https://docs.opensearch.org/latest/vector-search/) |
| kNN 필드 | [knn-vector type](https://docs.opensearch.org/latest/mappings/supported-field-types/knn-vector/) |
| ANN 알고리즘 | HNSW (Faiss/Lucene/NMSLIB), IVF (Faiss) |
| 최대 차원 | 16,000 |
| 새 기능 | gRPC API (3.2+), GPU 가속 인덱싱 |

## clau-doom에서의 역할 (Level 2 검색)

```
게임 틱 → 상황 피처 벡터 추출 (Rust)
    → OpenSearch kNN 검색 (~20ms 목표)
    → Top-K 전략 문서 반환
    → Rust 스코어링 → 액션 선택
```

## 인덱스 설계 고려사항

```json
{
  "settings": {
    "index": { "knn": true, "knn.algo_param.ef_search": 100 }
  },
  "mappings": {
    "properties": {
      "situation_embedding": {
        "type": "knn_vector",
        "dimension": 128,
        "method": {
          "name": "hnsw",
          "engine": "faiss",
          "space_type": "cosinesimil",
          "parameters": { "ef_construction": 256, "m": 16 }
        }
      },
      "situation_tags": { "type": "keyword" },
      "agent_id": { "type": "keyword" },
      "generation": { "type": "integer" },
      "quality.success_rate": { "type": "float" },
      "quality.sample_size": { "type": "integer" },
      "quality.confidence_tier": { "type": "keyword" }
    }
  }
}
```

## 성능 최적화 포인트
- **in_memory 모드**: 최소 지연 (clau-doom 기본)
- **ef_search 튜닝**: 정확도 vs 속도 트레이드오프
- **pre-filter**: situation_tags로 검색 범위 사전 축소
- **warmup API**: 인덱스를 메모리에 미리 로드

## 미결 사항
- 임베딩 차원 수 결정 (128? 256? 384?)
- ONNX 로컬 임베딩 vs Ollama 임베딩 성능 비교
- 전략 문서 수 증가 시 검색 지연 프로파일링

---

# T-04: RAG 서베이

## Agentic RAG (2025.01)
| 항목 | 내용 |
|------|------|
| arXiv | [2501.09136](https://arxiv.org/abs/2501.09136) |
| 핵심 | RAG 파이프라인에 autonomous AI agent를 내장 |

### clau-doom 관련 요소
- **동적 검색 전략**: 상황에 따라 검색 쿼리/필터 자동 조정
- **반복 정제**: 검색 결과가 불충분하면 쿼리 수정 후 재검색
- **적응적 응답 생성**: 검색 결과 품질에 따라 행동 전략 조정

→ clau-doom의 비동기 정제(Ollama)가 이 패턴의 축소판

## Comprehensive RAG Survey (2025.05)
| 항목 | 내용 |
|------|------|
| arXiv | [2506.00054](https://arxiv.org/abs/2506.00054) |
| 핵심 | RAG 아키텍처, 개선 기법, robustness 종합 정리 |

### clau-doom 관련 요소
- **문서 생명주기 관리**: 생성 → 검증 → 승격/퇴화
- **하이브리드 검색**: 벡터 + 키워드 + 메타데이터 필터 결합
- **RAG 견고성**: 노이즈 문서, 오래된 문서 처리 전략

→ clau-doom의 전략 문서 품질 관리(confidence_tier, last_validated)에 직접 적용
