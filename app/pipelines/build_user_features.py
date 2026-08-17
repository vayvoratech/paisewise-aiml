from app.pipelines.feature_pipeline import run_behaviour_feature_pipeline


def build_user_features():

    return run_behaviour_feature_pipeline()


if __name__ == "__main__":
    build_user_features()
