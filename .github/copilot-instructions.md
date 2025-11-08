# GitHub Copilot Instructions for vai Repository

## Repository Overview

This is a Flask-based web application for vulnerability scanning and security assessment. The application provides three tiers of security scanning services (básico, intermediário, and avançado) with user management and authentication.

## Technology Stack

- **Backend Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: Werkzeug security (password hashing)
- **Templates**: Jinja2 (Flask's default templating engine)
- **Session Management**: Flask sessions

## Project Structure

```
vai/
├── scr/
│   └── projeto/
│       ├── app/
│       │   ├── __init__.py          # Flask app factory
│       │   ├── models.py            # Database models
│       │   ├── routes.py            # Route definitions and controllers
│       │   ├── ferramentas/         # Scanner utilities
│       │   │   ├── scanner_basico.py
│       │   │   ├── scanner_intermediario.py
│       │   │   └── scanner_avancado.py
│       │   ├── templates/           # HTML templates
│       │   └── static/              # CSS, JS, images
│       ├── instance/                # Database files (gitignored)
│       ├── main.py                  # Application entry point
│       └── requirements.txt         # Python dependencies
```

## Database Models

### Cliente (User Model)
- Main user model with authentication
- Fields: `id`, `cliente_nome`, `cliente_email`, `cliente_senha`, `cliente_status`, `nivel_acesso`
- Access levels: `'basico'`, `'intermediario'`, `'avancado'`
- Status values: `'ativo'`, `'inativo'`
- Relationships with three report types

### Report Models
Three separate models for different report tiers:
- **RelatorioBasico**: Basic security reports
- **RelatorioIntermediario**: Intermediate security reports  
- **RelatorioAvancado**: Advanced security reports

All reports have: `id`, `conteudo`, `data_criacao`, and foreign key to Cliente

## Code Conventions

### Naming Conventions
- **Variables**: snake_case (e.g., `cliente_nome`, `nivel_acesso`)
- **Functions**: snake_case (e.g., `cliente_novo`, `executar_scanner_avancado`)
- **Classes**: PascalCase (e.g., `Cliente`, `RelatorioBasico`)
- **Database fields**: snake_case matching model attributes
- **Routes**: snake_case with underscores (e.g., `/cliente_novo`, `/executar_scanner_basico`)

### Language
- **Primary Language**: Portuguese (Brazil)
- Code comments, variable names, and UI text are in Portuguese
- Keep consistency with existing Portuguese naming

### Flask Patterns
- Use Blueprint pattern: `main_bp = Blueprint('main', __name__)`
- Route functions return rendered templates or redirects
- Flash messages for user feedback with categories: `'success'`, `'danger'`, `'warning'`
- Session management for authentication: `session['cliente_id']`

### Database Operations
- Always use `db.session.add()` followed by `db.session.commit()`
- Use `query.filter_by()` for simple queries
- Use `query.get_or_404()` for fetching by ID with automatic 404 handling
- Models use relationships with cascade delete: `cascade="all, delete-orphan"`

### Security Patterns
- Password hashing: `generate_password_hash(senha, method='pbkdf2:sha256')`
- Password verification: `check_password_hash(cliente.cliente_senha, senha)`
- Route protection: Check `'cliente_id' not in session` and redirect to login
- Permission checks: Verify `cliente.nivel_acesso` before allowing access to features

## Scanner Tools

The application includes three scanner modules in `app/ferramentas/`:
- `scanner_basico.py`: Basic vulnerability scanning - function `rodar_scan_basico(alvo)`
- `scanner_intermediario.py`: Intermediate scanning - function `rodar_scan_intermediario(alvo)`
- `scanner_avancado.py`: Advanced scanning - function `rodar_scan_avancado(alvo)`

All scanner functions take a target parameter (`alvo`) and return report content.

## Development Guidelines

### Adding New Routes
1. Define route in `routes.py` using `@main_bp.route()` decorator
2. Add authentication check if needed: `if 'cliente_id' not in session:`
3. Add permission checks if tier-specific: `if cliente.nivel_acesso != 'avancado':`
4. Use flash messages for user feedback
5. Return rendered template or redirect
6. Create corresponding template in `app/templates/`

### Modifying Database Models
1. Edit model class in `models.py`
2. Consider migration implications (currently using `db.create_all()`)
3. Update relationships if adding foreign keys
4. Maintain consistency with existing naming patterns

### Working with Forms
- Extract form data using: `request.form.get('field_name')`
- Validate inputs before database operations
- Provide user feedback via flash messages
- Redirect after POST to prevent duplicate submissions

### Error Handling
- Use try-except blocks for scanner operations
- Flash error messages with `'danger'` category
- Redirect to appropriate page on errors
- Log exceptions if needed

## Common Issues to Avoid

1. **Typo in models.py**: Line 44 has `_repr_` instead of `__repr__` in RelatorioIntermediario
2. **Foreign key inconsistency**: RelatorioIntermediario and RelatorioAvancado use `client_id` instead of `cliente_id`
3. **Scanner route duplication**: Routes for intermediario and basico incorrectly call `rodar_scan_avancado()` and save to `RelatorioAvancado`
4. **Permission checks**: All three scanner routes check for `nivel_acesso != 'avancado'` instead of their respective levels

## Testing Considerations

- No formal test infrastructure exists yet
- Manual testing required for:
  - User registration and login
  - Access level restrictions
  - Scanner functionality
  - Report generation and storage
- Run the application: `python main.py` from `scr/projeto/` directory

## Dependencies

Install required packages:
```bash
pip install -r scr/projeto/requirements.txt
```

Current dependencies:
- Flask
- Flask-SQLAlchemy

## Application Configuration

Configuration is hardcoded in `app/__init__.py`:
- Secret key: `'PePeU'` (should be changed for production)
- Database: SQLite at `sqlite:///meuapp.db`
- Debug mode enabled in `main.py`

## Best Practices for This Repository

1. **Maintain Portuguese naming**: Keep all user-facing text and most variable names in Portuguese
2. **Follow existing patterns**: Use the same structure for new routes and models
3. **Protect routes appropriately**: Always check authentication and authorization
4. **Use flash messages**: Provide clear feedback to users in Portuguese
5. **Maintain model relationships**: Ensure foreign keys and relationships are properly defined
6. **Fix known issues**: Be aware of the typos and inconsistencies mentioned above
7. **Keep scanner logic separate**: Scanner implementations belong in `ferramentas/` directory
