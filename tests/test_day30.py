"""Prepared competition assets, local interaction and request boundaries."""
import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
from streamlit.testing.v1 import AppTest
from support import load_app_helpers
from prepared_demo import prepare, install_prepared, ASSETS
from interactive_lab import build_lab_chart, clean_interactive_lab, compute_curves, default_values
from source_atlas.model import semantic_catalog

ROOT = Path(__file__).resolve().parents[1]


class PreparedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = load_app_helpers()

    def test_projectile_derivative_preserves_archive_math_and_ids(self):
        original = json.loads((ASSETS.parent/'projectile/archived_scene.json').read_text(encoding='utf8'))
        derived = json.loads((ASSETS.parent/'projectile/scene.json').read_text(encoding='utf8'))
        for group in ('objects','series','metrics','bindings','inverse_bindings','experiments','invariants'):
            self.assertEqual(original[group],derived[group])
        for a,b in zip(original['quantities'],derived['quantities']):
            self.assertEqual(a,{k:v for k,v in b.items() if k!='provenance'})
        for a,b in zip(original['parameters'],derived['parameters']):
            for key in ('id','min','max','default','step','source_pages'):self.assertEqual(a[key],b[key])
            self.assertEqual(b['provenance'],'hypothetical_exploration')
        self.assertEqual(derived['time'],original['time'])

    def test_both_assets_validate_without_key_and_pdf_hash_matches(self):
        with patch.dict(os.environ,{'VLL_LIVE_AI':'','OPENAI_API_KEY':''}),patch('openai.OpenAI') as provider:
            for e in ('harmonic','projectile'):
                data=prepare(self.h,e)
                self.assertEqual(data['prepared_demo'],e)
                self.assertFalse(data['source_atlas_state']['atlas']['diagnostics'])
                self.assertTrue(set(data['source_atlas_state']['atlas']['processed_pages'])<=set(data['allowed_source_pages']))
            provider.assert_not_called()
        pdf=(ASSETS.parent/'projectile/source.pdf').read_bytes()
        self.assertEqual(hashlib.sha256(pdf).hexdigest(),'688a232388f914ed834e02b28ba343c10b3866e23c3cd94ff38f859957d0c5ec')
        from production_safety import checked_pdf
        with self.assertRaises(ValueError):checked_pdf(pdf,public=True)

    def test_corruption_and_path_ids_preserve_active_material(self):
        for example in ('../harmonic','unknown'):
            with self.assertRaises(ValueError):prepare(self.h,example)
        current=prepare(self.h)
        before=copy.deepcopy(current)
        with patch('prepared_demo.prepare',side_effect=ValueError('controlled integrity rejection')),patch('streamlit.error'):
            install_prepared(current,self.h,'projectile')
        self.assertEqual(current,before)
        original=Path.read_bytes
        def corrupt(p):
            return b'{}' if p.name=='scene.json' else original(p)
        with patch.object(Path,'read_bytes',corrupt),self.assertRaisesRegex(ValueError,'integrity'):
            prepare(self.h,'projectile')

    def test_asset_size_bound_precedes_read(self):
        with patch.object(Path,'stat',return_value=type('Size',(),{'st_size':5*1024*1024})()),self.assertRaisesRegex(ValueError,'bound'):
            prepare(self.h)

    def test_sessions_and_switching_have_independent_stores(self):
        a=prepare(self.h,'projectile');b=prepare(self.h,'projectile');before=copy.deepcopy(b)
        a['learning_scene_state']['world']['parameters']['v0']=50
        a['learning_canvas']['source']['pages']['canary']={}
        self.assertEqual(b,before)
        a['product_language']='en';a['quiz_canary']='old'
        install_prepared(a,self.h,'harmonic')
        self.assertEqual(a['product_language'],'en');self.assertNotIn('quiz_canary',a)
        self.assertNotIn('learning_scene_state',a)

    def lab(self):
        d=prepare(self.h);a=d['analysis'];pages=d['allowed_source_pages']
        path=self.h['clean_learning_path'](a['learning_path'],pages,'flow',a['_formal_representations']['visual_flow'])
        return clean_interactive_lab(a['interactive_lab'],pages,path,self.h['valid_source_pages'],catalog=semantic_catalog(None,a),material=d['analysis_id'])['demos'][0]

    def test_wave_parameters_and_immutable_reference(self):
        demo=self.lab();initial=default_values(demo);base=compute_curves(demo,initial)[1]
        ids=[s['id'] for s in demo['series']]
        for p in demo['parameters']:
            changed=initial | {p['id']:p['min']}
            curves=compute_curves(demo,changed)[1]
            self.assertFalse(np.allclose(base[ids[0]],curves[ids[0]]))
            np.testing.assert_array_equal(base[ids[-1]],curves[ids[-1]])
        from manipulation.lab import targets
        self.assertEqual(targets(demo,initial,'amplitude_phase'),[])
        chart=build_lab_chart(demo,initial,True)
        self.assertEqual(len(chart.data),5)  # Two exploratory pairs + ONE source.
        self.assertEqual(chart.data[-1].line.dash,'dash')

    def test_only_explicit_prepared_labels_follow_ui_language(self):
        demo=self.lab();values=default_values(demo)
        with patch('streamlit.session_state',{'product_language':'zh-TW'}):
            normal=build_lab_chart(demo,values,False)
            prepared=build_lab_chart(demo,values,False,prepared_labels=True)
        self.assertEqual(normal.data[0].name,demo['series'][0]['label'])
        self.assertEqual(normal.layout.xaxis.title.text,demo['x']['label'])
        self.assertEqual(prepared.data[0].name,'探索位移')
        np.testing.assert_array_equal(normal.data[-1].y,prepared.data[-1].y)

    def test_projectile_inverse_atomic_rejection_and_unsupported_ownership(self):
        from manipulation.world import targets,commit
        from manipulation.runtime import world_payload
        d=prepare(self.h,'projectile');wrapper=d['learning_scene_state'];scene=wrapper['scene'];state=wrapper['world']
        state['focus']='vx0';data=world_payload(scene,wrapper)
        target=next(t for t in targets(scene,state) if t['object_id']=='initial_velocity_vector' and t['semantic_id']=='vx0')
        event=dict(scene=data['identity'],revision=state['revision'],token='day30-release',kind='manipulate',target=target['id'],x=25.,y=25.,time=state['time'])
        self.assertTrue(commit(scene,state,data['identity'],event))
        self.assertAlmostEqual(state['parameters']['v0'],np.hypot(25,25))
        before=copy.deepcopy(state)
        self.assertFalse(commit(scene,state,data['identity'],event));self.assertEqual(before,state)
        for changes in ({'revision':-1},{'scene':'wrong'},{'x':float('nan')},{'x':1e7}):
            invalid=event | dict(token='bad',revision=state['revision']) | changes
            self.assertFalse(commit(scene,state,data['identity'],invalid));self.assertEqual(before,state)
        self.assertFalse(any(t['semantic_id']=='x_position' for t in targets(scene,state)))


