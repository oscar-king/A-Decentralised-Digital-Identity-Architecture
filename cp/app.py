from cp import create_app

if __name__ == '__main__':
    app = create_app()
    app.run()
else:
    cp_gunicorn = create_app()
