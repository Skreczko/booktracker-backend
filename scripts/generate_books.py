import random
import argparse
from faker import Faker
from sqlalchemy import insert
from tqdm import tqdm  # type: ignore

from db.model_books import Book
from db.database import SessionLocal

fake = Faker()


def generate_books(n: int = 10_000_000, batch_size: int = 10_000) -> None:
    with SessionLocal() as session:
        for _ in tqdm(range(0, n, batch_size), desc="Inserting books"):
            batch = []
            for _ in range(batch_size):
                batch.append(
                    {
                        "title": fake.sentence(nb_words=random.randint(1, 5)).rstrip(
                            "."
                        ),
                        "author": fake.name(),
                        "isbn": fake.isbn13(separator="-"),
                        "pages": random.randint(100, 1000),
                        "rating": random.randint(1, 5),
                    }
                )

            session.execute(insert(Book), batch)
            session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake books.")
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=10_000_000,
    )

    args = parser.parse_args()
    generate_books(n=args.count)
