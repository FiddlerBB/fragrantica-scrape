from playwright.sync_api import sync_playwright, Playwright
import time, csv, re
from selectolax.parser import HTMLParser

width_pattern = re.compile(r'width:\s*([^;]+);')

base_url = 'https://www.fragrantica.com'

def get_html(p: Playwright, link: str, output: str, save_file: bool=False):
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto(f"{link}")
    time.sleep(5)
    content = page.content()
    if save_file:
        with open(f'{output}.html', 'w') as f:
            f.write(content)
    browser.close()
    return content


def parse_links(designer: str):
    with open(f'./out/{designer}.html', 'r') as f:
        html = HTMLParser(f.read())
    
    frags = html.css('div.flex-child-auto')
    frags_link = []
    for frag in frags:
        
        name = frag.text().strip()
        link = f"{base_url}{frag.css_first('a').attrs['href']}"
        frags_link.append({'name': f"{name}", 'link': f"{link}"})
    with open('./out/frag_links.csv', mode='w', newline='', encoding='utf-8') as f:
        headers = ['name', 'link']
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for record in frags_link:
            writer.writerow(record)
    return frags_link    


def get_fragrances(p:Playwright, frags: dict):
    time.sleep(2)
    file_path = f"./out/{frags['name'].lower().replace(' ', '_')}.html"
    get_html(p, frags['link'],file_path , False)

    # change to content later
    

def parse_frag(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    html = HTMLParser(content)
    accords = html.css('div[class="cell accord-box"')
    main_accords = []
    for accord in accords:
        main_accords.append(accord.text)

    like = html.css_first('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div:nth-child() > div')
    votes = like.css('div[style="display: flex; flex-direction: column; justify-content: space-around; cursor: pointer;"]')
    vote_result = {}
    for vote in votes:
        vote_name = vote.css_first('span[class="vote-button-legend show-for-medium"]').text().strip()
        # the attribe will be like this
        # {'style': 'border-radius: 0.2rem; height: 0.3rem; background: rgb(255, 118, 111); width: 100%; opacity: 1;'}
        vote_rate = vote.css_first('div[class="voting-small-chart-size"] > div > div').attributes['style'].split(';')[-3].replace(' width: ', '')
        vote_result[vote_name] = vote_rate
    
    selector = '#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div:nth-child() > div'
    occasions = get_votes(html, selector)
    print(occasions)


def get_votes(html: HTMLParser, selector: str):
    result = {}
    search_css = html.css_first(selector)
    res = search_css.css('div[style="display: flex; flex-direction: column; justify-content: space-around; cursor: pointer;"]')
    for r_ in res:
        name = r_.css_first('span[class="vote-button-legend show-for-medium"]').text().strip()
        rate = r_.css_first('div[class="voting-small-chart-size"] > div > div').attributes['style'].split(';')[-3].replace(' width: ', '')
        result[name] = rate
    return result





# def parse_frag()
    





def main():
    designer = "Beaufort-London"
    designer_url = f"https://www.fragrantica.com/designers/{designer}.html"
    # with sync_playwright() as playwright:
        # get_html(p=playwright, link=designer_url, output=f"./out/{designer}", True)
        # frags = parse_links(designer)
        
        # get_fragrances(playwright,frags)
    file_path = f"./out/terror_&_magnificence.html"
    parse_frag(file_path)

main()