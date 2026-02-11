def max_consecutive_work(assignment, employee, days, max_days=5):
    count = 0
    for d in days:
        if (employee, d) in assignment and assignment[(employee, d)] != '-':
            count += 1
            if count > max_days:
                return False
        else:
            count = 0
    return True


def rest_after_L(assignment, employee):
    for d in range(27):
        if assignment.get((employee, d)) == 'L':
            if assignment.get((employee, d+1), '-') != '-':
                return False
    return True


def is_consistent(assignment, employees, days):
    for e in employees:
        if not max_consecutive_work(assignment, e, days):
            return False
        if not rest_after_L(assignment, e):
            return False
    return True
