
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Decision, Outcome, Comment, User
from app.forms import DecisionForm, OutcomeForm, CommentForm
from datetime import datetime

main = Blueprint('main', __name__)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    return redirect(url_for('auth.login'))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@main.route('/dashboard')
@login_required
def dashboard():
    total_decisions = Decision.query.count()

    my_decisions = Decision.query.filter_by(
        user_id=current_user.id
    ).count()

    pending_review = Decision.query.filter(
        Decision.status.in_(['Implemented', 'Under Review'])
    ).count()

    recent_decisions = Decision.query.order_by(
        Decision.created_at.desc()
    ).limit(5).all()

    good = Outcome.query.filter_by(result='Good').count()
    neutral = Outcome.query.filter_by(result='Neutral').count()
    bad = Outcome.query.filter_by(result='Bad').count()

    return render_template(
        'dashboard.html',
        total_decisions=total_decisions,
        my_decisions=my_decisions,
        pending_review=pending_review,
        recent_decisions=recent_decisions,
        good=good,
        neutral=neutral,
        bad=bad
    )


# --------------------------------------------------
# LIST DECISIONS
# --------------------------------------------------

@main.route('/decisions')
@login_required
def list_decisions():
    status = request.args.get('status')
    search = request.args.get('search')

    query = Decision.query

    if status:
        query = query.filter_by(status=status)

    if search:
        query = query.filter(
            Decision.title.contains(search) |
            Decision.tags.contains(search)
        )

    decisions = query.order_by(
        Decision.created_at.desc()
    ).all()

    return render_template(
        'decisions/list.html',
        decisions=decisions
    )


# --------------------------------------------------
# CREATE DECISION
# --------------------------------------------------

@main.route('/decisions/create', methods=['GET', 'POST'])
@login_required
def create_decision():
    form = DecisionForm()

    if form.validate_on_submit():
        decision = Decision(
            title=form.title.data,
            context=form.context.data,
            alternatives=form.alternatives.data,
            chosen_option=form.chosen_option.data,
            rationale=form.rationale.data,
            status=form.status.data,
            tags=form.tags.data,
            project=form.project.data,
            user_id=current_user.id
        )

        db.session.add(decision)
        db.session.commit()

        flash('Decision recorded successfully!', 'success')

        return redirect(
            url_for('main.detail_decision', id=decision.id)
        )

    return render_template(
        'decisions/create.html',
        form=form
    )


# --------------------------------------------------
# DECISION DETAILS
# --------------------------------------------------

@main.route('/decisions/<int:id>')
@login_required
def detail_decision(id):
    decision = Decision.query.get_or_404(id)

    outcome_form = OutcomeForm()
    comment_form = CommentForm()

    return render_template(
        'decisions/detail.html',
        decision=decision,
        outcome_form=outcome_form,
        comment_form=comment_form
    )


# --------------------------------------------------
# EDIT DECISION
# --------------------------------------------------

@main.route('/decisions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_decision(id):
    decision = Decision.query.get_or_404(id)

    if decision.user_id != current_user.id and current_user.role != 'admin':
        abort(403)

    form = DecisionForm(obj=decision)

    if form.validate_on_submit():
        decision.title = form.title.data
        decision.context = form.context.data
        decision.alternatives = form.alternatives.data
        decision.chosen_option = form.chosen_option.data
        decision.rationale = form.rationale.data
        decision.status = form.status.data
        decision.tags = form.tags.data
        decision.project = form.project.data
        decision.updated_at = datetime.utcnow()

        db.session.commit()

        flash('Decision updated successfully!', 'success')

        return redirect(
            url_for('main.detail_decision', id=decision.id)
        )

    return render_template(
        'decisions/edit.html',
        form=form,
        decision=decision
    )


# --------------------------------------------------
# DELETE DECISION
# --------------------------------------------------

@main.route('/decisions/<int:id>/delete', methods=['POST'])
@login_required
def delete_decision(id):
    decision = Decision.query.get_or_404(id)

    if decision.user_id != current_user.id and current_user.role != 'admin':
        abort(403)

    db.session.delete(decision)
    db.session.commit()

    flash('Decision deleted successfully.', 'info')

    return redirect(url_for('main.list_decisions'))


# --------------------------------------------------
# ADD OR UPDATE OUTCOME
# --------------------------------------------------

@main.route('/decisions/<int:id>/outcome', methods=['POST'])
@login_required
def add_outcome(id):
    decision = Decision.query.get_or_404(id)

    form = OutcomeForm()

    if form.validate_on_submit():

        if decision.outcome:
            decision.outcome.result = form.result.data
            decision.outcome.impact = form.impact.data
            decision.outcome.lessons_learned = form.lessons_learned.data
            decision.outcome.reviewed_at = datetime.utcnow()
            decision.outcome.reviewed_by = current_user.id

        else:
            outcome = Outcome(
                decision_id=decision.id,
                result=form.result.data,
                impact=form.impact.data,
                lessons_learned=form.lessons_learned.data,
                reviewed_by=current_user.id
            )

            db.session.add(outcome)

        decision.status = 'Closed'

        db.session.commit()

        flash('Outcome saved successfully!', 'success')

    return redirect(
        url_for('main.detail_decision', id=decision.id)
    )


# --------------------------------------------------
# ADD COMMENT
# --------------------------------------------------

@main.route('/decisions/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    decision = Decision.query.get_or_404(id)

    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            decision_id=decision.id
        )

        db.session.add(comment)
        db.session.commit()

        flash('Comment added.', 'success')

    return redirect(
        url_for('main.detail_decision', id=decision.id)
    )


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

@main.route('/analytics')
@login_required
def analytics():

    # Total decisions
    total = Decision.query.count()

    # Decisions grouped by status
    by_status = {
        'Draft': Decision.query.filter_by(status='Draft').count(),
        'Recorded': Decision.query.filter_by(status='Recorded').count(),
        'Implemented': Decision.query.filter_by(status='Implemented').count(),
        'Under Review': Decision.query.filter_by(status='Under Review').count(),
        'Closed': Decision.query.filter_by(status='Closed').count()
    }

    # Outcome statistics
    good = Outcome.query.filter_by(result='Good').count()
    neutral = Outcome.query.filter_by(result='Neutral').count()
    bad = Outcome.query.filter_by(result='Bad').count()

    # Render analytics template
    return render_template(
        'decisions/analytics.html',
        total=total,
        by_status=by_status,
        good=good,
        neutral=neutral,
        bad=bad
    )
