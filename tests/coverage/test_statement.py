from amaranth import *
from amaranth.sim import Simulator, Tick
from amaranth.sim._coverage import StatementCoverageObserver 
import unittest

class StatementDUT(Elaboratable):
    def __init__(self):
        self.out = Signal()

    def elaborate(self, platform):
        m = Module()
        self.counter = Signal(3)
        m.d.sync += self.counter.eq(self.counter + 1)
        m.d.sync += self.out.eq(self.counter == 0)
        return m


class StatementCoverageTest(unittest.TestCase):
    def run_simulation(self):
        observer = StatementCoverageObserver()
        dut = StatementDUT()
        sim = Simulator(dut)

        def process():
            for _ in range(4):
                counter_val = (yield dut.counter)

                if counter_val == 0:
                    observer.record_statement_hit("if_counter_0")
                else:
                    observer.record_statement_hit("else_counter_nonzero")

                observer.record_statement_hit("counter_increment")

                yield Tick()

        sim.add_clock(1e-6)
        sim.add_testbench(process)
        sim.run()
        return observer.get_result()

    def test_statement_coverage(self):
        print("\n[TEST] Statement coverage")
        results = self.run_simulation()

        for stmt in ["if_counter_0", "else_counter_nonzero", "counter_increment"]:
            self.assertIn(stmt, results)
            self.assertGreater(results[stmt], 0, f"Statement '{stmt}' was never hit.")
            print(f"Statement '{stmt}' hit {results[stmt]} time(s)")


if __name__ == "__main__":
    unittest.main()
