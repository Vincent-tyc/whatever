

# 学科知识整合智能体

基于AI的医学教材知识整合系统。支持多格式教材上传、知识图谱构建与可视化、跨教材知识整合（压缩至30%）、RAG精准问答、多轮对话迭代优化。
## 写在前面：该项目的不足是没有成功使用embedding，使得教材的读取缓慢，只能手动每次读取一部分。其余部分运作正常。
## 环境要求

### Python 依赖

```bash
pip install -r requirements.txt
```

**Windows 用户注意事项：** `faiss-cpu` 在 Windows 上可能没有预编译的 pip wheel。如果 pip 安装失败，请通过 conda 安装：

```bash
conda install -c pytorch faiss-cpu
```

### 前端依赖

```bash
cd src/frontend
npm install
```

## 配置说明

复制 `.env.example` 为 `.env`，填入 DeepSeek API Key：

```
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

## 启动命令

```bash
# 终端1：启动后端（端口8001）
python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8001 --reload

# 终端2：启动前端（端口5173）
cd src/frontend
npx vite
```

打开浏览器访问 **http://localhost:5173**

## 使用说明

1. 后端启动时自动预加载 `extracted_texts/` 目录下的7本医学教材
2. 点击教材旁的「构建图谱」为每本教材生成知识图谱（约30秒/本）
3. 上传2本以上教材后，点击「执行跨教材整合」进行语义对齐和去重
4. 切换到「RAG问答」Tab，点击「建立RAG索引」后可进行精准问答
5. 在「对话」Tab中与系统交互调整整合方案
6. 在「报告」Tab查看整合报告并导出 Markdown

## 项目结构

```
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── backend/
│   │   ├── main.py              # FastAPI入口
│   │   ├── config.py            # 配置模块
│   │   ├── models/schemas.py    # Pydantic数据模型
│   │   ├── routers/             # API路由
│   │   │   ├── upload.py        # 上传
│   │   │   ├── graph.py         # 图谱
│   │   │   ├── integration.py   # 整合
│   │   │   ├── rag.py           # RAG
│   │   │   └── dialogue.py      # 对话
│   │   └── services/            # 业务逻辑
│   │       ├── parser.py        # 文件解析
│   │       ├── extractor.py     # LLM知识提取
│   │       ├── graph_builder.py # 图谱构建
│   │       ├── embedder.py      # BGE嵌入
│   │       ├── integrator.py    # 跨教材整合
│   │       ├── rag_service.py   # RAG服务
│   │       └── dialogue.py      # 对话管理
│   └── frontend/
│       ├── vite.config.js
│       └── src/
│           ├── App.vue          # 三栏布局
│           ├── api.js           # API封装
│           └── components/
│               ├── LeftPanel.vue      # 教材管理
│               ├── GraphView.vue      # 知识图谱(ECharts)
│               ├── RightPanel.vue     # Tab容器
│               ├── IntegrationTab.vue # 整合操作
│               ├── RagTab.vue         # RAG问答
│               ├── DialogueTab.vue    # 多轮对话
│               └── ReportTab.vue      # 整合报告
├── docs/
│   ├── 需求分析.md
│   ├── 系统设计.md
│   ├── Agent架构说明.md
│   └── 接口文档.md
└── report/
    └── 整合报告.md
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI (Python) |
| 前端框架 | Vue 3 + Vite |
| 大模型 | DeepSeek API |
| 向量嵌入 | BGE-small-zh (sentence-transformers) |
| 向量检索 | FAISS |
| 知识图谱可视化 | ECharts |
| 文件解析 | PyMuPDF (PDF) + 原生解析 (MD/TXT) |

## 引用开源项目

- FastAPI (MIT)
- Vue.js (MIT)
- ECharts (Apache 2.0)
- FAISS (MIT)
- PyMuPDF (AGPL)
- sentence-transformers (Apache 2.0)
