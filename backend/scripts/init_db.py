from app.core.database import Base, engine
from app.models import load_all_models


def main() -> None:
    load_all_models()
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()
