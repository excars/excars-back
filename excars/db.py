def create_tables(db):
    with db:
        db.create_tables([], safe=True)
