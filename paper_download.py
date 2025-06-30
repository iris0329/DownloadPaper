import os
import threading
import time
import requests
from bs4 import BeautifulSoup


class PaperListDownloader:
    def Handler(self, start, end, url, filename):
        headers = {'Range': f'bytes={start}-{end}'}
        r = requests.get(url, headers=headers, stream=True)
        with open(filename, "r+b") as fp:
            fp.seek(start)
            fp.write(r.content)

    def download_file(self, url_of_file, name, number_of_threads):
        r = requests.head(url_of_file)
        if name:
            file_name = name
        else:
            file_name = url_of_file.split('/')[-1]
        try:
            file_size = int(r.headers['content-length'])
        except:
            print("Invalid URL")
            return

        part = file_size // number_of_threads
        with open(file_name, "wb") as fp:
            fp.truncate(file_size)

        threads = []
        for i in range(number_of_threads):
            start = part * i
            end = file_size - 1 if i == number_of_threads - 1 else (start + part - 1)
            t = threading.Thread(target=self.Handler,
                                 kwargs={'start': start, 'end': end, 'url': url_of_file, 'filename': file_name})
            t.setDaemon(True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in "._- ").rstrip()


def get_title_from_url(url):
    try:
        if "arxiv.org" in url:
            # use abstract page to get title
            paper_id = url.split('/')[-1].replace('.pdf', '')
            abs_url = f"https://arxiv.org/abs/{paper_id}"
            r = requests.get(abs_url)
        else:
            r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text.strip()
            # arXiv titles are like "Title of Paper | arXiv..."
            title = title.split("|")[0].strip()
            return sanitize_filename(title) + ".pdf"
        return None
    except Exception as e:
        print(f"[Title Error] Cannot get title from {url}: {e}")
        return None


if __name__ == '__main__':
    info_txt_path = './paper_list.txt'  # todo:1
    save_path = './papers/'  # todo:2

    os.makedirs(save_path, exist_ok=True)

    paper_list_downloader = PaperListDownloader()

    with open(info_txt_path) as file:
        for line in file:
            pdf_url = line.strip()
            if not pdf_url:
                continue

            print('\nDownloading pdf: {}'.format(pdf_url))

            title_filename = get_title_from_url(pdf_url)
            if not title_filename:
                title_filename = pdf_url.split('/')[-1]

            full_path = os.path.join(save_path, title_filename)

            ts = time.time()
            paper_list_downloader.download_file(
                url_of_file=pdf_url,
                name=full_path,
                number_of_threads=1
            )
            te = time.time()
            print('{:.0f}s [Complete] {}'.format(te - ts, title_filename))
