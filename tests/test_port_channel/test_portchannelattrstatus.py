import unittest
import random

from mdssdk.connection_manager.errors import CLIError
from mdssdk.portchannel import PortChannel
from tests.test_port_channel.vars import *

log = logging.getLogger(__name__)


class TestPortChannelAttrStatus(unittest.TestCase):

    def setUp(self) -> None:
        self.switch = sw
        log.debug(sw.version)
        log.debug(sw.ipaddr)
        self.interfaces = sw.interfaces
        while True:
            self.pc_id = random.randint(1, 256)
            if "port-channel" + str(self.pc_id) not in self.interfaces.keys():
                break
        self.pc = PortChannel(self.switch, self.pc_id)

    def test_status_read(self):
        self.pc.create()
        self.assertEqual('noOperMembers', self.pc.status)
        self.pc.delete()

    def test_status_read_nonexisting(self):
        self.assertIsNone(self.pc.status)

    def test_status_write(self):
        self.pc.create()
        status = "shutdown"
        self.pc.status = status
        self.assertEqual("down", self.pc.status)
        status1 = "no shutdown"
        self.pc.status = status1
        self.assertEqual("noOperMembers", self.pc.status)
        self.pc.delete()

    def test_status_write_invalid(self):
        status = "asdf"
        with self.assertRaises(CLIError) as e:
            self.pc.status = status
        self.assertEqual("The command \" terminal dont-ask ; interface port-channel" + str(self.pc_id) + " ; " + str(
            status) + " ; no terminal dont-ask \" gave the error \" % Invalid command \".", str(e.exception))

    def tearDown(self) -> None:
        self.pc.delete()
        self.assertEqual(self.interfaces.keys(), self.switch.interfaces.keys())
