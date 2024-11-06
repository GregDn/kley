import requests
# from dotenv import load_dotenv
import datetime
import os
import time

# load_dotenv()


# =========== Get today's date, month and year ===========
today = datetime.datetime.today()
today_month = today.month
today_year = today.year

# =========== Set current month's first day ===========
start_of_month = datetime.datetime(year=today_year,
                                   month=today_month,
                                   day=1)
print(f"start_of_month: {start_of_month}")

# =========== Set current month's last day ===========

# Here we're getting the last day of prev month. We don't know what it is or if it's a leap year,
# so we need to check four possible last dates: 31st, 30th, 29th and 28th.

try:
    end_of_month = datetime.datetime(year=today_year,
                                     month=today_month,
                                     day=31,
                                     hour=23,
                                     minute=59,
                                     second=59)
except ValueError:
    try:
        end_of_month = datetime.datetime(year=today_year,
                                         month=today_month,
                                         day=30,
                                         hour=23,
                                         minute=59,
                                         second=59)
    except ValueError:
        try:
            end_of_month = datetime.datetime(year=today_year,
                                             month=today_month,
                                             day=29,
                                             hour=23,
                                             minute=59,
                                             second=59)
        except ValueError:
            end_of_month = datetime.datetime(year=today_year,
                                             month=today_month,
                                             day=28,
                                             hour=23,
                                             minute=59,
                                             second=59)

print(f"end of month: {end_of_month}")


# =========== We'll also need dates of start and end of previous month ===========

# Here we're getting the start of prev month. If it's January, we can't just subtract, so we set the date manually
if today.month == 1:
    prev_year = (today - datetime.timedelta(days=35)).year
    start_of_prev_month = datetime.datetime(year=prev_year,
                                            month=12,
                                            day=1)

# If it's not January, we can just subtract one from month number
else:
    start_of_prev_month = datetime.datetime(year=today.year,
                                            month=today.month - 1,
                                            day=1)

start_of_prev_month_unix = time.mktime(start_of_prev_month.timetuple())


# Here we're getting the last day of prev month. We don't know what it is or if it's a leap year,
# so we need to check four possible last dates: 31st, 30th, 29th and 28th.

try:
    end_of_prev_month = datetime.datetime(year=start_of_prev_month.year,
                                          month=start_of_prev_month.month,
                                          day=31,
                                          hour=23,
                                          minute=59,
                                          second=59)
except ValueError:
    try:
        end_of_prev_month = datetime.datetime(year=start_of_prev_month.year,
                                              month=start_of_prev_month.month,
                                              day=30,
                                              hour=23,
                                              minute=59,
                                              second=59)
    except ValueError:
        try:
            end_of_prev_month = datetime.datetime(year=start_of_prev_month.year,
                                                  month=start_of_prev_month.month,
                                                  day=29,
                                                  hour=23,
                                                  minute=59,
                                                  second=59)
        except ValueError:
            end_of_prev_month = datetime.datetime(year=start_of_prev_month.year,
                                                  month=start_of_prev_month.month,
                                                  day=28,
                                                  hour=23,
                                                  minute=59,
                                                  second=59)

end_of_prev_month_unix = time.mktime(end_of_prev_month.timetuple())


