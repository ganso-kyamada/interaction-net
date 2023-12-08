from sqlalchemy.dialects.postgresql import ENUM

SCRAPE_STATUS_ENUM = ENUM(
    "pending",
    "in_progress",
    "completed",
    "error",
    name="scrape_status_types",
    create_type=True,
)
