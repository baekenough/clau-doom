//! Benchmark for the full decision cascade pipeline.
//!
//! Measures end-to-end latency from GameState input to Action output,
//! covering Level 0 rule matching and scoring. Target: < 100ms P99.

use criterion::{criterion_group, criterion_main, Criterion};

fn bench_decision_cascade(c: &mut Criterion) {
    c.bench_function("decision_cascade_noop", |b| {
        b.iter(|| {
            // Placeholder: will benchmark full cascade once types are defined.
            std::hint::black_box(42)
        })
    });
}

criterion_group!(benches, bench_decision_cascade);
criterion_main!(benches);
