from user import create_app, db

app = create_app()

if __name__ == '__main__':
    db.create_all(app=app)
    app.run()