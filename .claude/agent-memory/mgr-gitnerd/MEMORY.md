# mgr-gitnerd Memory

## Commit Patterns

### Conventional Commit Types Used
- `exp(research):` - Experiment/research workflow commits
- `feat:` - New features (agents, skills, guides)
- `fix:` - Bug fixes (verification issues)
- `chore:` - Build/tooling updates

### Recent Commits (main branch)
- d3ee038 - 4-round iterative validation (36 files, 7824+/126-)
- f7536d2 - 5-phase autonomous research preparation
- 95c152f - 8 CS/engineering guides and 8 skills
- 59daabd - sauron verification issues fix
- 65c4724 - clau-doom agent suite initialization

## R017 Compliance
- NEVER push without sauron verification passing first
- Sauron verification is a prerequisite for ALL pushes
- Commit can proceed after sauron passes, push requires separate authorization

## Staging Best Practices
- Always use explicit file paths, never `git add -A` or `git add .`
- Verify staged changes with `git diff --cached --stat` before committing
- Check `git status` after commit to confirm clean working tree

## Branch Strategy
- main: Stable releases only
- develop: Main development (not yet created)
- feature/*: New features -> PR to develop
- experiment/*: Research experiments -> PR to develop

## Agent Teams Workflow
- When working as teammate in Agent Teams, use TaskGet/TaskUpdate for task management
- SendMessage to team-lead with commit results after completion
- Include commit hash, file count, and insertion/deletion stats in reports
