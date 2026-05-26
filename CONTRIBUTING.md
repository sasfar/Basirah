# Contributing to Basirah

Thank you for your interest in contributing to Basirah! We welcome contributions from the community to help build a better Islamic knowledge system.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in [GitHub Issues](https://github.com/sasfar/Basirah/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - System information (OS, Docker version, etc.)
   - Relevant logs or error messages

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/sasfar/Basirah.git
   cd Basirah
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed
   - Keep commits atomic and well-described

3. **Test your changes**
   ```bash
   # Run tests
   pytest
   
   # Test API endpoints
   curl http://localhost:8081/health
   ```

4. **Submit pull request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure CI passes

## Development Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Git
- 32GB+ RAM recommended

### Local Development

```bash
# Clone repository
git clone https://github.com/sasfar/Basirah.git
cd Basirah

# Start infrastructure
cd infra/compose
docker compose up -d basirah-postgres basirah-qdrant

# Run API in development mode
cd ../../apps/api
pip install -r requirements.txt
uvicorn main:app --reload
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Add docstrings for functions/classes
- Keep functions focused and small

**Example:**
```python
def calculate_confidence(
    answer: str,
    evidence: List[Dict[str, Any]],
    retrieval_scores: List[float]
) -> float:
    """
    Calculate confidence score for generated answer

    Args:
        answer: Generated answer
        evidence: Retrieved evidence passages
        retrieval_scores: Scores from retrieval

    Returns:
        Confidence score between 0 and 1
    """
    # Implementation
```

### Docker

- Use multi-stage builds
- Minimize layer count
- Pin dependency versions
- Add healthchecks

### Documentation

- Update README.md for new features
- Add inline comments for complex logic
- Include examples in API docs

## Testing

### Unit Tests

```python
# apps/api/tests/test_confidence.py
def test_confidence_calculation():
    answer = "This is [Quran 2:183] about fasting."
    evidence = [{"reference": "Quran 2:183", "text": "..."}]
    scores = [0.9]
    
    confidence = calculate_confidence(answer, evidence, scores)
    assert 0.0 <= confidence <= 1.0
```

### Integration Tests

```bash
# tests/integration/test_rag_pipeline.py
curl -X POST http://localhost:8081/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is fasting?", "top_k": 10}'
```

## Areas for Contribution

### High Priority

- [ ] Arabic language support
- [ ] Query performance optimization
- [ ] Mobile-responsive frontend
- [ ] User authentication system
- [ ] Advanced search filters

### Medium Priority

- [ ] Export citations (PDF, BibTeX)
- [ ] Query history and bookmarks
- [ ] Analytics dashboard
- [ ] Batch query processing
- [ ] Caching layer (Redis)

### Low Priority

- [ ] Dark mode UI
- [ ] Accessibility improvements
- [ ] Internationalization (i18n)
- [ ] Progressive web app (PWA)

## Corpus Contributions

If you want to add new Islamic sources:

1. Ensure authenticity (scholarly consensus)
2. Provide source metadata
3. Create ingestion script
4. Update schema if needed
5. Document the source

## Review Process

1. Maintainer reviews PR within 5 business days
2. Feedback provided via PR comments
3. Address feedback and update PR
4. Once approved, maintainer merges

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Assume good intent
- Respect Islamic values and scholarship

## Questions?

- Open a [GitHub Discussion](https://github.com/sasfar/Basirah/discussions)
- Email: syed@saasglobal.ca

Thank you for contributing to Basirah! 🌙
