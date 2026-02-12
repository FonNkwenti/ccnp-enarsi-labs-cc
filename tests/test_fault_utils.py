import unittest
from unittest.mock import patch, MagicMock
import socket
from labs.common.tools.fault_utils import FaultInjector

class TestFaultInjector(unittest.TestCase):
    def setUp(self):
        self.injector = FaultInjector(host="127.0.0.1")

    @patch('socket.socket')
    def test_execute_commands_success(self, mock_socket):
        # Setup mock
        mock_tn = MagicMock()
        mock_socket.return_value = mock_tn
        
        commands = ["interface Gi0/1", "shutdown"]
        result = self.injector.execute_commands(5001, commands, "Test Fault")
        
        self.assertTrue(result)
        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_tn.settimeout.assert_called_with(5)
        mock_tn.connect.assert_called_with(("127.0.0.1", 5001))
        mock_tn.sendall.assert_any_call(b"enable\r\n")
        mock_tn.sendall.assert_any_call(b"configure terminal\r\n")
        mock_tn.sendall.assert_any_call(b"interface Gi0/1\r\n")
        mock_tn.sendall.assert_any_call(b"shutdown\r\n")
        mock_tn.close.assert_called_once()

    @patch('socket.socket')
    def test_execute_commands_failure(self, mock_socket):
        # Setup mock to raise exception
        mock_socket.side_effect = Exception("Connection refused")
        
        result = self.injector.execute_commands(5001, ["no int Gi0/1"], "Fail Test")
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()