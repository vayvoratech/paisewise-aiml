from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    BigInteger,
    Numeric,
    SmallInteger,
    String,
    Text,
)
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
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


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
    generated_at = Column(DateTime, server_default=func.now())


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
    completed_at = Column(DateTime, server_default=func.now())


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    quiz_name = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    attempted_at = Column(DateTime, server_default=func.now())


class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    symbol = Column(String(20), nullable=False)
    buy_price = Column(Numeric(10, 2), nullable=False)
    sell_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    profit_percent = Column(Numeric(6, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


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
    min_sip_amount = Column(Numeric(10, 2), nullable=False, default=100)
    min_lumpsum = Column(Numeric(10, 2), nullable=False, default=1000)
    sip_multiplier = Column(Numeric(10, 2), nullable=False, default=1)
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
    is_active = Column(Boolean, nullable=False, default=True)
    is_tax_saver = Column(Boolean, nullable=False, default=False)
    lock_in_years = Column(Integer, nullable=False, default=0)
    dividend_option = Column(Boolean, nullable=False, default=False)
    growth_option = Column(Boolean, nullable=False, default=True)
    bse_scheme_code = Column(String(20))
    nse_symbol = Column(String(20))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
