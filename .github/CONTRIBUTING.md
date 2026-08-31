# Contributing

Thank you for helping improve this customer-support analytics project.

## Before making a change

1. Create a focused branch from the latest `main` branch.
2. Keep each pull request limited to one clear purpose.
3. Do not commit raw customer data, generated local CSV files, credentials, or personal information.

## Validate your work

For Python pipeline changes, run:

```powershell
python -m unittest discover -s tests -v
```

For SQL or Power BI changes, review the affected validation scripts, model relationships, measures, and report visuals. Confirm that analytical limitations remain visible to report readers.

## Open a pull request

Explain the reason for the change, list the checks you performed, and call out any assumptions or known limitations. Review the changed-file list before submitting the pull request.
