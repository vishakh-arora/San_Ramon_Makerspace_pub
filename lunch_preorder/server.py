from flask import Flask, request, render_template, redirect, jsonify, send_from_directory
from subprocess import call
import os, subprocess, time
import fulfill_orders

app = Flask(__name__,static_url_path='')

# @app.route('/stop')
# def stop():
#     # mosquitto_pub -d -t omnihacks -m \"record\"
#     os.system("python publish.py")
#     return render_template("STOP.html")
#
# @app.route('/start')
# def start():
#     os.system("python stopublish.py")
#     print("generating transcript")
#     global blood_pressure, heart_rate
#     # metrics = os.system("python TranscriptGeneration/transcript_create.py")
#     time.sleep(15)
#     metrics = transcript_gen()
#     print(type(metrics), len(metrics))
#     blood_pressure = str(metrics[0])
#     heart_rate = str(metrics[1])
#     print("done generating transcript")
#     print("sending email")
#     send_email()
#     print("sent email")
#     return render_template("START.html")
#
# @app.route('/metrics')
# def metrics():
#     #adafruit.main(0, blood_pressure)
#     return redirect("https://io.adafruit.com/vishakh_arora29/dashboards/omnihacks-metrics")
#
# @app.route('/transcript')
# def transcript():
#     fin = open("transcript.txt","r")
#     return fin.read()


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/refresh')
def refresh():
  return fulfill_orders.reload()

@app.route('/getorder/<orderID>')
def get_order(orderID):
  return fulfill_orders.getOrder(orderID)

@app.route('/shutdown')
def shutdown():
  fulfill_orders.write_timestamp()
  fulfill_orders.cron_write_timestamps('off')
  call("sudo shutdown -P now", shell=True)

@app.route('/write-timestamp/<onoff>')
def write_timestamps(onoff):
  return fulfill_orders.cron_write_timestamps(onoff)

@app.route('/img/<path:path>')
def showImage(path):
    return send_from_directory('images', path)

if __name__ == "__main__":
    refresh()
    app.run(debug=False)
