from bs4 import BeautifulSoup as BS
from loguru import logger
from pathlib import Path
import click
import requests
import time
import webbrowser

headers = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/85.0.4183.102 "
        "Safari/537.36"
    )
}


def get_with_useragent(url):
    """
    Get a url with Google Chrome useragent
    """
    return requests.get(url, headers=headers)


def get_product_urls(url):
    """
    Gets list of product urls from lttstore.com url
    """
    try:
        res = get_with_useragent(url)
        html = BS(res.content, "lxml-html")
        producturls = {
            "https://www.lttstore.com" + product.attrs["href"]
            for product in html.find_all(
                "a", {"class": "ProductItem__ImageWrapper"}
            )
        }
        return producturls

    except Exception as e:
        # LTT hates my script :c
        logger.exception("Couldn't fetch product urls", e)


@click.command()
@click.argument("outputfile", type=click.Path())
def load_products(outputfile):
    click.secho(
        "Downloading list of existing product urls to {}...".format(
            outputfile
        ),
        fg="cyan",
    )

    # Emtpy set
    urls = set()

    # Load products from page 1
    urls |= get_product_urls("https://www.lttstore.com/collections/all?page=1")

    # Load products from page 2
    urls |= get_product_urls("https://www.lttstore.com/collections/all?page=2")

    # Write product urls to a file
    with open(outputfile, "w") as f:
        for url in urls:
            f.write(url + "\n")

    click.secho(
        "Downloaded list of existing product urls to {}".format(outputfile),
        fg="green",
    )


@click.command()
@click.option(
    "--browser",
    "browserpath",
    type=click.Path(),
    help="Path to the browser binary",
)
@click.option(
    "--existing-products",
    "existing_products_path",
    type=click.Path(),
    help="Path to the browser binary",
)
@click.option(
    "--interval",
    "interval",
    type=float,
    default=0.5,
    help="Interval between fetches",
)
def watch_products(browserpath, existing_products_path, interval):
    # Check that browserpath exists and is a file
    browserpath_path = Path(browserpath)

    if not browserpath_path.exists():
        click.secho("Invalid browser path: path doesn't exist", fg="red")
        return

    if not browserpath_path.is_file():
        click.secho("Invalid browser path: path is not a file", fg="red")
        return

    # Register the browser to the webbrowser library
    webbrowser.register(
        name="mybrowser",
        klass=None,
        instance=webbrowser.BackgroundBrowser(browserpath),
        preferred=True,
    )

    # Check that existing_products_path exists and is a file
    existing_products_path = Path(existing_products_path)

    if not existing_products_path.exists():
        click.secho("Invalid browser path: path doesn't exist", fg="red")
        return

    if not existing_products_path.is_file():
        click.secho("Invalid browser path: path is not a file", fg="red")
        return

    # Read urls from the file into a set
    existing_products = set(
        existing_products_path.read_text().strip().splitlines()
    )

    click.secho("Started watching for new products", fg="green")

    # Loop over the watchdog code
    while True:
        # Empty set
        urls = set()

        # Load products from page 1
        urls |= get_product_urls(
            "https://www.lttstore.com/collections/all?page=1"
        )

        # Load products from page 2
        urls |= get_product_urls(
            "https://www.lttstore.com/collections/all?page=2"
        )

        # Remove product urls that were listed in the file
        urls -= existing_products

        # If there are still urls, open them in the browser and exit
        if urls:
            click.secho("Found new products, opening urls", fg="green")
            for url in urls:
                webbrowser.get("mybrowser").open(url)
            break
            click.secho("Urls opened", fg="green")
        time.sleep(interval)

    click.secho("Exiting", fg="green")


cli = click.Group(
    name="lttstorewatchdog",
    commands={"loadproducts": load_products, "watchproducts": watch_products},
)

if __name__ == "__main__":
    cli()
