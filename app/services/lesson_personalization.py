
from collections import defaultdict
from statistics import mean

from app.config.lesson_curriculum import LESSON_ORDER, LESSON_PREREQUISITES

WEAK_SCORE_THRESHOLD = 60  # task: "if user scores < 60% on quiz"
SLOW_LEARNER_ATTEMPT_THRESHOLD = 2  # avg attempts per lesson before advancing


def analyse_completion_patterns(lesson_progress_rows):
   
    started_counts = defaultdict(int)
    completed_counts = defaultdict(int)

    for row in lesson_progress_rows:
        lesson_name = row["lesson_name"]
        started_counts[lesson_name] += 1
        if row.get("completed"):
            completed_counts[lesson_name] += 1

    drop_off_report = []
    for lesson_name, started in started_counts.items():
        completed = completed_counts.get(lesson_name, 0)
        drop_off_rate = 1 - (completed / started) if started else 0
        drop_off_report.append(
            {
                "lesson_name": lesson_name,
                "started": started,
                "completed": completed,
                "drop_off_rate": round(drop_off_rate, 3),
            }
        )

    # highest drop-off first, 
    # so the worst lessons are easy to spot
    drop_off_report.sort(key=lambda item: item["drop_off_rate"], reverse=True)
    return drop_off_report



def classify_lesson_difficulty(quiz_score):
    
    if quiz_score >= 80:
        return "easy"
    if quiz_score >= 60:
        return "medium"
    return "hard"


def classify_user_lesson_difficulties(quiz_attempts):
    
    scores_by_lesson = defaultdict(list)
    for attempt in quiz_attempts:
        scores_by_lesson[attempt["quiz_name"]].append(attempt["score"])

    return {
        lesson_name: classify_lesson_difficulty(mean(scores))
        for lesson_name, scores in scores_by_lesson.items()
    }


def needs_prerequisite_review(quiz_score, lesson_name):
   
    if quiz_score >= WEAK_SCORE_THRESHOLD:
        return None

    prerequisites = LESSON_PREREQUISITES.get(lesson_name, [])
    return prerequisites[0] if prerequisites else None


# 4. Learning path algorithm

def get_next_lesson(completed_lessons, quiz_scores):
   
    completed_set = set(completed_lessons)


    for lesson_name in reversed(LESSON_ORDER):
        if lesson_name in completed_set and lesson_name in quiz_scores:
            prerequisite = needs_prerequisite_review(
                quiz_scores[lesson_name], lesson_name
            )
            if prerequisite:
                return prerequisite
            break

    for lesson in LESSON_ORDER:
        if lesson in completed_set:
            continue

        prerequisites = LESSON_PREREQUISITES.get(lesson, [])
        if all(prereq in completed_set for prereq in prerequisites):
            return lesson

    return None  

# 5. User learning profile

def build_user_learning_profile(quiz_attempts, sessions):
   
    attempts_per_lesson = defaultdict(int)
    for attempt in quiz_attempts:
        attempts_per_lesson[attempt["quiz_name"]] += 1

    avg_attempts = mean(attempts_per_lesson.values()) if attempts_per_lesson else 0
    slow_learner = avg_attempts > SLOW_LEARNER_ATTEMPT_THRESHOLD

    time_of_day_counts = defaultdict(int)
    format_counts = defaultdict(int)
    for session in sessions:
        if session.get("time_of_day"):
            time_of_day_counts[session["time_of_day"]] += 1
        if session.get("lesson_format"):
            format_counts[session["lesson_format"]] += 1

    preferred_time_of_day = (
        max(time_of_day_counts, key=time_of_day_counts.get)
        if time_of_day_counts
        else None
    )
    lesson_format_preference = (
        max(format_counts, key=format_counts.get) if format_counts else None
    )

    return {
        "slow_learner": slow_learner,
        "preferred_time_of_day": preferred_time_of_day,
        "lesson_format_preference": lesson_format_preference,
    }


# 6. Learning path generator

def generate_learning_path(completed_lessons, quiz_scores, path_length=3):

    path = []
    simulated_completed = set(completed_lessons)
    simulated_scores = dict(quiz_scores)

    for _ in range(path_length):
        next_lesson = get_next_lesson(simulated_completed, simulated_scores)
        if next_lesson is None:
            break

        path.append(next_lesson)
        simulated_completed.add(next_lesson)
        # assume a passing score so the simulation can keep moving forward
        simulated_scores[next_lesson] = 75

    return path
