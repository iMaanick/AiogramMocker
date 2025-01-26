# Test Tools for Aiogram

This repository provides an example of test tools for the Aiogram library. Most core classes are taken from [aiogram_dialog](https://github.com/Tishka17/aiogram_dialog), and this repository includes minor extensions specifically tailored for use in Aiogram-based projects.

## Examples of Use

### Run Tests with Coverage Report in Terminal
```bash
pytest --cov=app/test_groosha --cov-report=term-missing tests/test_groosha.py
```
```bash
pytest --cov=app/test_groosha --cov-report=html tests/test_groosha.py
```

```bash
pytest --cov=app/test_di --cov-report=term-missing tests/test_di.py
```