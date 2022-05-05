import os
import threading
import time

import requests


class Paper_list_download():
    def Handler(self, start, end, url, filename):
        # specify the starting and ending of the file
        headers = {'Range': 'bytes=%d-%d' % (start, end)}
        # request the specified part and get into variable
        r = requests.get(url, headers=headers, stream=True)
        # open the file and write the content of the html page into file.
        with open(filename, "r+b") as fp:
            fp.seek(start)
            var = fp.tell()
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

        part = int(file_size) / number_of_threads
        fp = open(file_name, "wb")
        fp.close()
        for i in range(number_of_threads):
            start = int(part * i)
            end = int(start + part)
            # create a Thread with start and end locations
            t = threading.Thread(target=self.Handler,
                                 kwargs={'start': start, 'end': end, 'url': url_of_file, 'filename': file_name})
            t.setDaemon(True)
            t.start()

        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()


if __name__ == '__main__':

    info_txt_path = 'D:\\Code\\poincloudProcessor-P2PContrast\\tasks\\test_semantickitti\\paper_list.txt'  # todo:1
    '''
    example:
    https://arxiv.org/pdf/2202.01810.pdf
    https://openaccess.thecvf.com/content/CVPR2021/papers/Roh_Spatially_Consistent_Representation_Learning_CVPR_2021_paper.pdf
    '''
    save_path = 'F:\\zotero papers\\'  # todo: 2 #

    paper_list_downloader = Paper_list_download()

    file = open(info_txt_path)
    for line in file.readlines():
        pdf_url = line.strip("\n")

        (path, filename) = os.path.split(pdf_url)

        print('\nDownloadingpdf :{}.'.format(pdf_url))

        # pdf_url = 'https://arxiv.org/pdf/1709.06508.pdf'

        # print('\nDownloading {} ...'.format(filename))
        # pdf_url = 'https://arxiv.org/pdf/{}.pdf'.format(arxiv_id)
        # filename = filename_replace(paper_title) + '.pdf'
        ts = time.time()
        paper_list_downloader.download_file(url_of_file=pdf_url, name=os.path.join(save_path, filename),
                                            number_of_threads=1)
        te = time.time()
        print('{:.0f}s [Complete] {}'.format(te - ts, filename))
