import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('trigger',Path(__file__).with_name('actions-trigger.py'))
trigger=importlib.util.module_from_spec(spec)
spec.loader.exec_module(trigger)
class TriggerTests(unittest.TestCase):
    def test_valid_revision(self):
        self.assertEqual(trigger.request('fivek','deploy '+'a'*40),'a'*40)
    def test_shell_commands_and_other_apps_rejected(self):
        for app,command in [('fivek','bash'),('fivek','deploy '+'a'*40+'; id'),('fivek','deploy main'),('other','deploy '+'a'*40)]:
            with self.assertRaises(ValueError): trigger.request(app,command)
if __name__=='__main__': unittest.main()
