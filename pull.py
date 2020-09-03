from connect import p_db
import pandas as pd
import yagmail
import os


def send_email(csv):
    with yagmail.SMTP(
        os.environ["GMAIL_USERNAME"], os.environ["GMAIL_PASSWORD"]
    ) as yag:
        yag.send(os.environ['RECIPIENT'], "NEW ORDER", 'attached', attachments=csv)


if __name__ == "__main__":
    df = pd.DataFrame(list(p_db.find({}, {"_id": 0})))
    df.to_csv("current_standing.csv", index=False)
