import requests

# Herd coded for now, can easily be changed if needed
URL = "https://a3.sckr.si/EviVss/IzpitniRoki46-1-1.htm"


def get_files():
    print(f"Getting HTM file from {URL}...")
    response = requests.get(URL)
    response.encoding = "windows-1250"

    print("Saving HTM file to ./files/rezultati.example.htm...")
    with open("./files/rezultati.example.htm", "w", encoding="windows-1250") as f:
        f.write(response.text)


if __name__ == "__main__":
    get_files()
