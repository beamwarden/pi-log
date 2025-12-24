from app.logging import get_logger

log = get_logger("pi-log")


def record_ingestion(record: dict):
    """
    Minimal metrics hook.

    Tests patch this function and assert call counts.
    The real implementation is intentionally omitted.
    """
    log.debug(f"Metrics: recorded ingestion of {record}")
    return None
