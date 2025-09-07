Compare documentation and API changes between library versions using Context7.

Steps:
1. Query Context7 for both specified versions of the library
2. Extract documentation for each version
3. Identify breaking changes, new features, and deprecated APIs
4. Generate migration recommendations
5. Assess impact on current implementation
6. Store comparison results in ConPort

Arguments: [library_name] [old_version] [new_version] [focus]

Example: /context7-compare requests 2.28.0 2.31.0 breaking-changes
Example: /context7-compare fastapi 0.100.0 0.104.1 new-features
Example: /context7-compare sqlalchemy 2.0 2.1 migration

Expected output: Version comparison report, breaking changes, new features, and migration recommendations.