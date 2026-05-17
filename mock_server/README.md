# Mock Server

This is a simple mock server that can be used to test the app. It simulates the behaviour of the actual school website.


## Why?

Before adding this, testing to see if the app worked was a pain. I had to wait for school to update the results page, which could take a while. With this mock server, I can test my changes immediately without having to wait for the school to make any updates.


## Usage

First, run the `get_files.py` script to create a `rezultati.example.htm` file, copy it and name it `rezultati.htm`. Server will return the contents of `rezultati.htm` file when a request is made. 


**Be careful with the encoding,** files should be encoded in `windows-1250` encoding, same as the actual school website. This should be handle by the `get_files.py` script, but just in case check it before running the server.

There are other files already provided in the `files/` directory (.css and gifs) that are used by the `rezultati.htm`. Right now I don't have time to make get script also download those files, and this approach is good enough for testing purposes. But in the future, I might add that functionality as well.

After gathering the files, you can run the server using the following command:

```bash
python server.py
```

The server will start on `http://localhost:8001`. To make the app use mock server, add the new Major, name it as you wish and set the URL to the link above.

Something like this:

```bash
python manage.py shell

>>Major.objects.create(name="localhost", url="http://localhost:8001")

>>exit()

python manage.py scrape
```

When you want to make changes, you can simply just edit the `rezultati.htm` file, refresh the mock server and run scraper again to check for the changes.
