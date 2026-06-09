# Lab Solution — Day 09: Multi-Agent MCP-A2A

**Sinh viên:** Trần Hoàng Hà  
**Ngày:** 09/06/2026  
**Repo:** `https://github.com/tranhoangha94/Batch02-Day9_Multi-Agent_MCP-A2A`

Tài liệu này ghi lại các bài Lab đã hoàn thành trên lớp (Stage 1–4, Exercises, Challenges nâng cao).

---

## Cấu trúc thư mục

```
Lab_Solution/
├── Lab-Solution.md              ← file này
├── common/
│   └── llm.py                   ← Bài 1.2: temperature + max_tokens
├── stage_1_direct_llm/
│   └── main.py                  ← Bài 1.1
├── stage_2_rag_tools/
│   └── main.py                  ← Bài 2.1, 2.2
├── stage_3_single_agent/
│   └── main.py                  ← Bài 3.1, 3.2
├── stage_4_multi_agent/
│   ├── main.py                  ← Bài 4.1, 4.2, Bước 3 vẽ graph
│   └── architecture.png         ← sơ đồ LangGraph
├── exercises/
│   ├── exercise_2_tools.py
│   └── exercise_4_multiagent.py
└── challenges/
    └── demo_challenges.py       ← Challenges 1–4 (CODELAB Phần 6)
```

> **Lưu ý:** Các file trong `Lab_Solution/` import module `common` từ **root repo** (`sys.path` trỏ lên 2 cấp). Chạy lệnh từ thư mục gốc project.

---

## Chuẩn bị môi trường

```powershell
# Từ thư mục gốc repo
uv sync
copy .env.example .env
# Sửa .env: OPENROUTER_API_KEY, OPENROUTER_MODEL
```

**Model đề xuất (tiết kiệm credit):**
```env
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_MAX_TOKENS=1024
```

**OpenRouter API base URL:** `https://openrouter.ai/api/v1`

---

## Phần 1: Direct LLM Calling

### Bài 1.1 — Đổi câu hỏi

**File:** `Lab_Solution/stage_1_direct_llm/main.py`

```python
QUESTION = "Sử dụng bao nhiêu kg ma túy trở lên thì bị tử hình?"
```

**Chạy:**
```powershell
uv run python Lab_Solution/stage_1_direct_llm/main.py
```

### Bài 1.2 — Thêm `temperature=0.3`

**File:** `Lab_Solution/common/llm.py` (và `common/llm.py` ở root)

```python
return ChatOpenAI(
  ...
  max_tokens=int(os.getenv("OPENROUTER_MAX_TOKENS", "1024")),
  temperature=0.3,
)
```

---

## Phần 2: LLM + RAG & Tools

### Bài 2.1 — Thêm `labor_law` vào `LEGAL_KNOWLEDGE`

Entry `labor_law` với keywords tiếng Việt (`lao động`, `sa thải`, …).

### Bài 2.2 — Tool `search_case_law` (Stage 3)

Đã thêm `@tool search_case_law` trong Stage 3; Stage 2 dùng `search_legal_database` + `calculate_damages`.

### Câu hỏi demo Stage 2

```python
QUESTION = (
    "What are the legal remedies and damages available when a company "
    "breaches a contract under the UCC?"
)
```

**Chạy:**
```powershell
uv run python Lab_Solution/stage_2_rag_tools/main.py
```

**Sửa lỗi đã gặp:** `QUESTION` phải là `str`, không phải `tuple` (tránh dấu phẩy thừa sau chuỗi).

---

## Phần 3: Single Agent (ReAct)

### Bài 3.1 — Tool `search_case_law`

```python
@tool
def search_case_law(keywords: str) -> str:
    ...
TOOLS = [..., search_case_law]
```

### Bài 3.2 — Bỏ `verbose=True`

`create_react_agent()` phiên bản mới **không hỗ trợ** `verbose=True`. Dùng `graph.astream()` để in log từng bước.

**Chạy:**
```powershell
uv run python Lab_Solution/stage_3_single_agent/main.py
```

---

## Phần 4: Multi-Agent System

### Bài 4.1 — Thêm `privacy_agent`

