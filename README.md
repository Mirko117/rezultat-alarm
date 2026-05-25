# rezultat-alarm

Readme soon... More details on [Notion](https://www.notion.so/rezultat-alarm-345d1b824ba18022947cca2b9ca705d1)

## Testing

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure the mock server is running on `http://localhost:8001` and serving `rezultati.htm`:
   ```bash
   cd mock_server
   python get_files.py
   # copy results to files/rezultati.htm if needed
   python server.py
   ```
3. Run pytest (uses sqlite and the test settings module):
   ```bash
   python -m pytest
   ```
