import pytest
from ortools.sat.python import cp_model
from scheduler.solver import MaintenanceScheduleSolver


class TestOnePersonSchedule:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.rooms = ['type_A', 'type_B', 'type_C']
        self.personnel = ['P0']
        self.availability = [10]
        self.skills = [
            {'type_A': True, 'type_B': True, 'type_C': True}
        ]
        self.times = [1, 2, 3]  # Time required to clean each room
        self.delays = [  # Delay after rooms to catch breath
            [0, 1, 0]
        ]
        self.lunch_break = 12  # Fixed lunch break start time
        self.lunch_duration = 1  # Fixed lunch break duration
        self.solver = MaintenanceScheduleSolver(self.rooms, self.personnel, self.availability, self.skills, self.times, self.delays, self.lunch_break, self.lunch_duration)

    def test_total_time(self):
        solver = cp_model.CpSolver()
        solver.Solve(self.solver.model)

        schedule = self.solver.schedule_for_person(0, solver)
        total_time = sum(u[3] for u in schedule) + sum(u[4] for u in schedule)  # sum of time and delay
        assert total_time == sum(self.times) + sum(self.delays[0])
        assert schedule[0][0] == 0  # start the day at 0
        # ============================================================
        print("\n\n=== Schedule ===")
        for start_time, end_time, r, t, d in schedule:
            if d == 0:
                print(f' [{start_time}, {end_time}]: Room {r} [{t}Δ]')
            else:
                print(f' [{start_time}, {end_time} + {d}]: Room {r} [{t}Δ]')


if __name__ == '__main__':
    pytest.main()
