# filename: app/ingestion/geiger_reader.py

import argparse
import logging
import sys
import tomllib
from typing import Any, Dict

from app.ingestion.api_client import PushClient
from app.ingestion.serial_reader import SerialReader
from app.ingestion.watchdog import WatchdogSerialReader
from app.health import start_health_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="geiger_reader",
        description="Ingestion loop for MightyOhm Geiger counter readings.",
    )

    parser.add_argument("--config", required=False, type=str,
                        help="Path to TOML config file (overrides individual flags)")
    parser.add_argument("--device", required=False, type=str)
    parser.add_argument("--baudrate", required=False, type=int, default=9600)
    parser.add_argument("--device-type", required=False, default="mightyohm",
                        choices=["mightyohm"])
    parser.add_argument("--db", required=False, type=str)
    parser.add_argument("--api-url", required=False, type=str)
    parser.add_argument("--api-token", required=False, default="", type=str)
    parser.add_argument("--device-id", required=False, type=str)
    parser.add_argument("--device-name", required=False, type=str,
                        help="Beamwarden serial_number for this device")
    parser.add_argument("--device-token", required=False, default="", type=str,
                        help="Beamwarden device bearer token")

    return parser


def _load_toml(path: str) -> Dict[str, Any]:
    with open(path, "rb") as f:
        return tomllib.load(f)


def main() -> int:
    args = build_parser().parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.config:
        cfg = _load_toml(args.config)
        serial_device = cfg["serial"]["device"]
        baudrate = int(cfg["serial"].get("baudrate", 9600))
        db_path = cfg["storage"]["db_path"]
        api_url = cfg["push"]["url"]
        api_token = cfg["push"].get("api_token", "")
        device_name = cfg["device"]["name"]
        device_token = cfg["device"].get("token", "")
        device_id = device_name
    else:
        if not args.device or not args.db or not args.api_url or not args.device_id:
            logging.error("--config or (--device --db --api-url --device-id) required")
            return 1
        serial_device = args.device
        baudrate = args.baudrate
        db_path = args.db
        api_url = args.api_url
        api_token = args.api_token
        device_name = args.device_name or args.device_id
        device_token = args.device_token
        device_id = args.device_id

    start_health_server()

    logging.info("Starting ingestion agent")
    logging.info(f"Device: {serial_device}")
    logging.info(f"Baudrate: {baudrate}")
    logging.info(f"DB path: {db_path}")
    logging.info(f"API URL: {api_url}")
    logging.info("API token: <empty>" if not api_token else "API token: <provided>")
    logging.info(f"Device name: {device_name}")
    logging.info("Device token: <empty>" if not device_token else "Device token: <provided>")

    base_reader = SerialReader(
        device=serial_device,
        baudrate=baudrate,
    )

    reader = WatchdogSerialReader(base_reader)

    client = PushClient(
        api_url=api_url,
        api_token=api_token,
        device_id=device_id,
        db_path=db_path,
        device_name=device_name,
        device_token=device_token,
    )

    reader.set_handler(client.handle_record)
    reader.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
