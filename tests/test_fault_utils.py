import unittest
from unittest.mock import patch, MagicMock
from labs.common.tools.fault_utils import FaultInjector

class TestFaultInjector(unittest.TestCase):
    def setUp(self):
        self.injector = FaultInjector(host="127.0.0.1")

    @patch('telnetlib.Telnet')
    def test_execute_commands_success(self, mock_telnet):
        # Setup mock
        mock_tn = MagicMock()
        mock_telnet.return_value = mock_tn
        
        commands = ["interface Gi0/1", "shutdown"]
        result = self.injector.execute_commands(5001, commands, "Test Fault")
        
        self.assertTrue(result)
        mock_telnet.assert_called_with("127.0.0.1", 5001, timeout=5)
        mock_tn.write.assert_any_call(b"enable\n")
        mock_tn.write.assert_any_call(b"configure terminal\n")
        mock_tn.write.assert_any_call(b"interface Gi0/1\n")
        mock_tn.write.assert_any_call(b"shutdown\n")
        mock_tn.close.assert_called_once()

    @patch('telnetlib.Telnet')
    def test_execute_commands_failure(self, mock_telnet):
        # Setup mock to raise exception
        mock_telnet.side_effect = Exception("Connection refused")
        
        result = self.injector.execute_commands(5001, ["no int Gi0/1"], "Fail Test")
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()