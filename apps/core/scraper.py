import hashlib
import re
from datetime import date, time

import requests
from bs4 import BeautifulSoup

from .models import Exam, Major, PageSnapshot, Professor, SchoolClass


def scrape_from_major(major: Major):
    response = requests.get(major.url)
    response.encoding = "windows-1250"

    html = response.text

    page_hash = hashlib.sha256(response.content).hexdigest()
    last_snapshot: PageSnapshot = major.snapshots.order_by("-fetched_at").first()  # type: ignore

    if not last_snapshot:
        print(f"No previous snapshot found for {major.name}. Creating new snapshot.")
        PageSnapshot.objects.create(major=major, page_hash=page_hash)
    elif last_snapshot.page_hash and last_snapshot.page_hash == page_hash:
        print(f"No changes detected for {major.name}. Skipping.")
        return
    else:
        print(f"Changes detected for {major.name}. Updating database.")
        PageSnapshot.objects.create(major=major, page_hash=page_hash)

    soup = BeautifulSoup(html, "lxml")

    school_classes = soup.find_all("a", id=re.compile(r"^PrTAG\d+$"))

    for school_class in school_classes:
        # Extract class name
        class_name = school_class.find_next("h2")
        if class_name:
            class_name = class_name.text.strip()
        else:
            class_name = "Neznan predmet"

        # Extract professor's full name
        professor_full_name = school_class.find_next("p")
        if professor_full_name:
            professor_full_name = professor_full_name.text.strip()
        else:
            professor_full_name = "Neznan profesor"

        ## Check against the database

        professor, _ = Professor.objects.get_or_create(full_name=professor_full_name)

        # class_ because class is a reserved keyword in Python
        class_ = SchoolClass.objects.filter(name=class_name, major=major).first()
        if class_:
            if class_.professor != professor:
                class_.professor = professor
                class_.save()
        else:
            class_ = SchoolClass.objects.create(name=class_name, major=major, professor=professor)

        table = school_class.find_next("table")
        if table:
            rows = table.find_all("tr")

            table_length = len(rows)
            if table_length < 2:
                continue  # Skip tables that don't have exams

            # First row is the header, skip it
            for i in range(1, len(rows)):
                row = rows[i]
                cells = row.find_all("td")
                if len(cells) == 4:
                    exam_name = cells[0].text.strip()
                    exam_date = cells[1].text.strip()
                    exam_time_and_classroom = cells[2].text.strip()

                    # Check if the exam has results available
                    exam_results = cells[3].find_next("img")
                    if exam_results:
                        exam_results = exam_results["src"] == "EvidencaRez.gif"
                    else:
                        exam_results = False

                    exam_time_and_classroom = exam_time_and_classroom.split(", ")

                    exam_time = ""
                    exam_classroom = ""

                    if len(exam_time_and_classroom) == 1:
                        exam_time = exam_time_and_classroom[0]
                        exam_classroom = ""
                    elif len(exam_time_and_classroom) >= 2:
                        exam_time = exam_time_and_classroom[0]
                        exam_classroom = ", ".join(exam_time_and_classroom[1:])

                    ## Process extracted data

                    if exam_date != "":
                        # Convert to ISO format
                        exam_date = exam_date.split(". ")[::-1]
                        for i in range(len(exam_date)):
                            exam_date[i] = exam_date[i].zfill(2)
                        exam_date = "-".join(exam_date)
                        exam_date = date.fromisoformat(exam_date)
                    else:
                        exam_date = None

                    if exam_time != "":
                        # Convert to ISO format
                        exam_time = exam_time.replace(".", ":")
                        exam_time = time.fromisoformat(exam_time)
                    else:
                        exam_time = None

                    # TODO: Maybe add additional regex check to ensure the time and date are in the
                    #       correct format just to be safe

                    # Check if the exam already exists in the database
                    exams = class_.exams.order_by("-date", "-time")  # type: ignore

                    if not exams.filter(name=exam_name).exists():
                        Exam.objects.create(
                            name=exam_name,
                            date=exam_date,
                            time=exam_time,
                            classroom=exam_classroom,
                            results_available=exam_results,
                            school_class=class_,
                        )
                    else:
                        # Check is there are any differences
                        current_exam = exams.filter(name=exam_name).first()

                        if (
                            current_exam.date != exam_date
                            or current_exam.time != exam_time
                            or current_exam.classroom != exam_classroom
                            or current_exam.results_available != exam_results
                        ):
                            current_exam.date = exam_date
                            current_exam.time = exam_time
                            current_exam.classroom = exam_classroom
                            current_exam.results_available = exam_results
                            current_exam.save()

                            # TODO: Send Email about the change
                            # TODO: Maybe send email to admin if error occurs
