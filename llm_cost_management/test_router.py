from cost_manager import CostManager


manager = CostManager()


premium_model = manager.select_model(
    user_tier="premium",
    feature="portfolio"
)

free_model = manager.select_model(
    user_tier="free",
    feature="jargon"
)


print("Premium user model:", premium_model)
print("Free user model:", free_model)