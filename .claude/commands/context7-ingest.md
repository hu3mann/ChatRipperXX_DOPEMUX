Ingest library documentation into Context7 for future querying.

Steps:
1. Check if library documentation is already available in Context7
2. If not found, ingest the library documentation from official sources
3. Verify ingestion success and documentation availability
4. Test query functionality with basic examples
5. Update ConPort with available documentation resources

Arguments: [library_name] [version] [source_url]

Example: /context7-ingest requests latest https://requests.readthedocs.io
Example: /context7-ingest fastapi 0.104.1 https://fastapi.tiangolo.com

Expected output: Ingestion status, documentation size, and available search endpoints.