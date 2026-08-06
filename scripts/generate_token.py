from langchain_google_community._utils import get_google_credentials

credentials = get_google_credentials(
    token_file="token.json",
    client_secrets_file="credentials.json",
    scopes=["https://www.googleapis.com/auth/gmail.send"],
)

print("Token generated successfully! Check token.json at project root")