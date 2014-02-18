4chan-downloader
================

Ugly, multithreaded 4chan downloader

## Usage:
`python 4chan-downloader.py -t [THREAD] -f [NAME] -s URLS`

- `URLS` required, pass a single url, or a list of urls

- `-t [THREAD]` Optional, number of threads to spawn. Default is 4

- `-f [NAME]` Optional, name of the downloaded files. If left empty, the  default is `%id_thread%/%filename%%extension%`

   If it's a relative path, then files will be downloaded in the current folder

   It's possible to use any variables specified in the [4chan api](https://github.com/4chan/4chan-API) for the filenames, put between two `%`, plus `%id_thread%` and `%board%`

- `-s` Optional, silent. The program will not output anything
