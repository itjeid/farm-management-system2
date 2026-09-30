# Farm Management System — Professional Upgrade

## Database safety
Keep `instance/farm.db`. This upgrade does not delete or reset the existing database.

## Local run
1. Create/activate venv.
2. `pip install -r requirements.txt`
3. `python app.py`
4. Open `http://127.0.0.1:5000`

Default admin created only when no `admin` user exists:
- Username: `admin`
- Password: `Admin@123`

## Optional AI
Set `OPENAI_API_KEY` in the environment. The default model is `gpt-5.6-luna`. AI health scan is preliminary decision support, not veterinary diagnosis.

## Render
Set `DATABASE_URL`, `SECRET_KEY`, and optionally `OPENAI_API_KEY`. Use start command:
`gunicorn app:app`

## Important
Do not delete or replace `instance/farm.db` before validating the upgraded application locally.
