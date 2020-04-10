from user import create_app

if __name__ == '__main__':
    app = create_app()
    app.run()
else:
    user_gunicorn = create_app()