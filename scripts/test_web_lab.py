"""Offline checks: no AWS requests or resources are created."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('web_lab', Path(__file__).with_name('web-lab.py'))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class LabTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        lab.STATE_DIR = Path(self.tmp.name)
        lab.STATE = lab.STATE_DIR / 'state.json'
        lab.PROFILE = 'lab'
        lab.ACCOUNT = '123456789012'
        lab.state = {}

    def test_open_ssh_is_rejected_before_creation(self):
        with patch.object(lab, 'aws') as aws:
            with self.assertRaises(ValueError):
                lab.create('0.0.0.0/0')
            aws.assert_not_called()
            self.assertFalse(lab.STATE.exists())

    def test_partial_creation_preserves_vpc_for_cleanup(self):
        def fake(service, *args):
            if args[0] == 'describe-images':
                return {'Images': [{'ImageId': 'ami-test', 'CreationDate': '2026', 'RootDeviceName': '/dev/sda1'}]}
            if args[0] == 'create-vpc':
                return {'Vpc': {'VpcId': 'vpc-test'}}
            if args[0] == 'create-subnet':
                raise ValueError('simulated API failure')
            return {}
        with patch.object(lab, 'aws', side_effect=fake):
            with self.assertRaises(ValueError):
                lab.create('203.0.113.10/32')
        self.assertEqual(json.loads(lab.STATE.read_text())['vpc'], 'vpc-test')

    def test_cleanup_only_targets_recorded_resources(self):
        lab.state = dict(account=lab.ACCOUNT, profile='lab', region=lab.REGION, run='test',
                         instance='i-test', volumes=['vol-test'], vpc='vpc-test',
                         subnet='subnet-test', route_table='rtb-test', association='rtbassoc-test',
                         security_group='sg-test', igw='igw-test', igw_attached=True, key_name='key-test')
        lab.save()
        def fake(service, *args):
            return {'Volumes': []} if args[0] == 'describe-volumes' else {}
        with patch('builtins.input', return_value='DELETE'), patch.object(lab, 'aws', side_effect=fake) as aws:
            lab.cleanup()
        actions = [call.args[1] for call in aws.call_args_list]
        self.assertLess(actions.index('terminate-instances'), actions.index('delete-subnet'))
        self.assertLess(actions.index('detach-internet-gateway'), actions.index('delete-vpc'))
        self.assertNotIn('delete-volume', actions)
        self.assertFalse(lab.STATE.exists())
        self.assertTrue((lab.STATE_DIR / 'cleaned-test.json').exists())


if __name__ == '__main__':
    unittest.main()
