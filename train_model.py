from training.model_training import train_and_save_best_model


if __name__ == "__main__":
    report = train_and_save_best_model()
    print("Training complete.")
    print(f"Selected model: {report['selected_model']}")
    for metric_name, metric_value in report["metrics"].items():
        print(f"{metric_name}: {metric_value}")
