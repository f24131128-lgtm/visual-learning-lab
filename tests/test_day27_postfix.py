"""POST_FIX A/B invariants, malicious state/ownership, and local source roundtrip."""
import ast
import copy
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from interactive_lab import (_clean_demo, clean_interactive_lab, commit_lab_values,
    compute_curves, default_values, ensure_lab_state, _reset_parameters, _save_parameter)
from quantity_contract import can_commit, source_values
from representation_contract import bind, registrations
from source_atlas.model import semantic_catalog
from workspace.grounded_twin import derive_links
from workspace.state import open_workspace
from manipulation import lab as direct_lab
from scene.world.state import new_state, apply_parameters, apply_patch
from scene.world.validator import normalize_world
from world_fixtures import complete_projectile_world


def raw_demo(value=-.499):
    return dict(id="demo", title="Model exploration", learning_goal="Compare a source value and a what-if",
        formula_display="y = q x", source_facts=[dict(id="reported", label="Reported quantity", unit="",
            value=value, provenance="source_fixed", source_pages=[1], source_evidence="The material reports this value.")],
        x=dict(id="coordinate", label="Input", min=0., max=2., points=50,
            semantic_role="independent_variable", provenance="source_variable"),
        parameters=[dict(id="exploration", label="Reported quantity", unit="", min=-1., max=101.,
            default=value, step=.1, provenance="hypothetical_exploration", source_baseline_ref="reported",
            source_evidence="", source_pages=[1], expose_control=True, semantic_refs=["entity"])],
        series=[dict(id="curve", label="Model", expression="exploration*coordinate", provenance="derived", semantic_refs=["entity"])],
        derived_metrics=[dict(id="metric", label="Calculated", expression="2*exploration", unit="", provenance="derived", semantic_refs=["entity"])],
        try_this=[], source_pages=[1], related_step_ids=["lesson"])


CAT = {"entity": dict(label="Formal meaning", pages=[1], kind="concept_map", equation="", representations=[]),
       "other": dict(label="Formal meaning", pages=[1], kind="concept_map", equation="", representations=[])}


def demo(raw=None):
    return _clean_demo(raw or raw_demo(), [1], {"lesson"}, lambda p, a: [x for x in p if x in a],
                       version="2.0", catalog=CAT, material="material")


def saved(d):
    return dict(specification=d, values=default_values(d), compare=True, control_generation=0)


def atlas_state():
    return dict(key=("material", "pdf", "en", "1.0", (1,), "fingerprint"),
        atlas=dict(processed_pages=[1], regions=[dict(region_id="region", page=1, bbox=None,
            label="Evidence", type="formula", semantic_ids=["entity"], confidence="low")]))


