from sqlalchemy import select

from db import SessionLocal
from models import OfferCode

codes = [
    "A132429",
    "A132430",
    "A117475",
    "A1012765",
    "A1012766",
    "A1012767",
]


def seed_offers():
    with SessionLocal.begin() as session:
        existing_codes = set(
            session.scalars(select(OfferCode.code).where(OfferCode.code.in_(codes)))
        )

        session.add_all(
            OfferCode(code=code) for code in codes if code not in existing_codes
        )

    print("Offer codes seeded successfully.")


if __name__ == "__main__":
    seed_offers()
