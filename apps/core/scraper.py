import hashlib
import logging
import re
from datetime import date, time

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from .models import Exam, Major, PageSnapshot, Professor, SchoolClass

"""
Function with the underscore are ment to be private functions and should not be used outside of this
file.

They are also partially unstable, and when you use they you should wrap them in try except block to
catch any potential errors that might occur during the scraping process.
"""

logger = logging.getLogger("django")


def scrape_from_major(major: Major):
    try:
        response = requests.get(major.url)
        response.encoding = "windows-1250"

        html = response.text

        # Calculate the hash of the page content to detect changes
        # If hash is the same as the last snapshot, that means that the page has not changed and we
        # skip
        page_hash = hashlib.sha256(response.content).hexdigest()
        last_snapshot: PageSnapshot = major.snapshots.order_by("-fetched_at").first()  # type: ignore

        if last_snapshot and last_snapshot.page_hash and last_snapshot.page_hash == page_hash:
            logger.info(f"No changes detected for {major.name}. Skipping.")
            return

        soup = BeautifulSoup(html, "lxml")

        school_classes = soup.find_all("a", id=re.compile(r"^PrTAG\d+$"))

        if not school_classes:
            logger.info(f"No classes found for {major.name}.")
            return

        for school_class in school_classes:
            try:
                _scrape_majors_class(major, school_class)
            except Exception as e:
                logger.exception(f"Error occurred while scraping class for {major.name}: {e}")
                continue

        logger.info(f"Finished scraping {major.name}. Saving snapshot to the database.")

        if not last_snapshot:
            logger.info(f"No previous snapshot found for {major.name}. Creating new snapshot.")
            PageSnapshot.objects.create(major=major, page_hash=page_hash)
        else:
            logger.info(f"Changes detected for {major.name}. Updating database.")
            PageSnapshot.objects.create(major=major, page_hash=page_hash)

    except Exception as e:
        logger.critical(f"Error occurred while scraping {major.name}: {e}", exc_info=True)
        return


def _scrape_majors_class(major: Major, school_class: Tag):
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

    # Check against the database

    professor, created = Professor.objects.get_or_create(full_name=professor_full_name)
    if created:
        logger.info(f"New professor found: {professor_full_name}. Added to the database.")

    # class_ because class is a reserved keyword in Python
    class_ = SchoolClass.objects.filter(name=class_name, major=major).first()
    if class_:
        if class_.professor != professor:
            class_.professor = professor
            class_.save()
            logger.info(
                f"Professor updated for {class_name}."
                f" {class_.professor.full_name} -> {professor.full_name}"
            )
    else:
        class_ = SchoolClass.objects.create(name=class_name, major=major, professor=professor)
        logger.info(f"New class found: {class_name}. Added to the database.")

    table = school_class.find_next("table")
    if not table:
        logger.warning(f"Table not found for {class_name}. Skipping.")
        return

    exam_rows = table.find_all("tr")

    table_length = len(exam_rows)
    if table_length < 2:
        logger.info(f"Table for {class_name} is empty. Skipping.")
        return  # Skip tables that don't have exams

    # First row is the header, skip it
    for i in range(1, len(exam_rows)):
        try:
            row = exam_rows[i]
            _scrape_class_exam(class_, class_name, row)

        except Exception as e:
            logger.exception(f"Error occurred while scraping exam for {class_name}: {e}")
            continue


