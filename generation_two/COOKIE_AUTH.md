# Cookie-Based Authentication Guide

This project now uses cookie-based authentication instead of username/password credentials.

## How to Get Your Cookie String

1. **Open WorldQuant Brain in your browser**
   - Go to https://platform.worldquantbrain.com
   - Log in with your credentials

2. **Open Browser Developer Tools**
   - **Chrome/Edge**: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - **Firefox**: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - **Safari**: Enable Developer Tools first in Preferences > Advanced, then press `Cmd+Option+I`

3. **Navigate to Cookies**
   - Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox)
   - In the left sidebar, expand **Cookies**
   - Click on `https://platform.worldquantbrain.com` or `https://api.worldquantbrain.com`

4. **Copy All Cookies**
   - You need to copy all cookies in the format: `key1=value1; key2=value2; key3=value3`
   - Look for important cookies like `t` (token), `_ga`, `_gcl_au`, etc.

5. **Alternative Method - Copy from Network Tab**
   - Go to the **Network** tab in Developer Tools
   - Refresh the page or make a request to WorldQuant Brain
   - Click on any request to `api.worldquantbrain.com`
   - Find the **Cookie** header in the Request Headers section
   - Copy the entire cookie string

## How to Use Your Cookie

### Option 1: Create cookie.txt File

Create a file named `cookie.txt` in one of these locations:
- `generation_two/cookie.txt` (recommended)
- `worldquant-miner/cookie.txt`
- Current working directory

**Format:**
```
_gcl_au=1.1.524283951.1766295055; _ga=GA1.1.17466726069820b83e5d6113c8; _ga_FXKNEPLB1N=GS2.1.s1767543636$o1$g1$t1767544336$j60$l0$h0; t=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJIRmM3S2laWGFlbzJwSWJhd1lWSmNLd3p5M1hiTjNhMyIsImV4cCI6MTc2NzU1OTAxN30.nml4Au3IS06e5PQRS4tQSxqLddqF2zrhM3yGH9tRPNw; _ga_9RN6WVT1K1=GS2.1.s1767541796$o2$g1$t1767544693$j47$l0$h0
```

Just paste your cookie string as-is, no formatting needed.

### Option 2: Enter Cookie via GUI

If no `cookie.txt` file is found, the GUI will show a login dialog where you can paste your cookie string.

## Running the Application

Start the application as usual:

```bash
python gui/run_gui.py
```

The application will:
1. Search for `cookie.txt` in standard locations
2. If found, load and validate the cookie
3. If not found, show a login dialog for manual cookie entry

## Cookie Expiration

**Important:** Cookies expire after a certain period. If you get authentication errors:
1. Go back to your browser
2. Refresh the WorldQuant Brain page
3. Copy the new cookie string
4. Update your `cookie.txt` file

## Security Notes

- **Never commit `cookie.txt` to version control**
- The file is already added to `.gitignore`
- Keep your cookie string private - it gives full access to your account
- Treat cookies like passwords

## Troubleshooting

### Authentication Failed
- Make sure you copied the entire cookie string
- Check that the cookie hasn't expired
- Verify you're logged in to WorldQuant Brain in your browser
- Try copying the cookie again from a fresh login

### No Cookie File Found
- Check the file is named exactly `cookie.txt` (not `cookie.txt.txt`)
- Verify it's in one of the searched locations
- The application will prompt you to enter the cookie manually if not found

## Example

See `cookie.txt.example` for the format of a valid cookie string.
