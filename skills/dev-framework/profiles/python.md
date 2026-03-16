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

## 服务端验收测试
- 启动（FastAPI）: `PORT=18080 uvicorn app.main:app --host 0.0.0.0 --port 18080 &`
- 启动（Flask）: `PORT=18080 flask run --port 18080 &`
- 启动（Django）: `python manage.py runserver 18080 &`
- 等待就绪: `for i in $(seq 1 10); do curl -sf http://localhost:18080/health && break || sleep 1; done`
- 关停: `pkill -f 'uvicorn|flask|runserver'`
- 测试端口: 18080（避免与开发端口冲突）

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

## 数据库测试

当 project.yaml 中 `has_database: true` 时，Developer 和 Tester 需遵循以下策略：

### 推荐方案（按优先级）

| 方案 | 适用场景 | 示例 |
|------|----------|------|
| **SQLite 内存** | 轻量 SQLAlchemy 项目 | `create_engine("sqlite:///:memory:")` |
| **testcontainers-python** | 需要真实 PG/MySQL/Redis | `PostgresContainer("postgres:16")` |
| **Protocol/ABC Mock** | 单元测试隔离 DB 层 | 定义 Protocol，注入 MagicMock |

### 测试隔离模式

```python
# 方式 1: Protocol + MagicMock（单元测试）
from typing import Protocol
from unittest.mock import MagicMock

class UserRepository(Protocol):
    def save(self, user: User) -> None: ...
    def find_by_id(self, id: str) -> User | None: ...

@pytest.fixture
def mock_repo():
    repo = MagicMock(spec=UserRepository)
    repo.find_by_id.return_value = User(id="1", name="test")
    return repo

# 方式 2: SQLite 内存 + fixture（集成测试）
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()

# 方式 3: testcontainers（集成测试）
@pytest.fixture(scope="session")
def pg_container():
    with PostgresContainer("postgres:16") as pg:
        yield pg.get_connection_url()
```

### Developer 要求

- 数据库操作通过 Repository 类封装，依赖通过构造函数注入
- 使用 Alembic / Django migrations 管理表结构
- 测试 fixture 负责 setup/teardown，不依赖全局状态

## 外部 API 测试

当 project.yaml 中 `has_external_api: true` 时：

### 推荐方案

| 方案 | 适用场景 | 示例 |
|------|----------|------|
| **Protocol Mock** | 单元测试 | `MagicMock(spec=PaymentClient)` |
| **responses / respx** | 集成测试 | 拦截 requests/httpx 请求 |
| **pytest-recording** | 录制回放 | VCR.py 录制真实 HTTP 请求 |

```python
# responses 拦截 requests（同步）
import responses

@responses.activate
def test_external_api():
    responses.add(responses.GET, "https://api.example.com/data",
                  json={"status": "ok"}, status=200)
    result = my_client.fetch_data()
    assert result["status"] == "ok"

# respx 拦截 httpx（异步）
import respx

@respx.mock
async def test_async_api():
    respx.get("https://api.example.com/data").respond(200, json={"status": "ok"})
    result = await my_async_client.fetch_data()
    assert result["status"] == "ok"
```
