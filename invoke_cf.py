import requests
import google.auth
import google.auth.transport.requests
import json

# creds, project = google.auth.default()

# creds.valid is False, and creds.token is None
# Need to refresh credentials to populate those

# auth_req = google.auth.transport.requests.Request()
# creds.refresh(auth_req)

r = requests.post(
    "https://europe-west3-cloud-computing-project-418718.cloudfunctions.net/test-cf",
    headers={
        # "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    },
    json={"test_input": "testowe cos"},
)
out = r.content.decode("ascii")
out = json.loads(out)
print(out["test"])