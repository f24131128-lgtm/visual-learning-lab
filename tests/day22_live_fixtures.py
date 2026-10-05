"""Shape-derived from human live Queue report and normal production reproduction.

Not a captured verbatim failing response: old compiler discarded that response.
No production code imports this fixture. Semantic/runtime ID reuse reproduces
the old validator's independently confirmed identity-contract defect.
"""
from day22_fixtures import plan, empty_process
from support import fixture

EXACT_QUEUE_TEXT = """A queue is a FIFO data structure.

FIFO means First In, First Out.

enqueue(x):
adds x to the rear of the queue.

dequeue():
removes the item at the front.

front:
returns the first item without removing it.

Example:
Start with A, B.
Enqueue C → A, B, C.
Dequeue → B, C."""


def analysis():
    result = fixture("flow")
    labels = dict(queue="佇列 Queue", fifo="FIFO 先進先出", rear="後端 rear", front_end="前端 front", enqueue="enqueue(x)", dequeue="dequeue()", front_operation="front")
    result["concept_map"].update(suitable=True, nodes=[dict(id=i, label=l, source_pages=[], role="central" if i == "queue" else "primary") for i, l in labels.items()], edges=[])
    flow = dict(add_step="從後端加入元素", order_step="依加入順序排列", observe_step="查看前端元素", remove_step="從前端移除元素")
    result["visual_flow"].update(suitable=True, nodes=[dict(id=i, label=l, source_pages=[], role="primary") for i, l in flow.items()], edges=[dict(source="add_step", target="order_step", label="加入"), dict(source="order_step", target="observe_step", label="查看"), dict(source="observe_step", target="remove_step", label="移除")])
    result["primary_visualization"] = dict(type="flow", reason="觀察操作之間的順序。")
    result["learning_scene_candidate"] = dict(suitable=False, domain="none", reason="離散操作，沒有物理模型。")
    result["quick_summary"] = "從後端加入、從前端移除的先進先出有序集合。"
    for item in result["key_concepts"]: item["source_pages"] = []
    for item in result["relationships"]: item["source_pages"] = []
    result["interactive_lab"] = dict(suitable=False, reason="", demos=[])
    return result


def candidate(kind="fifo"):
    process = empty_process()
    process["collections"] = [dict(id="queue", semantic_id="queue", label="", initial=["A", "B"], capacity=6, first_label="Front", last_label="Rear")]
    for semantic, operation in (("enqueue", "append"), ("dequeue", "remove_first" if kind == "fifo" else "remove_last")):
        process["transitions"].append(dict(id=semantic, semantic_id=semantic, label="", explanation="", operation=operation, target_id="queue", from_state="", to_state=""))
    process["annotations"] = [dict(semantic_id="unknown_decoration", text="Unsupported optional decoration"), dict(semantic_id="fifo", text="保持剩餘項目的原有順序。")]
    return plan("process", ["queue", "enqueue", "dequeue", "fifo"], ["ordered_collection", "transitions", "structure", "interaction_value"], pages=[], process=process)
