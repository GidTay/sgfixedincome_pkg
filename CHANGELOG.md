# Changelog

<!--next-version-placeholder-->

## v0.1.2 - (13/12/2024)

- First functional release of `sgfixedincome_pkg` on TestPyPI!

## v0.1.9 - (15/12/2024)

- Fix dependency management issues in pyproject.toml and poetry.lock.
  Previously in v0.1.2, seaborn and matplotlib were not automatically installed
  upon pip install.
- Made the streamlit app part of the base package rather than an optional add-on
- Fix the README.md's instructions on how to run the streamlit app
- Improved the streamlit app's caching system to not fetch data every time current SSB holding input is changed
- Added a few more test functions (for developers)
- Published on PyPI

## v0.2.0 - (17/12/2024)

### Added
- GitHub-based caching system for Streamlit app
  - Reduces API calls and improves performance
  - Shares cached data across all cloud app users
  - Falls back to direct fetching for local installations
- Data timestamp display in Streamlit sidebar
- Option to use latest successful version when current version has failures
- Local secrets configuration to suppress warnings

### Changed
- Improved error handling for data fetching
- Updated Streamlit UI with clearer data source information