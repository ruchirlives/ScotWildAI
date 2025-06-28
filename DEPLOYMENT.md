# Deployment Setup

## Quick Start

1. Set up your environment variables:

   ```bash
   copy .env.example .env
   ```
   
   Then edit `.env` and set your `GCLOUD_PROJECT_ID` and other required values.

2. Run the deployment:

   ```powershell
   .\deployment.ps1
   ```

   The script will automatically use the `GCLOUD_PROJECT_ID` from your `.env` file, or prompt you if not set.

## Alternative Setup

If you prefer not to use a `.env` file, you can:

1. Set the environment variable directly:

   ```powershell
   $env:GCLOUD_PROJECT_ID = "your-project-id"
   ```

2. Or let the script prompt you interactively.

## Security Note

The `deployment.ps1` file is gitignored to prevent accidentally committing sensitive project information. The `.env` file is also gitignored for the same reason. Always use the example files as templates.
