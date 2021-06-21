from flask import Flask,render_template,Response,url_for,request
from camera import VideoCamera
from camMobile import VideoCameraMob
import urllib.request
from pyzbar import pyzbar
import argparse
import datetime
import time
import cv2
import tablib
import os
import pandas as pd
from datetime import date
glatt=[]
found=[]
checkPer=[]
ap = argparse.ArgumentParser()
ap.add_argument("-o","--output",type=str,default="Attendance.csv",help="path")
args = vars(ap.parse_args())
csv = open(args["output"],"w")
app=Flask(__name__)
dataset1 = tablib.Dataset()
dataset3 = tablib.Dataset()

@app.route('/')
def index():
	with open(os.path.join(os.path.dirname(__file__), 'Details.csv')) as f:
		dataset1.csv = f.read()
	
	
	with open(os.path.join(os.path.dirname(__file__), 'Attendance.csv')) as h:
		dataset3.csv = h.read()
	per=0	
	d1 = dataset1.html
	d3 = dataset3.html
	fn=''
	ln=''
	em=''
	mo=''
	peratt=''
	dlen = pd.read_csv('Details.csv')
	total=dlen.shape[0]
	per = (len(found)/total)*100
	if len(found)!=0:
		id = found[-1]
	else:
		id =None
	if id!=None:
		df1=pd.read_csv('Details.csv')
		for index,row in df1.iterrows():
			if row['Id']==id:
				fn=row['First Name']
				ln=row['Last Name']
				em=row['Email Id']
				mo=row['Mobile No']
	if len(glatt)==0:
		msgAtt=''
	else:

		msgAtt='The Attendance percentage of '+str(checkPer[-1])+' is '+str(glatt[-1])+'%'
		peratt=checkPer[-1]

	
	return render_template('index.html', data1=d1, data3=d3,id=id,FName=fn,LName=ln,email=em,mobile=mo,per=round(per,2),msgAtt=msgAtt,peratt=peratt,todate=date.today().strftime('%d-%m-%Y'))


