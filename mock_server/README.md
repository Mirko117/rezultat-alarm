# Mock Server

This is a simple mock server that can be used to test the app. It simulates the behaviour of the actual school website.


## Why?

Before adding this, testing to see if the app worked was a pain. I had to wait for school to update the results page, which could take a while. With this mock server, I can test my changes immediately without having to wait for the school to make any updates.


## Usage

First, create a copy of a `rezultati.example.htm` file and name it `rezultati.htm`. Server will return the contents of this file when a request is made. 


**Be careful with the encoding,** files should be encoded in `windows-1250` encoding, same as the actual school server.

Then, run the server using the following command:

```bash
python server.py
```

The server will start on `http://localhost:8001`. To make the app use mock server, add the new Major, name it as you wish and set the URL to the link above.

When you want to make changes, you can simply just edit the `rezultati.htm` file, refresh the mock server and run scraper again to see the changes.

Something like this:

```bash
python manage.py shell

>>Major.objects.create(name="localhost", url="http://localhost:8001")

>>exit()

python manage.py scrape
```