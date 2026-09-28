# 接口自动化测试框架（学习项目）

基于 **Python + pytest + requests** 搭建的接口自动化测试框架，以 **GitHub 官方 API** 作为真实被测接口，覆盖请求封装、数据驱动、失败重试、测试报告、多环境、jsonpath 断言等能力。

本 README 同时是项目的知识沉淀文档，覆盖全部关键知识点。

---

## 技术栈

| 组件 | 用途 |
|---|---|
| Python 3.13 | 开发语言 |
| requests | HTTP 请求库 |
| pytest | 测试框架（用例、断言、参数化、fixture） |
| pytest-html | 生成可视化测试报告 |
| pytest-rerunfailures | 失败自动重试，降低网络抖动误报 |
| jsonpath | 从 JSON 响应里精准取值断言 |

## 被测接口

- **GitHub REST API**：`https://api.github.com`
- 无需注册即可访问公开接口（查用户、仓库、搜索）
- 真实接口才有的规则：
  - 请求头必须带 `User-Agent`，否则返回 403
  - 未认证限流 **60 次/小时**；带 Token 认证后升到 **5000 次/小时**

## 项目结构

```
.
├── pytest.ini              # pytest 配置（重试、默认参数、收集目录）
├── conftest.py             # 共享 fixture + --env 多环境参数
├── requirements.txt        # 依赖清单
├── common/                 # 封装层
│   ├── http_client.py      # 统一请求 + 断言 + Token 认证
│   └── config.py           # 多环境配置
├── tests/                  # 用例层
│   ├── test_github_basic.py  # 基础：查用户/仓库、404、限流头
│   ├── test_parametrize.py   # 参数化与数据驱动
│   ├── test_encapsulated.py  # 封装后的用例（调用 common/http_client.py）
│   ├── test_fixture.py       # fixture 与 Session 复用
│   ├── test_env.py           # 多环境切换
│   └── test_jsonpath.py      # jsonpath 断言
├── examples/               # 入门演示
│   ├── demo_github.py        # requests 基础用法（打印真实响应）
│   └── test_rerun_demo.py    # 失败重试演示
└── README.md
```

## 快速开始

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 运行全部测试（已配置失败重试 + 详细输出）
pytest

# 3. 生成测试报告（手动）
pytest --html=report.html --self-contained-html
```

## 获取 GitHub Token（可选，推荐）

未认证访问限流 60 次/小时，跑几轮测试就容易用完（报 403）。建议配置一个 Token：

1. GitHub → 头像 → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**
2. 权限选 **只读公共数据**（Repository access → Public Repositories）即可
3. 生成后复制 Token，在本机设置环境变量：

```bash
# macOS（写入 ~/.zshrc 永久生效）
export GITHUB_TOKEN=你的token
```

配置后 `common/http_client.py` 会自动带上 `Authorization: Bearer` 请求头，限流升到 5000 次/小时。

---

## 核心知识点

> 学习路线：requests 发请求 → pytest 断言 → 参数化 → 封装分层 → fixture/Session → 多环境 → jsonpath → 失败重试 → 测试报告 → 真实接口的坑 → Git/GitHub

### 1. requests 发请求

```python
import requests

requests.get(url, params={"q": "pytest"})          # 查询参数 → URL 拼 ?q=pytest
requests.post(url, json={"name": "x"})             # JSON 请求体（body）
requests.get(url, headers={"User-Agent": "my-tool"}) # 请求头
```

- **要点**：HTTP 方法是「动作」（GET 查 / POST 建 / PUT 改 / DELETE 删），body 是「带的东西」。
- GET 一般不带 body（参数放 URL）；POST/PUT/PATCH 才带 body。
- `params` 会自动拼到 URL 上；`json=` 会自动序列化并设置 `Content-Type: application/json`。

### 2. pytest 断言

```python
def test_simple_get():
    r = requests.get("https://api.github.com/users/octocat", headers={"User-Agent": "x"})
    assert r.status_code == 200   # 条件成立才通过，否则标红失败
```

- `assert` 是测试的灵魂：表达式为 `True` 通过，为 `False` 则失败并抛 AssertionError。
- **命名规则**：文件名、函数名都要 `test_` 开头，pytest 才会自动发现。

### 3. 参数化 @pytest.mark.parametrize

```python
import pytest

@pytest.mark.parametrize("username", ["octocat", "torvalds", "gaearon"])
def test_user_exists(username):
    r = requests.get(f"https://api.github.com/users/{username}", headers={"User-Agent": "x"})
    assert r.status_code == 200
    assert r.json()["login"] == username
```

- **一个函数跑多组数据**：`parametrize` 第一个参数名要和函数参数对上，列表里每个值跑一遍。
- 多参数写法：`@pytest.mark.parametrize("owner,repo", [("a","b"), ("c","d")])`。
- 这就是「数据驱动」的真身：把测试数据和用例逻辑分离。

### 4. 封装分层（框架的本质）

- **用例层**（`tests/`）：只写「测什么」——调什么接口、断言什么结果。
- **封装层**（`common/`）：管「怎么发请求、怎么断言」。

```python
# common/http_client.py
BASE_URL = "https://api.github.com"

def api_get(path, **kwargs):
    return requests.get(f"{BASE_URL}{path}", headers=..., **kwargs)

def assert_status(resp, code=200):
    assert resp.status_code == code, f"期望 {code}，实际 {resp.status_code}"
```

```python
# 用例层
from common.http_client import api_get, assert_status

def test_get_user():
    r = api_get("/users/octocat")
    assert_status(r)
    assert r.json()["login"] == "octocat"
