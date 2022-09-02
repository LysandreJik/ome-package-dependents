import tqdm
from bs4 import BeautifulSoup
import requests
from time import sleep


def scrape_dependents(owner, repository, dependent_type='repository'):
    if dependent_type == 'repository':
        url = f"https://github.com/{owner}/{repository}/network/dependents"
    elif dependent_type == 'package':
        url = f"https://github.com/{owner}/{repository}/network/dependents?dependent_type=PACKAGE"
    else:
        raise ValueError(f'Unknown dependent type: {dependent_type}')

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    box = soup.select(".Box-header")[0]
    repositories, packages = [int(x.text.strip().split()[0].replace(',', '')) for x in box.select('.btn-link')[:2]]

    if dependent_type == 'repository':
        pbar = tqdm.tqdm(total=repositories)
    else:
        pbar = tqdm.tqdm(total=packages)

    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        box_rows = soup.select('.Box-row')
        repos = []
        failed_fetches = 0
        for box_row in box_rows:
            try:
                repos.append({
                    'name': box_row.select("a[data-hovercard-type=repository]")[0]["href"].lstrip("/"),
                    'stars': int(box_row.select('.flex-justify-end')[0].select('span')[0].text.strip().replace(',', '')),
                    'forks': int(box_row.select('.flex-justify-end')[0].select('span')[1].text.strip().replace(',', '')),

                })
            except IndexError:
                failed_fetches += 1
        yield from repos

        pbar.update(len(repos) + failed_fetches)
        try:
            next_link = soup.select(".paginate-container")[0].find("a", text="Next")
        except IndexError:
            break

        if next_link is not None:
            url = next_link["href"]
            sleep(0.5)
        else:
            url = None