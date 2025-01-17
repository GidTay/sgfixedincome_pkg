# sgfixedincome_pkg

[![codecov](https://codecov.io/gh/GidTay/sgfixedincome_pkg/branch/main/graph/badge.svg)](https://codecov.io/gh/GidTay/sgfixedincome_pkg)

A python package to aggregate and analyse data on SGD-denominated retail fixed income products in Singapore.

Are you a non-technical user? Use the app [here](https://sgfixedincome.streamlit.app/).

Lazy to read the documentation? Watch [this video](https://youtu.be/X_r8mnLpAo8) for an overview of the package and web app.

## Introduction

This python package contains:

- `scraper.py`: A generalized web scraper to extract fixed deposit rates data from bank websites that display this data in a suitable table format.
- `mas_api_client.py`: An API client that interacts with several Monetary Authority of Singapore (MAS) bonds and bills API endpoints. In particular, we provide functions to extract data on Singapore Savings Bonds (SSB) and Treasury bills (T-bills).
- `consolidate.py`: Functions to format, merge, and consolidate data obtained from scraping bank websites and from the MAS API.
- `analysis.py`: Functions to analyse and visualise extracted fixed income product data.
- `streamlit_app/app.py`: code for streamlit web interface 

## Installation

The package can be installed using:

```bash
$ pip install sgfixedincome_pkg
```

## Documentation and Usage

Detailed documentation can be found on [Read the Docs](https://sgfixedincome-pkg.readthedocs.io/en/latest/).

You can also explore detailed vignettes demonstrating the package's functionality:

- [Main vignette](https://github.com/GidTay/sgfixedincome_pkg/blob/main/docs/vignettes/vignette_main.ipynb): fetch, analyze, and visualize retail fixed income product data.
- [MAS vignette](https://github.com/GidTay/sgfixedincome_pkg/blob/main/docs/vignettes/vignette_mas.ipynb): how to use the MAS bonds and bills API client and related functions
- [Scraper vignette](https://github.com/GidTay/sgfixedincome_pkg/blob/main/docs/vignettes/vignette_scraper.ipynb): how to use functions that scrape bank fixed deposit websites

Or simply explore the [streamlit app](https://sgfixedincome.streamlit.app/).

## Running the Streamlit App
After installation, find the installation location with:
```bash
$ pip show sgfixedincome_pkg
```

Then run:
```bash
$ streamlit run "C:\Path\To\site-packages\sgfixedincome_pkg\streamlit_app\app.py"
```

For example:
```bash
$ streamlit run "C:\Users\John\Desktop\Folder\test_env\Lib\site-packages\sgfixedincome_pkg\streamlit_app\app.py"
```

This will open a browser window with an interactive dashboard.

Note: The web interface requires an active internet connection to fetch current rates and product information.

## The App's Data Fetching & Caching Logic
To optimize performance and reliability:
1. Data is scraped and stored in a central cache once every 24 hours, using this [Github repository](https://github.com/GidTay/sgfixedincome_cache).
2. If the cached data has any fetch failures but a previous successful version exists (no failures), you'll see an option to use that version instead.
3. If the cached data is more than 2 days old, the tool will fetch fresh data directly.

When running the tool:
- If you're using the hosted web app, you'll see whether the data is from the cache or freshly fetched
- If you're running locally (streamlit run after pip install), the tool will always fetch fresh data
- The data timestamp (in Singapore time) is always displayed in the sidebar

If present, warnings and failures will be shown in the sidebar to highlight any data fetching issues.  

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`sgfixedincome_pkg` was created by [Gideon Tay](https://github.com/GidTay). It is licensed under the terms of the MIT license.

## Contact

Reach out to me on [LinkedIn](https://www.linkedin.com/in/gideon-tay-yee-chuen/) if you have any questions or suggestions.

## Credits

`sgfixedincome_pkg` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
