# M-01: Wilson Score Interval — 전략 문서 신뢰도 스코어링

## 개요

clau-doom의 Rust 스코어링 엔진에서 전략 문서의 **신뢰도(confidence)**를 평가하는 핵심 알고리즘. OpenSearch kNN Top-K 결과에 대해 유사도(0.4) + 신뢰도(0.4) + 최신성(0.2) 가중 스코어링을 적용하며, 신뢰도 산출에 Wilson Score Interval 하한값을 사용.

## 원리

### 문제
전략 문서 A: 성공 3/3 (100%) vs 전략 문서 B: 성공 80/100 (80%)
→ 단순 평균이면 A가 우세하지만, 표본 3개로 100%인 것은 운일 수 있음

### Wilson Score Lower Bound 해결

```
WilsonLB(p̂, n, z) = (p̂ + z²/2n - z·√(p̂(1-p̂)/n + z²/4n²)) / (1 + z²/n)

p̂ = 관측된 성공 비율
n = 총 시도 횟수
z = 신뢰 수준에 해당하는 z-score (95% → 1.96)
```

### 예시 계산

| 문서 | 성공/시도 | p̂ | WilsonLB (95%) |
|------|----------|-----|----------------|
| A | 3/3 | 1.00 | **0.438** |
| B | 80/100 | 0.80 | **0.712** |
| C | 8/10 | 0.80 | **0.494** |
| D | 1/1 | 1.00 | **0.206** |

→ 표본 적은 문서(A, D)를 보수적으로 평가. 표본 큰 문서(B)가 높은 신뢰도.

## 참고 자료
| 자료 | URL |
|------|-----|
| 핵심 블로그 (Evan Miller) | [evanmiller.org/how-not-to-sort-by-average-rating.html](https://www.evanmiller.org/how-not-to-sort-by-average-rating.html) |
| 원논문 | Wilson, E. B. (1927), "Probable Inference, the Law of Succession, and Statistical Inference," JASA, 22, 209-212 |
| npm 구현 | [wilson-score](https://www.npmjs.com/package/wilson-score) |
| GitHub 구현 모음 | [gist: honza/5050540](https://gist.github.com/honza/5050540) |

## Rust 구현 스케치

```rust
fn wilson_lower_bound(successes: u32, total: u32, confidence: f64) -> f64 {
    if total == 0 { return 0.0; }
    
    let n = total as f64;
    let p_hat = successes as f64 / n;
    let z = z_score(confidence); // 0.95 → 1.96
    let z2 = z * z;
    
    (p_hat + z2 / (2.0 * n) 
        - z * ((p_hat * (1.0 - p_hat) + z2 / (4.0 * n)) / n).sqrt())
        / (1.0 + z2 / n)
}

fn strategy_confidence(doc: &StrategyDoc) -> f64 {
    wilson_lower_bound(
        doc.quality.successes,
        doc.quality.sample_size,
        0.95
    )
}
```

## 가중 스코어링 공식 (Rust 스코어링 엔진)

```
final_score = w_sim × cosine_similarity    // 0.4
            + w_conf × wilson_lower_bound   // 0.4
            + w_rec × recency_decay         // 0.2

recency_decay = exp(-λ × days_since_validation)
```

### 가중치 선택 근거
- **유사도 0.4**: 상황 매칭이 부정확하면 좋은 전략이라도 무용
- **신뢰도 0.4**: 검증되지 않은 전략은 위험 → 유사도와 동등 중요도
- **최신성 0.2**: 메타 변화(맵/적 패턴 변경) 반영, 단 유사도·신뢰도보다 중요도 낮음

## confidence_tier 매핑

| tier | 조건 | 의미 |
|------|------|------|
| high | WilsonLB ≥ 0.7 AND sample ≥ 30 | 실전 검증 완료, 신뢰 가능 |
| medium | WilsonLB ≥ 0.5 AND sample ≥ 10 | 유망하지만 추가 검증 필요 |
| low | 그 외 | 탐험적, 표본 부족 |
| deprecated | WilsonLB < 0.3 AND sample ≥ 30 | 성과 나쁨, 퇴출 후보 |

---

# M-02: MD 파일 기반 진화 알고리즘 설계 노트

## 개요

clau-doom의 세대 진화에서 DOOM_PLAYER_{SEQ}.MD 파일을 유전체(genome)로 사용하는 진화 알고리즘 설계. LLM(Claude Code)이 mutation/crossover 연산자 역할 수행.

## 이론적 근거
- S-04 서베이: LLM을 진화 연산자로 사용하는 패턴
- P-05 EvoAgent: 에이전트 프레임워크의 진화적 확장
- P-08 AlphaEvolve: LLM+진화 폐루프
- LLM_GP (Genetic Programming & Evolvable Machines, 2024): 텍스트 기반 유전체의 LLM 진화

## 진화 연산

### Selection (선택)
```
fitness(agent) = w1 × kill_rate 
               + w2 × survival_time 
               + w3 × experiment_adoption_rate
               + w4 × knowledge_contribution_score

상위 K개 에이전트를 부모로 선택 (tournament selection or roulette wheel)
```

### Crossover (교차)
Claude Code가 상위 2개 에이전트의 MD를 읽고, 각각의 강점을 조합:

```markdown
## 교차 프롬프트 (예시)
Parent A의 전략: aggressive, retreat_threshold 0.30, shotgun 선호
Parent B의 전략: defensive, retreat_threshold 0.50, chaingun 선호

Parent A는 kill_rate가 높고, Parent B는 survival이 높다.
두 전략의 강점을 조합한 새 전략을 생성하라.
```

### Mutation (변이)
Claude Code가 파라미터를 의미 있는 방식으로 변경:

```markdown
## 변이 프롬프트 (예시)  
현재 전략: retreat_threshold 0.40
이 에이전트는 좁은 복도에서 사망률이 높다.
retreat_threshold를 조정하거나 새로운 규칙을 추가하라.
```

### Elitism (엘리트주의)
- 최고 성과 에이전트 1-2개는 변경 없이 다음 세대에 복제
- 진화 과정에서 최고 성과가 퇴보하지 않도록 보장

## MD 파일의 진화 가능 영역

| MD 섹션 | 진화 방식 | 예시 |
|---------|----------|------|
| Strategy Profile | 파라미터 값 변이 | play_style: aggressive → balanced |
| Learned Rules | 규칙 추가/수정/삭제 | "좁은 복도에서 shotgun 우선" → "좁은 복도에서 거리에 따라 무기 선택" |
| retreat_threshold | 수치 변이 | 0.40 → 0.35 |
| ammo_conservation | 수치 변이 | low → medium |
| 새 규칙 | 교차에서 도입 | Parent B의 "imp 3마리 이상 시 수류탄" 규칙 도입 |

## 미결 사항
- [ ] population size (세대당 에이전트 수) 결정
- [ ] 세대 길이 (에피소드 수) 결정
- [ ] mutation rate (변이 확률/강도) 결정
- [ ] crossover 시 충돌하는 규칙 해결 전략
- [ ] diversity preservation (MAP-Elites 등) 적용 여부
- [ ] 구체적 프롬프트 템플릿 설계 및 테스트
