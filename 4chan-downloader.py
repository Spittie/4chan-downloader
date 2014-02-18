import argparse
import os
import re
import threading
import urllib
import requests
import sys

urls = []
global stop
stop = 0
event = threading.Event()
event.clear()


def main():
    lock = threading.Lock()
    parser = argparse.ArgumentParser(description="Download images from 4chan")
    parser.add_argument('url', type=str, nargs='+')
    parser.add_argument('-t', '--threads')
    parser.add_argument('-f', '--filename')
    parser.add_argument('-s', '--silent', action="store_true", default=False)
    args = parser.parse_args()

    default_threads = 4
    if args.threads:
        default_threads = args.threads

    filename = "%id_thread%/%filename%%ext%"
    if args.filename:
        filename = args.filename

    options = {"silent": args.silent}

    for url in args.url:
        regex = re.search("https?://boards.4chan.org/([a-z0-9]{1,4})/res/(\d+)", url)
        if not regex:
            print "url not valid"
            exit()
        board = regex.group(1)
        id_thread = regex.group(2)
        json_url = "https://a.4cdn.org/" + board + "/res/" + id_thread + ".json"

        try:
            r = requests.get(json_url)
        except requests.ConnectionError:
            print "Connection Error"
            exit()

        if r.status_code != 200:
            print "error opening 4chan"
            exit()

        json = r.json()
        for post in json["posts"]:
            try:
                if post["filename"]:
                    img_url = "http://i.4cdn.org/" + board + "/src/" + str(post["tim"]) + post["ext"]
                    name = {}
                    for i in post:
                        name[i] = post[i]
                    name["board"] = board
                    name["id_thread"] = id_thread
                    urls.append([img_url, name])
                    lpath = [img_url, name]
            except KeyError:
                pass
        path = get_fullname(lpath, filename)
        directory = os.path.dirname(os.path.expanduser(path))
        if not os.path.exists(directory):
            os.makedirs(directory)

    for ai in range(0, int(default_threads)):
        t = DownloadImage(lock, default_threads, filename, options)
        t.start()

    try:
        while not event.is_set():
            pass
    except KeyboardInterrupt:
        global stop
        stop = 1
        print "Interrupted"
        sys.exit(1)

    sys.exit(0)


def get_fullname(url, filename):
    path = ""
    for i in filename.split("%"):
        try:
            path += str(url[1][i])
        except KeyError:
            path += str(i)
    return path


def get_filename(url, filename):
    path = ""
    for i in filename.split("%"):
        try:
            path += str(url[1][i])
        except KeyError:
            path += str(i)
    return path


class DownloadImage(threading.Thread):
    def __init__(self, lock, threads, filename, options):
        threading.Thread.__init__(self)
        self.lock = lock
        self.threads = threads
        self.filename = filename
        self.options = options

    def run(self):
        global stop
        while urls:
            if stop == 1:
                exit()
            self.lock.acquire()
            try:
                url = urls.pop()
                if not self.options["silent"]:
                    print url[0] + " --> " + get_filename(url, self.filename) + " (" + self.name + ")"
            except IndexError:
                self.lock.release()
                exit()
            self.lock.release()
            if not os.path.exists(os.path.expanduser(get_filename(url, self.filename))):
                urllib.urlretrieve(url[0], os.path.expanduser(get_filename(url, self.filename)))
                pass
        event.set()
        exit()


if __name__ == '__main__':
    main()