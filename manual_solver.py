import time

class ManualSolver:
    def __init__(self, data):
        self.employees = data['employees']
        self.days = list(range(data['days_count']))
        
        # Lista padrão de tentativas
        self.shifts = [s for s in data['shift_types'] if s != '-'] + ['-']
            
        self.cover_req = data['cover_requirements'] 
        self.days_off = data.get('days_off', {})
        self.shift_on_req = data.get('shift_on_requests', {}) 
        self.shift_off_req = data.get('shift_off_requests', {}) # NOVO
        
        self.solution = None
        self.nodes_visited = 0
        self.days_to_solve = []

    def solve(self, limit_days=5):
        print(f"\n>>> Iniciando Solver Manual (Backtracking)")
        print(f"    Horizonte: {limit_days} dias")
        print(f"    Heurísticas Ativas: ShiftOn (Priorizar) + ShiftOff (Evitar)")
        
        self.days_to_solve = list(range(limit_days))
        variables = []
        for d in self.days_to_solve:
            for e in self.employees:
                variables.append((e, d))
        
        start_time = time.time()
        success = self.backtrack({}, variables)
        end_time = time.time()
        
        return success, self.solution, (end_time - start_time), self.nodes_visited

    def backtrack(self, assignment, unassigned_vars):
        if not unassigned_vars:
            self.solution = assignment
            return True

        var = unassigned_vars[0]
        emp, day = var
        remaining = unassigned_vars[1:]

        self.nodes_visited += 1
        if self.nodes_visited % 50000 == 0:
            print(f"    ... {self.nodes_visited} nós visitados ...")

        # --- HEURÍSTICA DUPLA: Ordenação Inteligente ---
        current_possible_shifts = self.shifts[:] 
        
        # 1. SHIFT OFF: Joga para o final da fila (Penaliza)
        unwanted_shifts = self.shift_off_req.get((emp, day), [])
        for bad_shift in unwanted_shifts:
            if bad_shift in current_possible_shifts:
                current_possible_shifts.remove(bad_shift)
                current_possible_shifts.append(bad_shift) 
        
        # 2. SHIFT ON: Joga para o início da fila (Premia)
        preferred_shift = self.shift_on_req.get((emp, day))
        if preferred_shift and preferred_shift in current_possible_shifts:
            current_possible_shifts.remove(preferred_shift)
            current_possible_shifts.insert(0, preferred_shift) 

        # Loop de Tentativas
        for shift in current_possible_shifts:
            if self.is_valid(assignment, emp, day, shift):
                
                # Podas (mantidas)
                if shift != '-' and self.is_shift_full(assignment, day, shift):
                    continue 
                if self.is_day_closing(emp, day, unassigned_vars):
                    if not self.check_day_demand(assignment, day, shift):
                        continue 
                
                assignment[var] = shift
                
                if self.backtrack(assignment, remaining):
                    return True 
                
                del assignment[var]
        
        return False

    def is_valid(self, assignment, emp, day, shift):
        # 1. Folgas Fixas (Hard)
        if day in self.days_off.get(emp, []):
            if shift != '-': return False

        # 2. Descanso pós-noite
        if day > 0:
            prev = assignment.get((emp, day-1), '-')
            if prev == 'L' and shift != '-':
                return False

        # 3. Máximo 5 dias consecutivos
        if shift != '-':
            consecutive = 0
            for k in range(1, 6):
                d_check = day - k
                if d_check < 0: break
                if assignment.get((emp, d_check), '-') != '-':
                    consecutive += 1
                else: break
            if consecutive >= 5: return False 

        return True

    def is_shift_full(self, assignment, day, shift):
        required = self.cover_req.get(day, {}).get(shift, 0)
        if required == 0: return False
        
        current_count = 0
        for (e, d), s in assignment.items():
            if d == day and s == shift:
                current_count += 1
        return current_count >= required

    def is_day_closing(self, current_emp, current_day, remaining_vars):
        if not remaining_vars: return True
        next_emp, next_day = remaining_vars[0]
        return next_day != current_day

    def check_day_demand(self, assignment, day, current_shift):
        counts = {s: 0 for s in self.shifts}
        counts[current_shift] += 1
        
        for e in self.employees:
            if (e, day) in assignment:
                s = assignment[(e, day)]
                counts[s] += 1
        
        reqs = self.cover_req.get(day, {})
        for shift_req, min_val in reqs.items():
            if counts.get(shift_req, 0) < min_val:
                return False 
        return True