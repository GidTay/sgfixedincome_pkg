# sgfixedincome_pkg

[![codecov](https://codecov.io/gh/GidTay/sgfixedincome_pkg/branch/main/graph/badge.svg)](https://codecov.io/gh/GidTay/sgfixedincome_pkg)

A python package to aggregate and analyse data on SGD-denominated retail fixed income products in Singapore.

Are you a non-technical user? Use the app [here](https://sgfixedincome.streamlit.app/).

## Introduction

This python package contains:

- `scraper.py`: A generalized web scraper to extract data on fixed deposit rates from bank websites that display this data in a suitable table format.
- `mas_api_client.py`: An API client that interacts with several Monetary Authority of Singapore (MAS) bonds and bills API endpoints. In particular, we provide functions to extract data on Singapore Savings Bonds (SSB) and Treasury bills (T-bills).
- `consolidate.py`: Functions to format, merge, and consolidate data obtained from scraping bank websites and from the MAS API.
- `analysis.py`: Functions to analyse and visualise extracted fixed income product data.
- `streamlit_app/app.py`: code for streamlit web interface 

## Installation

The base package can be installed without the web interface using:

```bash
$ pip install sgfixedincome_pkg
```

Besides the base package, this package includes an optional Streamlit web interface for easy analysis of Singapore fixed income investments. To install the package with the web interface:

```bash
$ pip install sgfixedincome[app]
```

### Documentation and Usage

Detailed documentation can be found on Read the Docs.

You can also explore detailed vignettes demonstrating the package's functionality:

- [Main vignette](docs/vignettes/vignette_main.ipynb): fetch, analyze, and visualize retail fixed income product data.
- [MAS vignette](docs/vignettes/vignette_mas.ipynb): how to use the MAS bonds and bills API client and related functions
- [Scraper vignette](docs/vignettes/vignette_scraper.ipynb): how to use functions that scrape bank fixed deposit websites

Or simply explore the [streamlit app](https://sgfixedincome.streamlit.app/).

### Running the Web Interface
After installation with the [app] extra, you can launch the web interface using:
```bash
$ sgfixedincome-app
```

Alternatively, in the src/sgfixedincome_pkg/streamlit_app/ directory, run:
```bash
$ streamlit run app.py
```

This will open a browser window with an interactive dashboard.

Note: The web interface requires an active internet connection to fetch current rates and product information.

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`sgfixedincome_pkg` was created by [Gideon Tay](https://github.com/GidTay). It is licensed under the terms of the MIT license.

## Contact

Reach out to me on [LinkedIn](https://www.linkedin.com/in/gideon-tay-yee-chuen/) if you have any questions or suggestions.

## Credits

`sgfixedincome_pkg` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
