package experiment

// GenerateSeedSet creates a deterministic seed set.
// Formula: seed_i = base + i * step
// Default for DOE-001: base=42, step=31, count=70
func GenerateSeedSet(base, step, count int) []int {
	seeds := make([]int, count)
	for i := 0; i < count; i++ {
		seeds[i] = base + i*step
	}
	return seeds
}

// DefaultDOE001Seeds returns the standard 70-seed set for DOE-001.
func DefaultDOE001Seeds() []int {
	return GenerateSeedSet(42, 31, 70)
}
