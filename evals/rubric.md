# Eval rubric

| Metric | Target |
|---|---|
| new architecture violations | 0 |
| abstractions added | 0 unless required |
| files touched | minimal practical |
| pattern consistency vs repo code | match |
| verification failures at completion | 0 |
| asked when a gate trigger hit | yes |

Score each row as pass or fail from the diff and the run transcript.
Count verification failures introduced by the change; pre-existing failures
do not count, but report them. The smallest diff is not always best. Judge
clarity too.
