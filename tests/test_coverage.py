import unittest
from amaranth import *
from amaranth.sim import Simulator, Tick
from amaranth.sim._coverage import ToggleCoverageObserver, ToggleDirection


class ToggleDUT(Elaboratable):
    def __init__(self):
        self.out = Signal(name="out")

    def elaborate(self, platform):
        m = Module()
        counter = Signal(2, name="counter")
        m.d.sync += counter.eq(counter + 1)
        m.d.comb += self.out.eq(counter[1])
        return m


class IrregularToggleDUT(Elaboratable):
    def __init__(self):
        self.out = Signal(name="out")

    def elaborate(self, platform):
        m = Module()
        counter = Signal(4, name="counter")
        toggle = Signal()
        m.d.sync += counter.eq(counter + 1)
        with m.If((counter == 1) | (counter == 3) | (counter == 6)):
            m.d.sync += toggle.eq(~toggle)
        m.d.comb += self.out.eq(toggle)
        return m

class MultiBitToggleDUT(Elaboratable):
    def __init__(self):
        self.out = Signal(3, name="out")  # 3-bit output

    def elaborate(self, platform):
        m = Module()
        counter = Signal(3)
        m.d.sync += counter.eq(counter + 1)
        m.d.comb += self.out.eq(counter)
        return m


class ToggleCoverageTest(unittest.TestCase):
    def run_simulation(self, dut):
        sim = Simulator(dut)
        toggle_cov = ToggleCoverageObserver(sim._engine.state)
        sim._engine.add_observer(toggle_cov)

        def process():
            for _ in range(16):
                yield Tick()

        sim.add_clock(1e-6)
        sim.add_testbench(process)
        sim.run()
        return toggle_cov.get_results()

    def assert_bit_toggled(self, toggles, signal_name, bit=0):
        self.assertIn(signal_name, toggles)
        self.assertIn(bit, toggles[signal_name])
        bit_toggles = toggles[signal_name][bit]
        print(f"{signal_name}[{bit}]: 0→1={bit_toggles[ToggleDirection.ZERO_TO_ONE]}, 1→0={bit_toggles[ToggleDirection.ONE_TO_ZERO]}")
        self.assertGreaterEqual(bit_toggles[ToggleDirection.ZERO_TO_ONE], 1)
        self.assertGreaterEqual(bit_toggles[ToggleDirection.ONE_TO_ZERO], 1)

    def test_toggle_coverage_regular(self):
        print("\n[TEST] Regular toggle coverage")
        dut = ToggleDUT()
        results = self.run_simulation(dut)
        self.assert_bit_toggled(results, "out", bit=0)

    def test_toggle_coverage_irregular(self):
        print("\n[TEST] Irregular toggle coverage")
        dut = IrregularToggleDUT()
        results = self.run_simulation(dut)
        self.assert_bit_toggled(results, "out", bit=0)

    def test_toggle_coverage_multibit(self):
        print("\n[TEST] Multibit toggle coverage")
        dut = MultiBitToggleDUT()
        results = self.run_simulation(dut)
        for bit in range(3):
            self.assert_bit_toggled(results, "out", bit=bit)

if __name__ == "__main__":
    unittest.main()