# =========== Now we create a class that allows us to get, write, update and delete data in a Google sheet ===========
class DataManager:

    def __init__(self, post_stats):

        self.post_stats = post_stats
        self.sheety_endpoint = f"https://api.sheety.co/{os.environ["SHEETY_USERNAME"]}/kleyStats"
        self.headers = {
            "Authorization": f"Bearer {os.environ["SHEETY_TOKEN"]}"
        }

    def first_call_daily_sheet(self):

        """
        This method reads the data from "daily" page in a Google sheet.

        If it's empty, the method will fill it with data on posts from today to a month ago via POST request.
        Else, the method will escape.
        """

        response = requests.get(url=f"{self.sheety_endpoint}/daily", headers=self.headers)
        response.raise_for_status()

        if not response.json()["daily"]:
            # If there's no data, the method takes posts from it's "post_stats" attribute and
            # fills the table with their data.
            for post_link, post_data in self.post_stats.items():
                config = {
                    "daily": {
                        "postPreview": post_data["text"],
                        "postUrl": post_link,
                        "postDate": post_data["date"].strftime("%d.%m.%y"),
                        "sharesPerView": post_data["shares_per_view"],
                        "reactionsPerView": post_data["reactions_per_view"],
                    }
                }
                post_response = requests.post(url=f"{self.sheety_endpoint}/daily", json=config, headers=self.headers)
                post_response.raise_for_status()
                print(post_response.text)
                time.sleep(0.5)

        else:
            # If there is data, the method escapes.
            return

    def first_call_results_sheet(self):

        """
        This method reads the data from "results" page in a Google sheet.

        If it's empty, the method will fill it with data on posts from today to a month ago via POST request.
        Else, the method will escape.
        """

        response = requests.get(url=f"{self.sheety_endpoint}/results", headers=self.headers)
        response.raise_for_status()

        if not response.json()["results"]:
            # If there's no data

            if datetime.datetime(year=today_year,
                                 month=today_month,
                                 day=14) <= today <= datetime.datetime(year=today_year,
                                                                       month=today_month,
                                                                       day=16,
                                                                       hour=23,
                                                                       minute=59,
                                                                       second=59):
                # and if today's date is 14th, 15th or 16th,
                # the method takes posts from it's "post_stats" attribute and fills the table with their data.

                for post_link, post_data in self.post_stats.items():
                    config = {
                        "result": {
                            "postPreview": post_data["text"],
                            "postUrl": post_link,
                            "postDate": post_data["date"].strftime("%d.%m.%y"),
                            "sharesPerView": post_data["shares_per_view"],
                            "reactionsPerView": post_data["reactions_per_view"],
                        }
                    }
                    post_response = requests.post(url=f"{self.sheety_endpoint}/results",
                                                  json=config,
                                                  headers=self.headers)
                    post_response.raise_for_status()
                    print(post_response.text)
                    time.sleep(0.5)

            else:
                # If there's no data but the date is not 14th, 15th or 16th,
                # the method fills table with a placeholder.

                config = {
                    "result": {
                        "postPreview": "постики",
                        "postUrl": "крутятся",
                        "postDate": "просмотры",
                        "sharesPerView": "мутятся",
                        "reactionsPerView": "🤙🤙🤙",
                    }
                }
                post_response = requests.post(url=f"{self.sheety_endpoint}/results", json=config, headers=self.headers)
                post_response.raise_for_status()

        else:
            # If there is data, the method escapes.
            return

    def update_daily(self):

        """
        This method reads data from "daily" sheet and updates it. If there's no data, the method escapes.

        Post are updated following the logic:

        1. The method finds outdated posts by looking for links that are in the sheet, but
        not in the "post_stats" attribute. These links are older than one month,
        so the rows, containing them, should be deleted via DELETE request.

        2. After deletion, the method finds posts that need to be updated via PUT request
        by looking for links that are in the sheet and in the "post_stats" attribute.

        3. In the end the method finds new posts by looking for links that are not in the sheet,
        but in the "post_stats" attribute. These posts should be added to sheet via POST request.
        """

        response = requests.get(url=f"{self.sheety_endpoint}/daily", headers=self.headers)
        response.raise_for_status()

        if not response.json()["daily"]:
            return

        else:

            # Step 1: Check what post from table are not in the response from API.

            table_post_links_and_ids = {row["postUrl"]: row["id"] for row in response.json()["daily"]}

            rows_to_clear = [row_id for url, row_id in table_post_links_and_ids.items() if url not in self.post_stats]

            for i in range(len(rows_to_clear)):

                resp = requests.get(url=f"{self.sheety_endpoint}/daily", headers=self.headers)
                table_data = {row["postUrl"]: row["id"] for row in resp.json()["daily"]}

                actual_rows_to_clear = [row_id for url, row_id in table_data.items() if url not in self.post_stats]

                del_response = requests.delete(url=f"{self.sheety_endpoint}/daily/{actual_rows_to_clear[0]}",
                                               headers=self.headers)
                del_response.raise_for_status()

                time.sleep(0.5)

            # Step 2: Update posts, that are in both dictionaries

            response_after_del = requests.get(url=f"{self.sheety_endpoint}/daily", headers=self.headers)
            response_after_del.raise_for_status()

            table_post_links_and_ids_after_del = {row["postUrl"]: row["id"] for row
                                                  in response_after_del.json()["daily"]}
            rows_to_update = {row_id: url for url, row_id
                              in table_post_links_and_ids_after_del.items()
                              if url in self.post_stats}
            for id_, post_url in rows_to_update.items():

                put_config = {
                    "daily": {
                        "postPreview": self.post_stats[post_url]["text"],
                        "postUrl": post_url,
                        "postDate": self.post_stats[post_url]["date"].strftime("%d.%m.%y"),
                        "sharesPerView": self.post_stats[post_url]["shares_per_view"],
                        "reactionsPerView": self.post_stats[post_url]["reactions_per_view"],
                    }
                }

                put_response = requests.put(url=f"{self.sheety_endpoint}/daily/{id_}",
                                            json=put_config,
                                            headers=self.headers)
                put_response.raise_for_status()
                time.sleep(0.5)

            # Step 3: Add rows with new posts

            posts_to_add = [link for link, post_data
                            in self.post_stats.items()
                            if link not in table_post_links_and_ids_after_del]
            for post_link in posts_to_add:

                post_config = {
                    "daily": {
                        "postPreview": self.post_stats[post_link]["text"],
                        "postUrl": post_link,
                        "postDate": self.post_stats[post_link]["date"].strftime("%d.%m.%y"),
                        "sharesPerView": self.post_stats[post_link]["shares_per_view"],
                        "reactionsPerView": self.post_stats[post_link]["reactions_per_view"],
                    }
                }
                post_response = requests.post(url=f"{self.sheety_endpoint}/daily",
                                              json=post_config,
                                              headers=self.headers)
                post_response.raise_for_status()
                time.sleep(0.5)

    def update_results(self):

        """
        This method reads data from "results" sheet and updates it. If there's no data, the method escapes.

        Post are updated following the logic:

        1. If today's date is not 14th, 15th or 16th, the method deletes all rows in the sheet and writes a placeholder

        2. Else, the method checks for placeholder. If it finds it, it deletes the placeholder and
        fills the sheet with data on posts dated from start to end of previous month.

        3. If there's no placeholder, then there's data in the sheet, thus it needs to be updated via PUT request.
        """

        response = requests.get(url=f"{self.sheety_endpoint}/results", headers=self.headers)
        response.raise_for_status()
        print(response.json())

        if datetime.datetime(year=today_year,
                             month=today_month,
                             day=14) <= today <= datetime.datetime(year=today_year,
                                                                   month=today_month,
                                                                   day=16,
                                                                   hour=23,
                                                                   minute=59,
                                                                   second=59):

            if response.json()["results"][0]["postPreview"] == "постики":
                del_response = requests.delete(url=f"{self.sheety_endpoint}/results/2", headers=self.headers)
                del_response.raise_for_status()

                for post_url, post_data in self.post_stats.items():
                    post_config = {
                        "result": {
                                "postPreview": post_data["text"],
                                "postUrl": post_url,
                                "postDate": post_data["date"].strftime("%d.%m.%y"),
                                "sharesPerView": post_data["shares_per_view"],
                                "reactionsPerView": post_data["reactions_per_view"],
                            }
                    }

                    post_response = requests.post(url=f"{self.sheety_endpoint}/results",
                                                  json=post_config,
                                                  headers=self.headers)
                    post_response.raise_for_status()
                    time.sleep(0.5)

            else:

                table_post_links_and_ids = {row["postUrl"]: row["id"] for row in response.json()["results"]}

                for post_url, row_id in table_post_links_and_ids.items():
                    put_config = {
                        "result": {
                            "sharesPerView": self.post_stats[f"{post_url}"]["shares_per_view"],
                            "reactionsPerView": self.post_stats[f"{post_url}"]["reactions_per_view"],
                        }
                    }

                    put_response = requests.put(url=f"{self.sheety_endpoint}/results/{row_id}",
                                                json=put_config,
                                                headers=self.headers)
                    put_response.raise_for_status()
                    time.sleep(0.5)

        else:

            if response.json()["results"][0]["postPreview"] != "постики":

                for i in range(len(response.json()["results"])):
                    del_resp = requests.delete(url=f"{self.sheety_endpoint}/results/2", headers=self.headers)
                    del_resp.raise_for_status()

                post_cfg = {
                    "result": {
                        "postPreview": "постики",
                        "postUrl": "крутятся",
                        "postDate": "просмотры",
                        "sharesPerView": "мутятся",
                        "reactionsPerView": "🤙🤙🤙",
                    }
                }

                pst_response = requests.post(url=f"{self.sheety_endpoint}/results", json=post_cfg, headers=self.headers)
                pst_response.raise_for_status()
