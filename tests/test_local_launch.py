import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('local_launch',ROOT/'tools/run_local.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)

class LocalLaunchTests(unittest.TestCase):
    def test_loopback_only_and_bounded_port(self):
        command=launcher.launch_command(8502)
        self.assertEqual(command[command.index('--server.address')+1],'127.0.0.1')
        self.assertNotIn('--server.enableXsrfProtection',command)
        for port in (0,1023,65536):
            with self.assertRaises(ValueError):launcher.launch_command(port)

    def test_demo_never_prompts_and_forces_ai_off(self):
        with patch('sys.argv',['run_local','--demo']),patch.dict(os.environ,{'VLL_LIVE_AI':'private'}),patch.object(launcher.getpass,'getpass') as prompt,patch.object(launcher.subprocess,'call',return_value=0) as call:
            self.assertEqual(launcher.main(),0)
            prompt.assert_not_called()
            self.assertEqual(call.call_args.kwargs['env']['VLL_LIVE_AI'],'')

    def test_private_key_stays_in_child_environment(self):
        with patch('sys.argv',['run_local']),patch.dict(os.environ,{},clear=True),patch.object(launcher.getpass,'getpass',return_value='offline-test-key'),patch.object(launcher.subprocess,'call',return_value=0) as call:
            launcher.main()
            self.assertEqual(call.call_args.kwargs['env']['OPENAI_API_KEY'],'offline-test-key')
            self.assertNotIn('offline-test-key',' '.join(call.call_args.args[0]))
            self.assertEqual(call.call_args.kwargs['env']['VLL_LIVE_AI'],'private')

    def test_prompt_key_replaces_stale_environment_key(self):
        with patch('sys.argv',['run_local','--prompt-key']),patch.dict(os.environ,{'OPENAI_API_KEY':'stale'}),patch.object(launcher.getpass,'getpass',return_value='replacement'),patch.object(launcher.subprocess,'call',return_value=0) as call:
            launcher.main()
            self.assertEqual(call.call_args.kwargs['env']['OPENAI_API_KEY'],'replacement')

    def test_private_client_uses_environment_without_secrets_access(self):
        from production_safety import create_client
        with patch.dict(os.environ,{'VLL_LIVE_AI':'private','OPENAI_API_KEY':'offline-test-key'}),patch('openai.OpenAI') as client:
            create_client()
            self.assertEqual(client.call_args.kwargs['api_key'],'offline-test-key')
            self.assertEqual(client.call_args.kwargs['max_retries'],0)

if __name__=='__main__':unittest.main()
