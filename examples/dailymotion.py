from kaiiddo_dld.dailymotion import DailymotionDL

url = input("Enter Dailymotion URL: ")
info = DailymotionDL().fetch_info(url)
print(info)
