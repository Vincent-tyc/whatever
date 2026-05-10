from openai import OpenAI
from src.backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from src.backend.models.schemas import DialogueMessage, DialogueRequest, DialogueResponse, IntegrationDecision
from src.backend.services.integrator import integration_result_store

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

DIALOGUE_SYSTEM_PROMPT = """你是学科知识整合助教。教师可以与你讨论整合决策，你可以：
1. 解释为什么某项决策被做出（合并/保留/删除）
2. 根据教师反馈修改整合决策
3. 回答关于知识图谱和整合结果的问题

当前整合结果：
{integration_context}

请在回答时：引用具体的决策ID、解释推理过程、接受教师合理建议并修改。
"""


async def process_dialogue(req: DialogueRequest) -> DialogueResponse:
    ctx_parts = []
    if integration_result_store:
        ctx_parts.append(f"压缩比: {integration_result_store.compression_ratio:.1%}")
        ctx_parts.append(f"决策总数: {len(integration_result_store.decisions)}")
        for d in integration_result_store.decisions[:10]:
            ctx_parts.append(f"  {d.decision_id}: {d.action} {d.result_name} (置信度{d.confidence}) — {d.reason[:80]}")

    system_prompt = DIALOGUE_SYSTEM_PROMPT.format(integration_context="\n".join(ctx_parts))

    messages = [{"role": "system", "content": system_prompt}]
    for msg in req.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.5,
        max_tokens=800
    )

    reply = response.choices[0].message.content

    new_history = req.history + [
        DialogueMessage(role="user", content=req.message),
        DialogueMessage(role="assistant", content=reply)
    ]

    decision_updates = _detect_decision_changes(req.message)

    return DialogueResponse(
        reply=reply,
        history=new_history,
        decision_updates=decision_updates
    )


def _detect_decision_changes(message: str) -> list[IntegrationDecision]:
    """简单关键词检测：如果教师说"保留"/"删除"/"合并"，尝试修改对应决策"""
    updates = []
    if not integration_result_store:
        return updates

    for d in integration_result_store.decisions:
        if d.result_name in message:
            if "保留" in message and d.action == "remove":
                d.action = "keep"
                updates.append(d)
            elif "不应该" in message and "合并" in message and d.action == "merge":
                d.action = "keep_separate"
                updates.append(d)
    return updates
