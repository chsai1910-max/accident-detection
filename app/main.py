import argparse

from loguru import logger

from app.pipeline import DeepStreamTrafficPipeline


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True
    )

    parser.add_argument(
        "--output",
        default="outputs/result.mp4"
    )

    parser.add_argument(
        "--events",
        default="outputs/events.json"
    )

    parser.add_argument(
        "--analytics-config",
        default="configs/nvdsanalytics_config.txt"
    )

    parser.add_argument(
        "--pgie-config",
        default="configs/pgie_trafficcamnet.txt"
    )

    return parser.parse_args()


def main():

    args = parse_args()

    logger.info(
        "Initializing DeepStream Traffic System"
    )

    pipeline = DeepStreamTrafficPipeline(

        input_path=args.input,

        output_path=args.output,

        events_path=args.events,

        pgie_config=args.pgie_config,

        analytics_config=args.analytics_config
    )

    pipeline.build()

    pipeline.run()


if __name__ == "__main__":

    main()