class BrowserBoundaryTests(unittest.TestCase):
    def test_public_ui_wave_reset_navigation_material_switch_without_requests(self):
        with patch.dict(os.environ,{'VLL_LIVE_AI':'','OPENAI_API_KEY':''}),patch('openai.resources.responses.Responses.create') as responses,patch('openai.resources.files.Files.create') as files:
            app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=45);app.secrets.clear();app.run()
            self.assertFalse(app.exception);self.assertTrue(app.button(key='analyze-material').disabled)
            app.button(key='prepared-open').click().run();self.assertFalse(app.exception)
            self.assertEqual(len(app.get('plotly_chart')),1)
            lab=app.session_state['interactive_lab_state'];material=app.session_state['analysis_id'];demo=next(iter(lab['demos']))
            source=copy.deepcopy(app.session_state['learning_canvas']['source']['pdf_bytes'])
            sliders=list(app.slider)
            self.assertEqual(len(sliders),3)
            sliders[0].set_value(4.).run();self.assertFalse(app.exception)
            self.assertEqual(app.session_state['interactive_lab_state']['demos'][demo]['values']['trial_amplitude'],4.)
            for mode in ('source','practice','explore'):
                app.radio(key='workspace-mode-'+material).set_value(mode).run();self.assertFalse(app.exception)
            self.assertEqual(app.session_state['interactive_lab_state']['demos'][demo]['values']['trial_amplitude'],4.)
            reset=next(b for b in app.button if b.key.endswith('-reset') and b.key.startswith('lab-widget-'))
            reset.click().run();self.assertFalse(app.exception)
            self.assertEqual(app.session_state['interactive_lab_state']['demos'][demo]['values']['trial_amplitude'],3.)
            self.assertEqual(app.session_state['learning_canvas']['source']['pdf_bytes'],source)
            app.button(key='prepared-projectile').click().run();self.assertFalse(app.exception)
            self.assertNotEqual(app.session_state['analysis_id'],material)
            self.assertEqual(app.session_state['prepared_demo'],'projectile')
            app.radio(key='workspace-mode-'+app.session_state['analysis_id']).set_value('explore').run();self.assertFalse(app.exception)
            app.button(key='prepared-open').click().run();self.assertFalse(app.exception)
            self.assertNotIn('world',app.session_state['learning_scene_state'])
            responses.assert_not_called();files.assert_not_called()


if __name__=='__main__':unittest.main()
