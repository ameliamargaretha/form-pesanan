from connect import p_db
import pandas as pd
import yagmail
import os


def send_email(temp_df,csv=None):
    keep = list(temp_df.columns)
    keep.remove('tanggal_dipesan')
    temp_df.drop_duplicates(inplace=True, subset=keep, ignore_index=True)
    temp_df.to_csv('temp.csv')
    with yagmail.SMTP(
        os.environ["GMAIL_USERNAME"], os.environ["GMAIL_PASSWORD"]
    ) as yag:
        yag.send(os.environ['RECIPIENT'], "NEW ORDER", 'attached', attachments=csv)
    os.system('rm ./temp.csv')

if __name__ == "__main__":
    df = pd.DataFrame(list(p_db.find({}, {"_id": 0})))
    df.drop_duplicates(inplace=True)
    df.to_csv("current_standing.csv", index=False)