class ProvenanceTests(unittest.TestCase):
    def test_source_fact_pool_keeps_per_expression_safety_and_supports_constants(self):
        r=raw_demo()
        for i in range(6):r['source_facts'].append(dict(r['source_facts'][0],id='fact'+str(i),value=i))
        r['series'][0]['expression']='reported+exploration*coordinate'
        d=demo(r);compute_curves(d,default_values(d))
        r['series'][0]['expression']='fact0+fact1+fact2+fact3+fact4+fact5'
        with self.assertRaises(ValueError):demo(r)

    def test_empirical_probability_coefficient_and_example_shapes(self):
        for value in (-.499, 1/3, 100., 5., 0.):
            with self.subTest(value=value):
                d=demo(raw_demo(value));s=saved(d);before=copy.deepcopy(d)
                commit_lab_values(d,s,{"exploration":value+.1})
                self.assertEqual(source_values(d),{"reported":value})
                self.assertEqual(d,before)
                self.assertNotEqual(d['source_facts'][0]['id'], d['parameters'][0]['id'])

    def test_fixed_parameter_is_never_a_control(self):
        r=raw_demo();p=r['parameters'][0]
        p.update(provenance='source_fixed',source_baseline_ref=None,source_evidence='The source gives this fixed value.',
                 min=5.,max=5.,default=5.,step=0.,expose_control=False)
        d=demo(r);s=saved(d);before=copy.deepcopy(s)
        for value in (5.,4.,float('nan')):
            with self.assertRaises(ValueError):commit_lab_values(d,s,{'exploration':value})
            self.assertEqual(s,before)
        self.assertFalse(can_commit(d['parameters'][0]))

    def test_fixed_cannot_declare_range_or_widget(self):
        for changes in (dict(min=0.,max=5.,default=5.,step=.1,expose_control=False),
                        dict(min=5.,max=5.,default=5.,step=0.,expose_control=True)):
            r=raw_demo();r['parameters'][0].update(provenance='source_fixed',source_baseline_ref=None,
                source_evidence='Source fact',**changes)
            with self.assertRaises(ValueError):demo(r)

    def test_derived_cannot_become_parameter_or_free_write(self):
        r=raw_demo();r['parameters'][0]['provenance']='derived'
        with self.assertRaises(ValueError):demo(r)
        d=demo();s=saved(d);before=copy.deepcopy(s)
        with self.assertRaises(ValueError):commit_lab_values(d,s,{'metric':2.})
        self.assertEqual(s,before)

    def test_variable_requires_explicit_exposure(self):
        r=raw_demo();r['parameters'][0].update(provenance='source_variable',source_baseline_ref=None,
            source_evidence='This is a source variable.',expose_control=False)
        d=demo(r);self.assertFalse(can_commit(d['parameters'][0]))
        with self.assertRaises(ValueError):commit_lab_values(d,saved(d),{'exploration':.5})

    def test_separate_baseline_id_reference_is_checked(self):
        for ref in ('exploration','missing'):
            r=raw_demo();r['parameters'][0]['source_baseline_ref']=ref
            with self.assertRaises(ValueError):demo(r)
        r=raw_demo();r['source_facts'][0]['id']='exploration'
        with self.assertRaises(ValueError):demo(r)

    def test_bad_source_evidence_and_pages_rejected(self):
        for changes in (dict(source_pages=[2]),dict(source_pages=[]),dict(source_evidence=''),dict(source_evidence='<script>')):
            r=raw_demo();r['source_facts'][0].update(changes)
            with self.assertRaises(ValueError):demo(r)

    def test_forged_widget_and_stale_widget_preserve_all_values(self):
        d=demo();s=saved(d);state=dict(demos={'demo':s});before=copy.deepcopy(s)
        with patch('streamlit.session_state',{'widget':5.}):
            _save_parameter(state,'demo','reported','widget',0)
            _save_parameter(state,'demo','exploration','widget',-1)
        self.assertEqual(s,before)

    def test_atomic_batch_rejects_fixed_and_unsafe_values(self):
        d=demo();s=saved(d);before=copy.deepcopy(s)
        for change in ({'exploration':.5,'reported':1.}, {'exploration':102.}, {'exploration':float('inf')}, {'exploration':True}):
            with self.assertRaises(ValueError):commit_lab_values(d,s,change)
            self.assertEqual(s,before)

    def test_reset_navigation_preserve_source_and_initial_vs_current(self):
        d=demo();lab=dict(demos=[d]);store={}
        with patch('streamlit.session_state',store):
            state=ensure_lab_state('material',lab);s=state['demos']['demo']
            commit_lab_values(d,s,{'exploration':.5})
            workspace=dict(material_id='material',mode='source',focus='entity')
            self.assertTrue(open_workspace(workspace,'explore','entity',CAT))
            self.assertTrue(open_workspace(workspace,'source','entity',CAT))
            self.assertEqual(source_values(d),{'reported':-.499})
            self.assertEqual(s['values']['exploration'],.5)
            self.assertEqual(d['parameters'][0]['default'],-.499)
            _reset_parameters(state,d,'widgets')
            self.assertEqual(s['values'],default_values(d))
            self.assertEqual(source_values(d),{'reported':-.499})

    def test_legacy_is_read_only_and_not_reclassified(self):
        r=raw_demo();r.pop('source_facts');r['x'].pop('semantic_role');r['x'].pop('provenance')
        for p in r['parameters']:
            for k in ('provenance','source_baseline_ref','source_evidence','source_pages','expose_control','semantic_refs'):p.pop(k)
        for group in ('series','derived_metrics'):
            for item in r[group]:item.pop('provenance');item.pop('semantic_refs')
        d=_clean_demo(r,[1],{'lesson'},lambda p,a:p)
        self.assertEqual(d['contract_version'],'legacy_read_only')
        self.assertNotIn('provenance',d['parameters'][0])
        compute_curves(d,default_values(d))
        with self.assertRaises(ValueError):commit_lab_values(d,saved(d),{'exploration':.5})

    def test_runtime_time_is_not_provenance_or_parameter(self):
        r=raw_demo();r['x'].update(semantic_role='runtime_time',provenance=None)
        self.assertIsNone(demo(r)['x']['provenance'])
        r['x']['provenance']='source_variable'
        with self.assertRaises(ValueError):demo(r)

    def test_world_patch_batch_and_tampered_state_protect_source_fact(self):
        raw=complete_projectile_world();p=raw['parameters'][-1]
        p.update(provenance='source_fixed',expose_control=False,min=9.8,max=9.8,default=9.8,step=0.)
        scene=normalize_world(raw,[1]);s=new_state(scene);before=copy.deepcopy(s)
        for action in (lambda:apply_patch(scene,s,dict(op='set_parameter',target_id='grav',value=9.8)),
                       lambda:apply_parameters(scene,s,{'speed':30.,'grav':9.8},s['focus'])):
            with self.assertRaises(ValueError):action()
            self.assertEqual(s,before)

    def test_provenance_decisions_do_not_read_labels(self):
        d=demo();p=d['parameters'][0]
        for label in ('Probability','R','不可調整','source_fixed','time','NASA'):
            changed=dict(p,id='unrelated',label=label)
            self.assertTrue(can_commit(changed))
        tree=ast.parse(Path('quantity_contract.py').read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.FunctionDef) and node.name in ('can_commit','check_commit'):
                self.assertNotIn('label',ast.unparse(node));self.assertNotIn('topic',ast.unparse(node))