- Node `privacy_agent` chuyên GDPR / privacy
- State thêm `privacy_analysis`
- `aggregate` gộp section Privacy & GDPR

### Bài 4.2 — Conditional routing theo keyword

```python
def check_routing(state) -> list[Send]:
    if any(kw in question_lower for kw in ["tax", "irs", "thuế"]):
        tasks.append(Send("call_tax_specialist", state))
    if any(kw in question_lower for kw in ["compliance", "sec", "regulation"]):
        tasks.append(Send("call_compliance_specialist", state))
    if any(kw in question_lower for kw in ["data", "privacy", "gdpr", "dữ liệu"]):
        tasks.append(Send("privacy_agent", state))
```

### Bước 3 — Vẽ graph

Hàm `display_graph()` lưu `architecture.png` trong `stage_4_multi_agent/`.

**Chạy:**
```powershell
uv run python Lab_Solution/stage_4_multi_agent/main.py
```

**Topology:**
```
analyze_law → check_routing → [tax | compliance | privacy] → aggregate → END
```

---

## Exercises

```powershell
uv run python Lab_Solution/exercises/exercise_2_tools.py
uv run python Lab_Solution/exercises/exercise_4_multiagent.py
```

| Exercise | Nội dung |
|----------|----------|
| 2 | `labor_law` KB + `check_statute_of_limitations` |
| 4 | `privacy_agent` + routing + aggregate |

---

## Phần 5: Distributed A2A (Stage 5)

**Windows — khởi động services:**
```powershell
.\start_all.ps1
```

**Test client:**
```powershell
uv run python test_client.py
```

| Service | URL |
|---------|-----|
| Registry | http://localhost:10000 |
| Customer Agent | http://localhost:10100 |
| Law Agent | http://localhost:10101 |
| Tax Agent | http://localhost:10102 |
| Compliance Agent | http://localhost:10103 |

**Dừng services:** `.\stop_all.ps1`

### Bài 5.1 — Trace `trace_id`

`test_client.py` in `trace_id` — tìm trong logs các agent.

### Bài 5.3 — Tax agent prompt ngắn hơn

Đã sửa `tax_agent/graph.py`: *"Keep every response under 150 words."*

---

## Bài tập nâng cao (Challenges 1–4)

**Demo:**
```powershell
uv run python Lab_Solution/challenges/demo_challenges.py
```

| Challenge | Module (root repo) | Mô tả |
|-----------|-------------------|--------|
| 1 Memory | `common/conversation_memory.py` | Customer Agent nhớ theo `context_id` |
| 2 Auth | `common/auth.py` | Header `X-API-Key` khi set `A2A_API_KEY` |
| 3 Retry | `common/retry.py` | Exponential backoff trong `a2a_client.py` |
| 4 Observability | `common/observability.py` | Metrics + LangSmith tùy chọn |

---

## Bảng tổng kết 5 Stages

| Stage | Pattern | File Lab Solution |
|-------|---------|-------------------|
| 1 | Direct LLM | `stage_1_direct_llm/main.py` |
| 2 | LLM + Tools/RAG | `stage_2_rag_tools/main.py` |
| 3 | ReAct Agent | `stage_3_single_agent/main.py` |
| 4 | Multi-Agent | `stage_4_multi_agent/main.py` |
| 5 | A2A Distributed | `start_all.ps1` + `test_client.py` (root) |

---

## Lỗi thường gặp & cách xử lý

| Lỗi | Nguyên nhân | Cách sửa |
|-----|-------------|----------|
| `uv not found` | Chưa cài uv | `pip install uv` |
| HTTP 402 | Hết credit OpenRouter | Đổi model rẻ / nạp credit |
| `UnicodeEncodeError` | Terminal Windows | `sys.stdout.reconfigure(encoding="utf-8")` |
| Agent không gọi tool | `QUESTION` là tuple | Bỏ dấu phẩy thừa |
| `verbose=True` TypeError | API LangGraph mới | Xóa tham số `verbose` |
| `ModuleNotFoundError: IPython` | Thiếu ipython | `uv add ipython` hoặc dùng `architecture.png` |
