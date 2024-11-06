import requests
import datetime as dt
from dotenv import load_dotenv
import os
import time

load_dotenv()

# =========== Get today's date ===========
today = dt.datetime.today()  # dt.datetime(year=2024, month=10, day=16, hour=10)
today_unix = time.mktime(today.timetuple())

# =========== Calculate which date it was a month ago ===========
a_month_ago = today - dt.timedelta(days=31)
a_month_ago_unix = time.mktime(a_month_ago.timetuple())


# =========== We'll need dates of start and end of previous month ===========

# Here we're getting the start of prev month. If it's January, we can't just subtract, so we set the date manually
if today.month == 1:
    prev_year = (today - dt.timedelta(days=35)).year
    start_of_prev_month = dt.datetime(year=prev_year,
                                      month=12,
                                      day=1)


# If it's not January, we can just subtract one from month number
else:
    start_of_prev_month = dt.datetime(year=today.year,
                                      month=today.month - 1,
                                      day=1)

start_of_prev_month_unix = time.mktime(start_of_prev_month.timetuple())


# Here we're getting the last day of prev month. We don't know what it is or if it's a leap year,
# so we need to check four possible last dates: 31st, 30th, 29th and 28th.

try:
    end_of_prev_month = dt.datetime(year=start_of_prev_month.year,
                                    month=start_of_prev_month.month,
                                    day=31,
                                    hour=23,
                                    minute=59,
                                    second=59)
except ValueError:
    try:
        end_of_prev_month = dt.datetime(year=start_of_prev_month.year,
                                        month=start_of_prev_month.month,
                                        day=30,
                                        hour=23,
                                        minute=59,
                                        second=59)
    except ValueError:
        try:
            end_of_prev_month = dt.datetime(year=start_of_prev_month.year,
                                            month=start_of_prev_month.month,
                                            day=29,
                                            hour=23,
                                            minute=59,
                                            second=59)
        except ValueError:
            end_of_prev_month = dt.datetime(year=start_of_prev_month.year,
                                            month=start_of_prev_month.month,
                                            day=28,
                                            hour=23,
                                            minute=59,
                                            second=59)

end_of_prev_month_unix = time.mktime(end_of_prev_month.timetuple())


