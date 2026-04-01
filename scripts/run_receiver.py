from app.pipelines.receiver_pipeline import ReceiverPipeline


def main():
    pipeline = ReceiverPipeline(config_path="../configs/system.yaml")
    pipeline.run()


if __name__ == "__main__":
    main()
