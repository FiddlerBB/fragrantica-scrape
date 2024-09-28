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
        with open(f'{output}', 'w') as f:
            f.write(content)
    browser.close()
    return content


def get_html_frag(p: Playwright, link: str, output: str):
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto(f"{link}")
    time.sleep(2)
    button_selector = 'button[class="hollow button small"]'
    while True:
        button = page.locator(button_selector)
        if button.count() > 0:
            button.click(force=True)
            # page.click(button_selector)
            print('clicked button')
            page.wait_for_timeout(1)
        else:
            print("Button no longer exists. Exiting loop.")
            break
    content = page.content()
    with open ('./out/test.html', 'w') as f:
        f.write(content)
    



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
    get_html(p, frags['link'],file_path , True)

    # change to content later
    

def parse_frag(content: str):
    html = HTMLParser(content)
    accords = html.css('div[class="cell accord-box"')
    main_accords = []
    for accord in accords:
        main_accords.append(accord.text)

    reaction_vote = get_votes(html, '#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div:nth-child(1)')
    occasion_vote = get_votes(html, "#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(2) > div:nth-child(4) > div:nth-child(2)")

    rating = html.css_first('span[itemprop="ratingValue"]').text().strip()
    number_of_rating = html.css_first('span[itemprop="ratingCount"]').text().strip()

    description = html.css_first('div[itemprop="description"] > p').text().strip().replace('<b>', '')
    top_notes = description.split("Top notes are ")[1].split(";")[0].replace(' and', ',').strip()
    mid_notes = description.split("middle notes are ")[1].split(";")[0].replace(' and', ',').strip()
    base_notes = description.split("base notes are ")[1].split(".")[0].replace(' and', ',').strip()

    overview_review = parse_pros_cons(html)


def parse_pros_cons(html: HTMLParser):
    pros_cons: list[HTMLParser] = html.css('#main-content > div:nth-child(1) > div.small-12.medium-12.large-9.cell > div > div:nth-child(4) > div > div')
    overview_review = {'pros': [], 'cons': []}
    if pros_cons:
        for pc in pros_cons:
            overview = pc.css_first('h4[class="header"]').text().strip().lower()
            reviews = pc.css('div[class="cell small-12"]')
            review_result = [review.text().strip() for review in reviews]
            overview_review[overview] = review_result
    return overview_review



def get_votes(html: HTMLParser, selector: str):
    result = {}
    search_css = html.css_first(selector)
    res = search_css.css('div[style="display: flex; flex-direction: column; justify-content: space-around; cursor: pointer;"]')
    for r_ in res:
        name = r_.css_first('div[style="display: flex; justify-content: center;"]').text().strip()
        # the attribe will be like this
        # {'style': 'border-radius: 0.2rem; height: 0.3rem; background: rgb(255, 118, 111); width: 100%; opacity: 1;'}
        rate = r_.css_first('div[class="voting-small-chart-size"] > div > div').attributes['style'].split(';')[-3].replace(' width: ', '')
        result[name] = rate
    return result


# def parse_frag()
    


def main():
    designer = "Beaufort-London"
    designer_url = f"https://www.fragrantica.com/designers/{designer}.html"
    # with sync_playwright() as playwright:
    #     get_html(p=playwright, link=designer_url, output=f"./out/{designer}", save_file=True)
    #     frags = parse_links(designer)[5]
        
    #     get_fragrances(playwright,frags)
    # file_path = f"./out/fathom_v.html"
    # with open(file_path, 'r') as f:
    #     content = f.read()
    # parse_frag(content)

# main()
def test():
    with sync_playwright() as playwright:
        url = 'https://www.fragrantica.com/perfume/BeauFort-London/Fathom-V-40732.html'
        get_html_frag(playwright, url, None)
test()