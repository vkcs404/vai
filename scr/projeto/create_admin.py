#Script auxiliar para tarefas de manutenção, provavelmente para criar o primeiro usuário administrador no banco de dados (meuapp.db), essencial para acessar o admin_dashboard.html.

#!/usr/bin/env python
"""
Script to create a default admin user in the database
"""
from app import create_app, db
from app.models import Administrador
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Check if admin already exists
    existing_admin = Administrador.query.filter_by(admin_email='admin@vai.com').first()
    
    if existing_admin:
        print("Admin user already exists!")
        print(f"Email: {existing_admin.admin_email}")
    else:
        # Create default admin
        senha_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
        admin = Administrador(
            admin_nome='Administrador',
            admin_email='admin@vai.com',
            admin_senha=senha_hash
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("Default admin user created successfully!")
        print("Email: admin@vai.com")
        print("Password: admin123")
        print("\n⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