def _scrape_class_exam(class_: SchoolClass, class_name: str, exam_row: Tag):
    cells = exam_row.find_all("td")
    if len(cells) != 4:
        logger.error(f"Unexpected number of cells in row for {class_name}. Skipping.")
        return

    # Extract exam data
    exam_name = cells[0].text.strip()
    exam_date = cells[1].text.strip()
    exam_time_and_classroom = cells[2].text.strip()
    exam_results = cells[3].find_next("img")
    exam_code = cells[3].find_next("a")

    # First do exam_code ckecks because code is mandatory

    if not exam_code:
        logger.warning(f"No exam code found for {exam_name} in {class_name}. Skipping.")
        return
        # Right now we are skipping exams without code because we have no way to
        # identify them in the database and they are not that important anyway,
        # but maybe in the future we can add unique constraint to the records with
        # no code and identify them by their name, date and time or something like
        # that

    # RezultatiRoka17393.htm -> 17393
    exam_code = str(exam_code["href"])
    exam_code = re.search(r"\d+", exam_code)
    if exam_code:
        exam_code = exam_code.group(0)
    else:
        logger.warning(f"Could not extract exam code for {exam_name} in {class_name}. Skipping.")
        return

    if not exam_name:
        exam_name = "Neznan izpit"
        logger.warning(
            f"No exam name found for exam code {exam_code} in {class_name}. Using default name."
        )

    if exam_date != "" and exam_date is not None:
        # Convert to ISO format
        # Check if date has space after dot
        split_symbol = ". " if ". " in exam_date else "."

        # Split it and reverse it to get it in the correct order for ISO format (YYYY-MM-DD)
        # 6. 1. 2026 -> ["2026", "1", "6"]
        exam_date = exam_date.split(split_symbol)[::-1]

        # Add leading zeros if needed
        for i in range(len(exam_date)):
            exam_date[i] = exam_date[i].zfill(2)

        # Join it back together
        exam_date = "-".join(exam_date)

        # Validate the date format using regex
        is_valid_date_format = re.match(r"\d{4}-\d{2}-\d{2}", exam_date)

        if not is_valid_date_format:
            logger.warning(
                f"Exam date {exam_date} for {exam_name} in {class_name} is not in the"
                " correct format. Setting to None."
            )
            exam_date = None
        else:
            # Convert to date object
            exam_date = date.fromisoformat(exam_date)
    else:
        exam_date = None

    # Same as above
    # Just this time it splits it in time and classroom
    # Example from site: 14.45, 352 Učilnica -> ["14.45", "352 Učilnica"]
    split_symbol = ", " if ", " in exam_time_and_classroom else ","
    exam_time_and_classroom = exam_time_and_classroom.split(split_symbol)

    exam_time = ""
    exam_classroom = ""

    if len(exam_time_and_classroom) == 1:
        exam_time = exam_time_and_classroom[0]
        exam_classroom = ""
    elif len(exam_time_and_classroom) >= 2:
        exam_time = exam_time_and_classroom[0]
        # I have seen some exams with multiple classrooms for some reason
        exam_classroom = ", ".join(exam_time_and_classroom[1:])

    if exam_time != "":
        # Convert to ISO format (HH:MM)
        exam_time = exam_time.replace(".", ":")

        is_valid_time_format = re.match(r"\d{2}:\d{2}", exam_time)

        if not is_valid_time_format:
            logger.warning(
                f"Exam time {exam_time} for {exam_name} in {class_name} is not in the"
                " correct format. Setting to None."
            )
            exam_time = None
        else:
            exam_time = time.fromisoformat(exam_time)
    else:
        exam_time = None

    # Check if the exam has results available
    if exam_results:
        exam_results = exam_results["src"] == "EvidencaRez.gif"
    else:
        exam_results = False

    # Check if the exam already exists in the database
    exams = class_.exams.order_by("-date", "-time")  # type: ignore

    if not exams.filter(code=exam_code).exists():
        Exam.objects.create(
            name=exam_name,
            code=exam_code,
            date=exam_date,
            time=exam_time,
            classroom=exam_classroom,
            results_available=exam_results,
            school_class=class_,
        )
        logger.info(f"New exam {exam_name} in {class_name} has been added to the database.")
    else:
        # Check is there are any differences
        current_exam: Exam = exams.filter(code=exam_code).first()

        if (
            current_exam.name != exam_name
            or current_exam.date != exam_date
            or current_exam.time != exam_time
            or current_exam.classroom != exam_classroom
            or current_exam.results_available != exam_results
        ):
            current_exam.name = exam_name
            current_exam.date = exam_date
            current_exam.time = exam_time
            current_exam.classroom = exam_classroom
            current_exam.results_available = exam_results
            current_exam.save()

            logger.info(f"Exam {exam_name} in {class_name} has been updated.")

            # TODO: Send Email about the change
            # TODO: Maybe send email to admin if error occurs
