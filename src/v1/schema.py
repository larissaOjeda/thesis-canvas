from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text, Float
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from db_config import Base
import enum

# Enums from schema
class ContextModuleProgressionsWorkflowState(enum.Enum):
    completed = 'completed'
    locked = 'locked'
    started = 'started'
    unlocked = 'unlocked'

class HTTPMethod(enum.Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

class EnrollmentType(enum.Enum):
    StudentEnrollment = 'StudentEnrollment'
    TeacherEnrollment = 'TeacherEnrollment'
    TaEnrollment = 'TaEnrollment'
    DesignerEnrollment = 'DesignerEnrollment'
    ObserverEnrollment = 'ObserverEnrollment'

class EnrollmentWorkflowState(enum.Enum):
    active = 'active'
    completed = 'completed'
    creation_pending = 'creation_pending'
    deleted = 'deleted'
    invited = 'invited'
    rejected = 'rejected'
    inactive = 'inactive'

class ContextModuleProgression(Base):
    __tablename__ = 'context_module_progressions'
    __table_args__ = {'schema': 'canvas'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('canvas.users.id'))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    workflow_state = Column(Enum(ContextModuleProgressionsWorkflowState), nullable=False)
    requirements_met = Column(Text)
    collapsed = Column(Boolean)
    current_position = Column(Integer)
    completed_at = Column(DateTime)
    current = Column(Boolean)
    evaluated_at = Column(DateTime)
    incomplete_requirements = Column(Text)
    context_module_id = Column(Integer, ForeignKey('canvas.context_modules.id'))
    lock_version = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User", back_populates="module_progressions")
    context_module = relationship("ContextModule", back_populates="progressions")

class WebLog(Base):
    __tablename__ = 'web_logs'
    __table_args__ = {'schema': 'canvas_logs'}

    id = Column(UUID, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('canvas.users.id'))
    real_user_id = Column(Integer, ForeignKey('canvas.users.id'))
    course_id = Column(Integer, ForeignKey('canvas.courses.id'))
    quiz_id = Column(Integer, ForeignKey('canvas.quizzes.id'))
    discussion_id = Column(Integer, ForeignKey('canvas.discussion_topics.id'))
    conversation_id = Column(Integer, ForeignKey('canvas.conversations.id'))
    assignment_id = Column(Integer, ForeignKey('canvas.assignments.id'))
    url = Column(Text, nullable=False)
    http_method = Column(Enum(HTTPMethod), nullable=False)
    remote_ip = Column(INET, nullable=False)
    interaction_micros = Column(Integer, nullable=False)
    participated = Column(Boolean, nullable=False)

class Enrollment(Base):
    __tablename__ = 'enrollments'
    __table_args__ = {'schema': 'canvas'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('canvas.users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('canvas.courses.id'), nullable=False)
    type = Column(Enum(EnrollmentType), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    workflow_state = Column(Enum(EnrollmentWorkflowState), nullable=False)
    completed_at = Column(DateTime)
    start_at = Column(DateTime)
    end_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Submission(Base):
    __tablename__ = 'submissions'
    __table_args__ = {'schema': 'canvas'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('canvas.users.id'), nullable=False)
    assignment_id = Column(Integer, ForeignKey('canvas.assignments.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('canvas.courses.id'), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    workflow_state = Column(String)
    submitted_at = Column(DateTime)
    score = Column(Float)
    grade = Column(String)

    # Relationships
    comments = relationship("SubmissionComment", back_populates="submission")

class SubmissionComment(Base):
    __tablename__ = 'submission_comments'
    __table_args__ = {'schema': 'canvas'}

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('canvas.submissions.id'))
    author_id = Column(Integer, ForeignKey('canvas.users.id'))
    comment = Column(Text)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    hidden = Column(Boolean, nullable=False)

    # Relationships
    submission = relationship("Submission", back_populates="comments")
    author = relationship("User")

class LearningOutcomeResult(Base):
    __tablename__ = 'learning_outcome_results'
    __table_args__ = {'schema': 'canvas'}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('canvas.users.id'))
    learning_outcome_id = Column(Integer, ForeignKey('canvas.learning_outcomes.id'))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    score = Column(Float)
    possible = Column(Float)
    mastery = Column(Boolean)
    attempt = Column(Integer)
    assessed_at = Column(DateTime)
    title = Column(String)

    # Relationships
    learning_outcome = relationship("LearningOutcome", back_populates="results")
    user = relationship("User", back_populates="outcome_results")

class LearningOutcome(Base):
    __tablename__ = 'learning_outcomes'
    __table_args__ = {'schema': 'canvas'}

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer)
    short_description = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    data = Column(Text)

    # Relationships
    results = relationship("LearningOutcomeResult", back_populates="learning_outcome")