```

- **要点**：换环境、换认证方式、改断言规则，只改封装层一处，用例一行不动。

### 5. fixture 与 Session 复用

```python
import pytest

@pytest.fixture
def test_data():
    print("准备数据")      # ← setup（类似构造函数）
    yield {"user": "shi"} # ← yield 是分界
    print("清理数据")      # ← teardown（类似析构函数）

@pytest.fixture(scope="session")
def client():
    s = requests.Session()  # 复用 TCP 连接（keep-alive）
    yield s
    s.close()
```

- **fixture** = 测试的前置/后置，类比 C++ 构造函数 / 析构函数。
- **yield** 之前是 setup，之后是 teardown。
- **scope**：`function`（默认，每个用例建一次）/ `module`（每文件）/ `session`（整个会话）。
- `requests.Session()` 复用同一连接 + 统一请求头，省掉每次三次握手开销。

### 6. 多环境配置（--env）

```python
# conftest.py（pytest 自动读取的特殊文件）
def pytest_addoption(parser):
    parser.addoption("--env", default="test", help="选择环境")

@pytest.fixture(scope="session")
def base_url(request):
    env = request.config.getoption("--env")
    return ENVIRONMENTS[env]
```

```python
# common/config.py
ENVIRONMENTS = {
    "test": "https://api.github.com",
    "staging": "https://api.github.com",
    "prod": "https://api.github.com",
}
```

- `conftest.py` 放共享 fixture 和自定义命令行参数，pytest 自动加载。
- 换环境只改 `pytest --env=prod` 一个参数，代码一行不动。
- 真实公开 API 只有一个地址，所以三个环境暂时同址；接入公司后端后就是三个真实域名。

### 7. jsonpath 断言

```python
from jsonpath import jsonpath

data = {"owner": {"login": "octocat"}, "repos": [{"name": "a"}, {"name": "b"}]}

jsonpath(data, "$.owner.login")   # ['octocat'] 逐层取值
jsonpath(data, "$.repos[*].name") # ['a', 'b']  取列表所有元素
```

- 语法：`$` 根、`.key` 字段、`[0]` 下标、`[*]` 全部、`..key` 递归搜索。
- **坑**：返回的是**列表**（即使单个值），要单值就 `[0]`；字段不存在返回 `False` 而非抛异常。

### 8. 失败重试（pytest-rerunfailures）

```ini
# pytest.ini
reruns = 2        # 失败后最多重试 2 次
reruns_delay = 1  # 每次重试前等待 1 秒
```

- **flaky test（不稳定测试）**：用例本身没错，但网络/环境抖动偶尔挂。
- **区分**：真 bug 每次必挂；flaky 时好时坏 → 用重试解决，而不是当成 bug。
- 也可命令行临时指定：`pytest --reruns 2 --reruns-delay 1`。

### 9. 测试报告（pytest-html）

```bash
pytest --html=report.html --self-contained-html
```

- `--html=report.html`：报告输出文件。
- `--self-contained-html`：CSS/JS 内嵌，单文件双击即开，不用联网。
- **原理**：pytest 收集结果 → 插件（pytest-html）用 jinja2 模板渲染成 HTML。
- **手动 vs 自动**：手动在命令行加参数；自动写进 `pytest.ini` 的 `addopts`。

### 10. pytest.ini 配置管理

```ini
[pytest]
addopts = -v -s           # 默认命令行参数（-v 详细、-s 显示 print）
testpaths = tests         # 只收集 tests/ 目录
pythonpath = .            # 把项目根目录加入 sys.path，让 common 包可导入
python_files = test_*.py  # 只收集 test_ 开头的文件
reruns = 2
reruns_delay = 1
```

- `addopts`：每次 pytest 自动带上的参数。
- **优先级**：命令行参数 > pytest.ini 配置。
- 语法规则：`[pytest]` 段落标题 + `键 = 值`，`#` 开头是注释。

### 11. 真实接口的坑（GitHub API 实战）

1. **User-Agent 隐性要求**：不带（或空）`User-Agent` 返回 403，很多真实 API 都有这类「文档没明说」的坑。
2. **限流（Rate Limit）**：未认证 60 次/小时，认证 5000 次/小时；每次响应头都带 `X-RateLimit-Remaining`（剩余额度），可读取判断。
3. **认证**：`Authorization: Bearer <token>`；Token 从环境变量注入（`os.environ.get("GITHUB_TOKEN")`），不写死在代码里、不进 git 仓库。
4. **鉴权测试**：验证未认证的写操作被拒绝（401），是接口测试里的安全类用例。

### 12. Git / GitHub

```bash
git init -b main                          # 初始化
git add . && git commit -m "说明"          # 暂存 + 提交
git remote add origin git@github.com:xxx/xxx.git
git push -u origin main                   # 首次推送
git push                                 # 后续推送
```

- `.gitignore`：排除 `__pycache__/`、`report.html` 等生成物，别把环境变量/token 提交进去。
- 修改已推送的提交作者：`git commit --amend --reset-author` + `git push --force-with-lease`。

---

## 框架设计

- **分层**：用例层（`tests/`）与封装层（`common/`）分离，用例只关心"测什么"；
- **配置集中**：域名、Token、重试规则集中在 `common/` / `pytest.ini`，换环境只改一处；
- **稳定性**：失败自动重试（默认 2 次、间隔 1 秒），应对网络抖动；
- **鉴权测试**：验证未认证的写操作被拒绝（401），覆盖安全类用例；
- **报告**：一键生成 HTML 可视化报告。
