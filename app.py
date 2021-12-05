from re import I
from flask.scaffold import F
from flask.wrappers import Request
from requests.models import encode_multipart_formdata
from flask import Flask, render_template, request, Markup, redirect
import sched
import time
from datetime import date, datetime, timedelta
from global_vars import *
from covid_news_handling import news_API_request
from covid_data_handler import *
import threading


s = sched.scheduler(time.time, time.sleep)


app = Flask(__name__)


@app.route("/")
def root_to_index() -> render_template:

    return render_template('index.html',
                           title=Markup("<b>Smart Covid Dashboard</b>"),
                           image='image.jpg',
                           location=Markup("<b>Exeter</b>"),
                           local_7day_infections=covid_data[0],
                           nation_location=Markup("<b>England</b>"),
                           national_7day_infections=covid_data[1],
                           hospital_cases=Markup(
                               str("<b> Hospital Cases: </b>")) + str(covid_data[2]),
                           deaths_total=Markup(str("<b> Total Deaths: </b>")
                                               ) + str(covid_data[3]),
                           news_articles= news_list[0:5],
                           updates= update_list)


@app.route("/index", methods=['GET'])  # gets link
def main():
    s.run(blocking=False)

    if request.method == 'GET':

        # delete schedule
        if request.args.get("update_item"):
            which_schedule = request.args.get("update_item")
            for update in update_list:
                if update["title"] == which_schedule:
                    print("trying to cancel")
                    s.cancel(update["sched"])
                    update_list.remove(update)
                

        # delete news
        if request.args.get("notif"):
            which_news = request.args.get("notif")
            for news in news_list:
                if news["title"] == which_news:
                    print("deleted!!!")
                    news_list.remove(news)

        print("/index entered")
        time_until_alarm = 0
        if request.args.get("two"):
            content = request.args.get("update")  # get time of update
            print("IF ENTERED")
            # converting time string to datetime
            formatted_content = datetime.strptime(content, '%H:%M')

            # gets data from schedule update
            update_name = request.args.get("two")  # update name
            choice_covid = bool(request.args.get("covid-data"))
            choice_news = bool(request.args.get("news"))
            repeat_button = bool(request.args.get("repeat"))

            now = datetime.now()
            current_time = now.strftime('%H:%M')
            current_time = datetime.strptime(current_time, '%H:%M')

            time_until_alarm = formatted_content - current_time
            time_until_alarm = int(time_until_alarm.total_seconds())

            widet = (f'time of alarm: {str(content)} update covid data: {str(choice_covid)} update news data: {str(choice_news)} repeat:{str(repeat_button)}')

            updates = {"title": update_name,  # update name
                    "content": widet, 
                    "time": str(content), # time of update
                    "covid": choice_covid, # did tick covid?
                    "news": choice_news, # did tick news?
                    "repeat": repeat_button,  # did tick repeat button?
                    }  
            print(repeat_button)
            if repeat_button:
                print('Called repeat sched')
                sched = s.enter(time_until_alarm, 1, repeat_scheduler, (updates,))
            else:
                sched = s.enter(time_until_alarm, 1, update_everything, (updates,))
            updates["sched"] = sched #adds sched to updates dict

            update_list.append(updates)

            '''
            thread = threading.Thread(target = s.run)
            thread.start()
            '''

        return redirect("/", code=302)
    
    return redirect("/", code=302)


def update_everything(update):
    print("display update", update)
    print('ENTERING UPDATE')
    
    global covid_data
    if update["news"] and not update["covid"]:
        print("news stuff")
        #news_list =  news_API_request()
        for news in news_list[:6]:
            news_list.remove(news)

    elif update["covid"] and not update["news"]:
        print("covid stuff")
        covid_data = all_data()


    elif update["news"] and update["covid"]:
        print("news stuff")
        #news_list =  news_API_request()
        for news in news_list[:6]:
            news_list.remove(news)

        print("covid stuff")
        covid_data = all_data()

    print('DATA UPDATED')

    print(update['repeat'])
    if update['repeat'] == False:
        for update_val in update_list:
            if update_val["title"] == update["title"]:
                update_list.remove(update_val)
                print(update_val["title"], "has been removed")
                break
    
    print('UPDATE REMOVED')



def repeat_scheduler(update):
    

    formatted_content = datetime.strptime(update["time"], '%H:%M')
    
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_time = datetime.strptime(current_time, '%H:%M')

    time_until_alarm = formatted_content - current_time
    time_until_alarm = int(time_until_alarm.total_seconds()) + 86400
    print(time_until_alarm)
    sched = s.enter(time_until_alarm, 1, repeat_scheduler, (update,))

    update["sched"] = sched

    #Carry out updates on covid data and news 
    update_everything(update)

if __name__ == '__main__':
    news_list = news_API_request()
    covid_data = all_data()
    app.run(debug=True)
