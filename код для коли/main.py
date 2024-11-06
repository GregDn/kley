import posts_getter
import data_manager

stats_calculator = posts_getter.StatCalculator()

raw_daily_posts_data = stats_calculator.get_daily_posts_data()
raw_monthly_posts_data = stats_calculator.get_monthly_posts_data()

stats_calculator.find_first_link(raw_daily_posts_data, "daily")
stats_calculator.find_first_link(raw_monthly_posts_data, "monthly")

stats_calculator.cut_text(stats_calculator.daily_posts)
stats_calculator.cut_text(stats_calculator.monthly_posts)

stats_calculator.order_post_chronologically("daily")
stats_calculator.order_post_chronologically("monthly")

daily_post_stats = stats_calculator.calculate_posts_stats(stats_calculator.daily_posts)
monthly_post_stats = stats_calculator.calculate_posts_stats(stats_calculator.monthly_posts)

daily_data_manager = data_manager.DataManager(daily_post_stats)
monthly_data_manager = data_manager.DataManager(monthly_post_stats)

daily_data_manager.first_call_daily_sheet()
monthly_data_manager.first_call_results_sheet()

daily_data_manager.update_daily()
monthly_data_manager.update_results()
