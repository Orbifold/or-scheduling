import pytest
from ortools.sat.python import cp_model
from scheduler.solver import MaintenanceScheduleSolver


class TestMaintenanceScheduleSolver:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.rooms = ['type_A', 'type_B', 'type_C', 'type_B', 'type_A', 'type_B', 'type_C', 'type_C']
        self.personnel = ['P0', 'P1', 'P2', 'P3', 'P4']
        self.availability = [10, 3, 15, 10, 8]
        self.skills = [
            {'type_A': True, 'type_B': False, 'type_C': True},
            {'type_A': True, 'type_B': True, 'type_C': False},
            {'type_A': False, 'type_B': True, 'type_C': True},
            {'type_A': False, 'type_B': True, 'type_C': True},
            {'type_A': False, 'type_B': False, 'type_C': True},
        ]
        self.times = [6, 4, 2, 3, 2, 4, 2, 3]  # Time required to maintain each room
        self.delays = [  # Delay between rooms for each personnel
            [0, 1, 2, 1, 0, 1, 2, 1],
            [1, 0, 1, 2, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1],
        ]
        self.lunch_break = 12  # Fixed lunch break start time
        self.lunch_duration = 1  # Fixed lunch break duration
        self.solver = MaintenanceScheduleSolver(self.rooms, self.personnel, self.availability, self.skills, self.times, self.delays, self.lunch_break, self.lunch_duration)

    def test_create_variables(self):
        assert len(self.solver.assignments) == self.solver.num_rooms * self.solver.num_personnel  # every combination of room and personnel has a Boolean assignment variable
        assert len(self.solver.start_times) == self.solver.num_rooms * self.solver.num_personnel # every combination of room and personnel has a start time variable
        assert len(self.solver.end_times) == self.solver.num_rooms * self.solver.num_personnel # every combination of room and personnel has an end time variable

    def test_add_constraints(self):
        # Check if constraints are added correctly
        assert len(self.solver.model.Proto().constraints) > 0

    def test_solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.solver.model)
        assert status in [cp_model.OPTIMAL, cp_model.FEASIBLE]

    def test_personnel_availability(self):
        # Ensure that personnel are not assigned more than their availability
        solver = cp_model.CpSolver()
        solver.Solve(self.solver.model)
        for p in range(self.solver.num_personnel):
            total_time = sum(self.solver.times[r] for r in range(self.solver.num_rooms) if solver.Value(self.solver.assignments[r, p]))
            assert total_time <= self.availability[p], f'Personnel {p} is assigned more than their availability'

    def test_lunch_break(self):
        # Ensure that lunch break is respected
        solver = cp_model.CpSolver()
        solver.Solve(self.solver.model)
        for p in range(self.solver.num_personnel):
            for r in range(self.solver.num_rooms):
                start_time = solver.Value(self.solver.start_times[r, p])
                end_time = solver.Value(self.solver.end_times[r, p])
                assert not (self.lunch_break <= start_time < self.lunch_break + self.lunch_duration)
                assert not (self.lunch_break < end_time <= self.lunch_break + self.lunch_duration)


if __name__ == '__main__':
    pytest.main()
