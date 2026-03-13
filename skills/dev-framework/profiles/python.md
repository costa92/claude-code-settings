# Python Language Profile

## 检测标志
- `pyproject.toml` 或 `setup.py` 或 `requirements.txt` 存在

## 项目结构规范
```
src/{package}/  # 源码
tests/          # 测试
pyproject.toml  # 项目配置
```

## 测试
- 命令: `pytest tests/ -v --tb=short`
- 覆盖率: `pytest tests/ --cov=src --cov-report=term-missing`
- 框架: pytest

## Lint / Format
- Format: `black .` 或 `ruff format .`
- Lint: `ruff check .`
- Type check: `mypy src/`（如有配置）

## 惯用模式
- Type hints: 所有公共函数签名
- 数据类: 优先 dataclass 或 Pydantic model
- 异步: async/await，避免混用同步阻塞调用
- 命名: snake_case（类用 PascalCase）

## 常见陷阱（Reviewer 关注）
- 可变默认参数（`def f(x=[])`）
- 循环导入
- 未处理的异常被吞
- async 函数内调用同步阻塞 IO
- 缺少 `__init__.py` 导致导入失败