def gen(camera):
	while True:
		frame=camera.get_frame()
		barcodes = pyzbar.decode(frame)
		for barcode in barcodes:
			(x, y, w, h) = barcode.rect
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
			barcodeData = barcode.data.decode("utf-8")
			barcodeType = barcode.type
			text = "{} ({})".format(barcodeData, barcodeType)
			cv2.putText(frame, text, (x, y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
			with app.app_context():			
				if barcodeData not in found:
					openFile=pd.read_csv('Details.csv')
					FirstName = ' '
					LastName = ' '
					FullName = ' '
					for index,row in openFile.iterrows():
						if row['Id']==barcodeData:
							FirstName = row['First Name']
							LastName = row['Last Name']
							FullName = FirstName + " "+ LastName
					csv.write("{},{},{}\n".format(datetime.datetime.now().strftime('%d-%m-%Y %H:%M'),barcodeData, FullName))
					csv.flush()
					found.append(barcodeData)
					dataDetails = pd.read_csv('Attendee.csv')
					today=date.today()
					d=today.strftime('%d-%m-%Y')
					for index,row in dataDetails.iterrows():
						if row['Id']==barcodeData:
							row[d]='P'
					
					dataDetails.to_csv(r'./Attendee.csv',index=False)
							
					
					
		ret,jpeg=cv2.imencode('.jpg',frame)
		jpeg=jpeg.tobytes()
		yield (b'--frame\r\n'b'Content-Type:image/jpeg\r\n\r\n'+jpeg+b'\r\n\r\n')
		
	csv.close()

def genCam(camMobile):
	while True:
		frame=camMobile.get_frame()
		barcodes = pyzbar.decode(frame)
		for barcode in barcodes:
			(x, y, w, h) = barcode.rect
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
			barcodeData = barcode.data.decode("utf-8")
			barcodeType = barcode.type
			text = "{} ({})".format(barcodeData, barcodeType)
			cv2.putText(frame, text, (x, y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
			with app.app_context():			
				if barcodeData not in found:
					openFile=pd.read_csv('Details.csv')
					FirstName = ' '
					LastName = ' '
					FullName = ' '
					for index,row in openFile.iterrows():
						if row['Id']==barcodeData:
							FirstName = row['First Name']
							LastName = row['Last Name']
							FullName = FirstName + " "+ LastName
					csv.write("{},{},{}\n".format(datetime.datetime.now().strftime('%d-%m-%Y %H:%M'),barcodeData, FullName))
					csv.flush()
					found.append(barcodeData)
					dataDetails = pd.read_csv('Attendee.csv')
					today=date.today()
					d=today.strftime('%d-%m-%Y')
					for index,row in dataDetails.iterrows():
						if row['Id']==barcodeData:
							row[d]='P'
					
					dataDetails.to_csv(r'./Attendee.csv',index=False)
							
					
					
		ret,jpeg=cv2.imencode('.jpg',frame)
		jpeg=jpeg.tobytes()
		yield (b'--frame\r\n'b'Content-Type:image/jpeg\r\n\r\n'+jpeg+b'\r\n\r\n')
		
	csv.close()



@app.route('/response',methods=['POST'])
def response():
	idNo = request.form['ID']
	FName = request.form['First_Name']
	LName = request.form['Last_Name']
	Email = request.form['Email_Id']
	Mobile = request.form['Mobile_Number']
	isThere = False
	df1=pd.read_csv('Details.csv')
	for index,row in df1.iterrows():
		if row['Id']==idNo:
			
			isThere=True
			return render_template('response.html',msg="Already Exists")
	if isThere!=True:
		df2=pd.DataFrame({'Id':[idNo],'First Name':[FName],'Last Name':[LName],'Email Id':[Email],'Mobile No':[Mobile]})
		dff=df1.append(df2,ignore_index=True,sort=False)
		dff.to_csv(r'./Details.csv',index=False)
		
		return render_template('response.html',msg="Success")

@app.route('/responseMob',methods=['POST'])
def responseMob():
	idNo = request.form['ID']
	FName = request.form['First_Name']
	LName = request.form['Last_Name']
	Email = request.form['Email_Id']
	Mobile = request.form['Mobile_Number']
	isThere = False
	df1=pd.read_csv('Details.csv')
	for index,row in df1.iterrows():
		if row['Id']==idNo:
			
			isThere=True
			return render_template('responseMob.html',msg="Already Exists")
	if isThere!=True:
		df2=pd.DataFrame({'Id':[idNo],'First Name':[FName],'Last Name':[LName],'Email Id':[Email],'Mobile No':[Mobile]})
		dff=df1.append(df2,ignore_index=True,sort=False)
		dff.to_csv(r'./Details.csv',index=False)
		
		return render_template('responseMob.html',msg="Success")


@app.route('/from_to_mob',methods=['POST'])
def from_to_mob():
	id_Name=request.form['Id_Name']
	checkPer.append(id_Name)
	day = request.form['from_day']
	month=request.form['from_Month']
	year = request.form['from_Year']
	fromdate = day+'-'+month+'-'+year
	day = request.form['to_day']
	month=request.form['to_Month']
	year = request.form['to_Year']
	todate = day+'-'+month+'-'+year
	print(fromdate,'\n',todate)
	AttendData = pd.read_csv('Attendee.csv')
	for index,row in AttendData.iterrows():
		if row['Id']==id_Name:			
			lt=list(row[fromdate:todate])
			p=lt.count('P')
			a=lt.count('A')
			attper=(p/(p+a))*100
			glatt.append(round(attper,2))
	return render_template('from_to_mob.html')			 
	
@app.route('/front',methods=['POST'])
def front():
	return render_template('front.html')
@app.route('/from_to',methods=['POST'])
def from_to():
	id_Name=request.form['Id_Name']
	checkPer.append(id_Name)
	day = request.form['from_day']
	month=request.form['from_Month']
	year = request.form['from_Year']
	fromdate = day+'-'+month+'-'+year
	day = request.form['to_day']
	month=request.form['to_Month']
	year = request.form['to_Year']
	todate = day+'-'+month+'-'+year
	print(fromdate,'\n',todate)
	AttendData = pd.read_csv('Attendee.csv')
	for index,row in AttendData.iterrows():
		if row['Id']==id_Name:			
			lt=list(row[fromdate:todate])
			p=lt.count('P')
			a=lt.count('A')
			attper=(p/(p+a))*100
			glatt.append(round(attper,2))
	return render_template('from_to.html')			 
	
	
@app.route('/cam',methods=['POST','GET'])
def cam():
	return render_template('cam.html')

@app.route('/goDesk',methods=['POST','GET'])
def goDesk():
	with open(os.path.join(os.path.dirname(__file__), 'Details.csv')) as f:
		dataset1.csv = f.read()
	
	
	with open(os.path.join(os.path.dirname(__file__), 'Attendance.csv')) as h:
		dataset3.csv = h.read()
	per=0	
	d1 = dataset1.html
	d3 = dataset3.html
	fn=''
	ln=''
	em=''
	mo=''
	peratt=''
	dlen = pd.read_csv('Details.csv')
	total=dlen.shape[0]
	per = (len(found)/total)*100
	if len(found)!=0:
		id = found[-1]
	else:
		id =None
	if id!=None:
		df1=pd.read_csv('Details.csv')
		for index,row in df1.iterrows():
			if row['Id']==id:
				fn=row['First Name']
				ln=row['Last Name']
				em=row['Email Id']
				mo=row['Mobile No']
	if len(glatt)==0:
		msgAtt=''
	else:

		msgAtt='The Attendance percentage of '+str(checkPer[-1])+' is '+str(glatt[-1])+'%'
		peratt=checkPer[-1]

	
	return render_template('index.html', data1=d1, data3=d3,id=id,FName=fn,LName=ln,email=em,mobile=mo,per=round(per,2),msgAtt=msgAtt,peratt=peratt,todate=date.today().strftime('%d-%m-%Y'))


@app.route('/reg',methods=['POST','GET'])
def reg():
	if len(found)!=0:
		id = found[-1]
	else:
		id =None
	fn=''
	ln=''
	em=''
	mo=''
	if id!=None:
		df1=pd.read_csv('Details.csv')
		for index,row in df1.iterrows():
			if row['Id']==id:
				fn=row['First Name']
				ln=row['Last Name']
				em=row['Email Id']
				mo=row['Mobile No']
	return render_template('reg.html',id=id,FName=fn,LName=ln,email=em,mobile=mo)

@app.route('/att',methods=['POST','GET'])
def att():
	with open(os.path.join(os.path.dirname(__file__), 'Details.csv')) as f:
		dataset1.csv = f.read()
	with open(os.path.join(os.path.dirname(__file__), 'Attendance.csv')) as h:
		dataset3.csv = h.read()
	d1 = dataset1.html
	d3 = dataset3.html
	per=0	
	peratt=''
	dlen = pd.read_csv('Details.csv')
	total=dlen.shape[0]
	per = (len(found)/total)*100
	if len(glatt)==0:
		msgAtt=''
	else:

		msgAtt='The Attendance percentage of '+str(checkPer[-1])+' is '+str(glatt[-1])+'%'
		peratt=checkPer[-1]
	return render_template('att.html',data1=d1,data3=d3,per=round(per,2),msgAtt=msgAtt,peratt=peratt,todate=date.today().strftime('%d-%m-%Y'))

@app.route('/video_feed_mob')
def video_feed_mob():
	
	return Response(genCam(VideoCameraMob()),mimetype='multipart/x-mixed-replace;boundary=frame')


@app.route('/video_feed')
def video_feed():
	
	return Response(gen(VideoCamera()),mimetype='multipart/x-mixed-replace;boundary=frame')

@app.route('/red',methods=['POST','GET'])	
def red():
	return render_template('cam.html')


if __name__=='__main__':
	app.run(host='0.0.0.0',debug=True)

