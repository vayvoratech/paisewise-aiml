from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Index,
    Integer,
    BigInteger,
    JSON,
    Numeric,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    full_name = Column(String(100), nullable=False)
    age = Column(SmallInteger, nullable=False)
    annual_income = Column(Numeric(15, 2), nullable=False)
    monthly_investment = Column(Numeric(15, 2), nullable=False)
    portfolio_value = Column(Numeric(15, 2), nullable=False)
    risk_profile = Column(String(20), nullable=False)
    investment_experience_years = Column(SmallInteger)
    sip_count = Column(Integer, default=0)
    kyc_completed = Column(Boolean, default=False)
    kyc_city = Column(String(100))


class UserFeatures(Base):
    __tablename__ = "user_features"

    user_id = Column(BigInteger, primary_key=True)
    age = Column(SmallInteger, nullable=False)
    annual_income = Column(Numeric(15, 2), nullable=False)
    monthly_investment = Column(Numeric(15, 2), nullable=False)
    portfolio_value = Column(Numeric(15, 2), nullable=False)
    risk_profile = Column(String(20), nullable=False)
    investment_experience_years = Column(SmallInteger)
    sip_count = Column(Integer, default=0)
    kyc_completed = Column(Boolean, default=False)

    lesson_completion_rate = Column(Numeric(5, 4), default=0)
    quiz_avg_score = Column(Numeric(5, 2), default=0)
    streak_days = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    preferred_language = Column(String(30))
    onboarding_goal = Column(String(100))

    age_proxy = Column(SmallInteger)
    city_tier = Column(String(20))
    paper_trade_count = Column(Integer, default=0)
    paper_trade_profit_rate = Column(Numeric(5, 4), default=0)
    time_of_day = Column(String(20))
    session_duration = Column(Integer, default=0)
    screens_visited = Column(Integer, default=0)
    lessons_started = Column(Integer, default=0)
    quizzes_taken = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )


class JargonTerm(Base):
    __tablename__ = "jargon_terms"

    id = Column(Integer, primary_key=True)
    term = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    difficulty = Column(String(30), nullable=False)


class PortfolioInsight(Base):
    __tablename__ = "portfolio_insights"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    insight = Column(Text, nullable=False)
    language = Column(String(30), nullable=False)
    generated_at = Column(
        DateTime,
        server_default=func.now()
    )


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    symbol = Column(String(20), nullable=False)
    company_name = Column(String(150))
    quantity = Column(Numeric(18, 4), nullable=False)
    average_price = Column(Numeric(14, 4), nullable=False)


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    lesson_name = Column(String(100), nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(
        DateTime,
        server_default=func.now()
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    quiz_name = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    attempted_at = Column(
        DateTime,
        server_default=func.now()
    )


class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    symbol = Column(String(20), nullable=False)
    buy_price = Column(Numeric(10, 2), nullable=False)
    sell_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    profit_percent = Column(Numeric(6, 2), nullable=False)
    created_at = Column(
        DateTime,
        server_default=func.now()
    )


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    login_time = Column(DateTime, nullable=False)
    logout_time = Column(DateTime, nullable=False)
    session_duration = Column(Integer, nullable=False)
    screens_visited = Column(Integer, nullable=False)
    lessons_started = Column(Integer, default=0)
    quizzes_taken = Column(Integer, default=0)


class MFScheme(Base):
    __tablename__ = "mf_schemes"

    scheme_code = Column(String(20), primary_key=True)
    isin = Column(String(12), unique=True)
    scheme_name = Column(String(300), nullable=False)
    amc_name = Column(String(100), nullable=False)
    amc_code = Column(String(20))
    category = Column(String(50), nullable=False)
    sub_category = Column(String(50))
    scheme_type = Column(String(20), nullable=False)
    risk_level = Column(String(20), nullable=False)

    nav = Column(Numeric(12, 4))
    nav_date = Column(DateTime)

    min_sip_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=100
    )
    min_lumpsum = Column(
        Numeric(10, 2),
        nullable=False,
        default=1000
    )
    sip_multiplier = Column(
        Numeric(10, 2),
        nullable=False,
        default=1
    )

    returns_1y = Column(Numeric(8, 4))
    returns_3y = Column(Numeric(8, 4))
    returns_5y = Column(Numeric(8, 4))
    returns_since_launch = Column(Numeric(8, 4))

    benchmark_name = Column(String(100))
    benchmark_returns_1y = Column(Numeric(8, 4))

    expense_ratio = Column(Numeric(5, 4))
    fund_manager = Column(String(200))
    fund_size_cr = Column(Numeric(14, 2))

    launch_date = Column(DateTime)

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )
    is_tax_saver = Column(
        Boolean,
        nullable=False,
        default=False
    )

    lock_in_years = Column(
        Integer,
        nullable=False,
        default=0
    )

    dividend_option = Column(
        Boolean,
        nullable=False,
        default=False
    )
    growth_option = Column(
        Boolean,
        nullable=False,
        default=True
    )

    bse_scheme_code = Column(String(20))
    nse_symbol = Column(String(20))

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )


class RecommendationRun(Base):
    __tablename__ = "recommendation_runs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), nullable=False)
    experiment_name = Column(String(100), nullable=False)
    variant = Column(String(50), nullable=False)
    created_at = Column(
        DateTime,
        server_default=func.now()
    )


class RecommendationClick(Base):
    __tablename__ = "recommendation_clicks"

    id = Column(Integer, primary_key=True)
    recommendation_run_id = Column(
        Integer,
        nullable=False
    )
    user_id = Column(String(36), nullable=False)
    scheme_code = Column(String(20), nullable=False)
    created_at = Column(
        DateTime,
        server_default=func.now()
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(60), nullable=False)
    entity_type = Column(String(30), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    old_values = Column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True
    )
    new_values = Column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True
    )
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_id = Column(String(200), nullable=True)
    session_id = Column(String(100), nullable=True)
    request_id = Column(String(100), nullable=True)
    result = Column(
        String(10),
        nullable=False,
        server_default=text("'SUCCESS'")
    )
    failure_reason = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "result IN ('SUCCESS', 'FAILURE')",
            name="ck_audit_log_result"
        ),
        Index(
            "idx_audit_log_user_id",
            "user_id",
            "created_at",
            postgresql_where=(user_id.isnot(None))
        ),
        Index(
            "idx_audit_log_failures",
            "action",
            "result",
            "created_at",
            postgresql_where=(result == "FAILURE")
        ),
        Index(
            "idx_audit_log_entity",
            "entity_type",
            "entity_id",
            "created_at",
            postgresql_where=(entity_id.isnot(None))
        ),
        Index(
            "idx_audit_log_created_at",
            "created_at"
        ),
    )