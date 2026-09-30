# Professional Farm Management System — Feature Report

## 1. Purpose
A connected cow-farm management platform covering animal registration, health and treatment, milk production, workers, labor advances, income, expenses, finance, ledger, administration, reports and AI decision support.

## 2. Data-preservation policy
The existing `instance/farm.db` is preserved. No existing table is dropped or reset. Existing additive tables already present for `labor_advances` and `ledger_*` remain intact. The cow-only interface does not delete any historical records; the supplied database already contains five Cow records.

## 3. Main modules and relationships
- **Dashboard** reads Animals, Health, Production, Labor, Advances, Income and Expenses.
- **Cows → Health**: every health record belongs to a cow; the latest status updates the cow's current status.
- **Cows → Production**: milk production belongs to a cow and feeds production summaries.
- **Workers → Labor Activities**: each activity belongs to a worker and contributes to amount owed.
- **Workers → Advances**: advances belong to a worker and reduce the remaining balance.
- **Income/Expenses/Labor → Finance**: the finance page separates general expenses from labor cost.
- **Income/Expenses/Labor/Advances → Ledger**: source transactions are reflected in connected ledger views.
- **All modules → Reports**: report builder can include all sections or selected sections.
- **All relevant records → AI**: the assistant receives farm context for decision support.

## 4. Cow-only livestock
The application now registers and displays cows only. Existing database records are preserved. New non-cow registrations are not accepted by the cow-management interface.

## 5. Health and treatment
Health records support Healthy, Sick, Under Treatment, Recovered and Vaccinated statuses, symptoms/signs, medicine, vaccination, veterinarian and notes. Administrators can update records. A separate AI health scan accepts a written symptom and optional cow image; the result is explicitly preliminary and not a confirmed diagnosis.

## 6. Labor and advances
The labor interface focuses on activity amount rather than hours/payment presentation. A worker's amount owed is calculated from recorded activity amounts, falling back to the worker salary when no activity amount exists. Recorded advances are automatically subtracted to show the remaining balance.

**Remaining balance = Amount owed − Total advances**

## 7. Administration
Admin users can update core records through the administration center. Production totals are derived from morning + evening quantities, and health updates synchronize the related cow's current status.

## 8. AI
### Farmer AI Assistant
Natural-language farm questions about cows, health, production, labor, finance and management. With `OPENAI_API_KEY`, the system uses the configured model; otherwise a local fallback provides useful farm-context responses.

### AI Cow Health Scan
The health scan can combine a symptom description with an uploaded image when an AI API key is configured. It provides possible conditions and next steps while warning that veterinary examination is required for diagnosis and treatment.

## 9. Bilingual interface
English and Kinyarwanda language selection is available from the navigation and login page. Core navigation, common labels, statuses and management terminology are translated. The architecture is ready for expansion of the translation dictionary as additional wording is added.

## 10. Reports
The Reports section allows the user to choose **all sections or only selected sections**: Summary, Cows, Health, Production, Labor, Finance, Ledger and AI. The same selection can be downloaded as a PDF.

## 11. Professional design
The system includes a modern responsive navigation bar, interactive login page, metric cards, report builder, AI panels, consistent footer, responsive tables, Bootstrap icons and mobile-friendly layouts.

## 12. Security and deployment
Secrets such as `SECRET_KEY` and `OPENAI_API_KEY` are read from environment variables. Local development can continue with SQLite; Render can use `DATABASE_URL` for PostgreSQL. Never commit `.env` files or API keys.

## 13. Veterinary safety note
AI output is decision support only. A symptom or image can have multiple causes, and an image cannot replace physical examination, laboratory testing or veterinary judgment. Urgent or worsening cases should be referred to a qualified veterinarian.
