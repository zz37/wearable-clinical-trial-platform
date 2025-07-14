what are i am bulding:


delta load: 
is needed because when was the last run 'runned', so to solve this we can use a last_run.json, but where should it go?
--> ok, so last_run.json would be a simple local state that will record the last timestamp the ingestion script successfully ran. That is will have the timestamp of the las ok ingestion. 
----> Like a short-term memory, to know where it left off, so it can only ingest new rows each time.
-----> Will be key so ingestion is not flooded crucial for the `delta load` — 
so the system only ingests new rows each time.

-- > Go in: `ingestion/last_run.json`` or better in ingestion/state/last_run.json
