# godot-audit

**语言**：
[English](README.md) ·
[Français](README.fr.md) ·
[Deutsch](README.de.md) ·
[中文](README.zh.md) ·
[日本語](README.ja.md) ·
[Italiano](README.it.md) ·
[Español](README.es.md)

[![Python versions](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/olivierpons/godot-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/olivierpons/godot-audit/actions/workflows/ci.yml)

根据您的约定审计 Godot 项目布局。只读:从不修改任何文件。

`godot-audit` 检查您的 `.tscn` 和 `.gd` 文件是否被一致地组织(split 或 colocated)、资产文件名是否为 snake_case、是否没有过时的 `_old`/`_bak` 版本残留、以及是否没有 `.uid` / `.import` 伴随文件变为孤立。近似重复的文件名(例如 `skeleton` 对 `skeletton` 这样的拼写错误)会被标记,而带编号的变体(`v1`、`v2` 等)会被正确识别并忽略。

## 功能特性

- **支持两种项目布局**:
  - `split` — `scenes/entities/slime.tscn` + `scripts/entities/slime.gd`(Godot 默认文档化的约定)
  - `colocated` — `features/entities/slime.tscn` + `features/entities/slime.gd`(按功能分组,默认)
- **六种检查类别**:mirroring、naming、stale names、near-duplicates、backups、orphan companions。
- **Rich 终端输出**,带纯 ANSI 回退。
- **`-h` / `--help` 分离**:面向熟练用户的简短备忘录,带示例的发现式完整文档。
- **CI 友好**:非零退出代码、`--no-color`、`--no-rich`、JSON 输出。
- **多种输出格式**:文本(Rich 表格)、JSON、Markdown。
- **布局感知建议**:每个警告都附带具体的移动建议。

## 安装

直接从 GitHub 安装:

```bash
# 最新版本
pip install git+https://github.com/olivierpons/godot-audit.git

# 固定到特定发布版本
pip install git+https://github.com/olivierpons/godot-audit.git@v1.0.0
```

这将自动从其 GitHub 仓库拉取 `cli-toolkit[rich]`。

需要 Python 3.14 或更高版本。

## 快速开始

```bash
# 审计当前目录(默认 colocated 布局)
godot-audit

# 审计特定的 Godot 项目
godot-audit ~/godotprojects/my_game

# 改用 split 布局
godot-audit ~/godotprojects/my_game --layout split

# 长报告将摘要放在底部
godot-audit . --summary-position bottom

# 严格 CI 模式:即使是 INFO 问题也让构建失败
godot-audit . --strict --no-color --no-rich --quiet

# 导出为 JSON 以供进一步处理
godot-audit . --format json --output audit.json

# 用于 GitHub PR 评论的 Markdown 报告
godot-audit . --format markdown > audit.md
```

## 选项

每个选项都有短格式和长格式。`-h` 打印紧凑备忘录;`--help` 打印带示例的完整文档。

| 短 | 长 | 说明 |
| --- | --- | --- |
| | `PATH` | Godot 项目根路径(默认:当前目录) |
| `-y` | `--layout` | `split` 或 `colocated`(默认:`colocated`) |
| `-f` | `--format` | `text`、`json` 或 `markdown`(默认:`text`) |
| `-o` | `--output` | 写入文件而非 stdout |
| `-c` | `--category` | 只报告此类别(可重复) |
| `-s` | `--severity` | 最低严重程度:`INFO`、`WARN`、`ERROR`(默认:`INFO`) |
| `-t` | `--threshold` | 近似重复检测的相似度阈值(默认:`0.88`) |
| `-i` | `--ignore-dir` | 添加到忽略列表的目录(可重复) |
| `-p` | `--summary-position` | `top`、`bottom` 或 `none`(默认:`top`) |
| `-S` | `--strict` | 即使 INFO 问题也非零退出 |
| `-q` | `--quiet` | 隐藏摘要面板(`-p none` 的别名) |
| `-R` | `--no-rich` | 强制纯文本输出 |
| `-n` | `--no-color` | 禁用 ANSI 颜色 |
| `-v` | `--verbosity` | 0=silent, 1=normal, 2=verbose, 3=debug |
| `-l` | `--list-categories` | 列出所有检查类别并退出 |
| `-L` | `--list-ignored-dirs` | 列出默认忽略目录并退出 |
| `-V` | `--version` | 打印版本并退出 |
| `-h` | | 简短帮助备忘录 |
| | `--help` | 带示例的完整帮助 |

## 检查类别

| 类别 | 检测内容 |
| --- | --- |
| `mirroring` | 依赖布局。`split`:脚本位于 `scripts/` 根目录,而场景位于 `scenes/<subdir>/`。`colocated`:脚本的匹配场景存在于不同的目录中。 |
| `naming` | 非 snake_case 的文件名(空格、连字符、大写字母、特殊字符)。建议一个 snake_case 替代。严重程度:INFO。 |
| `stale_name` | 以 `_old`、`_bak`、`_backup`、`_copy`、`_tmp`、`_temp`、`_new`、`_todelete` 或 `_deprecated` 结尾的文件。升级或删除。 |
| `near_duplicate` | 同一目录中词干几乎相同的文件对(捕获像 `skeleton` 对 `skeletton` 这样的拼写错误)。带编号的变体(`v1`/`v2`、`01`/`02`、`Bird Call 1` / `Bird Call 3`)会被自动跳过。 |
| `backup` | 编辑器备份:`*.bak`、`*.bak.*`、`*.orig`、以 `~` 结尾的名称。 |
| `orphan_companion` | 源文件(`foo.gd`、`bar.mp3`)缺失的 `.uid` 或 `.import` 文件。可安全删除。 |

## 退出代码

| 代码 | 含义 |
| --- | --- |
| `0` | 当前严重程度筛选下没有问题 |
| `1` | 报告了至少一个 `WARN` 或 `ERROR`(或设置了 `--strict` 时的任何 `INFO`) |
| `2` | 无效输入:`PATH` 不存在或不是 Godot 项目 |

## 布局约定

### Split 布局(Godot 默认文档化)

```
res://
├── scenes/
│   ├── entities/
│   │   └── slime.tscn
│   └── levels/
│       └── level_01.tscn
└── scripts/
    ├── entities/
    │   └── slime.gd
    └── levels/
        └── level_01.gd
```

场景和脚本位于相互镜像的不同顶级目录中。审计:

```bash
godot-audit . --layout split
```

### Colocated 布局(默认,推荐)

```
res://
├── features/
│   ├── entities/
│   │   ├── slime.tscn
│   │   └── slime.gd
│   └── levels/
│       ├── level_01.tscn
│       └── level_01.gd
├── autoload/         # 单例,无 .tscn
├── components/       # 可复用逻辑,无 .tscn
└── addons/
```

场景和它的附加脚本并排存放。`autoload/`、`components/` 和 `addons/` 下的脚本免于共位检查,因为它们合法地只是脚本。审计:

```bash
godot-audit .
```

## 安全地移动文件

当某个问题建议移动脚本或场景时,**始终使用 Godot 的 FileSystem 面板**(编辑器内拖放),切勿在命令行使用 `mv`。Godot 在移动时会重写每个 `.tscn` 引用;而操作系统的 `mv` 不会,您的场景最终会指向丢失的脚本。

## 环境变量

| 变量 | 效果 |
| --- | --- |
| `NO_COLOR` | 设置时,禁用所有 ANSI 颜色和 Rich 样式。见 [no-color.org](https://no-color.org/)。 |

## 开发

```bash
git clone https://github.com/olivierpons/godot-audit.git
cd godot-audit
pip install -e .
pip install pytest pytest-cov ruff mypy

# 测试
pytest

# 代码检查 + 格式化
ruff check .
ruff format .

# 针对真实 Godot 项目运行
python -m godot_audit.cli ~/my_godot_project
```

## 许可证

MIT — 见 [LICENSE](LICENSE)。