# =========== Now we create a class that allows us to get data on different posts, sort it and calculate stats =========
class StatCalculator:

    def __init__(self):
        self.tgstat_token = os.environ["TG_STATS_TOKEN"]
        self.posts_from_channel_endpoint = "https://api.tgstat.ru/channels/posts"
        self.posts_stats_endpoint = "https://api.tgstat.ru/posts/stat"
        self.daily_posts = {}
        self.monthly_posts = {}

    def get_daily_posts_data(self):

        """
        This method retrieves data on posts dated from today to one month prior from TGStat API.
        Some posts go directly to posts dict (self.daily_posts), some are returned in a separate dict.

        Note that every mediafile in Telegram channel has its own link. We can tell, if some links are actually just
        different photos//videos in a single post, by looking at "group_id" attribute.

        If it's None, the method adds that post link, date and text to posts dictionary (self.daily_posts).
        Else (if it's anything but None), the method stores it in a dictionary,
        where all posts are grouped by their "group_id" attribute. At the end, the method returns that dictionary.
        """

        # Maximum number of posts returned in a single API call is 50. So, to get data on all post for one month,
        # we need to repeatedly call the API.

        offset = 0
        limit = 50
        count = 50
        links_and_dates = {}

        while count == limit:
            # If we get 50 posts in response to API call, it probably means, that we didn't get all the posts.
            # So we increase offset by limit (by 50) and repeat the call until we get a count which is less than limit.
            # If the number of posts is divisible by 50 with no remainder, the function will catch it and escape.

            get_posts_from_channel_params = {
                "token": self.tgstat_token,
                "channelId": "t.me/kleymedia",
                "startTime": a_month_ago_unix,
                "endTime": today_unix,
                "limit": limit,
                "offset": offset,
                "hideForwards": 1,
                "hideDeleted": 1,
                # "extended": 1,
            }

            posts_response = requests.get(url=self.posts_from_channel_endpoint, params=get_posts_from_channel_params)

            if posts_response.status_code != 200:
                print(f"API call error. Response code: {posts_response.status_code}")
                return
            print(posts_response.text)
            print(posts_response.json())
            print('============================')

            if posts_response.json()["response"]["count"] == 0:
                return

            posts_data = posts_response.json()["response"]["items"]

            for post in posts_data:
                if post["group_id"] is None:
                    self.daily_posts[post["link"]] = {
                        "date": dt.datetime.fromtimestamp(float(post["date"])),
                        "text": post["text"],
                    }

                elif post["group_id"] not in links_and_dates:
                    links_and_dates[post["group_id"]] = [
                        {
                            "date": dt.datetime.fromtimestamp(float(post["date"])),
                            "link": post["link"],
                            "text": post["text"],
                        }
                    ]

                else:
                    links_and_dates[post["group_id"]].append(
                        {
                            "date": dt.datetime.fromtimestamp(float(post["date"])),
                            "link": post["link"],
                            "text": post["text"],
                        }
                    )

            offset += count
            count = posts_response.json()["response"]["count"]
            time.sleep(1)

        return links_and_dates

    def get_monthly_posts_data(self):

        """
        This method retrieves data on posts dated from the start to the end of last month from TGStat API.
        Some posts go directly to monthly posts dict (self.monthly_posts), some are returned in a separate dict.

        Note that every mediafile in Telegram channel has its own link. We can tell, if some links are actually just
        different photos//videos in a single post, by looking at "group_id" attribute.

        If it's None, the method adds that post link, date and text to posts dictionary (self.monthly_posts).
        Else (if it's anything but None), the method stores it in a dictionary,
        where all posts are grouped by their "group_id" attribute. At the end, the method returns that dictionary.
        """

        # Maximum number of posts returned in a single API call is 50. So, to get data on all post for one month,
        # we need to repeatedly call the API.

        offset = 0
        limit = 50
        count = 50
        links_and_dates = {}

        if not dt.datetime(year=today.year,
                           month=today.month,
                           day=14) <= today <= dt.datetime(year=today.year,
                                                           month=today.month,
                                                           day=16,
                                                           hour=23,
                                                           minute=59,
                                                           second=59):
            print("wrong date")
            return links_and_dates

        else:

            while count == limit:
                # If we get 50 posts in response to API call, it probably means, that we didn't get all the posts.
                # So we repeat the call until we get a count which is less than limit.
                # If the number of posts is divisible by 50 with no remainder, the function will catch it and escape.

                get_posts_from_channel_params = {
                    "token": self.tgstat_token,
                    "channelId": "t.me/kleymedia",
                    "startTime": start_of_prev_month_unix,
                    "endTime": end_of_prev_month_unix,
                    "limit": limit,
                    "offset": offset,
                    "hideForwards": 1,
                    "hideDeleted": 1,
                    # "extended": 1,
                }

                posts_response = requests.get(url=self.posts_from_channel_endpoint,
                                              params=get_posts_from_channel_params)

                if posts_response.status_code != 200:
                    print(f"API call error. Response code: {posts_response.status_code}")
                    return

                if posts_response.json()["response"]["count"] == 0:
                    return

                posts_data = posts_response.json()["response"]["items"]

                for post in posts_data:
                    if post["group_id"] is None:
                        self.monthly_posts[post["link"]] = {
                            "date": dt.datetime.fromtimestamp(float(post["date"])),
                            "text": post["text"],
                        }

                    elif post["group_id"] not in links_and_dates:
                        links_and_dates[post["group_id"]] = [
                            {
                                "date": dt.datetime.fromtimestamp(float(post["date"])),
                                "link": post["link"],
                                "text": post["text"],
                            }
                        ]

                    else:
                        links_and_dates[post["group_id"]].append(
                            {
                                "date": dt.datetime.fromtimestamp(float(post["date"])),
                                "link": post["link"],
                                "text": post["text"],
                            }
                        )

                offset += count
                count = posts_response.json()["response"]["count"]
                time.sleep(1)

            return links_and_dates

    def find_first_link(self, posts_dict: dict, mode: str):

        """
        This method receives a dictionary of posts grouped by their "group_id" attribute,
        finds the link with the smallest number in its link
        and adds this posts link, date and text to the posts dictionary.

        If the mode parameter is set to "daily", the method saves these link,
        date and text to daily dictionary (self.daily_posts).
        If it's set to "monthly", data is saved to monthly dictionary (self.monthly_posts).

        We do this since same "group_id" indicates, that different links refer to different mediafiles in a single post.
        But only the first link (i.e. the link with the smallest number after /) has reactions, shares etc.
        """

        if posts_dict == {}:
            return

        else:

            for gr_id, pst_specs in posts_dict.items():

                links = [post["link"] for post in pst_specs]
                link_ints = [int(link.split("/")[-1]) for link in links]
                min_link = min(link_ints)

                first_link = links[link_ints.index(min_link)]
                first_link_date = [post["date"] for post in pst_specs if post["link"] == first_link][0]
                first_link_text = [post["text"] for post in pst_specs if post["link"] == first_link][0]

                if mode == "daily":
                    self.daily_posts[first_link] = {
                        "date": first_link_date,
                        "text": first_link_text
                    }

                elif mode == "monthly":
                    self.monthly_posts[first_link] = {
                        "date": first_link_date,
                        "text": first_link_text
                    }

    def cut_text(self, posts_dict: dict):

        """
        This method receives a dictionary of posts and redacts the "text" attribute of each item in dictionary.

        The resulting text is first ten words from the original text, followed by ellipsis (...).

        If the post has no text, the resulting text will be: "*пост без текста*".
        """

        if posts_dict == {}:
            return

        else:

            for post_link, post_data in posts_dict.items():

                string_list = []

                for word in post_data["text"].split():

                    temp1 = word.split(">")
                    # temp2 = ""

                    if temp1[-1] == "":
                        temp2 = temp1[0]
                    else:
                        temp2 = temp1[-1]

                    temp3 = temp2.split("<")[0]
                    string_list.append(temp3)

                text_redacted = " ".join(string_list[:10])
                if text_redacted == "":
                    text_redacted = "*пост без текста*"
                else:
                    text_redacted += "..."

                post_data["text"] = text_redacted

    def order_post_chronologically(self, mode: str):

        """
        This method reorders the posts dictionary so that posts are stored in chronological order.

        If the "mode" parameter is set to "daily", the method reorders daily dictionary.
        If "mode" is set to "monthly", the monthly dictionary is reordered.
        """

        if mode == "daily":
            copied_dict = self.daily_posts.copy()
        elif mode == "monthly":
            if self.monthly_posts == {}:
                return
            copied_dict = self.monthly_posts.copy()

        flipped_dict = {}
        ordered_dict = {}

        for link, data in copied_dict.items():
            if data["date"] not in flipped_dict:
                flipped_dict[data["date"]] = [
                    {"link": link,
                     "text": data["text"],
                     }
                ]
            else:
                flipped_dict[data["date"]].append(
                    {
                        "link": link,
                        "text": data["text"]
                    }
                )

        while len(flipped_dict) != 0:
            min_dt = today
            for date, data in flipped_dict.items():
                if date < min_dt:
                    min_dt = date
            for post in flipped_dict[min_dt]:
                ordered_dict[post["link"]] = {
                    "date": min_dt,
                    "text": post["text"]
                }

            flipped_dict.pop(min_dt)

        if mode == "daily":
            self.daily_posts = ordered_dict
        elif mode == "monthly":
            self.monthly_posts = ordered_dict

    def calculate_posts_stats(self, posts_dict: dict):

        """
        This method takes data from posts dict and gets data on every post by calling the TGStat API.

        It then calculates share_per_view and reactions_per_view proportions, rounds them and
        returns them in a dictionary together with post link, date and text.
        """

        if posts_dict == {}:
            return

        post_stats = {}

        for post_link, post_date_and_text in posts_dict.items():

            get_posts_stats_params = {
                "token": os.environ["TG_STATS_TOKEN"],
                "postId": post_link,
            }

            post_response = requests.get(url=self.posts_stats_endpoint, params=get_posts_stats_params)
            post_data = post_response.json()["response"]

            views_count = post_data["viewsCount"]
            shares_count = post_data["sharesCount"]
            reactions_count = post_data["reactionsCount"]

            share_per_view = round(shares_count / views_count * 100, 2)
            reaction_per_view = round(reactions_count / views_count * 100, 2)

            post_stats[f"{post_link}"] = {
                "shares_per_view": share_per_view,
                "reactions_per_view": reaction_per_view,
                "date": post_date_and_text["date"],
                "text": post_date_and_text["text"],
            }

        return post_stats
