# Migration Guide: credential.txt to cookie.txt

## Summary of Changes

This project has been updated to use **cookie-based authentication** instead of username/password credentials stored in `credential.txt`.

## Key Differences

### Generation One (Old - credential.txt)
- **File**: `credential.txt`
- **Format**: JSON array `["username", "password"]`
- **Authentication**: HTTPBasicAuth with POST to `/authentication`
- **Security**: Stores plaintext password

### Generation Two (New - cookie.txt)
- **File**: `cookie.txt`
- **Format**: Cookie string `key1=value1; key2=value2; ...`
- **Authentication**: Session cookies with GET to `/users/self`
- **Security**: No password storage, uses browser session cookies

## Benefits of Cookie Authentication

1. **More Secure**: No plaintext passwords stored
2. **Session Management**: Automatic session handling
3. **Better Compatibility**: Aligns with modern web practices
4. **Easier to Refresh**: Just copy new cookies when expired
5. **Browser Integration**: Leverages existing browser sessions

## What Changed

### 1. New Files Added
- [`credential_manager.py`](credential_manager.py) - Cookie-based authentication manager
- [`COOKIE_AUTH.md`](COOKIE_AUTH.md) - Detailed cookie authentication guide
- [`cookie.example.txt`](cookie.example.txt) - Example cookie format
- [`MIGRATION_GUIDE.md`](MIGRATION_GUIDE.md) - This file

### 2. Updated Files
- [`docker-compose.gpu.yml`](docker-compose.gpu.yml) - Changed volume mounts from `credential.txt` to `cookie.txt`
- [`.gitignore`](.gitignore) - Added `cookie.txt` to ignored files
- **All Python files** - Updated to use `CredentialManager` instead of direct file reading

### 3. Python Code Changes

#### Old Method (credential.txt):
```python
def setup_auth(self, credentials_path: str) -> None:
    """Set up authentication with WorldQuant Brain."""
    with open(credentials_path) as f:
        credentials = json.load(f)

    username, password = credentials
    self.sess.auth = HTTPBasicAuth(username, password)

    response = self.sess.post('https://api.worldquantbrain.com/authentication')
    if response.status_code != 201:
        raise Exception(f"Authentication failed: {response.text}")
```

#### New Method (cookie.txt):
```python
from credential_manager import CredentialManager

def __init__(self, credentials_path: str = None):
    self.sess = requests.Session()
    self.credential_manager = CredentialManager()

    # Try to load from file or prompt
    if credentials_path:
        self.credential_manager.load_from_file(Path(credentials_path))

    if not self.credential_manager.validate_credentials():
        raise Exception("Authentication failed")

    # Use authenticated session
    self.sess = self.credential_manager.get_session()
```

## Migration Steps

### Step 1: Get Your Cookie String
Follow the instructions in [COOKIE_AUTH.md](COOKIE_AUTH.md) to extract your cookie string from the browser.

### Step 2: Create cookie.txt
Create a file named `cookie.txt` in the project directory with your cookie string:
```
_gcl_au=...; _ga=...; t=...; _ga_9RN6WVT1K1=...
```

### Step 3: Update Docker Compose (Already Done)
The `docker-compose.gpu.yml` file has been updated to mount `cookie.txt` instead of `credential.txt`.

### Step 4: Remove Old credential.txt
Once you've verified cookie authentication works, you can safely delete `credential.txt`.

### Step 5: Update Your Code (If Custom)
If you have custom scripts that use the old authentication:

**Before:**
```python
# Old way
with open('credential.txt') as f:
    credentials = json.load(f)
username, password = credentials
sess.auth = HTTPBasicAuth(username, password)
sess.post('https://api.worldquantbrain.com/authentication')
```

**After:**
```python
# New way
from credential_manager import get_credential_manager

credential_manager = get_credential_manager()
if credential_manager.authenticate():
    sess = credential_manager.get_session()
else:
    raise Exception("Authentication failed")
```

## Files That Need Cookie Authentication

The following files have been updated to use cookie authentication:

- [x] `alpha_expression_miner.py`
- [x] `alpha_expression_miner_continuous.py`
- [x] `alpha_generator_ollama.py`
- [x] `alpha_orchestrator.py`
- [x] `improved_alpha_submitter.py`
- [x] `machine_miner.py`
- [x] `health_check.py`
- [x] `web_dashboard.py`
- [x] `test_orchestrator.py`

## Troubleshooting

### "No cookie file found"
- Ensure `cookie.txt` exists in the project directory
- Check the filename is exact (not `cookie.txt.txt`)
- The script will prompt you to enter the cookie manually

### "Authentication failed"
- Cookie may have expired - get a fresh one from your browser
- Ensure you copied the entire cookie string
- Verify you're logged in to WorldQuant Brain in your browser

### "Invalid cookie format"
- Cookie should be a single line
- Format: `key1=value1; key2=value2; ...`
- No quotes, no brackets, just the raw cookie string

## Docker Usage

### Start Services
```bash
docker-compose -f docker-compose.gpu.yml up
```

### Mount Your Cookie
The docker-compose file automatically mounts `./cookie.txt` to `/app/cookie.txt` in the container.

### Update Cookie While Running
If your cookie expires:
1. Get a new cookie string from your browser
2. Update `./cookie.txt`
3. Restart the container: `docker-compose -f docker-compose.gpu.yml restart`

## Security Best Practices

1. **Never commit cookie.txt** - Already in `.gitignore`
2. **Rotate cookies regularly** - Get fresh cookies periodically
3. **Don't share cookies** - They provide full account access
4. **Use secure permissions**: `chmod 600 cookie.txt` (Linux/Mac)
5. **Monitor expiration** - Cookies typically expire after 24-48 hours

## Compatibility

- **Backward Compatible**: Old `credential.txt` method still works if you haven't updated the code
- **Forward Compatible**: New cookie method is the recommended approach
- **Generation Two Aligned**: Now consistent with generation_two implementation

## Questions?

- See [COOKIE_AUTH.md](COOKIE_AUTH.md) for detailed cookie extraction guide
- Check [credential_manager.py](credential_manager.py) for implementation details
- Review generation_two project for reference implementation

## Rollback (If Needed)

If you need to temporarily roll back to credential.txt:

1. Keep your old `credential.txt` file
2. Revert docker-compose.gpu.yml volume mounts
3. Use old authentication code in Python files

However, cookie authentication is **strongly recommended** for security and compatibility.
