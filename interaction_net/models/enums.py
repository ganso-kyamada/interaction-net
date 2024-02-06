from sqlalchemy.dialects.postgresql import ENUM

SCRAPE_STATUS_ENUM = ENUM(
    "pending",
    "in_progress",
    "completed",
    "error",
    "canceled",
    name="scrape_status_types",
    create_type=True,
)
