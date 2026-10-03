# OpenNutritionScore (NutriScore Engine + Diet Builder)

## What we're building
A transparent, configurable nutrition scoring engine that rates foods 0-100, plus a diet builder that finds the highest-scoring diet a user can afford.

- **Scoring engine:** food data -> normalized metrics -> weighted subscores -> overall score + human-readable explanation.
- **Diet builder:** A system that takes user profile data and calculates daily targets, then finds the diet that maximizes the calorie-weighted average food score while meeting targets and budget.

**Disclaimer:** This is an educational tool, not medical or dietary advice.

## Structure
- `/engine` - scoring engine (pure functions + config + tests)
- `/data` - raw downloads, cleaning scripts, cleaned JSON
- `/optimizer` - diet optimizer + target calculator (pure functions + tests)
- `/web` - Next.js app (to be added)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
