"""Synthetic acceptance declarations/materials. Never imported by production."""
import copy
from learning_world.schema import FEATURES, VERSION
from support import fixture
from source_atlas.model import semantic_catalog
from analogy_fixtures import formal, spec as analogy_spec
from world_fixtures import complete_projectile_world
from scene.world.validator import normalize_world
from scene.validator import normalize_scene
from scene_fixtures import two_toss_scene


def empty_process(): return dict(collections=[], states=[], transitions=[], annotations=[])


def plan(preferred, ids, flags, pages=(1,), process=None):
    return dict(version=VERSION, focus_ids=list(ids), source_pages=list(pages),
                features={k: k in flags for k in FEATURES}, preferred=preferred,
                reason="The source structure supports this representation.", process=process or empty_process())


def discrete(kind="fifo"):
    analysis = fixture()
    labels = dict(collection="Ordered items", insert="Insert at the last end", remove="Remove at the first end")
    if kind == "lifo": labels["remove"] = "Remove at the last end"
    if kind == "states": labels = dict(collection="Workflow status", insert="Start work", remove="Finish work")
    nodes = [dict(id=i, label=l, source_pages=[1], role="primary") for i, l in labels.items()]
    analysis["concept_map"].update(nodes=nodes, edges=[])
    analysis["visual_flow"].update(suitable=False, nodes=[], edges=[])
    analysis["learning_scene_candidate"] = dict(suitable=False, domain="none", reason="Discrete state")
    # Practice refers to the same transition entity; no separate exercise identity.
    analysis["learning_path"]["steps"][0]["visual_refs"] = [dict(type="concept_map_node", id="remove")]
    process = empty_process()
    if kind == "states":
        process["states"] = [dict(id="status_state", semantic_id="collection", label="Status", values=["idle", "working", "done"], initial="idle")]
        for i, before, after in (("insert", "idle", "working"), ("remove", "working", "done")):
            process["transitions"].append(dict(id="act_"+i, semantic_id=i, label=labels[i], explanation="Observe the defined state transition.", operation="set_state", target_id="status_state", from_state=before, to_state=after))
    else:
        process["collections"] = [dict(id="items_state", semantic_id="collection", label="Ordered items", initial=["A", "B"], capacity=6, first_label="Front", last_label="Rear" if kind == "fifo" else "Top")]
        for i, op in (("insert", "append"), ("remove", "remove_first" if kind == "fifo" else "remove_last")):
            process["transitions"].append(dict(id="act_"+i, semantic_id=i, label=labels[i], explanation="The operation preserves the order of remaining items.", operation=op, target_id="items_state", from_state="", to_state=""))
    return analysis, semantic_catalog(None, analysis), plan("process", list(labels), ["structure", "transitions", "interaction_value"] + ([] if kind == "states" else ["ordered_collection"]), process=process)


def cases():
    result = []
    scene, catalog = formal("phase")
    result.append(dict(name="sinusoid / phase", family="dynamic", runtime="scene.world", scene=scene, catalog=catalog,
        raw=plan("dynamic", ["angle", "wave"], ["equations", "continuous_parameters", "time_dynamics", "spatial_relations", "interaction_value"])))
    analysis, catalog, raw = discrete()
    result.append(dict(name="FIFO queue", family="process", runtime="learning_world.process", scene=None, analysis=analysis, catalog=catalog, raw=raw))
    scene, catalog = formal("electricity")
    result.append(dict(name="Ohm's law", family="analogy", runtime="analogy", scene=scene, catalog=catalog,
        raw=plan("analogy", ["voltage", "resistance", "current"], ["equations", "continuous_parameters", "analogy_suitable", "interaction_value"])))
    scene = normalize_world(complete_projectile_world(), [1, 2])
    catalog = semantic_catalog(scene)
    result.append(dict(name="projectile", family="spatial", runtime="scene.world", scene=scene, catalog=catalog,
        raw=plan("spatial", ["vx", "gravity"], ["equations", "continuous_parameters", "time_dynamics", "spatial_relations", "interaction_value"])))
    scene = normalize_scene(two_toss_scene(), [1, 2])
    catalog = semantic_catalog(scene)
    result.append(dict(name="probability", family="structural", runtime="scene.probability", scene=scene, catalog=catalog,
        raw=plan("structural", list(catalog)[:2], ["finite_outcomes", "set_relations", "structure", "interaction_value"], pages=())))
    catalog = dict(definition=dict(label="A naming convention defines how a term is used, without state or quantitative relations.", pages=[1], kind="concept_map", equation="", representations=[]))
    result.append(dict(name="terminology definition", family="none", runtime="existing explanation", scene=None, catalog=catalog,
        raw=plan("none", ["definition"], [])))
    return copy.deepcopy(result)
