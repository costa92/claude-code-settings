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
- 覆盖率门槛: ≥ 70%（低于此值在测试报告中标注 Warning）

## Lint / Format
- Format: `black .` 或 `ruff format .`
- Lint: `ruff check .`
- Type check: `mypy src/`（如有配置）

## 惯用模式
- Type hints: 所有公共函数签名
- 数据类: 优先 dataclass 或 Pydantic model
- 异步: async/await，避免混用同步阻塞调用
- 命名: snake_case（类用 PascalCase）

## Developer 编码检查清单

编码完成后、提交 Reviewer 前，必须逐项自检：

- [ ] 函数参数不使用可变默认值（用 `None` + 函数体内初始化）
- [ ] 模块间无循环导入（必要时延迟导入或重构拆分）
- [ ] 所有异常被显式处理或重新抛出（不用裸 `except:` 或 `except Exception: pass`）
- [ ] async 函数内不调用同步阻塞 IO（用 `aiofiles`/`httpx` 等异步替代）
- [ ] 所有包目录有 `__init__.py`
- [ ] 公共函数有 type hints
- [ ] **修改函数签名或 Protocol/ABC 时，所有实现（含 test mock/patch）和调用点已同步更新**
- [ ] `ruff check .` 和 `mypy`（如配置）零告警（**必须实际运行，不可跳过**）

## 常见陷阱（Reviewer 关注）
- 可变默认参数（`def f(x=[])`）
- 循环导入
- 未处理的异常被吞
- async 函数内调用同步阻塞 IO
- 缺少 `__init__.py` 导致导入失败
