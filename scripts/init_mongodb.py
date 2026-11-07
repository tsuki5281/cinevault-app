# Creates the MongoDB reviews collection with validation rules and indexes.
# Run from the repository root:
#   python -m scripts.init_mongodb            (keeps existing reviews)
#   python -m scripts.init_mongodb --reset    (deletes all reviews first)

import sys

from db.mongodb import MONGO_DB_NAME, get_reviews_collection, setup_reviews_collection


def main():
    reset = "--reset" in sys.argv
    setup_reviews_collection(reset=reset)

    index_names = []
    for name in get_reviews_collection().index_information():
        index_names.append(name)

    print(f"MongoDB database: {MONGO_DB_NAME}")
    print("Collection 'reviews' ready with validation rules")
    print("Indexes:", ", ".join(index_names))


if __name__ == "__main__":
    main()
