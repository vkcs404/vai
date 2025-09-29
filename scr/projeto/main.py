from app import create_app

app = create_app()

if _name_ == "__main__":
    app.run(debug=True)

