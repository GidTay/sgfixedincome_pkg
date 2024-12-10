# sgfixedincome_pkg

A python package to aggregate and analyse data on SGD-denominated retail fixed income products in Singapore.

## Introduction

This python package contains:

- `scraper.py`: A generalized web scraper to extract data on fixed deposit rates from bank websites that display this data in a suitable table format.
- `mas_api_client.py`: An API client that interacts with several Monetary Authority of Singapore (MAS) bonds and bills API endpoints. In particular, we provide functions to extract data on Singapore Savings Bonds (SSB) and Treasury bills (T-bills).
- `consolidate.py`: Functions to format, merge, and consolidate data obtained from scraping bank websites and from the MAS API.
- `analysis.py`: Functions to analyse and visualise extracted fixed income product data.

## Installation

You can install this package using:

```bash
$ pip install sgfixedincome_pkg
```

## Documentation and Usage

Detailed documentation can be found on Read the Docs.

You can also explore detailed vignettes demonstrating the package's functionality:

- [Main vignette](vignettes/vignette_main.ipynb): fetch, analyze, and visualize retail fixed income product data.
- [MAS vignette](vignettes/vignette_mas.ipynb): how to use the MAS bonds and bills API client and related functions

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`sgfixedincome_pkg` was created by [Gideon Tay](https://github.com/GidTay). It is licensed under the terms of the MIT license.

## Contact

Reach out to me on [LinkedIn](https://www.linkedin.com/in/gideon-tay-yee-chuen/) if you have any questions or suggestions.

## Credits

`sgfixedincome_pkg` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
