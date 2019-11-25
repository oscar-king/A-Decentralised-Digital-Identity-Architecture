from cp import create_app, db

app = create_app()


@app.before_first_request
def create_tables():
    db.create_all(app=app)


if __name__ == '__main__':
    app.run()