class OwnershipTests(unittest.TestCase):
    def test_rejected_renderer_structure_cannot_register_a_model_claim(self):
        analysis=dict(concept_map=dict(suitable=True,nodes=[dict(id='entity',label='Meaning',source_pages=[1])]),
            _formal_representations=dict(concept_map=None,visual_flow=None,comparison=None))
        cat=semantic_catalog(None,analysis)
        self.assertEqual(cat['entity']['representations'],[])
        self.assertEqual(cat['entity']['pages'],[1])

    def test_registry_rechecks_material_and_spec_before_analogy_binding(self):
        from analogy.state import parameter_registry
        d=demo();lab=dict(demos=[d])
        good=parameter_registry(dict(material_id='material',scene=None),lab,None,CAT)
        self.assertEqual(good['lab:demo:exploration']['semantic_ids'],['entity'])
        bad=parameter_registry(dict(material_id='different',scene=None),lab,None,CAT)
        self.assertEqual(bad['lab:demo:exploration']['semantic_ids'],[])
        stale=copy.deepcopy(d);stale['series'][0]['expression']='coordinate'
        bad=parameter_registry(dict(material_id='material',scene=None),dict(demos=[stale]),None,CAT)
        self.assertEqual(bad['lab:demo:exploration']['semantic_ids'],[])

    def test_formal_graph_and_comparison_use_existing_ids(self):
        analysis=dict(primary_visualization=dict(type='concept_map'),concept_map=dict(suitable=True,nodes=[dict(id='entity',label='Meaning',source_pages=[1])]),
            comparison=dict(suitable=True,items=[dict(id='comparison',label='Choice')],criteria=[dict(values=[dict(item_id='comparison',source_pages=[1])])]))
        cat=semantic_catalog(None,analysis)
        self.assertEqual(cat['entity']['representations'][0]['id'],'entity')
        self.assertEqual(cat['comparison']['representations'][0]['id'],'comparison')

    def test_series_metric_and_control_register_exact_refs(self):
        d=demo();reg=registrations(d,CAT,'material',[1])
        self.assertEqual({r['local_id'] for r in reg['entity']},{'exploration','curve','metric'})
        self.assertNotIn('other',reg)

    def test_declared_many_to_many_is_supported(self):
        r=raw_demo();r['series'][0]['semantic_refs']=['entity','other']
        d=demo(r);reg=registrations(d,CAT,'material',[1])
        self.assertEqual([r['local_id'] for r in reg['other']],['curve'])
        self.assertEqual(len(reg['entity']),3)

    def test_lesson_membership_and_equal_labels_confer_no_owner(self):
        d=demo();d['series'][0]['semantic_refs']=[]
        self.assertIsNone(direct_lab.semantic_target(d,{'steps':[dict(id='lesson',visual_refs=[dict(id='other')])]},CAT))
        r=raw_demo()
        for group in ('parameters','series','derived_metrics'):
            for item in r[group]:item['semantic_refs']=[]
        d=demo(r);self.assertEqual(registrations(d,CAT,'material',[1]),{})

    def test_unknown_ref_and_disjoint_source_pages_rejected(self):
        for refs in (['invented'],['entity','entity']):
            r=raw_demo();r['series'][0]['semantic_refs']=refs
            with self.assertRaises(ValueError):demo(r)
        d=demo();cat=copy.deepcopy(CAT);cat['entity']['pages']=[2]
        self.assertEqual(registrations(d,cat,'material',[1,2]),{})

    def test_cross_material_stale_and_forged_registration_rejected(self):
        d=demo();self.assertEqual(registrations(d,CAT,'other-material',[1]),{})
        stale=copy.deepcopy(d);stale['series'][0]['expression']='coordinate'
        self.assertEqual(registrations(stale,CAT,'material',[1]),{})
        forged=copy.deepcopy(d);forged['ownership']['rows'][0]['semantic_id']='other'
        self.assertEqual(registrations(forged,CAT,'material',[1]),{})

    def test_exact_representation_does_not_create_handle(self):
        d=demo();reg=registrations(d,CAT,'material',[1]);links=derive_links(atlas_state(),'material',[1],CAT,[],reg)
        self.assertEqual(set(links['entity']['representation_ids']),{'lab:demo:parameters:exploration','lab:demo:series:curve','lab:demo:derived_metrics:metric'})
        self.assertFalse(links['entity']['manipulable'])
        self.assertEqual(direct_lab.targets(d,default_values(d),'entity'),[])

    def test_source_roundtrip_and_unsupported_focus(self):
        state=dict(material_id='material',mode='source',focus='other')
        for mode in ('explore','source'):
            self.assertTrue(open_workspace(state,mode,'other',CAT))
            self.assertEqual(state['focus'],'other')
        self.assertEqual(derive_links(atlas_state(),'material',[1],CAT)['entity']['representation_ids'],[])

    def test_invalid_optional_lab_preserves_other_learning(self):
        r=raw_demo();r['series'][0]['semantic_refs']=['forged']
        source=dict(version='2.0',suitable=True,reason='Reason',demos=[r])
        before=copy.deepcopy(source)
        result=clean_interactive_lab(source,[1],dict(steps=[]),lambda p,a:p,catalog=CAT,material='material')
        self.assertEqual(result['rejected'],1);self.assertEqual(source,before)


if __name__=='__main__':unittest.main()
