from flask import Blueprint, render_template, request, redirect, url_for, session
from src.auth import auth_required
# from src.expenses import EXPENSES, EXPENSES_CLOSED # Moved to inside functions to avoid circular import

planning_bp = Blueprint('planning', __name__)

from enum import Enum

class PlanningStatus(Enum):
    NOT_STARTED = "planning_not_started"
    IN_PROGRESS = "planning_in_progress"
    IN_REVIEW = "in_review_by_minister"
    CORRECTION = "correction_in_progress"

class PlanningState:
    def __init__(self):
        self.deadline = None
        self.status = PlanningStatus.NOT_STARTED

    def set_deadline(self, date_str):
        self.deadline = date_str

    def start_planning(self):
        self.status = PlanningStatus.IN_PROGRESS

    def submit_to_minister(self):
        self.status = PlanningStatus.IN_REVIEW

    def request_correction(self):
        self.status = PlanningStatus.CORRECTION
        # Side effect: Reset office approvals
        from src.expenses import EXPENSES_CLOSED
        for office in EXPENSES_CLOSED:
            EXPENSES_CLOSED[office] = False

    def submit_correction(self):
        self.status = PlanningStatus.IN_REVIEW

# Singleton instance
planning_state = PlanningState()

@planning_bp.route('/chief_dashboard', methods=['GET', 'POST'])
@auth_required
def chief_dashboard():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'start':
            deadline = request.form.get('deadline')
            if deadline:
                planning_state.set_deadline(deadline)
                planning_state.start_planning()
        elif action == 'submit_minister':
            planning_state.submit_to_minister()
        elif action == 'request_correction':
            planning_state.request_correction()
        elif action == 'submit_correction':
            planning_state.submit_correction()
            
        return redirect(url_for('planning.chief_dashboard'))
    
    from src.expenses import EXPENSES, EXPENSES_CLOSED
    offices_status = []
    total_all_needs = 0
    for office in ['office1', 'office2']:
        expenses = EXPENSES.get(office, [])
        total_needs = sum(e['financial_needs'] for e in expenses if e['financial_needs'] is not None)
        task_count = len(expenses)
        is_submitted = EXPENSES_CLOSED.get(office, False)
        
        total_all_needs += total_needs

        offices_status.append({
            'name': office,
            'status': 'Submitted' if is_submitted else 'Open',
            'total_needs': total_needs,
            'task_count': task_count,
            'expenses': expenses
        })

    return render_template('chief_dashboard.html', state=planning_state, offices_status=offices_status, total_all_needs=total_all_needs, PlanningStatus=PlanningStatus)

@planning_bp.route('/minister_dashboard', methods=['GET', 'POST'])
@auth_required
def minister_dashboard():
    from src.expenses import EXPENSES, EXPENSES_CLOSED
    
    offices_status = []
    total_all_needs = 0
    for office in ['office1', 'office2']:
        expenses = EXPENSES.get(office, [])
        total_needs = sum(e['financial_needs'] for e in expenses if e['financial_needs'] is not None)
        task_count = len(expenses)
        is_submitted = EXPENSES_CLOSED.get(office, False)
        
        total_all_needs += total_needs

        offices_status.append({
            'name': office,
            'status': 'Submitted' if is_submitted else 'Open',
            'total_needs': total_needs,
            'task_count': task_count,
            'expenses': expenses
        })

    return render_template('minister_dashboard.html', state=planning_state, offices_status=offices_status, total_all_needs=total_all_needs)

@planning_bp.route('/')
def index():
    return render_template('role_selection.html')

@planning_bp.route('/set_role', methods=['POST'])
def set_role():
    role = request.form.get('role')
    if role:
        session['role'] = role
        if role == 'chief':
            return redirect(url_for('planning.chief_dashboard'))
        elif role in ['office1', 'office2']:
            return redirect(url_for('expenses.list_expenses'))
        elif role == 'minister':
            return redirect(url_for('planning.minister_dashboard'))
    return redirect(url_for('planning.index'))
