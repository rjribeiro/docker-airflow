# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from airflow.operators.bash_operator import BashOperator
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from fipe import FipeSpider


def extract():
    today_ = datetime.today()
    feed = {
        f"/home/rafa/Documents/docker-airflow/data/{today_.year}_{today_.month}.csv": {
            'format': 'csv',
            'encoding': 'utf8'
        }
    }
    settings = {"FEED": feed,
                "LOG_LEVEL": "INFO",
                "DOWNLOAD_DELAY": 1}

    process = CrawlerProcess(settings)
    process.crawl(FipeSpider, ano=today_.year, mes=today_.month)
    process.start()


def load():
    today_ = datetime.today()
    print("extracao concluida")


# default_args = {
#     "owner": "Rafael Junior Ribeiro",
#     "start_date": datetime(2021, 2, 7),
# }
# dag = DAG("fipe", default_args=default_args, schedule_interval="16 * * * *")
# today = datetime.today()
#
# extract_task = PythonOperator(task_id="extract_task",
#                               python_callable=extract,
#                               dag=dag)
#
# load_task = BashOperator(task_id="load_task",
#                          bash_command="""echo "extracao feita"! """,
#                          dag=dag)
#
# extract_task >> load_task
