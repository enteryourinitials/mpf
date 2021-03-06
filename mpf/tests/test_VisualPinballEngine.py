import sys

from mpf.platforms.visual_pinball_engine import platform_pb2
from mpf.tests.MpfTestCase import MpfTestCase


class MockServer:

    async def stop(self):
        pass

    async def wait_for_termination(self):
        pass


class TestVPE(MpfTestCase):

    def get_config_file(self):
        return 'config.yaml'

    def get_machine_path(self):
        return 'tests/machine_files/vpe/'

    async def _connect_to_mock_client(self, service, port):
        self.service = service
        await self.simulator.connect(self.service)
        return MockServer()

    def _mock_loop(self):
        self.simulator.init_async()

    def setUp(self):
        if sys.version_info < (3, 6):
            self.skipTest("Test requires Python 3.6+")
            return
        try:
            from mpf.tests.vpe_simulator import VpeSimulation
        except SyntaxError:
            self.skipTest("Cannot import VPE simulator.")
            return

        self.simulator = VpeSimulation({"0": True, "3": False, "6": False})
        import mpf.platforms.visual_pinball_engine.visual_pinball_engine
        mpf.platforms.visual_pinball_engine.visual_pinball_engine.VisualPinballEnginePlatform.listen = self._connect_to_mock_client
        super().setUp()

    def get_platform(self):
        return False

    def test_vpe(self):
        self.assertSwitchState("s_sling", True)
        self.assertSwitchState("s_flipper", False)
        self.assertSwitchState("s_test", False)
        self.simulator.set_switch("6", True)
        self.advance_time_and_run(.1)
        self.assertSwitchState("s_test", True)

        self.simulator.set_switch("6", False)
        self.advance_time_and_run(.1)
        self.assertSwitchState("s_test", False)

        self.machine.lights["test_light1"].color("CCCCCC")
        self.advance_time_and_run(.1)
        self.assertAlmostEqual(0.8, self.simulator.lights["light-0"])

        self.machine.coils["c_flipper"].pulse()
        self.advance_time_and_run(.1)
        self.assertEqual("pulsed-10-1.0", self.simulator.coils["1"])

        self.machine.coils["c_flipper"].enable()
        self.advance_time_and_run(.1)
        self.assertEqual("enabled-10-1.0-1.0", self.simulator.coils["1"])

        self.machine.coils["c_flipper"].disable()
        self.advance_time_and_run(.1)
        self.assertEqual("disabled", self.simulator.coils["1"])

        self.machine.flippers["f_test"].enable()
        self.advance_time_and_run(.1)
        self.assertEqual(platform_pb2.ConfigureHardwareRuleRequest(
            coil_number="1", switch_number="3", pulse_ms=10, pulse_power=1.0, hold_power=1.0),
            self.simulator.rules["1-3"])

        self.machine.flippers["f_test"].disable()
        self.advance_time_and_run(.1)
        self.assertNotIn("1-3", self.simulator.rules)
